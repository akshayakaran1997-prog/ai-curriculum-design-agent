import re
from collections import Counter


# Words and phrases that should not become curriculum headings
IGNORED_PHRASES = {
    "facilitator notes",
    "facilitator note",
    "table of contents",
    "thank you",
    "questions",
    "do",
    "the",
    "and",
    "or",
    "basics"
}


# Detect lines that begin with bullet or numbering symbols
BULLET_PATTERN = re.compile(
    r"^\s*(?:[•●▪◦‣–—\-*]|\d+[.)]|[a-zA-Z][.)])\s*"
)


def is_heading_candidate(line):

    line = line.strip()

    # Ignore empty or very short lines
    if len(line) < 4:
        return False

    words = line.split()

    # Ignore long sentences
    if len(words) > 10 or len(line) > 90:
        return False

    # Ignore bullet points and numbered list items
    if BULLET_PATTERN.match(line):
        return False

    # Ignore lines ending with sentence punctuation
    if line.endswith((".", ",", ";", ":", "?", "!")):
        return False

    # Ignore lines containing only symbols or numbers
    if not re.search(r"[A-Za-z]", line):
        return False

    # Ignore known non-topic phrases
    if line.lower().strip() in IGNORED_PHRASES:
        return False

    # Ignore common standalone instruction words
    if len(words) == 1 and line.lower() in {
        "do", "go", "see", "read", "note", "next"
    }:
        return False

    # Check whether the line is mostly uppercase
    letters = [char for char in line if char.isalpha()]

    uppercase_ratio = (
        sum(char.isupper() for char in letters) / len(letters)
        if letters else 0
    )

    is_uppercase_heading = uppercase_ratio >= 0.75

    # Check whether the line resembles a title
    is_title_case = (
        len(words) >= 2
        and all(
            word[0].isupper()
            for word in words
            if word[0].isalpha()
        )
    )

    return is_uppercase_heading or is_title_case


def analyze_pdf_content(extracted_pages):

    # 1. Combine text from all PDF pages
    full_text = " ".join(
        page["content"] for page in extracted_pages
    )

    # 2. Count total words
    words = re.findall(r"\b[\w'-]+\b", full_text)

    # 3. Identify possible headings
    candidate_headings = []
    seen_headings = set()

    for page in extracted_pages:

        lines = page["content"].splitlines()

        for line in lines:

            line = line.strip()

            if not is_heading_candidate(line):
                continue

            # Avoid duplicate headings across the document
            heading_key = line.lower()

            if heading_key in seen_headings:
                continue

            seen_headings.add(heading_key)

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
                    re.findall(
                        r"\b[\w'-]+\b",
                        page["content"]
                    )
                )
            }
            for page in extracted_pages
        ]
    }

    return analysis_report
