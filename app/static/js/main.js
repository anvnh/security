// Main vanilla JavaScript for Bblog navigation and progressive enhancement
document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("sidebarToggle");
    const appShell = document.getElementById("appShell");

    if (toggleBtn && appShell) {
        const isMobile = () => window.matchMedia("(max-width: 900px)").matches;

        if (!isMobile() && localStorage.getItem("bblog_sidebar_collapsed") === "1") {
            appShell.classList.add("sidebar-collapsed");
            toggleBtn.setAttribute("aria-expanded", "false");
        }

        toggleBtn.addEventListener("click", function () {
            if (isMobile()) {
                const opened = appShell.classList.toggle("sidebar-open");
                toggleBtn.setAttribute("aria-expanded", opened ? "true" : "false");
            } else {
                const collapsed = appShell.classList.toggle("sidebar-collapsed");
                localStorage.setItem("bblog_sidebar_collapsed", collapsed ? "1" : "0");
                toggleBtn.setAttribute("aria-expanded", collapsed ? "false" : "true");
            }
        });
    }

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
