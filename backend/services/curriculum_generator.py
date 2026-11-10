
import json

from services.ai_service import generate_ai_response
from services.pdf_analyzer import extract_json_response


def generate_curriculum(analysis_report):
    """
    Uses Gemini to generate a screen-level
    instructional curriculum from PDF analysis.
    """

    # Step 1: Validate the analysis report
    if not isinstance(analysis_report, dict):
        raise ValueError("Invalid document analysis report.")

    main_topics = analysis_report.get("main_topics", [])

    if not main_topics:
        raise ValueError("No main topics found in the analysis report.")

    # Step 2: Prepare the prompt
    analysis_json = json.dumps(
        analysis_report,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are a senior instructional designer
and learning experience design expert.

Your task is to create a detailed,
screen-level eLearning curriculum.

Use the supplied document analysis as your source.

CURRICULUM REQUIREMENTS:

1. Create a logical module and lesson structure.
2. Create one row for every learner-facing screen.
3. Write measurable learning objectives.
4. Assign appropriate Bloom's taxonomy levels.
5. Assign L1, L2 or L3 content complexity.
6. Explain what each screen should teach.
7. Recommend suitable visuals and instructional strategies.
8. Include interactions where pedagogically appropriate.
9. Include assessments where appropriate.
10. Preserve source page references.
11. Do not invent technical facts.
12. Do not introduce topics unsupported by the source.
13. Avoid repetitive or unnecessary screens.
14. Ensure the curriculum has a logical learning progression.

IMPORTANT:
- L1 = foundational knowledge.
- L2 = intermediate understanding and application.
- L3 = advanced application, analysis or problem-solving.
- Select Bloom's levels based on the actual learning objective.
- Do not assign the same Bloom's level to every screen.
- Do not force an interaction or assessment onto every screen.
- If the source does not provide enough information,
  flag it for instructional designer or SME review.

RETURN ONLY VALID JSON.

Use this exact structure:

{{
    "total_slides": 0,
    "curriculum": [
        {{
            "serial_number": 1,
            "slide_number": 1,
            "module_id": "M01",
            "lesson_id": "L01",
            "screen_type": "Content",
            "slide_title": "",
            "learning_objective": "",
            "level": "L1",
            "blooms_taxonomy_level": "Understand",
            "learner_facing_content": "",
            "what_to_explain": "",
            "narration": "",
            "instructional_strategy": "",
            "interaction_type": "None",
            "learner_action": "",
            "expected_response": "",
            "feedback": "",
            "assessment": "",
            "visual_instructional_approach": "",
            "source_page": "",
            "review_comments": ""
        }}
    ]
}}

DOCUMENT ANALYSIS:

{analysis_json}
"""

    # Step 3: Ask Gemini to generate the curriculum
    ai_response = generate_ai_response(prompt)

    # Step 4: Extract JSON
    curriculum_data = extract_json_response(ai_response)

    # Step 5: Validate the generated curriculum
    if not isinstance(curriculum_data, dict):
        raise ValueError("Gemini returned an invalid curriculum object.")

    curriculum = curriculum_data.get("curriculum")

    if not isinstance(curriculum, list) or not curriculum:
        raise ValueError("Gemini did not generate any curriculum screens.")

    # Step 6: Normalize and validate each screen
    required_fields = [
        "slide_title",
        "learning_objective",
        "what_to_explain",
        "blooms_taxonomy_level"
    ]

    for index, screen in enumerate(curriculum, start=1):

        if not isinstance(screen, dict):
            raise ValueError(f"Invalid curriculum screen at row {index}.")

        for field in required_fields:
            if not screen.get(field):
                raise ValueError(
                    f"Screen {index} is missing required field: {field}"
                )

        screen["serial_number"] = index
        screen["slide_number"] = index

        # Keep source references in a workbook-friendly format
        source_page = screen.get("source_page", "")

        if isinstance(source_page, list):
            screen["source_page"] = ", ".join(
                str(page) for page in source_page
            )

    # Step 7: Return the curriculum
    return {
        "total_slides": len(curriculum),
        "curriculum": curriculum
    }
