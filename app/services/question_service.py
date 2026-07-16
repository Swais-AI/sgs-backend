"""
Question extraction service — read questions out of an uploaded PDF question
paper so Auto-Correct can grade real answers (no mock, no dedicated table).

Flow: PDF bytes -> text (pdfplumber) -> structured questions.
Primary parse uses the existing AI service; regex is the offline fallback.
"""

import io
import re
import json
from typing import List, Dict

import pdfplumber

from app.services.ai_service import _chat


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a (text-based) PDF."""
    parts: List[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def _coerce_questions(data) -> List[Dict]:
    if not isinstance(data, list):
        return []
    out: List[Dict] = []
    for i, q in enumerate(data):
        if not isinstance(q, dict):
            continue
        text = (q.get("question") or q.get("text") or "").strip()
        if not text:
            continue
        try:
            marks = int(q.get("maxMarks") or q.get("marks") or q.get("max_marks") or 1)
        except (TypeError, ValueError):
            marks = 1
        qtype = str(q.get("type") or "short").lower()
        if qtype not in ("mcq", "short", "long"):
            qtype = "short"
        options = q.get("options") if isinstance(q.get("options"), list) else []
        out.append({
            "id": len(out) + 1,
            "question": text,
            "maxMarks": max(1, marks),
            "type": qtype,
            "options": options,
        })
    return out


def _parse_ai_json(reply: str) -> List[Dict]:
    """Pull a JSON array of questions out of an AI reply (may be wrapped in prose/markdown)."""
    if not reply:
        return []
    match = re.search(r"\[.*\]", reply, re.DOTALL)
    if not match:
        return []
    try:
        return _coerce_questions(json.loads(match.group(0)))
    except (json.JSONDecodeError, TypeError):
        return []


def _regex_questions(raw: str) -> List[Dict]:
    """Offline fallback: detect numbered questions + inline marks like (5) / [2 marks]."""
    out: List[Dict] = []
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r"^(?:Q\s*\.?\s*)?\d+\s*[\.\)]\s*(.+)$", line)
        if not m:
            continue
        text = m.group(1).strip()
        marks = 1
        mm = re.search(r"[\(\[]\s*(\d+)\s*(?:marks?|mks?|m)?\s*[\)\]]", text, re.IGNORECASE)
        if mm:
            marks = int(mm.group(1))
        out.append({
            "id": len(out) + 1,
            "question": text,
            "maxMarks": max(1, marks),
            "type": "short",
            "options": [],
        })
    return out


async def extract_questions(file_bytes: bytes, teacher) -> List[Dict]:
    """Extract structured questions from an uploaded PDF paper."""
    raw = extract_text_from_pdf(file_bytes)
    if not raw:
        return []

    prompt = (
        "You are given the text of a question paper. Extract every question as a JSON array. "
        'Each item must be: {"question": string, "maxMarks": integer, '
        '"type": "mcq" | "short" | "long", "options": [string] (only for mcq)}. '
        "Infer maxMarks from markers like (5) or [2 marks]; use 1 if unknown. "
        "Return ONLY the JSON array, no commentary.\n\nQuestion paper:\n" + raw[:6000]
    )
    try:
        reply = await _chat(prompt, "English", teacher)
        questions = _parse_ai_json(reply)
    except Exception:
        questions = []

    if not questions:
        questions = _regex_questions(raw)
    return questions
