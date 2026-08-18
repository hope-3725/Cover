# Implementation Plan: Label Layout Management

**Branch**: `001-label-layout-management` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-label-layout-management/spec.md`

## Summary

Staff of the printing house can create, browse, and edit label "layouts" (макети) —
order records for a client's box-label print job. Each layout captures order details
(client, product, PO/SAP references) plus two production numbers, `quantity_in_cover`
(articles per box, printed on the label) and `issue` (total articles produced, internal
only). The system derives, live, how many labels and how many A4 sheets (2 columns × 4
labels each) the job needs, and persists every layout to SQLite so it can be reopened
and edited later. Technical approach: a Django project with a REST API layer (Django
REST Framework) backed by Django's ORM against SQLite, and a thin server-rendered
template layer that calls that API for live preview/recompute — resolving the
Django-vs-Prisma and Jest/Vitest-vs-Python conflicts the constitution flagged as
deferred (see Research §1–§2).

## Technical Context

**Language/Version**: Python 3.12, Django 5.x

**Primary Dependencies**: Django (ORM, templating, migrations), Django REST Framework
(API viewsets/serializers for the layout CRUD + compute endpoints)

**Storage**: SQLite, accessed through Django's built-in ORM (see Research §1 for why
this replaces the brief's literal "Prisma ORM" request)

**Testing**: Django's built-in test framework (`django.test.TestCase` /
`rest_framework.test.APITestCase`), run via `manage.py test` (see Research §2 for why
this replaces the brief's literal "Jest or Vitest" request)

**Target Platform**: Server-rendered web app; local development via `manage.py
runserver`, deployable to any WSGI-compatible host. No offline or mobile requirement.

**Project Type**: Web application — Django monolith with an internal API layer, not a
separate SPA frontend (see Structure Decision below for how client/server modularity
is still satisfied per Constitution Principle V)

**Performance Goals**: Not specified by the brief; this is a low-concurrency internal
tool (printing-house staff only, per FR-010). No specific throughput/latency target is
defined for this feature — default to typical small internal-tool responsiveness
(interactive preview recompute perceived as instant, i.e. well under 1s on local data).

**Constraints**: Print output is fixed at A4, 2 columns × 4 blocks (8 labels/sheet) per
Constitution Principle III; this feature computes counts against that constant but does
not yet render an actual print (out of scope per spec Assumptions).

**Scale/Scope**: Small internal deployment — a handful of concurrent staff users,
layouts numbering in the hundreds to low thousands over time. No scale-driven
architectural decisions are required.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Confirm Before Building | All label/template parameters and the label-count formula were confirmed with the user against a real reference label before this plan was written (see spec.md Clarifications). | PASS |
| II. Durable Storage Is the Source of Truth | Layouts persist via Django ORM → SQLite (FR-002); JSON import/export is explicitly out of scope here, so no conflict with "JSON is portability, not the store." | PASS |
| III. Print Output Fidelity | FR-007's sheet formula is built on the fixed 8-labels-per-A4-sheet (2×4) constant; this feature does not alter that geometry. | PASS |
| IV. Tested API Surface | Django REST Framework endpoints for create/list/retrieve/update layout and the compute action will have `APITestCase` coverage before being considered done (see tasks.md, generated separately by `/speckit-tasks`). | PASS (planned) |
| V. Modular Client/Server Separation | Two Django apps: `labels` (models, services, serializers, API — the server) and `layouts_ui` (templates, static JS/CSS calling the API — the client). See Structure Decision. | PASS |

No violations requiring justification — Complexity Tracking table is empty.

**Post-Phase 1 re-check**: `data-model.md`, `contracts/layouts-api.md`, and
`quickstart.md` introduce no new entities, endpoints, or dependencies beyond what the
table above already covers — all five principles remain PASS. Principle IV moves from
"PASS (planned)" to confirmed-coverable: `contracts/layouts-api.md` enumerates every
endpoint an `APITestCase` suite must cover, and `quickstart.md`'s Automated Tests
section names the concrete test modules (`test_services.py`, `test_api.py`).

## Project Structure

### Documentation (this feature)

```text
specs/001-label-layout-management/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/             # Phase 1 output (/speckit-plan command)
│   └── layouts-api.md
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
cover/                        # Django project package (settings, root urls, wsgi/asgi)
├── settings.py
├── urls.py
├── wsgi.py
└── asgi.py

labels/                        # "server": business logic + API (Constitution Principle V)
├── models.py                  # Layout model (data-model.md)
├── services.py                 # label/sheet-count formula (FR-007)
├── serializers.py              # DRF serializers + validation (FR-009)
├── api.py                      # DRF viewsets (CRUD) + compute action
├── urls.py                     # API route registration
├── migrations/
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_api.py

layouts_ui/                    # "client": server-rendered pages consuming the API
├── views.py                    # thin views rendering templates
├── urls.py
├── templates/layouts_ui/
│   ├── layout_list.html        # US2: browse/select
│   ├── layout_form.html        # US1/US3: create/edit + live preview
│   └── layout_detail.html
├── static/layouts_ui/
│   ├── layout_preview.js       # calls labels API to recompute preview (FR-008)
│   └── layout_form.css
└── tests/
    └── test_views.py

manage.py
requirements.txt
```

**Structure Decision**: Django project with two apps rather than a separate
frontend/backend service pair — there is no independent SPA client, so the template's
"Option 2: Web application" (distinct frontend/backend services) doesn't literally
apply. Instead, Constitution Principle V's client/server separation is satisfied at the
Django-app boundary: `labels` owns all data access, business rules (the count formula),
and the API contract; `layouts_ui` owns presentation only and talks to `labels`
exclusively through that API (never imports its models/services directly), so the two
remain swappable/testable independently.

## Complexity Tracking

*No entries — Constitution Check has no unjustified violations.*
