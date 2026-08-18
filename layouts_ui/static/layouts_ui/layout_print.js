(function () {
    "use strict";

    const printButton = document.getElementById("print-button");
    if (!printButton) {
        return;
    }

    // research.md S2: record the print event on explicit click, not on page
    // view, since a page load/refresh is not a reliable "staff printed this"
    // signal - the button click is the closest one available.
    function recordPrintEvent() {
        const layoutId = printButton.dataset.layoutId;
        const start = printButton.dataset.start;
        const end = printButton.dataset.end;
        return fetch("/api/layouts/" + layoutId + "/print-events/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sheet_start: Number(start), sheet_end: Number(end) }),
        });
    }

    printButton.addEventListener("click", function () {
        recordPrintEvent().finally(function () {
            window.print();
        });
    });
})();
