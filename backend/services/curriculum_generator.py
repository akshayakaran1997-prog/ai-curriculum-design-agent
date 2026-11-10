
import json
import re

from services.ai_service import generate_ai_response


def extract_json_response(response_text):
    """
    Extract valid JSON from Gemini's response.
    Handles responses wrapped in Markdown code fences.
    """

    cleaned = response_text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not match:
            raise ValueError(
                "Gemini did not return a valid JSON object."
            )

        return json.loads(match.group())


def generate_curriculum(analysis_report, extracted_pages=None):
    """
    Generates a screen-level instructional design
    curriculum using Gemini and extracted PDF content.
    """

    if not analysis_report:
        raise ValueError("Document analysis report is empty.")

    # Prepare source content with page references
    source_content = ""

    if extracted_pages:
        for page in extracted_pages:
            source_content += (
                f"\nPAGE {page['page_number']}\n"
                f"{page['content']}\n"
            )

    # Prepare document analysis
    analysis_context = {
        "topics": analysis_report.get("topics", []),
        "source_pages": analysis_report.get("source_pages", []),
        "identified_gaps": analysis_report.get(
            "identified_gaps", []
        ),
        "total_pages": analysis_report.get("total_pages", 0),
        "total_words": analysis_report.get("total_words", 0)
    }

    prompt = f"""
You are a senior instructional designer and
eLearning curriculum architect.

Your task is to create a detailed, screen-level
curriculum using the supplied source document.

DOCUMENT ANALYSIS:
{json.dumps(analysis_context, ensure_ascii=False)}

SOURCE DOCUMENT CONTENT:
{source_content[:30000]}

INSTRUCTIONS:

1. Create a logical learning sequence.
2. Each curriculum entry must represent one learner-facing screen.
3. Use appropriate Bloom's Taxonomy levels.
4. Write meaningful screen titles.
5. Explain what the learner should learn on each screen.
6. Recommend suitable instructional strategies and visuals.
7. Include interactions where appropriate.
8. Include assessment opportunities.
9. Preserve source page references.
10. Do not invent technical facts or organisational policies.
11. If information is missing, identify it for SME review.
12. Avoid unnecessary repetition.
13. Create a suitable number of screens based on the source content.

Return ONLY valid JSON using this structure:

{{
    "total_slides": 2,
    "curriculum": [
        {{
            "serial_number": 1,
            "slide_number": 1,
            "screen_id": "S01",
            "module_id": "M01",
            "lesson_id": "L01",
            "screen_type": "Content",
            "slide_title": "Example title",
            "learning_objective": "Example objective",
            "level": "L1",
            "blooms_taxonomy_level": "Understand",
            "what_to_explain": "Detailed explanation",
            "learner_facing_content": "Content displayed to learners",
            "narration": "Suggested narration",
            "instructional_strategy": "Explanation",
            "visual_instructional_approach": "Suggested visual",
            "interaction_type": "None",
            "learner_action": "",
            "correct_response": "",
            "feedback_correct": "",
            "feedback_incorrect": "",
            "branching_rule": "",
            "source_page": "1",
            "estimated_duration": 2,
            "assessment": "No",
            "sme_review_status": "Pending",
            "developer_notes": ""
        }}
    ]
}}

Return valid JSON only.
"""

    # Ask Gemini to generate the curriculum
    ai_response = generate_ai_response(prompt)

    # Convert Gemini response into Python data
    curriculum_data = extract_json_response(ai_response)

    curriculum = curriculum_data.get("curriculum", [])

    if not isinstance(curriculum, list) or not curriculum:
        raise ValueError(
            "Gemini did not generate a valid curriculum."
        )

    # Validate and standardise screen numbering
    for index, screen in enumerate(curriculum, start=1):

        screen["serial_number"] = index
        screen["slide_number"] = index
        screen.setdefault("screen_id", f"S{index:02d}")
        screen.setdefault("level", "L1")
        screen.setdefault(
            "blooms_taxonomy_level", "Understand"
        )
        screen.setdefault("source_page", "")
        screen.setdefault("sme_review_status", "Pending")

    return {
        "total_slides": len(curriculum),
        "curriculum": curriculum
    }
