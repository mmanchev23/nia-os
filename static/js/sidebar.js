document.addEventListener("DOMContentLoaded", function () {
    const collapses = document.querySelectorAll(".collapse");

    collapses.forEach(collapse => {
        const input = collapse.querySelector("input[type='checkbox']");

        input.addEventListener("change", () => {
            if (input.checked) {
                collapses.forEach(otherCollapse => {
                    const otherInput = otherCollapse.querySelector("input[type='checkbox']");

                    if (otherInput !== input) {
                        otherInput.checked = false;
                    }
                });
            }
        });
    });

    document.addEventListener("click", (e) => {
        const isInsideCollapse = e.target.closest(".collapse");

        if (!isInsideCollapse) {
            collapses.forEach(collapse => {
                const input = collapse.querySelector("input[type='checkbox']");
                input.checked = false;
            });
        }
    });

    const themeToggle = document.getElementById("theme-toggle");

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
        themeToggle.checked = savedTheme === "dark";
    }

    themeToggle.addEventListener("change", () => {
        const newTheme = themeToggle.checked ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
    });
});
