
import json
from services.ai_service import generate_ai_response


def extract_json_response(ai_response):
    """
    Extract valid JSON from Gemini's response.
    Handles Markdown code fences and additional text.
    """

    if not ai_response or not ai_response.strip():
        raise ValueError("Gemini returned an empty response.")

    response = ai_response.strip()

    # Remove Markdown code fences if present
    if response.startswith("```"):
        lines = response.splitlines()

        if lines[-1].strip() == "```":
            lines = lines[:-1]

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        response = "\n".join(lines).strip()

    # Decode JSON, even if explanatory text surrounds it
    decoder = json.JSONDecoder()

    for index, character in enumerate(response):
        if character == "{":
            try:
                data, _ = decoder.raw_decode(response[index:])
                return data
            except json.JSONDecodeError:
                continue

    raise ValueError(
        "No valid JSON object found in Gemini's response. "
        f"Response preview: {response[:500]}"
    )


def analyze_pdf_content(extracted_pages):

    if not extracted_pages:
        raise ValueError("No PDF content was extracted.")

    # Step 1: Prepare document text with page references
    document_text = ""

    for page in extracted_pages:
        document_text += (
            f"\n\nPAGE {page['page_number']}\n"
            f"{page['content']}"
        )

    # Step 2: Create the Gemini analysis prompt
    prompt = f"""
You are an expert instructional designer
and technical training analyst.

Analyse the source document provided below.

Identify:
1. Document overview
2. Main topics
3. Subtopics under each main topic
4. Important concepts and explanations
5. Important technical terminology
6. Potential learning opportunities
7. Source page references

Instructions:
- Use only information from the source document.
- Do not invent technical information.
- Do not create unsupported topics.
- Preserve the original meaning.
- Include source page numbers for every topic.
- If information is missing, mention it explicitly.
- Return a valid JSON object only.
- Do not use Markdown code fences.
- Do not include explanatory text outside the JSON.

Required JSON structure:

{{
    "document_overview": "",
    "main_topics": [
        {{
            "topic_id": "T01",
            "topic": "",
            "subtopics": [],
            "key_concepts": [],
            "technical_terms": [],
            "learning_opportunities": [],
            "source_pages": []
        }}
    ],
    "identified_gaps": []
}}

SOURCE DOCUMENT:

{document_text}
"""

    # Step 3: Send the document to Gemini
    ai_response = generate_ai_response(prompt)

    # Step 4: Convert Gemini response into Python data
    analysis_report = extract_json_response(ai_response)

    # Step 5: Validate the response structure
    if not isinstance(analysis_report, dict):
        raise ValueError("Gemini response must be a JSON object.")

    required_fields = [
        "document_overview",
        "main_topics",
        "identified_gaps"
    ]

    for field in required_fields:
        if field not in analysis_report:
            raise ValueError(
                f"Gemini response is missing the field: {field}"
            )

    if not isinstance(analysis_report["main_topics"], list):
        raise ValueError("main_topics must be a list.")

    if not isinstance(analysis_report["identified_gaps"], list):
        raise ValueError("identified_gaps must be a list.")

    # Step 6: Add document statistics
    analysis_report["total_pages"] = len(extracted_pages)

    analysis_report["total_words"] = sum(
        len(page["content"].split())
        for page in extracted_pages
    )

    return analysis_report
