# ColorKast · ABC Paint

A complete local implementation for the SE3002 Software Quality Engineering assignment. It implements exactly seven selected functional requirements and supports evaluation of three selected non-functional requirements from the supplied ABC Paint / ColorKast SRS v1.0. The labels FR-1–7 and NFR-1–3 are internal assignment labels, not original SRS requirement IDs.

**Stack:** Python 3.12+, Flask, Flask-SQLAlchemy, SQLite, Jinja2, Flask-Login, Flask-WTF, plain CSS/JavaScript, and pytest. No Node, external APIs, cloud services, or network access is needed at runtime. Python packages require an initial installation. Development was verified on Windows with Python 3.14.

## Setup — Windows PowerShell

From the project directory (requires Python 3.12+):

```powershell
cd D:\ColorKast
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Copy the generated random value into `SECRET_KEY` in `.env`. Supply your own three different passwords of 12–128 characters as `ADMIN_L1_PASSWORD`, `ADMIN_L2_PASSWORD`, and `ADMIN_L3_PASSWORD`. Do not commit `.env`. `python-dotenv` loads it automatically; shell environment variables take precedence. Keep `SECRET_KEY` stable across restarts to preserve browser sessions.

If `.env` already exists, **keep it** and skip `Copy-Item`. This working directory was configured during development with random local credentials; open the existing `.env` to retrieve them. The file is excluded from version control.

Alternatively, set values for the current PowerShell session (prompts avoid storing passwords in command history):

```powershell
$env:SECRET_KEY = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
$env:ADMIN_L1_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'Level 1 password (12–128 characters)' -AsSecureString)).Password
$env:ADMIN_L2_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'Level 2 password (12–128 characters)' -AsSecureString)).Password
$env:ADMIN_L3_PASSWORD = [System.Net.NetworkCredential]::new('', (Read-Host 'Level 3 password (12–128 characters)' -AsSecureString)).Password
```

Create the database, seed the demo, and start the app:

```powershell
.\.venv\Scripts\python.exe -m flask --app run init-db
.\.venv\Scripts\python.exe -m flask --app run seed
.\.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:5000**. Stop a foreground server with Ctrl+C. No virtual-environment activation is necessary. If a development verification server is already running on that port, use it or stop that process before starting another.

## Setup — Linux/macOS shell

From the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))'
```

Skip `cp` if `.env` already exists. Edit `.env` with your text editor and set the same four values described above. Then:

```bash
.venv/bin/python -m flask --app run init-db
.venv/bin/python -m flask --app run seed
.venv/bin/python run.py
```

For a Bash environment-only setup instead of `.env`:

```bash
export SECRET_KEY="$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')"
read -r -s -p 'Level 1 password (12–128 characters): ' ADMIN_L1_PASSWORD
export ADMIN_L1_PASSWORD
read -r -s -p 'Level 2 password (12–128 characters): ' ADMIN_L2_PASSWORD
export ADMIN_L2_PASSWORD
read -r -s -p 'Level 3 password (12–128 characters): ' ADMIN_L3_PASSWORD
export ADMIN_L3_PASSWORD
```

The default database is `instance/colorkast.db`. `DATABASE_URL` can select another SQLite file, e.g. `sqlite:///separate-demo.db` (relative to `instance/`). `init-db` creates tables without deleting existing data. `seed` fails clearly when any required password is missing/invalid. Rerunning seed fills missing demo rows but does not overwrite existing paints or reset existing admin passwords. On a fresh database it creates 4 collections, 40 paints, 20 mappings, and 3 admins. Run seed against a fresh database for a deterministic pristine demo; do not reseed a baseline during evidence collection.

## Admin logins

Visit `/admin/login`. Passwords are the values supplied when each user was first seeded.

| Username | Level | Paint permissions | Can create admins |
|---|---|---|---|
| `level1admin` | 1 | Add / view | Level 1 |
| `level2admin` | 2 | Add / view / update | Levels 1–2 |
| `level3admin` | 3 | Add / view / update / delete | Levels 1–3 |

All administrative URLs enforce permissions on the server. Forbidden access returns a friendly 403. Login errors are generic. Passwords are stored only as Werkzeug scrypt hashes. Logout is a CSRF-protected POST. Cookies are `HttpOnly` and `SameSite=Lax`; `COOKIE_SECURE=true` is available for HTTPS, while the local HTTP setup needs `false`. Log out on a shared computer. The palette is tied to the browser session, not to the admin account.

## Quick feature tour

| Task | Route | Demo to try |
|---|---|---|
| Graphical chooser | `/chooser` | Pick a color or type RGB `0, 128, 255`; preview and save it. Numeric input works with JavaScript disabled too. |
| Search | `/search` | Name `harbor`; number `100` (four matches across collections); RGB `32,102,158`; HEX `#20669E`. Select one collection to filter. |
| Translator | `/translate` | `H001`, Heritage → Horizon gives `N001`; Heritage → Studio gives `S001`. `H006` → Studio has no mapping; `H009` has no mapping to either. `UNKNOWN` is a distinct source-not-found result. |
| Closest colors | `/closest` | `H001`, old scheme, Heritage → Horizon, 5 results. Try 100 to return all 10 target paints; zero is invalid. |
| Palette | `/palette` | Add from any result card or chooser, remove an item, or clear. Another browser/profile has a separate palette. Snapshots expire after 30 days. |
| Paint management | `/admin/paints` | Add at all levels, update at levels 2–3, delete at level 3. A linked paint such as `H001` cannot be deleted; unlinked `H009` can. |
| Admin management | `/admin/users` | Create users at or below your own level. Invalid elevated requests are also rejected server-side. |

The header is shared across pages; the footer explains keyboard access keys. All swatches have text RGB/HEX equivalents. Name matching uses literal case-insensitive substrings; number/RGB/HEX matching is exact. Company is stored on the selected collection and validated in the paint form.

## Developer verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/performance_check.py --runs 30
```

On Linux/macOS, substitute `.venv/bin/python` for the Windows interpreter path. Tests create isolated temporary SQLite databases and random test passwords. They do not change the demo database and keep CSRF protection enabled. The test temporary directory `.pytest-tmp` is disposable and managed by pytest.

The performance helper requires the seeded database and `SECRET_KEY` but no running server. It uses Flask's local client and reports the actual `X-Processing-Time-ms` values returned by the three tool routes. Measurements include the first operation, SQL lookup/materialization and, for closest colors, distance computation and sorting. They exclude validation, collection dropdown loading, template rendering, request setup, and network transit. Timing is shown in the UI only after a valid request actually executes an operation, including no-result lookups.

See [AI_DEVELOPMENT_RECORD.md](AI_DEVELOPMENT_RECORD.md) for actual development checks. These checks are **not** the assignment's 12–15 manually documented test cases and do not establish NFR pass/fail conclusions. SonarQube analysis, Jira defect reporting, manual evidence, and the final quality judgment must be performed separately.

## Project structure

```text
app/
  __init__.py          Application factory, configuration, CLI, errors
  extensions.py       SQLAlchemy, LoginManager, CSRFProtect
  models.py           Collections, paints, translations, admins, palettes
  forms.py            Shared form validation
  color_utils.py      Pure RGB/HEX/distance/timing functions
  public/             Public routes and database lookup/palette services
  auth/               Login/logout and capability enforcement
  admin/              Paint CRUD and admin creation
  templates/          Shared layout and task screens
  static/             Local CSS and vanilla JavaScript
tests/                Developer tests (CSRF remains enabled)
tools/performance_check.py
seed.py               Deterministic fictional demo data
run.py                Local server entry point
requirements.txt      Small set of direct dependency ranges
requirements-lock.txt Exact dependency versions used in development
.env.example          Configuration template without secrets
README.md
SCOPE_MAPPING.md
ASSUMPTIONS.md
AI_DEVELOPMENT_RECORD.md
```

For exact dependency reproduction on compatible Python versions, install `requirements-lock.txt` instead of `requirements.txt`. No migration framework is included: preserve existing baseline databases and use a separate fresh SQLite database if the schema is changed later.

## Scope and limitations

The Color Sample Matcher, image uploads, customer registration, purchasing, and deployment infrastructure are intentionally out of scope. Collection and translation maintenance are provided through the deterministic seed data, not additional admin screens. SQLite and full result lists target a small local demo dataset. Screen swatches and RGB proximity do not guarantee physical paint matches. Modern browser use is assumed; original 2004 browser compatibility is not reproduced. The implementation and selected section mappings were subsequently reviewed against the supplied ABC Paint / ColorKast SRS v1.0.

The local development server binds only to `127.0.0.1`, with debug disabled. Public deployment is outside this assignment baseline. See the official [Flask server documentation](https://flask.palletsprojects.com/en/stable/tutorial/deploy/) and [Flask-WTF CSRF documentation](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/) for the framework guidance used in setup and form protection.

## Recommended Baseline Freeze Procedure

1. Manually run every major feature once, including each admin level.
2. Ensure the project starts from a clean environment using these instructions.
3. Review the source, assumptions, and environment exclusions; commit all application files. Keep `.env`, SQLite databases, and generated caches out of the commit.
4. Create a Git tag such as `baseline-v1` after you verify the baseline.
5. Do not modify that tagged version while collecting SonarQube and test evidence. Preserve a separate local snapshot of the demo database and configuration needed for reproduction, without publishing credentials.
6. If defects are fixed later, preserve the baseline separately and make fixes on another branch/version.

No baseline tag has been created automatically. No SonarQube findings, Jira issues, or manual-test evidence have been fabricated.
