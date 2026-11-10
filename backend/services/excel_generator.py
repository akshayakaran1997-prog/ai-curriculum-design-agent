
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Border, Side, Alignment
)
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
    """Return the first available field from a dictionary."""

    for key in keys:
        value = data.get(key)

        if value is not None and value != "":
            return value

    return default


def create_sheet(wb, title, heading, description, headers):
    """Create a consistently formatted workbook sheet."""

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
        "solid", fgColor="17365D"
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

    # Column headers
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
            "solid", fgColor="4472C4"
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
    """Add rows with consistent formatting."""

    for row_data in rows:

        ws.append([
            clean(value)
            for value in row_data
        ])

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
                    "solid", fgColor="F2F6FC"
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
    """Add a review status dropdown."""

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
    """Convert page references into readable text."""

    if isinstance(value, list):
        return ", ".join(str(page) for page in value)

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
    Generate an eight-sheet instructional design workbook.

    Existing main.py calls remain compatible:
    generate_excel(curriculum_data, output_path)
    """

    analysis_report = analysis_report or {}
    project_details = project_details or {}

    curriculum = curriculum_data.get(
        "curriculum", []
    )

    if not isinstance(curriculum, list):
        raise ValueError(
            "Curriculum must be a list of screens."
        )

    wb = Workbook()

    # Remove default worksheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # --------------------------------------------------
    # SHEET 1: PROJECT OVERVIEW
    # --------------------------------------------------

    ws = create_sheet(
        wb,
        "Project Overview",
        "AI CURRICULUM DESIGN | PROJECT OVERVIEW",
        "Project context and generation summary.",
        ["Project Information", "Details"]
    )

    project_rows = [
        ["Project Name",
         get_value(project_details, "project_name",
                   default="AI-Generated Curriculum")],

        ["Course Purpose",
         get_value(project_details, "course_purpose",
                   "business_requirement")],

        ["Target Audience",
         get_value(project_details, "target_audience")],

        ["Existing Knowledge",
         get_value(project_details, "existing_knowledge")],

        ["Learning Outcomes",
         get_value(project_details, "learning_outcomes")],

        ["Workplace Application",
         get_value(project_details, "workplace_application")],

        ["Source Document",
         get_value(analysis_report, "filename",
                   default="Uploaded PDF")],

        ["Total Source Pages",
         analysis_report.get("total_pages", 0)],

        ["Total Source Words",
         analysis_report.get("total_words", 0)],

        ["Total Curriculum Screens",
         len(curriculum)],

        ["Generation Status",
         "Generated - Pending Human Review"]
    ]

    add_data_rows(ws, project_rows)

    set_column_widths(ws, [30, 90])

    # --------------------------------------------------
    # SHEET 2: DOCUMENT ANALYSIS
    # --------------------------------------------------

    headers = [
        "Topic ID",
        "Main Topic",
        "Subtopic / Concept",
        "Key Information from Source",
        "Content Type",
        "Source Page(s)",
        "Evidence / Quote or Paraphrase",
        "Confidence",
        "Needs SME Review?",
        "Notes"
    ]

    ws = create_sheet(
        wb,
        "Document Analysis",
        "DOCUMENT ANALYSIS",
        "Source-grounded topics, evidence and document gaps.",
        headers
    )

    topics = analysis_report.get("topics", [])

    # Support the earlier candidate_headings format too
    if not topics:
        topics = analysis_report.get(
            "candidate_headings", []
        )

    document_rows = []

    for index, item in enumerate(topics, start=1):

        if isinstance(item, dict):

            topic = get_value(
                item, "topic", "heading", "main_topic",
                default="Unspecified topic"
            )

            source_page = get_value(
                item, "source_page", "page_number",
                "source_pages"
            )

            subtopic = get_value(
                item, "subtopic", "concept"
            )

            evidence = get_value(
                item, "evidence", "description",
                "content"
            )

            confidence = get_value(
                item, "confidence",
                default="Not assessed"
            )

        else:

            topic = str(item)
            source_page = ""
            subtopic = ""
            evidence = ""
            confidence = "Not assessed"

        document_rows.append([
            f"T{index:02d}",
            topic,
            subtopic,
            evidence,
            "Source Topic",
            normalise_source_pages(source_page),
            evidence,
            confidence,
            "Yes",
            "Verify source interpretation with SME."
        ])

    # Add identified gaps separately
    gaps = analysis_report.get(
        "identified_gaps", []
    )

    for gap in gaps:

        if isinstance(gap, dict):

            gap_text = get_value(
                gap, "description", "gap", "issue",
                default=str(gap)
            )

            gap_page = get_value(
                gap, "source_pages", "page_number"
            )

        else:

            gap_text = str(gap)
            gap_page = ""

        document_rows.append([
            "",
            "Identified Information Gap",
            gap_text,
            "Information requires further confirmation.",
            "Information Gap",
            normalise_source_pages(gap_page),
            "",
            "Not assessed",
            "Yes",
            "Do not invent missing information."
        ])

    add_data_rows(ws, document_rows)

    set_column_widths(
        ws,
        [12, 28, 28, 45, 18, 16, 40, 16, 18, 38]
    )

    # --------------------------------------------------
    # SHEET 3: CURRICULUM MAP
    # --------------------------------------------------

    headers = [
        "Module ID",
        "Module Title",
        "Lesson ID",
        "Lesson Title",
        "Learning Objective (measurable)",
        "Bloom's Level",
        "Prerequisite",
        "Instructional Strategy",
        "Estimated Duration (min)",
        "Assessment Method",
        "Source Topic IDs",
        "SME Review"
    ]

    ws = create_sheet(
        wb,
        "Curriculum Map",
        "CURRICULUM MAP",
        "Organise the learning journey at module and lesson level.",
        headers
    )

    curriculum_map = []
    seen_lessons = set()

    for index, screen in enumerate(curriculum, start=1):

        module_id = get_value(
            screen, "module_id", default="M01"
        )

        lesson_id = get_value(
            screen, "lesson_id",
            default=f"L{index:02d}"
        )

        lesson_key = (module_id, lesson_id)

        if lesson_key in seen_lessons:
            continue

        seen_lessons.add(lesson_key)

        curriculum_map.append([
            module_id,
            get_value(
                screen, "module_title",
                default="Module 1"
            ),
            lesson_id,
            get_value(
                screen, "lesson_title",
                "slide_title",
                default="Untitled lesson"
            ),
            get_value(
                screen, "learning_objective",
                "learning_objective_id"
            ),
            get_value(
                screen, "blooms_taxonomy_level",
                default="Not specified"
            ),
            get_value(screen, "prerequisite"),
            get_value(
                screen, "instructional_strategy"
            ),
            get_value(
                screen, "estimated_duration",
                default=0
            ),
            get_value(
                screen, "assessment",
                default="Not specified"
            ),
            get_value(
                screen, "source_topic_ids"
            ),
            "Pending"
        ])

    add_data_rows(ws, curriculum_map)

    set_column_widths(
        ws,
        [14, 30, 14, 32, 42, 18, 25, 30, 18, 25, 20, 18]
    )

    add_status_dropdown(ws, 12)

    # --------------------------------------------------
    # SHEET 4: SLIDE-BY-SLIDE DESIGN
    # --------------------------------------------------

    headers = [
        "Screen ID",
        "Module ID",
        "Lesson ID",
        "Sequence",
        "Screen Type",
        "Screen Title",
        "Learning Objective ID",
        "Bloom's Level",
        "Learner-Facing Content",
        "Narration / Facilitator Notes",
        "Instructional Strategy",
        "Interaction Type",
        "Learner Action",
        "Correct Response / Expected Behaviour",
        "Feedback (Correct)",
        "Feedback (Incorrect)",
        "Branching Rule / Next Screen",
        "Visual Direction / Layout",
        "Media / Asset Requirements",
        "Accessibility Notes",
        "Source Page(s) / Topic ID",
        "Estimated Duration (min)",
        "Assessment? (Y/N)",
        "SME Review Status",
        "Developer Build Notes"
    ]

    ws = create_sheet(
        wb,
        "Slide-by-Slide Design",
        "SCREEN-BY-SCREEN INSTRUCTIONAL DESIGN & BUILD SPECIFICATION",
        "One row per learner-facing screen. Designed for instructional designers, SMEs and developers.",
        headers
    )

    slide_rows = []

    for index, screen in enumerate(curriculum, start=1):

        slide_rows.append([
            get_value(
                screen, "screen_id",
                default=f"S{index:02d}"
            ),

            get_value(screen, "module_id", default="M01"),

            get_value(screen, "lesson_id", default="L01"),

            index,

            get_value(screen, "screen_type", default="Content"),

            get_value(
                screen, "slide_title",
                "screen_title",
                default="Untitled screen"
            ),

            get_value(screen, "learning_objective_id"),

            get_value(
                screen, "blooms_taxonomy_level",
                default="Not specified"
            ),

            get_value(
                screen, "learner_facing_content",
                "what_to_explain"
            ),

            get_value(
                screen, "narration",
                "narration_notes"
            ),

            get_value(screen, "instructional_strategy"),

            get_value(
                screen, "interaction_type",
                default="None"
            ),

            get_value(screen, "learner_action"),

            get_value(
                screen, "correct_response",
                "expected_behaviour"
            ),

            get_value(screen, "feedback_correct"),

            get_value(screen, "feedback_incorrect"),

            get_value(screen, "branching_rule"),

            get_value(
                screen, "visual_instructional_approach",
                "visual_direction"
            ),

            get_value(
                screen, "media_asset_requirements"
            ),

            get_value(screen, "accessibility_notes"),

            normalise_source_pages(
                get_value(screen, "source_page")
            ),

            get_value(
                screen, "estimated_duration",
                default=0
            ),

            get_value(
                screen, "assessment",
                default="No"
            ),

            get_value(
                screen, "sme_review_status",
                default="Pending"
            ),

            get_value(screen, "developer_notes")
        ])

    add_data_rows(ws, slide_rows)

    set_column_widths(
        ws,
        [
            12, 12, 12, 10, 20, 32, 18, 18, 50,
            45, 30, 22, 38, 40, 38, 38, 42,
            42, 35, 35, 20, 18, 16, 20, 40
        ]
    )

    add_status_dropdown(ws, 24)

    # --------------------------------------------------
    # SHEET 5: INTERACTION & BRANCHING
    # --------------------------------------------------

    headers = [
        "Interaction ID",
        "Trigger Screen ID",
        "Scenario / Prompt",
        "Choice ID",
        "Learner Choice",
        "Correct?",
        "Feedback Screen / State",
        "Next Screen ID",
        "Consequence / Explanation",
        "Retry Allowed?",
        "Scoring / Points",
        "Variable / State Change",
        "Source Topic ID",
        "SME Approval",
        "Developer Notes"
    ]

    ws = create_sheet(
        wb,
        "Interaction & Branching",
        "INTERACTION & BRANCHING SPECIFICATION",
        "Captures interaction and branching information explicitly generated by AI.",
        headers
    )

    interaction_rows = []

    for index, screen in enumerate(curriculum, start=1):

        interaction_type = get_value(
            screen, "interaction_type"
        )

        learner_action = get_value(
            screen, "learner_action"
        )

        branching_rule = get_value(
            screen, "branching_rule"
        )

        if (
            interaction_type
            or learner_action
            or branching_rule
        ):

            interaction_rows.append([
                f"INT{len(interaction_rows) + 1:02d}",
                get_value(
                    screen, "screen_id",
                    default=f"S{index:02d}"
                ),
                get_value(
                    screen, "scenario_prompt",
                    "slide_title"
                ),
                "",
                learner_action,
                "",
                "",
                branching_rule,
                get_value(
                    screen, "correct_response"
                ),
                "Not specified",
                "",
                "",
                get_value(screen, "source_topic_ids"),
                "Pending",
                get_value(screen, "developer_notes")
            ])

    add_data_rows(ws, interaction_rows)

    set_column_widths(
        ws,
        [
            14, 16, 38, 12, 38, 14, 24, 35,
            38, 18, 16, 28, 18, 18, 38
        ]
    )

    add_status_dropdown(ws, 14)

    # --------------------------------------------------
    # SHEET 6: GAMIFICATION PLAN
    # --------------------------------------------------

    headers = [
        "Mechanic ID",
        "Module / Screen",
        "Game Mechanic",
        "Trigger / Learner Behaviour",
        "Reward / Feedback",
        "Points / Badge",
        "Progression Rule",
        "Learning Purpose",
        "Accessibility / Fairness Notes"
    ]

    ws = create_sheet(
        wb,
        "Gamification Plan",
        "GAMIFICATION PLAN",
        "Gamification mechanics are not assumed. Populate after an explicit gamification design step.",
        headers
    )

    gamification_rows = []

    for index, screen in enumerate(curriculum, start=1):

        mechanic = get_value(
            screen, "game_mechanic"
        )

        if mechanic:

            gamification_rows.append([
                f"G{len(gamification_rows) + 1:02d}",
                get_value(
                    screen, "module_id",
                    default="M01"
                ) + " / " + get_value(
                    screen, "screen_id",
                    default=f"S{index:02d}"
                ),
                mechanic,
                get_value(screen, "trigger_behaviour"),
                get_value(screen, "reward_feedback"),
                get_value(screen, "points_badge"),
                get_value(screen, "progression_rule"),
                get_value(screen, "learning_purpose"),
                get_value(screen, "accessibility_notes")
            ])

    add_data_rows(ws, gamification_rows)

    if not gamification_rows:
        ws.append([
            "Not generated",
            "",
            "Gamification design pending",
            "",
            "",
            "",
            "",
            "Requires a separate instructional design decision.",
            ""
        ])

    set_column_widths(
        ws,
        [14, 20, 25, 38, 35, 20, 35, 40, 40]
    )

    # --------------------------------------------------
    # SHEET 7: ASSESSMENT BLUEPRINT
    # --------------------------------------------------

    headers = [
        "Question ID",
        "Module / Lesson",
        "Learning Objective ID",
        "Question / Task",
        "Question Type",
        "Bloom's Level",
        "Difficulty",
        "Options / Expected Response",
        "Correct Answer",
        "Feedback: Correct",
        "Feedback: Incorrect",
        "Points",
        "Source Page(s)",
        "SME Review"
    ]

    ws = create_sheet(
        wb,
        "Assessment Blueprint",
        "ASSESSMENT BLUEPRINT",
        "Only explicit assessment questions and answers are populated.",
        headers
    )

    assessment_rows = []

    for screen in curriculum:

        question = get_value(
            screen, "assessment_question",
            "question"
        )

        if not question:
            continue

        assessment_rows.append([
            f"Q{len(assessment_rows) + 1:02d}",

            get_value(screen, "module_id", default="M01")
            + " / "
            + get_value(screen, "lesson_id", default="L01"),

            get_value(screen, "learning_objective_id"),

            question,

            get_value(
                screen, "question_type",
                default="Not specified"
            ),

            get_value(
                screen, "blooms_taxonomy_level"
            ),

            get_value(
                screen, "difficulty",
                default="Not specified"
            ),

            get_value(
                screen, "options",
                "expected_response"
            ),

            get_value(screen, "correct_answer"),

            get_value(screen, "feedback_correct"),

            get_value(screen, "feedback_incorrect"),

            get_value(screen, "points"),

            normalise_source_pages(
                get_value(screen, "source_page")
            ),

            "Pending"
        ])

    add_data_rows(ws, assessment_rows)

    if not assessment_rows:
        ws.append([
            "Not generated",
            "",
            "",
            "No structured assessment questions were returned by AI.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Pending"
        ])

    set_column_widths(
        ws,
        [
            14, 20, 20, 45, 22, 18, 16,
            42, 25, 38, 38, 12, 18, 18
        ]
    )

    add_status_dropdown(ws, 14)

    # --------------------------------------------------
    # SHEET 8: QUALITY REVIEW
    # --------------------------------------------------

    headers = [
        "Check ID",
        "Quality Dimension",
        "Validation Question",
        "Status",
        "Evidence / Finding",
        "Required Action",
        "Owner",
        "Review Date"
    ]

    ws = create_sheet(
        wb,
        "Quality Review",
        "QUALITY REVIEW",
        "Human review checklist. These checks are not automatically approved.",
        headers
    )

    quality_checks = [
        [
            "QC01",
            "Source Traceability",
            "Does every factual screen have a source page or topic reference?"
        ],
        [
            "QC02",
            "Learning Objectives",
            "Are learning objectives measurable and aligned with the content?"
        ],
        [
            "QC03",
            "Bloom's Taxonomy",
            "Is the cognitive level appropriate for the learner action?"
        ],
        [
            "QC04",
            "Content Accuracy",
            "Has the SME verified technical and organisational information?"
        ],
        [
            "QC05",
            "Instructional Design",
            "Does each screen have a clear learning purpose?"
        ],
        [
            "QC06",
            "Interaction Design",
            "Are learner actions and feedback clearly specified?"
        ],
        [
            "QC07",
            "Assessment Alignment",
            "Do assessments measure the stated learning objectives?"
        ],
        [
            "QC08",
            "Accessibility",
            "Have accessibility requirements been considered?"
        ],
        [
            "QC09",
            "Developer Handoff",
            "Are the visual and build instructions sufficiently clear?"
        ],
        [
            "QC10",
            "Content Gaps",
            "Have missing information and SME questions been identified?"
        ]
    ]

    quality_rows = []

    for check in quality_checks:

        quality_rows.append([
            check[0],
            check[1],
            check[2],
            "Not started",
            "",
            "Review and record evidence.",
            "",
            ""
        ])

    add_data_rows(ws, quality_rows)

    set_column_widths(
        ws,
        [14, 25, 55, 20, 42, 42, 20, 18]
    )

    # Quality status dropdown
    quality_validation = DataValidation(
        type="list",
        formula1='"Not started,In Progress,Passed,Failed,Not Applicable"',
        allow_blank=True
    )

    ws.add_data_validation(quality_validation)

    quality_validation.add("D5:D500")

    # --------------------------------------------------
    # 3. Workbook-wide formatting
    # --------------------------------------------------

    for ws in wb.worksheets:

        ws.sheet_view.showGridLines = False

        ws.sheet_properties.pageSetUpPr.fitToPage = True

        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0

        ws.sheet_view.zoomScale = 85

    # Save workbook
    wb.save(output_path)

    return output_path
