# Master Codex Prompt — SE3002 Assignment 01 ColorKast System

You are the primary software engineer for a university Software Quality Engineering assignment. Your job is to build the **complete runnable baseline application** that will later be evaluated with SonarQube, manual/system testing, Jira defect reporting, and a written quality judgment.

Do **not** stop at scaffolding, pseudocode, mockups, or partially implemented routes. Produce a complete, locally runnable system with real persistence, validation, authentication/authorization, observable success/error feedback, seed data, setup instructions, and enough structure to make later testing straightforward.

The selected SRS is the **ABC Paint / ColorKast Software Requirements Specification, Version 1.0**. The assignment requires a selected scope of exactly **7 functional requirements (FRs) and 3 non-functional requirements (NFRs)**. Build the system below around that scope.

---

## 1. Primary Goal

Build a small but complete **web-based ColorKast application** for ABC Paint that supports:

1. Graphical Color Chooser
2. Old-to-new Paint Number Translator
3. Closest Colors
4. Color Search Engine
5. User Color Palette
6. Administrative Paint Management
7. Administrative Users and Permission Levels

The system must also support evaluation of these three NFRs:

1. Search performance
2. Security / administrative access control
3. Usability / consistent task-based interface and keyboard-oriented interaction

The application should be deliberately **simple, testable, understandable, and easy to demonstrate**. Do not overengineer it.

---

# 2. Technology Stack

Use this stack unless there is a strong technical reason not to:

- **Python 3.12+**
- **Flask**
- **Flask-SQLAlchemy**
- **SQLite**
- **Jinja2 templates**
- **Flask-Login** or an equivalent small authentication mechanism
- **Flask-WTF / CSRF protection** for state-changing forms
- Plain CSS and vanilla JavaScript
- `pytest` for developer smoke tests

Do not use React, Vue, Angular, Node, a separate SPA frontend, Docker, Redis, external APIs, cloud databases, or unnecessary infrastructure.

The project must run completely on a normal local machine with no external internet dependency after Python packages have been installed.

Prefer server-rendered pages. Keep the dependency list small.

---

# 3. Important Scope Rules

Implement only what is needed for the selected assignment scope plus small supporting features needed to make it coherent.

## Explicitly out of scope

Do **not** implement the SRS Color Sample Matcher / image-upload color extraction module. The original SRS marks this module as low priority and not required.

Also do not spend time reproducing obsolete browser support such as Internet Explorer 4.01. This assignment is evaluating the selected requirements, not recreating the entire 2004 deployment environment.

Do not add unnecessary features such as:

- shopping cart
- paint purchasing
- payment
- customer registration
- social login
- cloud deployment
- machine learning
- computer vision
- email
- external APIs

---

# 4. Functional Requirement Scope

Use the following source section references in code comments/documentation. Do not pretend the SRS has requirement IDs that it does not actually define.

## FR-1 — Graphical Color Chooser
**Source: SRS Section 4.1 and related UI constraints in Sections 2.5 and 3.1**

Provide a graphical color selection page.

Required behavior:

- Use an HTML graphical color input such as `<input type="color">`.
- Display the selected color visually.
- Display its RGB values.
- Display its HEX value.
- Also provide keyboard-editable RGB numeric inputs so the feature is usable without relying exclusively on a pointing device.
- RGB values must be validated as integers from **0 through 255 inclusive**.
- The user must receive clear validation feedback for invalid values.
- Allow the currently selected color to be added to the user's palette.
- If the selected color does not correspond to a named paint, the palette may store it as a custom color snapshot.

Keep this page simple and highly observable for later manual testing.

---

## FR-2 — Color Translator
**Source: SRS Section 4.2**

The translator converts an old-scheme paint to a new-scheme paint.

The SRS describes the input as:

- old paint number
- collection
- target collection

Required behavior:

- User enters/selects:
  - old paint number
  - source collection
  - target collection
- System finds the source old-scheme paint.
- System finds the translation mapping to a new-scheme paint in the requested target collection.
- Display:
  - source paint name
  - old paint number
  - source collection
  - source RGB / visual swatch
  - translated paint name
  - new paint number
  - target collection
  - translated RGB / visual swatch
- Unknown source paint must show a clear error.
- Valid source paint with no mapping for the selected target collection must show a distinct "no translation available" result.
- Do not silently substitute another collection.

This feature must use real database records, not hardcoded if/else statements.

---

## FR-3 — Closest Colors
**Source: SRS Section 4.3 and assumption in Section 2.7**

The original SRS explicitly assumes that nearest colors in RGB color space are acceptably similar.

Required behavior:

- Input:
  - a valid paint number
  - its collection
  - a target collection
  - requested number of results `N`
- Locate the source paint.
- Compare the source RGB value against paints in the target collection.
- Rank target paints using standard Euclidean RGB distance:

`distance = sqrt((R1-R2)^2 + (G1-G2)^2 + (B1-B2)^2)`

- Return the nearest `N` colors in ascending distance order.
- Show:
  - rank
  - paint name
  - paint number
  - collection
  - RGB
  - HEX
  - color swatch
  - numeric distance
- `N` must be a positive integer.
- If `N` is greater than the available number of target paints, return all available target paints rather than failing.
- Unknown source paint must produce a clear error.
- Empty target collection must be handled gracefully.

Do not use machine learning or advanced color-science libraries. The SRS basis is RGB-space proximity.

---

## FR-4 — Color Search Engine
**Source: SRS Section 4.4**

Search must support locating colors in one collection or across all collections using:

- paint name
- paint number
- color value

Required behavior:

### Search modes
Support these user-visible search options:

1. Paint name
2. Paint number
3. RGB value
4. HEX color value

The SRS says "industry standard common format" but does not define the exact format. Supporting RGB triplets and HEX is an explicit design decision.

### Collection filtering
- Search all collections, or
- search one selected collection.

### Name search
- Case-insensitive.
- Partial matching is acceptable and should be documented as a design decision.

### Paint number search
- Prefer exact match.
- If there are duplicate numbers across collections, show all matches unless a collection filter resolves them.

### RGB search
Accept:
- three separate numeric fields, or
- a string form such as `255,128,0`

Validate each component in 0..255.

### HEX search
Accept a standard 6-digit form such as:
- `#FF8000`
- `FF8000`

### Results
Each result must show:
- name
- paint number
- scheme
- collection
- company
- RGB
- HEX
- color swatch
- action to add the color to the user's palette

### No-result behavior
Show a clear user-facing "No matching paints found" message.

### Performance instrumentation
Measure **server-side processing time only**, using `time.perf_counter()` or equivalent, and display it with the results in milliseconds.

Also add an HTTP response header such as:

`X-Processing-Time-ms`

for search-related requests if practical.

Do not include network transit time in the measurement.

---

## FR-5 — User Color Palette
**Source: SRS Section 4.5**

The palette stores recent user color activity for a single client/session.

Required behavior:

- No customer account/login is required.
- Associate palette data with a persistent browser session identifier.
- User can add a paint from:
  - search results
  - color chooser
  - closest-colors result
  - translator result
- Palette page shows recent saved colors.
- For a saved database paint show:
  - paint name
  - number
  - collection
  - RGB / HEX
  - swatch
- For a custom chooser color show:
  - label such as "Custom Color"
  - RGB
  - HEX
  - swatch
- User can remove an individual palette item.
- User can clear the palette.
- Duplicate additions may either:
  - create another recent entry, or
  - refresh/move the existing entry to most recent.
  Choose one behavior and document it in the assumptions file.
- Palette data must expire after **30 days**, as specified by the SRS.
- Implement expiry using timestamps and remove stale records automatically when the palette is accessed, or with a small cleanup function called during relevant requests.

The original SRS mentions storing uploaded images only if the optional Color Sample Matcher is loaded. Since that feature is out of scope, do not implement uploaded-image storage.

The palette is private to the browser/session, but not a secure customer account.

---

## FR-6 — Administrative Paint Management
**Source: SRS Section 4.6**

Provide an authenticated administrative interface for paint information.

Required operations:

- Add paint
- View/list paints
- Update paint
- Delete paint

Each paint should contain at least:

- unique database ID
- paint name
- paint number
- scheme (`old` or `new`)
- collection
- company
- red
- green
- blue
- created timestamp
- updated timestamp

Validation requirements:

- name required
- number required
- collection required
- company required
- scheme must be `old` or `new`
- RGB components must each be 0..255
- invalid submissions must show field-level or clear form-level errors
- state-changing operations require CSRF protection
- authorization must be checked server-side, not only by hiding buttons

Deletion must handle dependent translation records safely. Use a consistent policy and document it. A reasonable design is to prevent deletion while a paint is referenced by a translation and show a clear explanation, unless you implement safe cascading deliberately.

---

## FR-7 — Administrative Users and Permission Levels
**Sources: SRS Sections 2.3, 4.6, and 5.5**

Implement three administrative levels exactly according to the SRS:

### Level 1
- Can add paint information.
- Cannot update existing paint information.
- Cannot delete paint information.
- Can create administrative users at **Level 1 only**.

### Level 2
- Can add paint information.
- Can update paint information.
- Cannot delete paint information.
- Can create administrative users at Level 1 or Level 2.
- Cannot create Level 3 users.

### Level 3
- Full add/update/delete paint permissions.
- Can create administrative users at Level 1, Level 2, or Level 3.

### General rules
- Default/non-admin users have no administrative functionality.
- No admin may create another admin above their own level.
- All admin routes must enforce permissions server-side.
- Unauthorized actions must return either:
  - a clear access-denied page/message, or
  - HTTP 403 with a user-friendly page.
- Do not merely hide forbidden buttons.
- Admin passwords must never be stored in plaintext.
- Use a modern password hash supported by Werkzeug or another standard library.
- Add logout functionality.
- Protect login session cookies reasonably for a local assignment application:
  - `HttpOnly`
  - `SameSite=Lax`
  - secret key loaded from environment
- Do not hardcode real passwords or secret keys in source code.

Create a small admin-management screen where authorized admins can create new admin users according to these level rules.

---

# 5. Non-Functional Requirement Scope

The application must be built so these NFRs can later be evaluated independently.

## NFR-1 — Performance
**Source: SRS Section 5.1**

The SRS states that color searches should be processed in **sub-second time on the server**.

Implementation support:

- Instrument:
  - color search
  - translator lookup
  - closest-colors computation
- Measure only server-side processing time.
- Display processing time in the UI for these operations.
- Make the system efficient enough that the included demo dataset easily runs below one second on normal hardware.
- Do not fake timings.
- Do not hardcode displayed timing values.

Create a small optional utility script such as:

`tools/performance_check.py`

that can issue repeated local requests or call service functions and print actual timings.

Do not claim that the NFR passed; merely make it measurable. The assignment evaluation will be performed later.

---

## NFR-2 — Security
**Source: SRS Section 5.3 and administrative rules**

The SRS requires privacy for user palette data and secure access permissions for administrative functions.

Implement at least:

- hashed admin passwords
- authentication
- server-side RBAC
- CSRF protection
- SQLAlchemy parameterized/database-safe access
- server-side validation
- no plaintext secrets in repository
- environment-based secret key
- session cookie protections
- clear 403 handling
- no privilege escalation through request manipulation
- no direct URL bypass of permission rules

Add comments only where useful. Do not add performative "security theater."

The assignment later uses SonarQube, so keep the code clean and avoid obvious security smells.

---

## NFR-3 — Usability / Consistent Interface
**Source: SRS Sections 3.1 and 2.5**

The SRS calls for:

- task-based screens
- similar navigation across screens
- consistent input confirmation and error notification
- keyboard-oriented use wherever possible
- accelerator keys

Implement:

- one shared base template
- consistent top or side navigation
- consistent page titles
- consistent alert styles for success, warning, error, and info messages
- semantic labels for all form controls
- keyboard focus visibility
- sensible tab order
- `accesskey` shortcuts on main navigation items where practical
- a small visible "Keyboard shortcuts" help section or modal
- keyboard-editable alternatives for color values
- no color-only status indicators; use text as well
- reasonable contrast
- responsive layout sufficient for laptop/desktop use

Do not spend excessive time on visual polish. Correct and observable behavior is more important.

---

# 6. Database Design

Use a relational structure approximately like this.

## Collection

Fields:
- `id`
- `name`
- `company`

Constraints:
- collection name should be unique within a company if practical

## Paint

Fields:
- `id`
- `name`
- `paint_number`
- `scheme` (`old` or `new`)
- `collection_id`
- `red`
- `green`
- `blue`
- `created_at`
- `updated_at`

Useful constraints/indexes:
- index on name
- index on paint number
- index on collection
- RGB validation at application level
- a sensible uniqueness rule such as `(paint_number, collection_id, scheme)`

## Translation

Fields:
- `id`
- `old_paint_id`
- `new_paint_id`

Rules:
- old side must reference an `old` paint
- new side must reference a `new` paint
- prevent duplicate identical mappings

## AdminUser

Fields:
- `id`
- `username`
- `password_hash`
- `level` (`1`, `2`, or `3`)
- `created_at`
- optionally `created_by`

Rules:
- username unique
- passwords hashed only

## PaletteItem

Fields:
- `id`
- `session_id`
- optional `paint_id`
- optional custom label
- stored `red`
- stored `green`
- stored `blue`
- `added_at`

Store an RGB snapshot even for a database paint so the item remains displayable if the underlying paint later changes. If this is implemented, record it as a design decision.

---

# 7. Seed Data

Create realistic but fictional demo data.

Target:

- **3 to 4 collections**
- **30 to 50 paint records total**
- mixture of old-scheme and new-scheme paints
- enough translation mappings to demonstrate:
  - successful translation
  - missing translation
  - target-collection differences
- enough different RGB values to make closest-color ranking meaningful

Do not use copyrighted proprietary paint databases or scrape external data.

Use clearly fictional names such as:

- Harbor Blue
- Desert Sand
- Pine Grove
- Sunset Clay
- Silver Mist
- Deep Plum

Create deterministic seed data so the same demo values exist each time.

Do not hardcode admin passwords in source code.

Provide a seeding command that reads admin passwords from environment variables, for example:

- `ADMIN_L1_PASSWORD`
- `ADMIN_L2_PASSWORD`
- `ADMIN_L3_PASSWORD`

Seed usernames may be:

- `level1admin`
- `level2admin`
- `level3admin`

If any required password environment variable is missing, fail with a clear message rather than silently using an insecure default.

---

# 8. Suggested Routes / Screens

The exact route naming may differ, but the application should expose something close to:

## Public

- `/` — Home/dashboard of available tasks
- `/chooser` — Graphical Color Chooser
- `/translate` — Old-to-new translator
- `/closest` — Closest colors
- `/search` — Search engine
- `/palette` — Session palette
- `/palette/add` — POST
- `/palette/remove/<id>` — POST
- `/palette/clear` — POST

## Authentication

- `/admin/login`
- `/admin/logout`

## Paint administration

- `/admin`
- `/admin/paints`
- `/admin/paints/new`
- `/admin/paints/<id>/edit`
- `/admin/paints/<id>/delete`

## Admin user management

- `/admin/users`
- `/admin/users/new`

## Optional translation management

Only add this if needed to make the application coherent and manageable:

- `/admin/translations`
- `/admin/translations/new`
- `/admin/translations/<id>/delete`

If implemented, restrict it sensibly, preferably to Level 3.

---

# 9. Architecture / Code Organization

Use a clean structure such as:

```text
colorcast/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   ├── auth/
│   │   ├── routes.py
│   │   └── permissions.py
│   ├── public/
│   │   ├── routes.py
│   │   └── services.py
│   ├── admin/
│   │   └── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── chooser.html
│   │   ├── search.html
│   │   ├── translate.html
│   │   ├── closest.html
│   │   ├── palette.html
│   │   ├── errors/
│   │   └── admin/
│   └── static/
│       ├── css/
│       └── js/
├── tools/
│   └── performance_check.py
├── tests/
│   └── ...
├── seed.py
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ASSUMPTIONS.md
├── AI_DEVELOPMENT_RECORD.md
└── SCOPE_MAPPING.md
```

Do not create dozens of tiny files with no benefit. Keep the code understandable for a student viva.

Use blueprints if helpful, but simplicity is more important than architectural ceremony.

---

# 10. Required Documentation Files

Generate these files as part of the project.

## `README.md`

Must include:

- project title
- purpose
- chosen technology stack
- prerequisites
- virtual environment creation
- dependency installation
- environment configuration
- database creation
- seed command
- how to start the application
- local URL
- how to log in as each admin level
- how the admin passwords are supplied
- quick feature tour
- how to run developer smoke tests
- how to run the performance helper
- note that manual assignment evaluation is performed separately
- note that Color Sample Matcher is out of scope

Make the instructions copy-paste friendly.

---

## `SCOPE_MAPPING.md`

Create a concise implementation map:

| Internal Label | SRS Source | Implemented Feature |
|---|---|---|
| FR-1 | Section 4.1 | Graphical Color Chooser |
| FR-2 | Section 4.2 | Color Translator |
| FR-3 | Section 4.3 | Closest Colors |
| FR-4 | Section 4.4 | Color Search Engine |
| FR-5 | Section 4.5 | User Color Palette |
| FR-6 | Section 4.6 | Administrative Paint Management |
| FR-7 | Sections 2.3, 4.6, and 5.5 | Admin Users / Levels |
| NFR-1 | Section 5.1 | Performance |
| NFR-2 | Section 5.3 | Security |
| NFR-3 | Sections 3.1 and 2.5 | Usability / Keyboard-oriented UI |

Do not claim these are original SRS requirement IDs. They are internal assignment labels mapped to actual SRS sections.

---

## `ASSUMPTIONS.md`

Record all material implementation choices not fully specified by the SRS.

At minimum document decisions such as:

- SQLite selected as local implementation database.
- RGB triplets and HEX selected as supported "common" color formats.
- Name search is case-insensitive and partial.
- Behavior for duplicate palette additions.
- Session identifier mechanism.
- 30-day palette expiry implementation.
- Policy for deleting paints referenced by translations.
- Exact meaning of server processing timing.
- Modern browser used for the university implementation instead of reproducing obsolete 2004 browser compatibility.
- Color Sample Matcher is intentionally out of selected scope.
- Any limit or behavior you introduce that is not explicit in the SRS.

For every assumption, label its basis as one of:

- **Supported by SRS**
- **Explicit design decision**
- **Unsupported / unresolved**

Avoid unsupported assumptions wherever possible. Never hide one.

---

## `AI_DEVELOPMENT_RECORD.md`

Create a brief factual log suitable for later assignment documentation.

Include:

- that the application was AI-assisted
- main technology choices
- major implementation assumptions
- major generated components
- any areas that required human review
- reminder that the generated system must be manually verified before quality conclusions are made

Do not invent claims about tests, SonarQube, or Jira that have not actually been performed.

---

# 11. Error Handling

Add user-friendly handlers for:

- 400
- 403
- 404
- 500

Requirements:

- user sees a clear message
- internal exception details are not exposed in production-style UI
- application logs useful server-side error information
- forms preserve useful input where practical
- database failures should be rolled back safely

Do not swallow exceptions silently.

---

# 12. Validation Rules

Centralize validation where practical.

At minimum:

### RGB
- integer only
- minimum 0
- maximum 255
- exact boundaries 0 and 255 must be valid

### Admin level
- exactly 1, 2, or 3

### Closest-color result count
- positive integer
- zero invalid
- negative invalid
- larger than available dataset should return all available results

### Paint data
- required fields cannot be blank
- scheme only `old` / `new`

### HEX
- 6 hexadecimal digits
- optional leading `#`
- invalid length or characters rejected

### Login
- generic invalid-credentials message
- do not reveal whether username or password specifically was wrong

---

# 13. Permission Enforcement

Create a reusable permission mechanism rather than duplicating level checks everywhere.

For example:

- `@admin_required`
- `@minimum_admin_level(2)`
- `@level3_required`

However, remember that Level 1/2/3 capabilities are **not simply one monotonic permission if actions differ**. Implement capability checks clearly.

Recommended permission model:

```text
add_paint:
  level 1, 2, 3

update_paint:
  level 2, 3

delete_paint:
  level 3

create_admin_level_1:
  level 1, 2, 3

create_admin_level_2:
  level 2, 3

create_admin_level_3:
  level 3
```

The server must reject manually crafted unauthorized POST requests.

The GUI should also hide or disable unavailable actions for usability, but this is not a substitute for backend enforcement.

---

# 14. Search / Color Utility Functions

Create reusable pure functions for:

- RGB validation
- HEX → RGB
- RGB → HEX
- Euclidean RGB distance
- closest-color ranking
- server timing formatting

Keep these functions easy to unit test and easy to explain in a viva.

---

# 15. Developer Smoke Tests

Add a small `pytest` suite to validate the implementation while developing.

These are **not** a replacement for the later assignment's 12–15 manually documented test cases.

Include useful smoke/unit tests such as:

- RGB 0 accepted
- RGB 255 accepted
- RGB -1 rejected
- RGB 256 rejected
- valid HEX conversion
- invalid HEX rejected
- RGB distance calculation
- search route returns results
- unknown search returns no-result message
- unauthenticated user cannot access admin route
- Level 1 cannot update/delete
- Level 2 can update but not delete
- Level 3 can delete
- lower-level admin cannot create a higher-level admin
- palette items are session-scoped

Do not intentionally create failing automated tests merely because the assignment later requires genuine FAILED/BLOCKED manual test outcomes.

---

# 16. SonarQube Friendliness

The application will later be scanned using SonarQube.

Write reasonably clean code:

- avoid duplicated business logic
- avoid giant functions
- avoid dead code
- avoid hardcoded secrets
- avoid broad `except Exception` unless logging/rethrowing is justified
- avoid SQL string concatenation
- avoid command execution
- avoid insecure deserialization
- do not disable CSRF
- do not store passwords in plaintext
- avoid unused imports
- use descriptive names
- keep complexity reasonable
- write comments for rationale, not obvious syntax

Do not attempt to "game" SonarQube or suppress issues globally.

---

# 17. Baseline / Assignment Integrity

This is very important.

The assignment requires the first complete runnable implementation to be frozen and later evaluated.

Your job is to create the application and development artifacts only.

Do **not**:

- fabricate SonarQube screenshots
- fabricate SonarQube findings
- fabricate Jira issues
- fabricate test execution evidence
- fabricate failed tests
- intentionally introduce bugs just so tests can fail
- claim NFRs passed before measurement
- generate fake manual-test screenshots
- claim the baseline was frozen before the user actually verifies it

Instead, create a system that can be genuinely evaluated later.

When implementation is complete, include a section in `README.md` titled:

`## Recommended Baseline Freeze Procedure`

with simple steps such as:

1. Manually run every major feature once.
2. Ensure the project starts from a clean environment.
3. Commit all application files.
4. Create a Git tag such as `baseline-v1`.
5. Do not modify that tagged version while collecting SonarQube and test evidence.
6. If defects are fixed later, preserve the baseline separately.

Do not automatically tag unless the repository is already under Git and the user explicitly wants that action.

---

# 18. UI Expectations

Use a clean student-project appearance.

Suggested home page cards:

- Choose a Color
- Search Paints
- Translate Old Paint
- Find Closest Colors
- My Palette
- Admin Login

Each feature page should have:

- heading
- short explanation
- input form
- clear submit button
- clear result/error panel
- link back to relevant task
- shared navigation

For paint results, render a small swatch using CSS background color.

Example:

```html
<div
  class="color-swatch"
  style="background-color: rgb(12, 140, 220)"
  aria-label="RGB 12 140 220">
</div>
```

Ensure text is always present beside visual color samples.

---

# 19. Performance Measurement Details

Because the SRS explicitly distinguishes server processing time from network transit time:

- start timer immediately before server-side operation
- stop timer immediately after query/computation is complete
- do not include template rendering if you can reasonably isolate the operation
- label the displayed result clearly, e.g.:

`Server processing time: 13.42 ms`

For search:
- database lookup timing

For translator:
- source/mapping lookup timing

For closest colors:
- source lookup + target retrieval + distance computation + sorting timing

Do not display fake zero values.

---

# 20. Session Palette Details

Use a generated UUID stored in the Flask session to identify the browser's palette.

Example concept:

- if no `palette_session_id` exists, create one with `uuid4()`
- save it in Flask session
- PaletteItem rows use this ID
- all palette queries filter by this ID
- cleanup removes items older than 30 days for that session, or globally via helper

Do not expose palette records from another session by changing URL parameters.

Removal actions should verify ownership by session ID.

---

# 21. Authentication Setup

Use an application secret from an environment variable:

`SECRET_KEY`

The application should fail clearly or generate a warning in development if no secure secret is supplied. Prefer failing with a clear setup message.

For demo admin seeding, use environment variables rather than source-code passwords.

Document example setup commands for:

### Windows PowerShell
and
### Linux/macOS shell

Keep them simple.

---

# 22. Deliverables You Must Produce

Do not stop until the repository contains at least:

1. Complete Flask application
2. Database models
3. All seven FRs implemented
4. Support for evaluating all three NFRs
5. Seed data
6. Admin authentication
7. Level 1/2/3 permissions
8. Session palette with 30-day expiry
9. Search/translator/closest-color timing
10. Consistent GUI
11. Validation and error feedback
12. `requirements.txt`
13. `.env.example`
14. `.gitignore`
15. `README.md`
16. `SCOPE_MAPPING.md`
17. `ASSUMPTIONS.md`
18. `AI_DEVELOPMENT_RECORD.md`
19. Small developer `pytest` suite
20. Performance helper script

---

# 23. Final Verification Checklist

Before declaring the project complete, actually run and verify the application.

Perform these checks yourself in the coding environment where possible:

### Installation
- dependencies install
- database initializes
- seed script works
- server starts without traceback

### Public features
- home loads
- chooser works
- RGB boundaries 0 and 255 work
- invalid RGB is rejected
- search by name works
- search by number works
- search by RGB works
- search by HEX works
- collection filter works
- translator successful case works
- translator missing case works
- closest-color ranking works
- palette add/remove/clear works

### Authentication / permissions
- unauthenticated user blocked from admin
- Level 1 can add paint
- Level 1 cannot update
- Level 1 cannot delete
- Level 1 cannot create Level 2/3 admin
- Level 2 can add/update
- Level 2 cannot delete
- Level 2 cannot create Level 3 admin
- Level 3 can add/update/delete
- Level 3 can create all levels

### Documentation
- README commands are correct
- assumptions match actual implementation
- scope mapping matches actual features
- no fake quality-evaluation evidence is included

### Code quality
- tests run
- no obvious hardcoded secrets
- no debug-only bypasses
- no placeholder `TODO` for required functionality
- no route returns fake/sample results instead of database-driven results

If anything fails, fix it before concluding.

---

# 24. Working Style

Follow these instructions while coding:

- Work autonomously.
- Inspect the existing repository before creating files.
- Reuse good existing files if present.
- Do not overwrite unrelated user work.
- Prefer the smallest correct implementation.
- Do not ask questions unless a genuinely blocking ambiguity prevents progress.
- When the SRS is ambiguous, choose a reasonable implementation and record it in `ASSUMPTIONS.md`.
- Do not silently expand scope.
- Keep the application easy for two students to understand and defend in a viva.
- Avoid clever abstractions that make the code harder to explain.
- Use readable naming and straightforward control flow.
- Run the application and tests instead of assuming generated code works.
- Fix runtime errors you encounter.
- Finish the whole system, not just the first feature.

---

# 25. Completion Response

When you are fully done, give me a concise completion report containing:

1. What was implemented
2. Project structure
3. Exact setup/run commands
4. Seed command and required environment variables
5. Demo usernames for Levels 1, 2, and 3
6. Which SRS sections map to the 7 FRs and 3 NFRs
7. Any assumptions/design decisions recorded
8. Test command and result
9. Any remaining limitations
10. Clear statement that no SonarQube/Jira/manual-test evidence was fabricated

Do not give me a plan and stop. Carry out the implementation first, verify it, then report completion.
