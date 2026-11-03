
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def generate_excel(curriculum_data, output_path):

    # Create a new Excel workbook
    workbook = Workbook()

    # Rename the first worksheet
    sheet = workbook.active
    sheet.title = "Slide-by-Slide Curriculum"

    # Define the Excel column headings
    headers = [
        "Serial Number",
        "Slide Number",
        "Level",
        "Bloom's Taxonomy Level",
        "Slide Title / Topic",
        "What to Explain",
        "Visual / Instructional Approach",
        "Source Page",
        "Review Comments"
    ]

    # Add headings to the first row
    sheet.append(headers)

    # Get curriculum rows
    curriculum_rows = curriculum_data.get("curriculum", [])

    # Add each slide as one Excel row
    for item in curriculum_rows:

        sheet.append([
            item.get("serial_number", ""),
            item.get("slide_number", ""),
            item.get("level", ""),
            item.get("blooms_taxonomy_level", ""),
            item.get("slide_title", ""),
            item.get("what_to_explain", ""),
            item.get("visual_instructional_approach", ""),
            item.get("source_page", ""),
            ""
        ])

    # Format the heading row
    header_fill = PatternFill(
        start_color="243F60",
        end_color="243F60",
        fill_type="solid"
    )

    for cell in sheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF",
            size=11
        )
        cell.fill = header_fill
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # Set suitable column widths
    column_widths = {
        "A": 14,
        "B": 14,
        "C": 12,
        "D": 24,
        "E": 32,
        "F": 55,
        "G": 42,
        "H": 14,
        "I": 30
    }

    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width

    # Format curriculum content
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    # Add borders
    thin_border = Border(
        bottom=Side(style="thin", color="D9E2F3")
    )

    for row in sheet.iter_rows():
        for cell in row:
            cell.border = thin_border

    # Improve worksheet navigation
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.row_dimensions[1].height = 35

    # Save the Excel file
    workbook.save(output_path)

    return output_path
