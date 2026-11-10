
import json

from services.ai_service import generate_ai_response


def analyze_pdf_content(extracted_pages):

    # Step 1: Prepare extracted PDF content
    document_text = ""

    for page in extracted_pages:
        document_text += (
            f"\n\nPAGE {page['page_number']}\n"
            f"{page['content']}"
        )

    # Step 2: Create the AI analysis prompt
    prompt = f"""
    You are an expert instructional designer
    and technical training analyst.

    Analyse the following source document.

    Identify:
    1. Document overview
    2. Main topics
    3. Subtopics under each main topic
    4. Important concepts and explanations
    5. Important technical terminology
    6. Potential learning opportunities
    7. Source page references

    Important instructions:
    - Use only information from the source document.
    - Do not invent technical information.
    - Do not create unsupported topics.
    - Preserve the original meaning.
    - Include source page numbers for every topic.
    - If information is missing, mention it explicitly.

    Return ONLY valid JSON using this structure:

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
    try:
        analysis_report = json.loads(ai_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned an invalid JSON response."
        ) from error

    # Step 5: Add document statistics
    analysis_report["total_pages"] = len(extracted_pages)

    analysis_report["total_words"] = sum(
        len(page["content"].split())
        for page in extracted_pages
    )

    return analysis_report
