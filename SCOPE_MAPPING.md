# Selected scope mapping

The implementation was initially generated from the assignment-specific development specification. The completed implementation was subsequently reviewed against the supplied ABC Paint / ColorKast SRS v1.0.

| Internal Label | SRS Source | Implemented Feature | Implementation / evaluation entry point |
|---|---|---|---|
| FR-1 | Section 4.1; UI Sections 2.5 and 3.1 | Graphical Color Chooser | `/chooser`; native color input, numeric RGB validation, preview, custom snapshot save |
| FR-2 | Section 4.2 | Color Translator | `/translate`; old source + source/target collection; relational mappings; distinct unknown/unmapped results |
| FR-3 | Section 4.3; assumption Section 2.7 | Closest Colors | `/closest`; Euclidean RGB ranking; result count, tie order, empty/unknown handling |
| FR-4 | Section 4.4 | Color Search Engine | `/search`; name, number, RGB, HEX; all/one collection; swatches and palette actions |
| FR-5 | Section 4.5 | User Color Palette | `/palette` and POST add/remove/clear; session UUID, persisted snapshots, automatic 30-day expiry |
| FR-6 | Section 4.6 | Administrative Paint Management | `/admin/paints`; add/list/update/delete; validation, safe dependent-record policy |
| FR-7 | Sections 2.3, 4.6, and 5.5 | Admin Users / Levels | `app/auth/permissions.py`, `/admin/users`; exact Level 1/2/3 capabilities; no elevation |
| NFR-1 | Section 5.1 | Performance | Real UI/header operation timings for search, translator, closest; `tools/performance_check.py` |
| NFR-2 | Section 5.3 and admin rules | Security | Scrypt, Flask-Login, server capabilities, CSRF, ORM, validation, private palette queries, environment configuration, cookie flags, friendly 403 |
| NFR-3 | Section 2.5 | Keyboard usability | Keyboard-accessible forms/navigation, visible focus, access keys/help, numeric chooser alternative; structured manual evaluation |

Supporting home navigation, logout, errors, setup commands, and seed data do not add additional selected requirements. There is no Color Sample Matcher. The table describes implementation and measurement support, not a finding that any NFR has passed.
