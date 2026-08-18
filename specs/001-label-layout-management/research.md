# Research: Label Layout Management

## 1. Data-access layer: Django ORM vs. Prisma

**Decision**: Use Django's built-in ORM against SQLite. Do not use Prisma.

**Rationale**: `Cover.md` literally requests "SQLite чрез Prisma ORM," but Prisma is a
Node.js/TypeScript-native tool with no official Python or Django integration. The only
option to honor it literally would be the unofficial, community-maintained "Prisma
Client Python" project, which does not integrate with Django's migrations, admin site,
or `ModelForm`/DRF-serializer ecosystem — using it would mean fighting the framework on
every feature for no functional benefit, and introduces a maintenance risk (unofficial,
smaller community, unclear longevity) for a requirement that SQLite persistence
(Constitution Principle II) does not actually depend on. Django's own ORM is the
standard, first-party way to reach SQLite from Django, ships with migrations and admin
integration out of the box, and is what the rest of this plan (DRF serializers, test
framework) is built around.

**Alternatives considered**:
- *Prisma Client Python*: rejected — unofficial, poor Django interop, no migrations
  integration, would require bypassing Django's model layer entirely.
- *Raw SQL / sqlite3 stdlib*: rejected — loses migrations, admin, and DRF
  ModelSerializer integration for no offsetting benefit.

## 2. API test framework: Django test framework vs. Jest/Vitest

**Decision**: Use Django's built-in test framework (`django.test.TestCase` for models,
`rest_framework.test.APITestCase` for API endpoints), run via `manage.py test`.

**Rationale**: `Cover.md` asks for "Jest или Vitest," but those are JavaScript test
runners with no ability to import or exercise Python/Django code — there is no JS
runtime component in this feature to test. Constitution Principle IV requires "Tested
API Surface," not a specific runner; Django's own test framework (plus DRF's
`APITestCase` for the REST endpoints) is the idiomatic, zero-extra-dependency choice
for testing a Django+DRF API, and integrates with `manage.py test` / CI without any
Node toolchain.

**Alternatives considered**:
- *pytest-django*: viable and slightly more ergonomic, but adds a dependency for a
  first feature with no other pytest usage yet; deferred unless a future feature's
  needs justify it.
- *Jest/Vitest against a hypothetical JSON API from Node*: rejected — there is no
  Node/JS backend surface in this project; these runners have nothing to invoke.

## 3. API layer: Django REST Framework vs. plain Django views

**Decision**: Use Django REST Framework (DRF) for the layout CRUD and compute-preview
endpoints.

**Rationale**: `Cover.md` and the ratified spec both refer to "API endpoints" that need
test coverage (Constitution Principle IV), and FR-008 requires the preview and label
count to recompute live as the user edits parameters — implying an AJAX/JSON call
pattern, not full-page reloads. DRF gives a conventional, well-tested way to define
that JSON contract (serializers double as the validation layer for FR-009) with minimal
boilerplate, and its `APITestCase` slots directly into the testing decision above.

**Alternatives considered**:
- *Plain Django views returning `JsonResponse`*: viable for a single endpoint, but
  would mean hand-rolling validation/error-shape conventions that DRF already
  standardizes, with no compensating simplicity gain once more than one endpoint exists.

## 4. Client/server folder separation

**Decision**: Two Django apps — `labels` (models, services, DRF serializers/viewsets:
the "server") and `layouts_ui` (templates, static JS/CSS, thin views: the "client") —
rather than a separate Node/SPA frontend package.

**Rationale**: `Cover.md` asks for "модулна структура от папки, разделяща клиента и
сървъра" (Constitution Principle V), but also specifies a Django-templates frontend —
there is no separate frontend runtime to split into its own service. Splitting at the
Django-app boundary achieves the same goal (server logic and presentation cannot
accidentally intermix, and each is independently testable) without inventing an SPA
that the brief never asked for.

**Alternatives considered**:
- *Single Django app for everything*: rejected — would blur the client/server boundary
  Principle V requires.
- *Separate Node/SPA frontend consuming a Django API*: rejected — over-scopes past
  "Django templates" as stated in the brief and the ratified constitution's Technology
  & Platform Constraints section.
