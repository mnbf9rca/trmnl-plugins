# AGENTS.md

Recipe plugins for TRMNL e-ink displays. One directory per plugin, each holding `settings.yml`, `shared.liquid`, and the four layout templates (`full`, `half_horizontal`, `half_vertical`, `quadrant`).

## How to work in this repo

- The main session orchestrates. Delegate research, file writing, and checks to subagents, and relay their results. Do work inline only for one-line edits.
- Build the smallest thing that works. No abstractions, scaffolding, or configuration for needs that do not exist yet.
- Follow the writing-clearly rules for any prose (README, specs, help text).
- Commit only when asked. Match the existing line endings of a file you edit (`README.md` uses CRLF).
- Design specs live in `docs/superpowers/specs/`. Read the relevant spec before changing a plugin.
- `TRMNL_FRAMEWORK_CHEAT_SHEET.md` lists every framework CSS class. Use it instead of guessing class names.

## Secrets

- Secrets live in 1Password, never in the repo or the shell environment. `.env.tpl` maps environment variable names to `op://` references and holds no values. `.envrc` loads only a service-account token. Both files are safe to commit.
- To run anything that needs a secret, wrap it: `op run --env-file=.env.tpl -- sh -c '...'` and read the variable inside that child process. Check `.env.tpl` for the variable names. Never `op read` a secret into the main shell, write it to a file, or print it.
- To add a new secret, add one line to `.env.tpl`. Do not document individual keys here.

## TRMNL facts that matter here

- Polling headers use `key=value` pairs separated by `&`, and can interpolate custom fields, for example `x-apikey={{ api_key }}`.
- Shared markup is prepended to every layout. Define reusable markup with `{% template name %}...{% endtemplate %}` and use it with `{% render "name", arg: value %}`. `render` has an isolated scope, so pass every variable explicitly.
- A JSON object response is exposed at the top level; a JSON array is wrapped as `data` (per TRMNL's `trmnlp` poller source). A non-200 JSON response is passed through to the template like any other (confirmed September 3, 2026: a 401 body rendered as "Invalid ApiKey" on screen). Do not trust the `trmnlp` dev tool on this; it discards them.
- Custom field types include `string`, `password`, `number`, `select`, `boolean`, and `author_bio`.

## National Rail Departures plugin

- Data source: Rail Data Marketplace product **Live Departure Board**, product code `P-d81d6eaf-8060-4467-a339-1c833e50cbbe` (version 1.1 of the series `P-9a01dd96-7211-4912-bcbb-c1b5d2e35609`). It is a JSON REST wrapper over the National Rail Darwin LDBWS `GetDepartureBoard` operation, authenticated with an `x-apikey` header.
- Verified against the live API on September 3, 2026: URL, header, and every field name the templates use match. Confirmed rendering inside TRMNL on September 3, 2026, including the Liquid `{% if %}` in `polling_url`. See the checklist in `docs/superpowers/specs/2026-09-03-national-rail-departures-design.md`.
- Local render check: `python3 national_rail_departures/check.py` (requires the `python-liquid` package). It renders the templates against a sample payload and must print `ok`.

## Decisions the TRMNL automated reviewer keeps questioning

Do not revisit these without new evidence from a device or the simulator:

- The `.board` style block in `shared.liquid` stays. The row limiter measures the table's parent height, so the wrapper must be flex-sized with `min-height: 0`; the framework's `stretch-y` class alone does not do that.
- No transform script. The Liquid `default` and `size` filters handle empty and error payloads, and `check.py` proves it.
- No `data-clamp` on title spans. It truncated "New Southgate via Finsbury Park" on the TRMNL X even with space to spare.
- No "National Rail" instance label on half vertical or quadrant. It collided with the title at 390 pixels wide.
- `image-dither` on the icon is harmless on a black silhouette; leave it.

