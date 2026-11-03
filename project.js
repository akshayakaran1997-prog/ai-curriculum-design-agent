
/* =========================================
   CURRICULUM AI - PROJECT WORKSPACE
   Dashboard functionality
========================================= */

// 1. Find the HTML elements we want to control.

const saveButton = document.getElementById("saveButton");

const saveStatus = document.getElementById("saveStatus");

const fileInput = document.getElementById("sourceFiles");

const fileList = document.getElementById("fileList");


// 2. List all project fields that we want to save.

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


// 3. Display selected document names.

fileInput.addEventListener("change", function () {

    const files = Array.from(fileInput.files);

    if (files.length === 0) {
        fileList.textContent = "No documents selected.";
        return;
    }

    const fileNames = files.map(function (file) {
        return file.name;
    });

    fileList.textContent =
        "Selected documents: " + fileNames.join(", ");

});


// 4. Collect the information entered in the form.

function collectProjectData() {

    const projectData = {};

    projectFields.forEach(function (fieldId) {

        const field = document.getElementById(fieldId);

        projectData[fieldId] = field.value.trim();

    });

    // Save document names as information only.
    // Actual document contents are not uploaded yet.

    projectData.documentNames = Array.from(fileInput.files).map(
        function (file) {
            return file.name;
        }
    );

    projectData.lastSaved = new Date().toISOString();

    return projectData;

}


// 5. Save the project draft in browser storage.

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


// 6. Connect the save button to the save function.

saveButton.addEventListener("click", saveProject);


// 7. Restore a previously saved project draft.

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
                "Previously selected document names: " +
                projectData.documentNames.join(", ") +
                ". Please select the files again.";

        }

        saveStatus.textContent =
            "Previous project draft restored from this browser.";

    } catch (error) {

        saveStatus.textContent =
            "Could not restore the previous project draft.";

        console.error("Project restore error:", error);

    }

}


// 8. Highlight the selected sidebar navigation link.

const navigationLinks = document.querySelectorAll(".nav-link");

navigationLinks.forEach(function (link) {

    link.addEventListener("click", function () {

        navigationLinks.forEach(function (item) {

            item.classList.remove("active");

        });

        link.classList.add("active");

    });

});


// 9. Load saved project information when the page opens.

document.addEventListener("DOMContentLoaded", loadProject);
