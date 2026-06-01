"""
Lesson Plan Generator Service
Currently uses smart templates to produce structured plans.

TODO: Replace generate_with_ai() with real Claude API call:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_claude_response(message.content[0].text)
"""

import asyncio
from typing import Optional


def _timing(duration: int):
    intro    = max(5,  round(duration * 0.11))
    main     = round(duration * 0.44)
    activity = round(duration * 0.28)
    wrap     = duration - intro - main - activity
    return intro, main, activity, max(5, wrap)


def _materials(chapter: str, subject: str) -> list[str]:
    base = [
        f"NCERT {subject} Textbook (Class 8)",
        "Blackboard / Whiteboard & chalk/markers",
        f"Key-terms handout for {chapter}",
    ]
    lower = chapter.lower()
    if any(w in lower for w in ["constitution", "parliament", "law", "judiciary"]):
        base += ["Printed copy of the Indian Constitution (excerpts)", "Flowchart of government structure"]
    elif any(w in lower for w in ["margin", "social", "facility", "justice"]):
        base += ["Case-study cards (real-world examples)", "Newspaper clippings on the topic"]
    elif "secular" in lower:
        base += ["Map of India showing religious diversity", "Timeline of historical events"]
    else:
        base += ["Chart paper and coloured markers", "Discussion prompt cards"]
    return base


def _core_concept(chapter: str, topic: str) -> str:
    subject = topic or chapter
    return (
        f"This lesson centres on '{subject}'. Students will build a conceptual "
        f"understanding by moving from definitions and facts toward analysis and "
        f"application. The teacher will use the Socratic method during the main "
        f"teaching phase, asking guiding questions rather than delivering a monologue, "
        f"so that learners construct meaning themselves. Special attention is given to "
        f"connecting the content to students' lived experiences and current events in India."
    )


def _objectives(chapter: str, topic: str, custom: list[str]) -> list[str]:
    if custom:
        return custom
    label = topic or chapter
    return [
        f"Recall and explain the key concepts of {label}",
        f"Analyse how {label} affects everyday life in India",
        f"Evaluate different perspectives related to {label} with evidence",
        f"Create a short written or visual response applying what they learned",
    ]


def _sections(chapter: str, topic: str, intro: int, main: int, activity: int, wrap: int) -> list[dict]:
    label = topic or chapter
    return [
        {
            "title": "Warm-Up & Prior Knowledge",
            "duration": intro,
            "activity": f"Quick Think-Pair-Share: 'What do you already know about {label}?'",
            "teacher_action": f"Pose an open question about {label}. Write key words on the board as students respond.",
            "student_action": "Discuss with a partner for 1 minute, then share one idea with the class.",
        },
        {
            "title": "Direct Teaching — Core Concept",
            "duration": main,
            "activity": f"Structured explanation of {label} with diagrams/examples on the board.",
            "teacher_action": (
                f"Introduce the topic using the textbook and board. Ask guiding questions every 5 minutes "
                f"to check understanding. Highlight key vocabulary."
            ),
            "student_action": "Take notes, underline key terms in the textbook, ask clarifying questions.",
        },
        {
            "title": "Collaborative Activity",
            "duration": activity,
            "activity": f"Group task: Create a mind-map or short skit illustrating one aspect of {label}.",
            "teacher_action": "Circulate among groups, prompt deeper thinking, ensure all students contribute.",
            "student_action": "Work in groups of 3–4. Present findings to the class in 1 minute.",
        },
        {
            "title": "Wrap-Up & Reflection",
            "duration": wrap,
            "activity": "Exit ticket: Each student writes one new thing they learned and one question they still have.",
            "teacher_action": f"Summarise the lesson. Preview the next topic. Collect exit tickets.",
            "student_action": "Write exit ticket. Share homework details.",
        },
    ]


def _assessment(chapter: str) -> str:
    lower = chapter.lower()
    if any(w in lower for w in ["constitution", "rights", "parliament"]):
        return (
            "Oral questioning during the lesson (formative). Exit ticket at the end. "
            "Summative: Short-answer quiz (5 questions) in the next class covering definitions, "
            "examples, and one application question."
        )
    return (
        "Continuous observation during group activity (formative). Exit ticket to gauge understanding. "
        "Summative: Written paragraph response — students explain the concept in their own words "
        "and give one real-life example."
    )


def _homework(chapter: str, topic: str) -> str:
    label = topic or chapter
    return (
        f"Read the textbook section on {label} once more and underline three facts you found "
        f"most interesting. Write a 4–5 sentence paragraph explaining how {label} is relevant "
        f"to modern Indian society. Bring it to the next class for peer discussion."
    )


def _differentiation(chapter: str) -> dict:
    return {
        "advanced": "Research one additional real-world case study and present a 2-minute verbal report next class.",
        "struggling": "Provide a printed graphic organiser with sentence starters. Allow partner support during activity.",
        "ell_support": "Key vocabulary list with simple definitions provided in advance.",
    }


async def generate(
    chapter: str,
    topic: Optional[str],
    duration: int,
    custom_objectives: list[str],
    special_notes: Optional[str],
    subject: str,
    class_name: Optional[str],
    section: Optional[str],
) -> dict:
    # Simulate generation delay (replace this with real Claude API call)
    await asyncio.sleep(1.5)

    intro, main, activity, wrap = _timing(duration)
    label = topic or chapter

    return {
        "title": f"Lesson Plan: {label}",
        "chapter_text": chapter,
        "subject": subject,
        "class_name": class_name or "8",
        "section": section or "A",
        "duration_minutes": duration,
        "objectives": _objectives(chapter, topic, custom_objectives),
        "materials": _materials(chapter, subject),
        "core_concept": _core_concept(chapter, topic),
        "plan_sections": _sections(chapter, topic, intro, main, activity, wrap),
        "assessment_method": _assessment(chapter),
        "homework": _homework(chapter, topic),
        "differentiation": _differentiation(chapter),
        "prompt_used": None,  # Will be set when real AI is integrated
        "modification_log": [],
    }
