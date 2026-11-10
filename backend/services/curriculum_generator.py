
import json

from services.ai_service import generate_ai_response


def extract_json_response(response_text):
    """
    Extract a valid JSON object from Gemini's response.
    Handles Markdown code fences and additional surrounding text.
    """

    if not response_text or not response_text.strip():
        raise ValueError("Gemini returned an empty response.")

    cleaned = response_text.strip()

    # Remove Markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines[-1].strip() == "```":
            lines = lines[:-1]

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        cleaned = "\n".join(lines).strip()

    # Find and decode the first valid JSON object
    decoder = json.JSONDecoder()

    for index, character in enumerate(cleaned):
        if character == "{":
            try:
                data, _ = decoder.raw_decode(cleaned[index:])
                return data
            except json.JSONDecodeError:
                continue

    raise ValueError("Gemini did not return a valid JSON object.")


def generate_curriculum(analysis_report, extracted_pages=None):
    """
    Generates a concise, source-grounded course curriculum.

    Each curriculum entry represents a module,
    not an individual eLearning screen.

    Output:
    1. Course Overview
    2. Curriculum Outline
    3. Source References
    4. SME Review
    """

    if not analysis_report:
        raise ValueError("Document analysis report is empty.")

    # --------------------------------------------------
    # STAGE 1: Prepare source document content
    # --------------------------------------------------

    source_content = ""

    if extracted_pages:

        for page in extracted_pages:

            source_content += (
                f"\n\nPAGE {page['page_number']}\n"
                f"{page['content']}"
            )

    if not source_content.strip():
        raise ValueError("No source document content available.")

    # --------------------------------------------------
    # STAGE 2: Prepare document analysis
    # --------------------------------------------------

    analysis_context = {
        "document_overview": analysis_report.get(
            "document_overview", ""
        ),
        "main_topics": analysis_report.get(
            "main_topics", []
        ),
        "identified_gaps": analysis_report.get(
            "identified_gaps", []
        ),
        "total_pages": analysis_report.get(
            "total_pages", 0
        ),
        "total_words": analysis_report.get(
            "total_words", 0
        )
    }

    # --------------------------------------------------
    # STAGE 3: Generate concise curriculum using Gemini
    # --------------------------------------------------

    prompt = f"""
You are an expert instructional designer and
learning curriculum architect.

YOUR TASK:

Create a concise, professional course curriculum
based on the supplied source document.

This is a COURSE OUTLINE, NOT a STORYBOARD.

The curriculum will be reviewed by:
- Subject Matter Experts (SMEs)
- Product Owners
- Business Stakeholders
- Instructional Designers

They must understand what the course covers,
why it is required, and how the learning
will progress.

DOCUMENT ANALYSIS:

{json.dumps(analysis_context, ensure_ascii=False)}

SOURCE DOCUMENT:

{source_content[:30000]}

DESIGN REQUIREMENTS:

1. Create a logical sequence of learning modules.

2. Each curriculum entry must represent a MODULE
   or major learning section.

3. Do not create individual screens or slides.

4. Explain what learners will learn in each module
   using simple, clear language.

5. Create measurable course-level learning objectives
   based on the supplied content.

6. Recommend an appropriate learning approach
   for each module, such as explanation,
   demonstration, workplace example or scenario.

7. Suggest a realistic estimated duration
   for each module.

8. Keep the curriculum concise.
   Avoid lengthy paragraphs and unnecessary details.

9. Preserve source page references for every module.

10. Do not invent technical facts, company policies,
    procedures or requirements.

11. Do not assume missing information.
    Record information gaps for SME confirmation.

12. Distinguish source-supported information
    from recommendations requiring approval.

13. Do not generate narration, screen content,
    developer notes, branching logic,
    gamification mechanics or storyboard details.

14. Do not force a fixed number of modules.
    Choose the number based on the source material.

15. Make the curriculum understandable
    to someone who is not an instructional designer.

RETURN ONLY VALID JSON.

Use this exact structure:

{{
    "course_overview": {{
        "course_title": "",
        "business_need": "",
        "course_purpose": "",
        "target_audience": "",
        "learning_objectives": [],
        "delivery_format": "",
        "total_duration_minutes": 0
    }},

    "curriculum_outline": [
        {{
            "module_number": 1,
            "module_title": "",
            "topics_covered": [],
            "what_learners_will_learn": "",
            "learning_approach": "",
            "estimated_duration_minutes": 0,
            "source_pages": []
        }}
    ],

    "source_references": [
        {{
            "module_number": 1,
            "module_title": "",
            "source_pages": [],
            "supporting_evidence": "",
            "evidence_status": "Source-supported"
        }}
    ],

    "sme_review": [
        {{
            "item": "",
            "reason_for_review": "",
            "related_module": "",
            "review_status": "Pending"
        }}
    ]
}}

IMPORTANT:

- Use only information supported by the source
  for factual statements.
- Use empty strings or empty arrays when
  information is unavailable.
- Use "Requires SME confirmation" where appropriate.
- Source page numbers must refer to the supplied PDF.
- Return valid JSON only.
"""

    ai_response = generate_ai_response(prompt)

    curriculum_data = extract_json_response(ai_response)

    # --------------------------------------------------
    # STAGE 4: Validate curriculum structure
    # --------------------------------------------------

    required_sections = [
        "course_overview",
        "curriculum_outline",
        "source_references",
        "sme_review"
    ]

    for section in required_sections:

        if section not in curriculum_data:
            raise ValueError(
                f"Gemini response is missing: {section}"
            )

    curriculum_outline = curriculum_data["curriculum_outline"]

    if not isinstance(curriculum_outline, list) or not curriculum_outline:
        raise ValueError(
            "Gemini did not generate a valid curriculum outline."
        )

    if not isinstance(curriculum_data["course_overview"], dict):
        raise ValueError("Invalid course overview.")

    if not isinstance(curriculum_data["source_references"], list):
        raise ValueError("Invalid source references.")

    if not isinstance(curriculum_data["sme_review"], list):
        raise ValueError("Invalid SME review section.")

    # --------------------------------------------------
    # STAGE 5: Standardise module numbering
    # --------------------------------------------------

    for index, module in enumerate(curriculum_outline, start=1):

        module["module_number"] = index

        module.setdefault("module_title", "")
        module.setdefault("topics_covered", [])
        module.setdefault("what_learners_will_learn", "")
        module.setdefault("learning_approach", "")
        module.setdefault("estimated_duration_minutes", 0)
        module.setdefault("source_pages", [])

    # --------------------------------------------------
    # STAGE 6: Return final curriculum
    # --------------------------------------------------

    curriculum_data["total_modules"] = len(curriculum_outline)

    return curriculum_data
