import datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.test import RequestFactory

from labels.api import LayoutViewSet

# Per plan.md's Structure Decision (Constitution Principle V), layouts_ui never
# imports labels.models directly - it goes through the labels API surface
# in-process via RequestFactory, the same way the real HTTP API is dispatched.
_factory = RequestFactory()


def _call_api(method, path, action, query=None, **view_kwargs):
    request = getattr(_factory, method)(path, query or {})
    view = LayoutViewSet.as_view({method: action})
    return view(request, **view_kwargs)


def layout_new(request):
    """User Story 1: new-layout creation form with live preview."""
    return render(
        request,
        "layouts_ui/layout_form.html",
        {
            "mode": "create",
            "layout_id": None,
            "layout": None,
        },
    )


def layout_list(request):
    """User Story 2: browse saved layouts."""
    response = _call_api("get", "/api/layouts/", "list")
    return render(request, "layouts_ui/layout_list.html", {"layouts": response.data["results"]})


def layout_detail(request, layout_id):
    """User Story 2: open a selected layout (read-only view)."""
    response = _call_api("get", f"/api/layouts/{layout_id}/", "retrieve", pk=layout_id)
    if response.status_code == 404:
        raise Http404("Layout not found")
    # 002-print-layout-a4 User Story 3: print history for this layout.
    print_events = _call_api(
        "get", f"/api/layouts/{layout_id}/print-events/", "print_events", pk=layout_id
    ).data["results"]
    return render(
        request,
        "layouts_ui/layout_detail.html",
        {"layout": response.data, "print_events": print_events},
    )


def layout_edit(request, layout_id):
    """User Story 3: edit an existing layout, pre-filled, saved in place via PUT."""
    response = _call_api("get", f"/api/layouts/{layout_id}/", "retrieve", pk=layout_id)
    if response.status_code == 404:
        raise Http404("Layout not found")
    return render(
        request,
        "layouts_ui/layout_form.html",
        {
            "mode": "edit",
            "layout_id": layout_id,
            "layout": response.data,
        },
    )


def layout_print(request, layout_id):
    """002-print-layout-a4 User Story 1/2: printable A4 page (full run or a range)."""
    query = {k: v for k, v in {"start": request.GET.get("start"), "end": request.GET.get("end")}.items() if v}
    response = _call_api(
        "get", f"/api/layouts/{layout_id}/print-sheets/", "print_sheets", query=query, pk=layout_id
    )
    if response.status_code == 404:
        raise Http404("Layout not found")
    if response.status_code != 200:
        # US2 T013: invalid ranges (FR-011) send staff back to the detail page
        # with an explanation, instead of showing a raw API error.
        error_message = response.data.get("errors", {}).get("range", "Невалиден диапазон от листове.")
        messages.error(request, f"Неуспешен печат: {error_message}")
        return redirect("layouts_ui:layout_detail", layout_id=layout_id)

    # Presentation-only: the reference label shows dates as "28.10.2025",
    # not the API's ISO "2025-10-28" - reformat here (client layer), not in
    # labels' API contract.
    data = response.data
    order_date = datetime.date.fromisoformat(data["layout"]["order_date"])
    data = {**data, "layout": {**data["layout"], "order_date": order_date.strftime("%d.%m.%Y")}}

    return render(request, "layouts_ui/layout_print.html", {"data": data, "layout_id": layout_id})
