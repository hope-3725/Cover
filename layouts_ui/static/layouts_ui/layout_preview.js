(function () {
    "use strict";

    const form = document.getElementById("layout-form");
    if (!form) {
        return;
    }

    const mode = form.dataset.mode; // "create" | "edit"
    const layoutId = form.dataset.layoutId;
    const countFields = ["quantity_in_cover", "issue"];
    const previewTargets = {
        full_label_count: document.getElementById("preview-full_label_count"),
        remainder: document.getElementById("preview-remainder"),
        total_label_count: document.getElementById("preview-total_label_count"),
        total_sheet_count: document.getElementById("preview-total_sheet_count"),
    };
    const errorsBox = document.getElementById("form-errors");

    let dirty = false;
    let justSubmitted = false;
    let debounceHandle = null;

    function markDirty() {
        dirty = true;
    }

    form.querySelectorAll("input, textarea").forEach(function (el) {
        el.addEventListener("input", markDirty);
    });

    // FR-012: warn before discarding unsaved changes.
    window.addEventListener("beforeunload", function (event) {
        if (dirty && !justSubmitted) {
            event.preventDefault();
            event.returnValue = "";
        }
    });

    function currentCountInputs() {
        const quantityInCover = form.querySelector("#quantity_in_cover").value;
        const issue = form.querySelector("#issue").value;
        return { quantity_in_cover: quantityInCover, issue: issue };
    }

    function renderPreview(data) {
        Object.keys(previewTargets).forEach(function (key) {
            previewTargets[key].textContent = data[key];
        });
    }

    function clearPreview() {
        Object.keys(previewTargets).forEach(function (key) {
            previewTargets[key].textContent = "-";
        });
    }

    // FR-006, FR-008: recompute the live preview as parameters change.
    function refreshPreview() {
        const { quantity_in_cover, issue } = currentCountInputs();
        if (quantity_in_cover === "" || issue === "") {
            clearPreview();
            return;
        }
        fetch("/api/layouts/preview/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                quantity_in_cover: Number(quantity_in_cover),
                issue: Number(issue),
            }),
        })
            .then(function (response) {
                if (!response.ok) {
                    clearPreview();
                    return null;
                }
                return response.json();
            })
            .then(function (data) {
                if (data) {
                    renderPreview(data);
                }
            })
            .catch(clearPreview);
    }

    countFields.forEach(function (name) {
        const el = form.querySelector("#" + name);
        el.addEventListener("input", function () {
            clearTimeout(debounceHandle);
            debounceHandle = setTimeout(refreshPreview, 200);
        });
    });

    function renderErrors(errors) {
        errorsBox.innerHTML = "";
        Object.keys(errors).forEach(function (field) {
            const message = Array.isArray(errors[field]) ? errors[field].join(" ") : String(errors[field]);
            const p = document.createElement("p");
            p.className = "field-error";
            p.dataset.field = field;
            p.textContent = field + ": " + message;
            errorsBox.appendChild(p);
        });
    }

    function collectPayload() {
        const payload = {};
        form.querySelectorAll("input[name], textarea[name]").forEach(function (el) {
            if (countFields.includes(el.name)) {
                payload[el.name] = el.value === "" ? el.value : Number(el.value);
            } else {
                payload[el.name] = el.value;
            }
        });
        return payload;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        errorsBox.innerHTML = "";

        const url = mode === "edit" ? "/api/layouts/" + layoutId + "/" : "/api/layouts/";
        const method = mode === "edit" ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(collectPayload()),
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                if (!result.ok) {
                    renderErrors(result.data);
                    return;
                }
                justSubmitted = true;
                window.location.href = "/layouts/" + result.data.id + "/";
            })
            .catch(function () {
                renderErrors({ non_field_errors: "Възникна грешка при запис. Опитайте отново." });
            });
    });

    // Initial preview render for edit mode, where fields are pre-filled.
    if (mode === "edit") {
        refreshPreview();
    }
})();
