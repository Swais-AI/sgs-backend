"""
Connection-pool sizing, derived rather than hand-set.

The pool is elastic: `pool_size` is the *idle floor* and `max_overflow` is burst
headroom. A quiet service holds one connection; a busy one grows and then
releases. Nothing needs retuning as traffic changes.

The ceiling is computed at startup from the database's own `max_connections`
divided by the number of workers sharing it, so resizing the instance or moving
to a school with a bigger database needs no code change — only DB_SERVICE_SLOTS
moves, and only when the number of services or workers changes.

Reference implementation. The other backends should copy this file; the
psycopg_pool and node-postgres equivalents use the same two numbers.
"""

import logging
import math
import os

from sqlalchemy import create_engine, text

log = logging.getLogger(__name__)

# How many *workers* share this database — not services. Four uvicorn workers
# across six APIs is 24, not 6. Getting this wrong is how you solve a
# concurrency problem by recreating a connection problem.
SLOTS = int(os.getenv("DB_SERVICE_SLOTS", "12"))

# Held back for migrations, pgAdmin and the superuser reserve. An instance run
# to its limit locks out the very sessions needed to diagnose it.
RESERVE = float(os.getenv("DB_RESERVE", "0.2"))

# Used only when the startup probe cannot reach the database. Deliberately
# small: a service that cannot measure should not assume it has room.
FALLBACK_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS_FALLBACK", "80"))


def _max_connections(url: str) -> int:
    """Ask the server its own limit. Never fatal — a service must still boot."""
    probe = None
    try:
        probe = create_engine(url, connect_args={"connect_timeout": 5})
        with probe.connect() as conn:
            return int(conn.execute(text("SHOW max_connections")).scalar())
    except Exception as exc:
        log.warning(
            "Could not read max_connections (%s); assuming %d",
            exc, FALLBACK_MAX_CONNECTIONS,
        )
        return FALLBACK_MAX_CONNECTIONS
    finally:
        if probe is not None:
            probe.dispose()


def build_engine(url: str, service: str):
    """An engine whose ceiling is this worker's fair share of the database."""
    share = max(2, math.floor(_max_connections(url) * (1 - RESERVE) / SLOTS))

    log.info("DB pool for %s: idle 1, burst to %d (slots=%d)", service, share, SLOTS)

    return create_engine(
        url,
        # Idle floor of one. With N workers the baseline cost is N connections,
        # not N x pool_size — which is what exhausted the shared instance.
        pool_size=1,
        max_overflow=share - 1,
        # Drop connections the network already killed, instead of handing a
        # dead one to a request.
        pool_pre_ping=True,
        # Rotate before RDS or the NAT gateway closes them silently.
        pool_recycle=1800,
        # Fail fast rather than hanging the request behind an exhausted pool.
        pool_timeout=10,
        # So pg_stat_activity names the culprit instead of showing a dozen
        # identical rows.
        connect_args={"application_name": service},
    )
