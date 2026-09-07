# Simple Tube Status plugin

Read the root `AGENTS.md` first for repo-wide rules, secrets and TRMNL platform facts.

## Data source and severity

- Data source: TfL Unified API, `GET https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status`. Free, no key. The array response arrives as `data`; a 400 for an unknown mode arrives as a top-level object with `message`.
- `shared.liquid` sets `api_error` from the top-level `message` field, since that is where the 400 body normally arrives, and falls back to `data.message` to cover a body that TRMNL wraps under `data`.
- Severity rule: a `lineStatuses` entry is disrupted when `statusSeverity` is not 10, 18 or 20. Do not use "below 10"; it misses 11 to 17 and 19.
- Each disrupted line renders exactly one row, whether in the single table or in compact mode's two-column tables, never one per disrupted status entry. `shared.liquid` picks that line's worst entry with its own worst-first ranking of severity codes: `1, 2, 16, 3, 4, 5, 11, 6, 8, 7, 15, 14, 9, 12, 13, 17, 0, 19` (`severity_rank`, defined once at the top of the `board` template). A status code missing from that list ranks after every listed code (fallback rank 99); among entries with an unranked code, or on a tie, the first as TfL lists them wins.
- Verified against the live API on September 4, 2026: endpoint, field names, severity codes and the 400 error shape.

## Board modes and caps

- Each layout carries two cap pairs: `max_with_reason`/`max_rows` for the original device, and `max_with_reason_lg`/`max_rows_lg` for the TRMNL X (the `lg:` breakpoint, 1024px min-width, device 1872x1404).
- With the reason toggle on and the disrupted count at or below `max_with_reason`, each row shows the chosen entry's reason on a second line under the name, in a `label lg:label--xxlarge lg:portrait:label--large block` span with `data-clamp="1"` (one line, ellipsis; the block class supplies the line break, so there is no `<br>`).
- Above `max_with_reason` but at or below `max_with_reason_lg`, the reason line still renders in the DOM (same span, same clamp) but with `hidden lg:visible` in place of `block`, so the original device hides it while the X shows it.
- Above `max_with_reason_lg`, or with the toggle off, the table shows name and status only.
- Above `max_rows` but at or below `max_rows_lg`, the board renders both the single table (wrapped in `<div class="hidden lg:visible">`, so only the X shows it) and the compact two-column block (wrapped in `<div class="lg:hidden">`, so only the original device shows it) from the same per-line severity selection, each loop run once.
- Above `max_rows_lg` the board switches to two side-by-side tables (`.columns` / `.column`) only, each a name-left, status-right list with no `<thead>`. The disrupted lines split column-major: the first `half` (`(disrupted + 1) / 2`, integer division) fill the first table in TfL order, the rest fill the second, always with short names.
- This compact mode has no overflow guard, unlike the single table, so on a day when nearly every line is disrupted it can run past the bottom of the board on the smaller sizes; that is the accepted trade-off for never hiding a line.
- The original-device caps are calculated, not guessed, from heights measured in the markup editor preview on September 7, 2026 (true device pixels): full board 359px, header 24px, name-only row 42px, reason row 62px; half_horizontal board 144px, row 31px, reason row 51px; half_vertical board 374px, row 31px, reason row 51px.
- `max_rows` = floor((board - header) / row) and `max_with_reason` = floor((board - header) / reason row), giving full 5/7, half_vertical 6/11, half_horizontal 2/3, quadrant 0/6 (unchanged; never shows a reason on the original device).
- The lg caps are full 6/9, half_vertical 6/11, half_horizontal 3/6, quadrant 2/7 (on September 7, 2026 a static-data test with nine disrupted lines pushed full's footer into the title bar in the editor's TRMNL X preview at `lg:table--base` padding; the fix was to keep `table--small` padding on the X too, because the X's two-column mode is capped by column width at `lg:value--base` and leaves most of the screen empty, so a nine-row single table is the better use of it).
- An lg cap must never be below its original-device cap, or the count between them renders nothing (the table needs `disrupted <= max_rows_lg` and the columns need `disrupted > max_rows`), so half_vertical's and full's reason lg caps were raised to match; the lg caps are still knobs, not measured limits.
- `max_with_reason`/`max_rows` and their `_lg` counterparts are both compared against the same total count of disrupted lines.
- The table carries no `data-table-limit`; the caps above are the only overflow control. Simple Tube Status no longer uses `data-table-limit`: the per-layout row caps are the only overflow control now.
- The title bar is a sibling placed after `layout`, so it renders as a footer, unlike National Rail which nests it. The good-service state uses `flex flex--center-x flex--center-y stretch-y`, not a nested `layout`.

## Text sizes and badges

- Status badges and text-size classes all carry matching `lg:`/`lg:portrait:` variants, mirroring the pattern National Rail Departures uses; the bullets below say how the badge is built and sized per device.
- The status badge sits right-aligned in the second column, whose `<td>` carries `style="white-space:nowrap"` because the framework has no no-wrap utility and the table's auto column split otherwise wrapped "Part Suspended" onto two lines on the halves (measured September 7, 2026).
- Text size classes on the original device: full uses `value value--base` names (38px on a 42px line) with a badge of the same size; both halves use `value value--small` names (26px) with a `value--xsmall` (20px) badge; the quadrant uses `label` with a plain `label label--inverted` badge.
- On full and the halves the badge is not a `label`: the label family tops out at `label--xxlarge` (30px), which looked half-size next to the X's 58px names, so the badge is a `value`-sized span built from the framework utilities `bg--black text--white rounded--xsmall px--1` (label--inverted's own styling is 4px corners and 1px 5px padding, so this is a close match).
- Width sets the badge size: on the X full table "Hammersmith & City" at 58px is about 620px, so beside "Part Suspended" the badge can be `lg:value--base` (about 300px) but not `lg:value--large`; on the 500px-wide X halves the short names leave room for `lg:value--small`.
- The reason line is `label lg:label--xxlarge lg:portrait:label--large` (16px on the original device, 30px on the X).
- Half vertical's compact columns (about 180px wide) and the quadrant keep the `label label--inverted` badge because nothing larger fits.
- The halves cannot take 38px: measured September 7, 2026, a 385px-wide half wrapped the badge, "Elizabeth line" and the footer at that size.
- Each layout passes `cell_class`, `badge_class`, `foot_class`, `col_class` and `col_badge_class`; the two-column compact mode uses the `col_` pair, one size down because each column is half the width (full and half_horizontal `value value--small` with `label label--large label--inverted`, half_vertical `value value--xsmall` with a plain `label label--inverted`, quadrant `label` with `label label--inverted`), after a September 7, 2026 editor render showed full's 38px names and 30px badges wrapping inside 390px columns.
- The footer "Good service on all other lines" uses `foot_class`, which is `cell_class` everywhere except half_vertical, where it drops to `value value--xsmall` so the sentence stays on one line at 385px.
- The full layout's table uses `table--small` on both devices, its layout carries `gap--none`, and its footer is `lg:value--base` on the X: with nine rows at `lg:value--large` (70px lines) the table ends 45px above the board's bottom, so a 70px footer plus the layout's 10px gap clipped into the title bar (measured September 7, 2026).
- Half vertical's footer is `lg:value--small lg:portrait:value--xsmall` on the X because "Good service on all other lines" wrapped at `lg:value--base` in its 500px-wide X preview.
- The error-state heading follows the layout's `head_class`.

## Short names

- Short names are "H&C", "W&C", "Elizabeth" and "Met" for Hammersmith & City, Waterloo & City, Elizabeth line and Metropolitan.
- In the single table a row uses the full name when its character count is within the layout's `max_name_chars` budget and the short name otherwise; Liquid cannot measure text, so the budget stands in for width.
- Budgets: full 99 and quadrant 99 (never shorten), both halves 13 (shortens the 14-, 15- and 18-character names; "Metropolitan" is 12 and stays).
- Compact two-column mode always uses short names.

## Reason toggle

- Reason text drops everything up to and including its first `": "`, because TfL prefixes every reason with the line name.
- The `show_disruptions` boolean custom field (added September 7, 2026, default off) gates the reason line entirely.
- Custom field values are not top-level template variables: they live at `trmnl.plugin_settings.custom_fields_values.<keyname>`, and a boolean field arrives as the string `"true"` or `"false"` (confirmed September 7, 2026 in the editor: a top-level `show_disruptions` never rendered a reason, and the merge-variables view showed only `data` and `trmnl`).
- `shared.liquid` reads that path, folds it into `show_reason` accepting either the string `"true"` or a boolean, and every layout passes `show_reason` into the `board` render.
- Off, every row is name and status only; the reason caps above only matter when it is on.
- `check.py` renders with the field on by default so the cap checks still bite, and separately proves missing, `"false"` and `False` all hide the reason.
- The reason toggle is a custom field value, so tick it on the settings page, not through MCP, and untick it afterwards.

## Testing

- Local render check: `python3 simple_tube_status/check.py` (requires the `python-liquid` package; `uv run --with python-liquid python3 simple_tube_status/check.py` works without installing it). It renders all four layouts against seven fixtures. The script must print `ok`.
- One fixture covers the all-good state.
- Another (`DISRUPTED`) covers three disrupted lines, using severities 6, 9, 10, 11, 18 and 20 and prefixed reasons; Piccadilly carries two disrupted entries (9 and 6) that must collapse to one row showing the worse Severe Delays, not Minor Delays.
- A third fixture (`RANK_ORDER`) proves the ranking, not numeric value or TfL's listed order, picks the winner: a line lists Minor Delays (9) before Part Closed (11), and the row must show Part Closed with its reason; a second line carries only an unranked code (42, "Mystery") to prove the fallback still renders it.
- A fourth fixture uses a larger set of nine disrupted lines to exercise the compact columns, including full's "both" mode (table and columns together) above its `max_rows` of 7 and at or below its `max_rows_lg` of 9.
- A fifth fixture (`FIVE`) holds five disrupted lines to land half_horizontal between its caps: `max_rows` (3) and `max_rows_lg` (6), so it renders both the table and the columns block; on full it lands exactly on `max_with_reason` (5), so all five reasons render.
- A sixth fixture holds a 400 error body. A seventh fixture holds an empty payload.
- `python3 simple_tube_status/check.py dump three|five|nine` prints the three fixtures used on September 7, 2026 (three disrupted lines; five, for reason rows with the toggle on; nine, for two-column mode) ready to paste.
- Static-fixture method: follow the generic steps in the root `AGENTS.md`. For this plugin, wrap the TfL array as `{"data": [...]}`, which is the shape polling produces, and restore with one call `{"strategy": "polling", "polling_url": "https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status", "static_data": ""}`. `IntegrationsRefreshDataTool` is not authorised for this plugin's MCP key, and the permission classifier sometimes blocks the strategy write in a subagent, so run those writes from the main session.
- Verified in the live TRMNL recipe editor on September 4, 2026: the poll works with `modes` left at its default (TRMNL applies the custom field's `default:` value), and the disruptions state rendered on all four layout sizes.

## Decisions the TRMNL automated reviewer keeps questioning

Do not revisit these without new evidence from a device or the simulator:

- No `data-table-limit` and no custom style block in Simple Tube Status: the limiter hid rows that fit because it reserves its own label row, Rob removed it on September 5, 2026, and the per-layout caps are the only overflow control. (National Rail Departures still uses its own `.board` style block; that is unrelated to this plugin.)
- No transform script. The Liquid `default` and `size` filters handle empty and error payloads, and `check.py` proves it.
- `image-dither` on the icon is harmless on a black silhouette; leave it.
- The Simple Tube Status layouts write the `title_bar` div by hand, as `tfl_bus_times` does, rather than `{% render 'title_bar' %}`. The cheat sheet only requires it to be a sibling of `layout`, and the hand-written version is what the device has shown.
- The recipe checker runs its "no layout class" and "no responsive classes" hints against the shared markup too, where neither belongs. The four layouts carry `layout layout--col`, and TRMNL X sizing uses `lg:` and `lg:portrait:` prefixes on the size classes passed into the board template.
- No validation on the `modes` field. A misspelt mode makes TfL return a 400, and the board shows "Could not fetch TfL status" with TfL's own message naming the bad mode, so the mistake is not silent. The help text already lists all five valid names.
- Compact mode is fixed at two columns on every size, so on a strike day the quadrant (about twelve rows) and half horizontal (about eight) can overrun with nineteen or twenty lines disrupted. Rob accepted that on September 5, 2026: people know when there is a strike. A per-layout column count or a group-by-status stage would be the next step if it ever matters.
