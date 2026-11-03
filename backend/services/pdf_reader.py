
import fitz


def extract_pdf_text(file_path):

    document = fitz.open(file_path)

    extracted_content = []

    for page_number, page in enumerate(document, start=1):

        page_text = page.get_text("text")

        extracted_content.append({
            "page_number": page_number,
            "content": page_text.strip()
        })

    document.close()

    return extracted_content
