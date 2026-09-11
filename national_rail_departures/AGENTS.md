# National Rail Departures plugin

Read the root `AGENTS.md` first for repo-wide rules, secrets and TRMNL platform facts.

- Data source: Rail Data Marketplace product **Live Departure Board**, product code `P-d81d6eaf-8060-4467-a339-1c833e50cbbe` (version 1.1 of the series `P-9a01dd96-7211-4912-bcbb-c1b5d2e35609`). It is a JSON REST wrapper over the National Rail Darwin LDBWS `GetDepartureBoard` operation, authenticated with an `x-apikey` header.
- Verified against the live API on September 3, 2026: URL, header, and every field name the templates use match. Confirmed rendering inside TRMNL on September 3, 2026, including the Liquid `{% if %}` in `polling_url`. See the checklist in `docs/superpowers/specs/2026-09-03-national-rail-departures-design.md`.
- Local render check: `python3 national_rail_departures/check.py` (requires the `python-liquid` package). It renders the templates against a sample payload and must print `ok`.
- The title bar is nested inside `layout`, unlike Simple Tube Status, which places it as a sibling after `layout` so it renders as a footer.

## Decisions the TRMNL automated reviewer keeps questioning

Do not revisit these without new evidence from a device or the simulator:

- National Rail Departures uses its own `.board` style block; that is unrelated to Simple Tube Status, which has no custom style block.
- No `data-clamp` on title spans. It truncated "New Southgate via Finsbury Park" on the TRMNL X even with space to spare.
- No "National Rail" instance label on half vertical or quadrant. It collided with the title at 390 pixels wide.
- Expected times (`Exp HH:MM`) are plain text like `On time`. Only `Cancelled`, `Delayed` and `No report` get the inverted label, so delays and cancellations stand out at a glance (September 11, 2026).
