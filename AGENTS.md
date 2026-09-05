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

- Secrets live in 1Password, never in the repo or the shell environment. Each plugin folder has a `.env.tpl` that maps environment variable names to `op://` references and holds no values. It always includes that plugin's `TRMNL_MCP_API_KEY`, plus any data-source secrets the plugin needs. `.envrc` loads only a service-account token. All of these files are safe to commit.
- Start Claude with `op_claude <plugin_dir>`. It runs `op run --env-file=<plugin_dir>/.env.tpl -- claude`, so the TRMNL MCP server talks to that one plugin and the secrets exist only inside that process.
- To run anything else that needs a secret, wrap it the same way: `op run --env-file=<plugin_dir>/.env.tpl -- sh -c '...'` and read the variable inside that child process. Never `op read` a secret into the main shell, write it to a file, or print it.
- To add a new secret, add one line to the plugin's `.env.tpl`. Do not document individual keys here.

## TRMNL facts that matter here

- Polling headers use `key=value` pairs separated by `&`, and can interpolate custom fields, for example `x-apikey={{ api_key }}`.
- Shared markup is prepended to every layout. Define reusable markup with `{% template name %}...{% endtemplate %}` and use it with `{% render "name", arg: value %}`. `render` has an isolated scope, so pass every variable explicitly.
- A JSON object response is exposed at the top level; a JSON array is wrapped as `data` (per TRMNL's `trmnlp` poller source). A non-200 JSON response is passed through to the template like any other (confirmed September 3, 2026: a 401 body rendered as "Invalid ApiKey" on screen). Do not trust the `trmnlp` dev tool on this; it discards them.
- Custom field types include `string`, `password`, `number`, `select`, `boolean`, and `author_bio`.
- The framework source is at https://github.com/usetrmnl/trmnl-framework. Check it when `TRMNL_FRAMEWORK_CHEAT_SHEET.md` names a class or data attribute but not how it behaves, for example how `data-table-limit` measures its container or how `data-clamp` truncates.
- The TRMNL MCP server also carries documentation: `DesignSystemTemplateGuideTool` (sections such as `framework_engines_data_attributes`, `custom_fields_form_builder`, `view_adaptation_strategy`) and `DesignSystemReferenceTool` (example markup per size). Ask those before guessing at framework behaviour.

## National Rail Departures plugin

- Data source: Rail Data Marketplace product **Live Departure Board**, product code `P-d81d6eaf-8060-4467-a339-1c833e50cbbe` (version 1.1 of the series `P-9a01dd96-7211-4912-bcbb-c1b5d2e35609`). It is a JSON REST wrapper over the National Rail Darwin LDBWS `GetDepartureBoard` operation, authenticated with an `x-apikey` header.
- Verified against the live API on September 3, 2026: URL, header, and every field name the templates use match. Confirmed rendering inside TRMNL on September 3, 2026, including the Liquid `{% if %}` in `polling_url`. See the checklist in `docs/superpowers/specs/2026-09-03-national-rail-departures-design.md`.
- Local render check: `python3 national_rail_departures/check.py` (requires the `python-liquid` package). It renders the templates against a sample payload and must print `ok`.

## Simple Tube Status plugin

- Data source: TfL Unified API, `GET https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status`. Free, no key. The array response arrives as `data`; a 400 for an unknown mode arrives as a top-level object with `message`.
- `shared.liquid` sets `api_error` from the top-level `message` field, since that is where the 400 body normally arrives, and falls back to `data.message` to cover a body that TRMNL wraps under `data`.
- Severity rule: a `lineStatuses` entry is disrupted when `statusSeverity` is not 10, 18 or 20. Do not use "below 10"; it misses 11 to 17 and 19.
- Each disrupted line renders exactly one row (or, in compact mode, one chip), never one per disrupted status entry. `shared.liquid` picks that line's worst entry with its own worst-first ranking of severity codes: `1, 2, 16, 3, 4, 5, 11, 6, 8, 7, 15, 14, 9, 12, 13, 17, 0, 19` (`severity_rank`, defined once at the top of the `board` template). A status code missing from that list ranks after every listed code (fallback rank 99); among entries with an unranked code, or on a tie, the first as TfL lists them wins.
- Below a layout's `max_with_reason` cap, each disrupted line's row sits in a two-column table with the line name on the left. The row also shows the chosen entry's reason on a second line under the name, in a `label` span with `data-clamp="2"`. The status word appears right-aligned in the second column. Above that cap and up to `max_rows`, the table drops the reason and shows name and status only. Above `max_rows` the board switches to a compact wrapped list (`flex flex--wrap gap--small`) of line name and inverted status label, with "Hammersmith & City" shortened to "H&C" and "Waterloo & City" to "W&C". This compact list has no overflow guard, unlike the table, so on a day when nearly every line is disrupted it can run past the bottom of the board on the smaller sizes; that is the accepted trade-off for never hiding a line. The caps per layout are full 5/10, half_vertical 6/12, half_horizontal 2/4, quadrant 0/6, so the quadrant table never shows a reason. `max_with_reason` and `max_rows` are both compared against the same total count of disrupted lines, so either every row shows a reason or none does, and either the table or the compact list is used, never a mix. `data-table-limit` on the table stays as a last-resort row limiter.
- Reason text drops everything up to and including its first `": "`, because TfL prefixes every reason with the line name.
- Text size classes: full uses `value value--small`, the halves use `value value--xsmall`, quadrant uses `label`. "Good service on all other lines" uses the same class as the rows.
- The error-state heading follows the layout's `head_class`.
- `data-table-limit` budgets the table's parent element height minus the `thead`, reserves its own row for "and N more", and runs on window load after images settle. `data-table-max-height` overrides that budget.
- `data-clamp` is a one-shot JavaScript text cut measured on an offscreen clone; if column widths change afterwards, the text can wrap to more lines again.
- `gap--small` is 7 pixels.
- Verified against the live API on September 4, 2026: endpoint, field names, severity codes and the 400 error shape.
- Verified in the live TRMNL recipe editor on September 4, 2026: the poll works with `modes` left at its default (TRMNL applies the custom field's `default:` value), and the disruptions state rendered on all four layout sizes.
- Custom field values cannot be set through the MCP settings tool; only the recipe's settings page can change them.
- Local render check: `python3 simple_tube_status/check.py` (requires the `python-liquid` package; `uv run --with python-liquid python3 simple_tube_status/check.py` works without installing it). It renders all four layouts against six fixtures. One fixture covers the all-good state. Another (`DISRUPTED`) covers three disrupted lines, using severities 6, 9, 10, 11, 18 and 20 and prefixed reasons; Piccadilly carries two disrupted entries (9 and 6) that must collapse to one row showing the worse Severe Delays, not Minor Delays. A third fixture (`RANK_ORDER`) proves the ranking, not numeric value or TfL's listed order, picks the winner: a line lists Minor Delays (9) before Part Closed (11), and the row must show Part Closed with its reason; a second line carries only an unranked code (42, "Mystery") to prove the fallback still renders it. A fourth fixture uses a larger set of eight disrupted lines to exercise the compact list. A fifth fixture holds a 400 error body. A sixth fixture holds an empty payload. The script must print `ok`.
- The title bar is a sibling placed after `layout`, so it renders as a footer, unlike National Rail which nests it. The good-service state uses `flex flex--center-x flex--center-y stretch-y`, not a nested `layout`.

## Decisions the TRMNL automated reviewer keeps questioning

Do not revisit these without new evidence from a device or the simulator:

- The `.board` style block in `shared.liquid` stays. The row limiter measures the table's parent height, so the wrapper must be flex-sized with `min-height: 0`; the framework's `stretch-y` class alone does not do that.
- No transform script. The Liquid `default` and `size` filters handle empty and error payloads, and `check.py` proves it.
- No `data-clamp` on title spans. It truncated "New Southgate via Finsbury Park" on the TRMNL X even with space to spare.
- No "National Rail" instance label on half vertical or quadrant. It collided with the title at 390 pixels wide.
- `image-dither` on the icon is harmless on a black silhouette; leave it.

- The Simple Tube Status layouts write the `title_bar` div by hand, as `tfl_bus_times` does, rather than `{% render 'title_bar' %}`. The cheat sheet only requires it to be a sibling of `layout`, and the hand-written version is what the device has shown.
- The recipe checker runs its "no layout class" and "no responsive classes" hints against the shared markup too, where neither belongs. The four layouts carry `layout layout--col`, and TRMNL X sizing uses `lg:` and `lg:portrait:` prefixes on the size classes passed into the board template.
- No validation on the `modes` field. A misspelt mode makes TfL return a 400, and the board shows "Could not fetch TfL status" with TfL's own message naming the bad mode, so the mistake is not silent. The help text already lists all five valid names.
