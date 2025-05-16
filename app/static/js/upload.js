document.addEventListener("DOMContentLoaded", () => {
        // Force all input[type="date"] to disable future dates visually (make them unselectable)
        const today = new Date().toISOString().split("T")[0];
        document.querySelectorAll('input[type="date"]').forEach(input => {
            input.setAttribute('max', today);
        });

        const hiddenInput = document.getElementById("csvCategory");
        const tabButtons = document.querySelectorAll("#uploadTabs button");
        tabButtons.forEach(button => {
            button.addEventListener("click", () => {
                const selectedTab = button.getAttribute("data-bs-target").substring(1); // "exercise", "diet", "sleep"
                hiddenInput.value = selectedTab;
            });
        });

       
    });