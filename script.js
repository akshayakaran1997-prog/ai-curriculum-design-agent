
// CURRICULUM AI
// Main frontend interaction controller

function startProject() {

    // Navigate to the project creation page.
    // We will create this page in our next development stage.

    window.location.href = "project.html";

}


// Smooth navigation for internal links

document.querySelectorAll('a[href^="#"]').forEach(link => {

    link.addEventListener("click", function(event) {

        const target = document.querySelector(
            this.getAttribute("href")
        );

        if (target) {
            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth"
            });
        }

    });

});


// Welcome message in browser console

console.log("Curriculum AI frontend loaded successfully.");
console.log("Welcome to the Intelligent Learning Design Workspace!");
