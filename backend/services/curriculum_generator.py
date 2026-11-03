
def generate_curriculum(analysis_report):
    """
    Converts the PDF analysis report into
    a structured, slide-by-slide curriculum.
    """

    candidate_headings = analysis_report.get(
        "candidate_headings", []
    )

    curriculum = []

    slide_number = 1

    for item in candidate_headings:

        # Get the topic and source page
        if isinstance(item, dict):
            topic = item.get("heading", "").strip()
            source_page = item.get("page_number", "")
        else:
            topic = str(item).strip()
            source_page = ""

        # Ignore empty topics
        if not topic:
            continue

        # Create one curriculum row
        curriculum.append({
            "serial_number": len(curriculum) + 1,
            "slide_number": slide_number,
            "level": "L1",
            "blooms_taxonomy_level": "Understand",
            "slide_title": topic,
            "what_to_explain": (
                f"Explain the key concepts of {topic} "
                "using information from the source document."
            ),
            "visual_instructional_approach": (
                "Use a relevant visual, diagram, "
                "or practical example."
            ),
            "source_page": source_page
        })

        slide_number += 1

    return {
        "total_slides": len(curriculum),
        "curriculum": curriculum
    }
