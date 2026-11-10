
/* =========================================
   CURRICULUM AI - PROJECT WORKSPACE
   Frontend + FastAPI Integration
========================================= */

// =========================================
// 1. BACKEND CONFIGURATION
// =========================================

// Replace this with your actual Codespaces
// forwarded port 8000 URL.
// Do not include a trailing slash.

const API_BASE_URL = "https://silver-cod-5v5jxx9rx9rrh7qrp-8000.app.github.dev";


// =========================================
// 2. FIND HTML ELEMENTS
// =========================================

const saveButton = document.getElementById("saveButton");
const saveStatus = document.getElementById("saveStatus");

const fileInput = document.getElementById("sourceFiles");
const fileList = document.getElementById("fileList");

const generateButton = document.getElementById("generateButton");
const generationStatus = document.getElementById("generationStatus");

const curriculumResults = document.getElementById("curriculumResults");
const downloadSection = document.getElementById("downloadSection");


// =========================================
// 3. PROJECT FIELDS
// =========================================

const projectFields = [
    "projectName",
    "courseType",
    "duration",
    "delivery",
    "difficulty",
    "businessNeed",
    "targetAudience",
    "existingKnowledge",
    "learningOutcomes",
    "workplaceApplication",
    "performanceGap"
];


// =========================================
// 4. DISPLAY SELECTED PDF
// =========================================

fileInput.addEventListener("change", function () {

    const file = fileInput.files[0];

    curriculumResults.innerHTML = "";
    downloadSection.innerHTML = "";

    if (!file) {
        fileList.textContent = "No document selected.";
        return;
    }

    const fileExtension = file.name.split(".").pop().toLowerCase();

    if (fileExtension !== "pdf") {

        fileList.textContent = "Please select a PDF document.";

        fileInput.value = "";

        return;
    }

    fileList.textContent =
        "Selected document: " + file.name;

    generationStatus.textContent =
        "Your PDF is ready for AI analysis.";

});


// =========================================
// 5. COLLECT PROJECT INFORMATION
// =========================================

function collectProjectData() {

    const projectData = {};

    projectFields.forEach(function (fieldId) {

        const field = document.getElementById(fieldId);

        projectData[fieldId] = field ? field.value.trim() : "";

    });

    projectData.documentNames = fileInput.files.length
        ? [fileInput.files[0].name]
        : [];

    projectData.lastSaved = new Date().toISOString();

    return projectData;

}


// =========================================
// 6. SAVE PROJECT DRAFT
// =========================================

function saveProject() {

    const projectName =
        document.getElementById("projectName").value.trim();

    if (!projectName) {

        saveStatus.textContent =
            "Please enter a project name before saving.";

        document.getElementById("projectName").focus();

        return;
    }

    const projectData = collectProjectData();

    try {

        localStorage.setItem(
            "curriculumAIProjectDraft",
            JSON.stringify(projectData)
        );

        saveStatus.textContent =
            "Project draft saved successfully in this browser.";

    } catch (error) {

        saveStatus.textContent =
            "Unable to save the project. Please try again.";

        console.error("Project save error:", error);

    }

}

saveButton.addEventListener("click", saveProject);


// =========================================
// 7. RESTORE PROJECT DRAFT
// =========================================

function loadProject() {

    const savedProject = localStorage.getItem(
        "curriculumAIProjectDraft"
    );

    if (!savedProject) {
        return;
    }

    try {

        const projectData = JSON.parse(savedProject);

        projectFields.forEach(function (fieldId) {

            const field = document.getElementById(fieldId);

            if (field && projectData[fieldId] !== undefined) {

                field.value = projectData[fieldId];

            }

        });

        if (
            projectData.documentNames &&
            projectData.documentNames.length > 0
        ) {

            fileList.textContent =
                "Previously selected document: " +
                projectData.documentNames.join(", ") +
                ". Please select the PDF again.";

        }

        saveStatus.textContent =
            "Previous project draft restored from this browser.";

    } catch (error) {

        saveStatus.textContent =
            "Could not restore the previous project draft.";

        console.error("Project restore error:", error);

    }

}


// =========================================
// 8. GENERATE CURRICULUM USING FASTAPI
// =========================================

async function generateCurriculum() {

    const file = fileInput.files[0];

    // Validate project name

    const projectName =
        document.getElementById("projectName").value.trim();

    if (!projectName) {

        generationStatus.textContent =
            "Please enter a project name first.";

        document.getElementById("projectName").focus();

        return;
    }

    // Validate PDF selection

    if (!file) {

        generationStatus.textContent =
            "Please upload a PDF document first.";

        return;
    }

    if (file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")) {

        generationStatus.textContent =
            "Only PDF documents are supported.";

        return;
    }

    // Validate backend URL

    if (API_BASE_URL.includes("PASTE_YOUR")) {

        generationStatus.textContent =
            "Please configure your FastAPI backend URL in project.js.";

        return;
    }

    // Clear previous results

    curriculumResults.innerHTML = "";
    downloadSection.innerHTML = "";

    // Show processing status

    generateButton.disabled = true;

    generateButton.textContent =
        "Generating Curriculum...";

    generationStatus.textContent =
        "Uploading document and analysing its content. Please wait...";

    try {

        // Prepare PDF for backend upload

        const formData = new FormData();

        formData.append("file", file);

        // Send PDF to FastAPI

        const response = await fetch(
            `${API_BASE_URL}/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        // Read backend response

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || data.message ||
                "Unable to generate curriculum."
            );

        }

        if (data.status !== "success" || !data.curriculum) {

            throw new Error(
                data.message || "Unexpected response from the backend."
            );

        }

        // Display success message

        generationStatus.textContent =
            "Curriculum generated successfully!";

        // Display curriculum preview

        displayCurriculum(data.curriculum);

        // Display Excel download link

        displayDownloadLink(data);

    } catch (error) {

        console.error("Curriculum generation error:", error);

        generationStatus.textContent =
            "Error: " + error.message;

    } finally {

        generateButton.disabled = false;

        generateButton.textContent =
            "✦ Generate Curriculum";

    }

}


// =========================================
// 9. DISPLAY GENERATED CURRICULUM
// =========================================

function displayCurriculum(curriculum) {

    curriculumResults.innerHTML = "";

    const overview = curriculum.course_overview || {};

    const modules = curriculum.curriculum_outline || [];

    // Course overview heading

    const heading = document.createElement("h3");

    heading.textContent = "Generated Course Overview";

    curriculumResults.appendChild(heading);

    // Course overview information

    const overviewContainer = document.createElement("div");

    overviewContainer.className = "generated-overview";

    addTextItem(
        overviewContainer,
        "Course Title",
        overview.course_title
    );

    addTextItem(
        overviewContainer,
        "Business Need",
        overview.business_need
    );

    addTextItem(
        overviewContainer,
        "Course Purpose",
        overview.course_purpose
    );

    addTextItem(
        overviewContainer,
        "Target Audience",
        overview.target_audience
    );

    addTextItem(
        overviewContainer,
        "Delivery Format",
        overview.delivery_format
    );

    addTextItem(
        overviewContainer,
        "Estimated Duration",
        overview.total_duration_minutes
            ? overview.total_duration_minutes + " minutes"
            : "Not specified"
    );

    // Learning objectives

    const objectiveHeading = document.createElement("h4");

    objectiveHeading.textContent = "Learning Objectives";

    overviewContainer.appendChild(objectiveHeading);

    const objectiveList = document.createElement("ul");

    (overview.learning_objectives || []).forEach(function (objective) {

        const item = document.createElement("li");

        item.textContent = objective;

        objectiveList.appendChild(item);

    });

    overviewContainer.appendChild(objectiveList);

    curriculumResults.appendChild(overviewContainer);


    // Module outline heading

    const moduleHeading = document.createElement("h3");

    moduleHeading.textContent =
        "Curriculum Outline (" + modules.length + " Modules)";

    curriculumResults.appendChild(moduleHeading);


    // Display each module

    modules.forEach(function (module) {

        const moduleCard = document.createElement("div");

        moduleCard.className = "generated-module";

        const title = document.createElement("h4");

        title.textContent =
            "Module " + module.module_number +
            ": " + module.module_title;

        moduleCard.appendChild(title);

        addTextItem(
            moduleCard,
            "What learners will learn",
            module.what_learners_will_learn
        );

        addTextItem(
            moduleCard,
            "Learning Approach",
            module.learning_approach
        );

        addTextItem(
            moduleCard,
            "Estimated Duration",
            module.estimated_duration_minutes
                ? module.estimated_duration_minutes + " minutes"
                : "Not specified"
        );

        addTextItem(
            moduleCard,
            "Source Pages",
            (module.source_pages || []).join(", ")
        );

        // Topics covered

        const topicsHeading = document.createElement("p");

        topicsHeading.textContent = "Topics Covered:";

        moduleCard.appendChild(topicsHeading);

        const topicList = document.createElement("ul");

        (module.topics_covered || []).forEach(function (topic) {

            const topicItem = document.createElement("li");

            topicItem.textContent = topic;

            topicList.appendChild(topicItem);

        });

        moduleCard.appendChild(topicList);

        curriculumResults.appendChild(moduleCard);

    });

}


// =========================================
// 10. HELPER TO DISPLAY TEXT SAFELY
// =========================================

function addTextItem(container, label, value) {

    const paragraph = document.createElement("p");

    const strong = document.createElement("strong");

    strong.textContent = label + ": ";

    const text = document.createTextNode(
        value !== undefined && value !== null && value !== ""
            ? String(value)
            : "Not specified"
    );

    paragraph.appendChild(strong);

    paragraph.appendChild(text);

    container.appendChild(paragraph);

}


// =========================================
// 11. DISPLAY EXCEL DOWNLOAD LINK
// =========================================

function displayDownloadLink(data) {

    downloadSection.innerHTML = "";

    const heading = document.createElement("h3");

    heading.textContent = "Download Your Curriculum";

    const description = document.createElement("p");

    description.textContent =
        "Your four-sheet curriculum workbook is ready.";

    const downloadLink = document.createElement("a");

    downloadLink.href =
        API_BASE_URL + data.download_url;

    downloadLink.textContent =
        "Download Curriculum Excel";

    downloadLink.className = "download-button";

    downloadLink.setAttribute("download", "");

    downloadSection.appendChild(heading);

    downloadSection.appendChild(description);

    downloadSection.appendChild(downloadLink);

}


// =========================================
// 12. CONNECT GENERATE BUTTON
// =========================================

generateButton.addEventListener(
    "click",
    generateCurriculum
);


// =========================================
// 13. SIDEBAR NAVIGATION
// =========================================

const navigationLinks =
    document.querySelectorAll(".nav-link");

navigationLinks.forEach(function (link) {

    link.addEventListener("click", function () {

        navigationLinks.forEach(function (item) {

            item.classList.remove("active");

        });

        link.classList.add("active");

    });

});


// =========================================
// 14. LOAD SAVED PROJECT ON PAGE OPEN
// =========================================

document.addEventListener(
    "DOMContentLoaded",
    loadProject
);
