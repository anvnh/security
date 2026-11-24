// Main vanilla JavaScript for security laboratory
document.addEventListener("DOMContentLoaded", function () {
    const toggleForm = document.getElementById("securityToggleForm");
    if (!toggleForm) return;

    toggleForm.addEventListener("submit", function (e) {
        // Allow progressive enhancement: if javascript fails or is disabled, standard POST form submit runs
        e.preventDefault();

        const formData = new FormData(toggleForm);

        fetch(toggleForm.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
            .then(response => {
                if (!response.ok) {
                    toggleForm.submit();
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;
                // Reload current page to update view according to new security mode
                window.location.reload();
            })
            .catch(() => {
                toggleForm.submit();
            });
    });
});
