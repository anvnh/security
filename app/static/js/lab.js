// JavaScript for Demonstration Guide copy buttons
document.addEventListener("DOMContentLoaded", function () {
    const copyButtons = document.querySelectorAll(".btn-copy");

    copyButtons.forEach(button => {
        button.addEventListener("click", function () {
            const targetId = button.getAttribute("data-target");
            const targetInput = document.getElementById(targetId);

            if (!targetInput) return;

            navigator.clipboard.writeText(targetInput.value).then(() => {
                const originalText = button.textContent;
                button.textContent = "Copied!";
                button.classList.add("btn-primary");
                button.classList.remove("btn-secondary");

                setTimeout(() => {
                    button.textContent = originalText;
                    button.classList.add("btn-secondary");
                    button.classList.remove("btn-primary");
                }, 2000);
            }).catch(err => {
                console.error("Failed to copy payload:", err);
                targetInput.select();
            });
        });
    });
});
