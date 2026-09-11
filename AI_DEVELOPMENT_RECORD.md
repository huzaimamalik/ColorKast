# AI-assisted development record

Date: 2026-09-11. The application was AI-assisted using the supplied `ColorKast_Codex_Master_Prompt.md`. The workspace initially contained only that prompt and was not a Git repository. No unrelated project files were overwritten.

## Generated components

- Flask application factory, SQLite models, explicit admin capabilities, login/logout, CSRF-protected forms, server validation, and friendly errors.
- Seven selected feature implementations with Jinja templates, local CSS/JavaScript, persistent browser palettes, and real processing timings.
- Forty fictional paints in four collections, twenty translation mappings, and three password-hashed demo administrators seeded from environment configuration.
- Developer tests, a performance measurement utility, setup documentation, assumptions, and SRS section mapping.

Technology choices: Python 3.12+, Flask, Flask-SQLAlchemy, SQLite, Flask-Login, Flask-WTF, Jinja2, vanilla JavaScript/CSS, python-dotenv, and pytest. Actual installed versions are in `requirements-lock.txt`. The development machine used Python 3.14.0 on Windows.

Material choices include literal partial name search, exact number/RGB/HEX search, deterministic RGB-distance tie breaking, UUID-scoped palette snapshots, duplicate palette entries, lazy 30-day expiry, restrictive translation-dependent deletion, and fixed seeded collections. See `ASSUMPTIONS.md` for the full classified list.

## Actual developer verification

Verification results are recorded after execution below. They are developer checks, not assignment manual-test evidence or a quality verdict.

- Virtual environment and dependencies installed. Sandbox restrictions on Python temporary directories required normal local execution permissions for installation and tests.
- Database initialized and deterministic seed command executed successfully in the local demo database.
- A local ignored `.env` was generated with random configuration and demo passwords; values were not embedded in source or printed in the development log.
- `python -m pytest -q --maxfail=3`: **89 passed in 36.65 seconds**. Coverage includes RGB/HEX boundaries and invalid values, all search modes, literal matching, filtering, real timing headers, successful/absent/unknown translations, RGB ranking and empty collections, palette isolation/expiry/snapshots, every admin-creation level combination, paint permissions/validation, CSRF rejection, login/logout, seed repeatability, secret-key validation, and logged friendly database errors. CSRF was never disabled.
- The local server started with debug off at `http://127.0.0.1:5000`; an actual HTTP home-page request returned **200**, with no startup traceback.
- `python tools/performance_check.py --runs 30` executed against the seeded demo database. Observed milliseconds are shown below; these are local development measurements, not NFR verdicts.

| Operation | Minimum ms | Mean ms | Median ms | Maximum ms |
|---|---:|---:|---:|---:|
| Search | 0.2531 | 0.3405 | 0.2649 | 1.8795 |
| Translator | 0.4793 | 0.6730 | 0.5614 | 2.5754 |
| Closest | 0.5041 | 0.6267 | 0.5701 | 1.4641 |

The browser automation tool reported no available browser (`[]`). Therefore no browser visual/keyboard review or browser screenshots were produced. Server-rendered routes and form behavior were exercised through the tests; the JavaScript picker synchronization and visual layout still require interactive browser verification. Early setup-only test errors caused by a missing temporary-directory parent were resolved by using a project-root pytest temporary path; the successful suite above ran after that correction.

## Human review still required

Verify all selected features and permission levels in the final student environment; assess keyboard behavior and task usability; review deployment/security assumptions; independently measure the selected NFRs; and execute/document the assignment's formal manual test cases. Developer automation is not a substitute for these activities.

No SonarQube scan, Jira defect reporting, or formal manual assignment test execution has been claimed. No screenshots, findings, failures, blocked outcomes, or quality-evaluation evidence have been fabricated. Codex did not create the baseline freeze, Git commit, or Git tag. Baseline freezing is performed separately by the students after verification.
