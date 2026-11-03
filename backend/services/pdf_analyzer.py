
import re
from collections import Counter


def analyze_pdf_content(extracted_pages):

    # 1. Combine text from all PDF pages
    full_text = " ".join(
        page["content"] for page in extracted_pages
    )

    # 2. Count the total number of words
    words = re.findall(r"\b[\w'-]+\b", full_text)

    # 3. Identify possible headings
    candidate_headings = []

    for page in extracted_pages:

        lines = page["content"].splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if (
                len(line.split()) <= 10
                and len(line) < 100
                and not line.endswith(".")
            ):
                candidate_headings.append({
                    "heading": line,
                    "page_number": page["page_number"]
                })

    # 4. Identify frequently occurring keywords
    stop_words = {
        "the", "is", "are", "was", "were",
        "and", "or", "of", "to", "in", "on",
        "for", "with", "a", "an", "this",
        "that", "by", "from", "as", "at",
        "be", "it", "can", "will", "which"
    }

    keywords = [
        word.lower()
        for word in words
        if word.lower() not in stop_words
        and len(word) > 3
    ]

    keyword_frequency = Counter(keywords)

    top_keywords = keyword_frequency.most_common(15)

    # 5. Prepare the analysis report
    analysis_report = {
        "total_pages": len(extracted_pages),
        "total_words": len(words),
        "candidate_headings": candidate_headings,
        "top_keywords": [
            {
                "keyword": keyword,
                "frequency": frequency
            }
            for keyword, frequency in top_keywords
        ],
        "page_references": [
            {
                "page_number": page["page_number"],
                "word_count": len(
                    re.findall(r"\b[\w'-]+\b", page["content"])
                )
            }
            for page in extracted_pages
        ]
    }

    return analysis_report
