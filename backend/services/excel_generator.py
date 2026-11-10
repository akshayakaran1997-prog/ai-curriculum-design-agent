
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter


# --------------------------------------------------
# 1. Common helper functions
# --------------------------------------------------

def clean(value, default=""):
    """Convert values into Excel-friendly text."""

    if value is None:
        return default

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        return str(value)

    return str(value)


def get_value(data, *keys, default=""):
    """Return the first available non-empty value."""

    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if value is not None and value != "":
            return value

    return default


def create_sheet(wb, title, heading, description, headers):
    """Create a consistently formatted worksheet."""

    ws = wb.create_sheet(title)

    total_columns = len(headers)

    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=total_columns
    )

    title_cell = ws.cell(row=1, column=1)
    title_cell.value = heading
    title_cell.font = Font(
        name="Arial",
        size=15,
        bold=True,
        color="FFFFFF"
    )
    title_cell.fill = PatternFill(
        "solid",
        fgColor="17365D"
    )
    title_cell.alignment = Alignment(
        vertical="center"
    )

    ws.row_dimensions[1].height = 32

    ws.merge_cells(
        start_row=2,
        start_column=1,
        end_row=2,
        end_column=total_columns
    )

    subtitle = ws.cell(row=2, column=1)
    subtitle.value = description
    subtitle.font = Font(
        name="Arial",
        size=10,
        italic=True,
        color="666666"
    )
    subtitle.alignment = Alignment(
        wrap_text=True,
        vertical="center"
    )

    ws.row_dimensions[2].height = 30

    for col_num, header in enumerate(headers, start=1):

        cell = ws.cell(
            row=4,
            column=col_num,
            value=header
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF",
            size=10
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="4472C4"
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    ws.row_dimensions[4].height = 38
    ws.freeze_panes = "A5"

    return ws


def add_data_rows(ws, rows):
    """Add consistently formatted data rows."""

    for row_data in rows:
        ws.append([clean(value) for value in row_data])

    thin_border = Border(
        bottom=Side(
            style="thin",
            color="D9E2F3"
        )
    )

    for row in ws.iter_rows(
        min_row=5,
        max_row=ws.max_row
    ):

        for cell in row:

            cell.font = Font(
                name="Arial",
                size=10,
                color="333333"
            )

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

            cell.border = thin_border

        if row[0].row % 2 == 0:

            for cell in row:
                cell.fill = PatternFill(
                    "solid",
                    fgColor="F2F6FC"
                )

    if ws.max_row >= 4:
        ws.auto_filter.ref = (
            f"A4:{get_column_letter(ws.max_column)}"
            f"{ws.max_row}"
        )


def set_column_widths(ws, widths):
    """Set readable column widths."""

    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[
            get_column_letter(index)
        ].width = width


def add_status_dropdown(ws, column, first_row=5):
    """Add SME review status dropdown."""

    validation = DataValidation(
        type="list",
        formula1='"Pending,In Review,Approved,Changes Required"',
        allow_blank=True
    )

    ws.add_data_validation(validation)

    validation.add(
        f"{get_column_letter(column)}{first_row}:"
        f"{get_column_letter(column)}500"
    )


def normalise_source_pages(value):
    """Convert source page references into readable text."""

    return clean(value)


# --------------------------------------------------
# 2. Main Excel generation function
# --------------------------------------------------

def generate_excel(
    curriculum_data,
    output_path,
    analysis_report=None,
    project_details=None
):
    """
    Generate a concise four-sheet course curriculum workbook.

    Sheets:
    1. Course Overview
    2. Curriculum Outline
    3. Source References
    4. SME Review
    """

    if not isinstance(curriculum_data, dict):
        raise ValueError("Curriculum data must be a dictionary.")

    analysis_report = analysis_report or {}
    project_details = project_details or {}

    course_overview = curriculum_data.get(
        "course_overview", {}
    )

    curriculum_outline = curriculum_data.get(
        "curriculum_outline", []
    )

    source_references = curriculum_data.get(
        "source_references", []
    )

    sme_review = curriculum_data.get(
        "sme_review", []
    )

    if not isinstance(curriculum_outline, list) or not curriculum_outline:
        raise ValueError("Curriculum outline is empty or invalid.")

    if not isinstance(course_overview, dict):
        raise ValueError("Course overview must be a dictionary.")

    if not isinstance(source_references, list):
        raise ValueError("Source references must be a list.")

    if not isinstance(sme_review, list):
        raise ValueError("SME review must be a list.")

    wb = Workbook()
    wb.remove(wb.active)

    # --------------------------------------------------
    # SHEET 1: COURSE OVERVIEW
    # --------------------------------------------------

    ws = create_sheet(
        wb,
        "Course Overview",
        "AI CURRICULUM DESIGN | COURSE OVERVIEW",
        "A concise summary of the proposed course for business stakeholders and SMEs.",
        ["Course Information", "Details"]
    )

    project_name = get_value(
        project_details,
        "project_name",
        default="AI-Generated Curriculum"
    )

    overview_rows = [
        [
            "Course Title",
            get_value(
                course_overview,
                "course_title",
                default=project_name
            )
        ],
        [
            "Business Need",
            get_value(
                course_overview,
                "business_need",
                "business_requirement"
            )
        ],
        [
            "Course Purpose",
            get_value(course_overview, "course_purpose")
        ],
        [
            "Target Audience",
            get_value(
                course_overview,
                "target_audience",
                default=get_value(project_details, "target_audience")
            )
        ],
        [
            "Delivery Format",
            get_value(
                course_overview,
                "delivery_format"
            )
        ],
        [
            "Estimated Course Duration (minutes)",
            get_value(
                course_overview,
                "total_duration_minutes",
                default=0
            )
        ],
        [
            "Total Modules",
            len(curriculum_outline)
        ],
        [
            "Source Document",
            get_value(
                analysis_report,
                "filename",
                default=project_name
            )
        ],
        [
            "Source Pages",
            analysis_report.get("total_pages", 0)
        ],
        [
            "Generation Status",
            "AI Generated - Pending SME Review"
        ]
    ]

    # Add course-level learning objectives
    objectives = course_overview.get(
        "learning_objectives", []
    )

    if not isinstance(objectives, list):
        objectives = []

    overview_rows.append([
        "Learning Objectives",
        "\n".join(
            f"{index}. {objective}"
            for index, objective in enumerate(
                objectives, start=1
            )
        )
    ])

    add_data_rows(ws, overview_rows)

    set_column_widths(ws, [38, 100])

    # --------------------------------------------------
    # SHEET 2: CURRICULUM OUTLINE
    # --------------------------------------------------

    headers = [
        "Module No.",
        "Module Title",
        "Topics Covered",
        "What Learners Will Learn",
        "Learning Approach",
        "Estimated Duration (min)",
        "Source Pages"
    ]

    ws = create_sheet(
        wb,
        "Curriculum Outline",
        "COURSE CURRICULUM OUTLINE",
        "The learning journey: what learners will study and how each module will be delivered.",
        headers
    )

    curriculum_rows = []

    for index, module in enumerate(
        curriculum_outline, start=1
    ):

        if not isinstance(module, dict):
            continue

        curriculum_rows.append([
            index,
            get_value(module, "module_title"),
            get_value(module, "topics_covered"),
            get_value(module, "what_learners_will_learn"),
            get_value(module, "learning_approach"),
            get_value(
                module,
                "estimated_duration_minutes",
                default=0
            ),
            normalise_source_pages(
                module.get("source_pages", [])
            )
        ])

    if not curriculum_rows:
        raise ValueError("No valid curriculum modules found.")

    add_data_rows(ws, curriculum_rows)

    set_column_widths(
        ws,
        [12, 32, 42, 55, 38, 20, 18]
    )

    # --------------------------------------------------
    # SHEET 3: SOURCE REFERENCES
    # --------------------------------------------------

    headers = [
        "Module No.",
        "Module Title",
        "Source Pages",
        "Supporting Evidence",
        "Evidence Status"
    ]

    ws = create_sheet(
        wb,
        "Source References",
        "SOURCE REFERENCES & EVIDENCE",
        "Traceability between proposed curriculum modules and the uploaded source document.",
        headers
    )

    reference_rows = []

    # Use AI-generated source references
    for reference in source_references:

        if not isinstance(reference, dict):
            continue

        reference_rows.append([
            get_value(reference, "module_number"),
            get_value(reference, "module_title"),
            normalise_source_pages(
                reference.get("source_pages", [])
            ),
            get_value(
                reference,
                "supporting_evidence"
            ),
            get_value(
                reference,
                "evidence_status",
                default="Requires SME confirmation"
            )
        ])

    # Fallback: use module source pages if the
    # AI did not return separate reference records.
    if not reference_rows:

        for index, module in enumerate(
            curriculum_outline, start=1
        ):

            if not isinstance(module, dict):
                continue

            reference_rows.append([
                index,
                get_value(module, "module_title"),
                normalise_source_pages(
                    module.get("source_pages", [])
                ),
                "No separate supporting evidence returned.",
                "Requires SME confirmation"
            ])

    add_data_rows(ws, reference_rows)

    set_column_widths(
        ws,
        [14, 32, 20, 70, 30]
    )

    # --------------------------------------------------
    # SHEET 4: SME REVIEW
    # --------------------------------------------------

    headers = [
        "Review No.",
        "Item Requiring Review",
        "Reason for Review",
        "Related Module",
        "Review Status",
        "SME Comments"
    ]

    ws = create_sheet(
        wb,
        "SME Review",
        "SUBJECT MATTER EXPERT REVIEW",
        "Review information gaps and confirm the accuracy and completeness of the proposed curriculum.",
        headers
    )

    review_rows = []

    for index, item in enumerate(sme_review, start=1):

        if not isinstance(item, dict):
            continue

        review_rows.append([
            index,
            get_value(item, "item"),
            get_value(item, "reason_for_review"),
            get_value(item, "related_module"),
            get_value(
                item,
                "review_status",
                default="Pending"
            ),
            ""
        ])

    # If Gemini has not identified review items,
    # retain a clear human-review reminder.
    if not review_rows:

        review_rows.append([
            1,
            "Review the complete curriculum",
            "Confirm factual accuracy, learning objectives and course coverage.",
            "All modules",
            "Pending",
            ""
        ])

    add_data_rows(ws, review_rows)

    set_column_widths(
        ws,
        [14, 38, 60, 25, 22, 55]
    )

    add_status_dropdown(ws, 5)

    # --------------------------------------------------
    # 3. Workbook-wide formatting
    # --------------------------------------------------

    for ws in wb.worksheets:

        ws.sheet_view.showGridLines = False

        ws.sheet_properties.pageSetUpPr.fitToPage = True

        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0

        ws.sheet_view.zoomScale = 85

        ws.sheet_properties.pageSetUpPr.autoPageBreaks = False

    # Save workbook
    wb.save(output_path)

    return output_path
