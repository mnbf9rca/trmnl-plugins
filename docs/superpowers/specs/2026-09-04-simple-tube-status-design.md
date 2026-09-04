# Simple Tube Status plugin

A TRMNL recipe that lists the TfL lines with a disruption and the reason, or says "Good service on all lines". It is the e-ink version of https://github.com/mnbf9rca/super_simple_tfl_status, without colour.

## Data source

TfL Unified API, endpoint `https://api.tfl.gov.uk/Line/Mode/{modes}/Status`, GET. No key needed, free. The response sets `Cache-Control` max-age to 30 seconds; we poll every 5 minutes.

The response is a JSON array of line objects. TRMNL wraps an array response as `data`.

Response fields used:

| Field | Use |
|---|---|
| `data[].name` | Line name, for example `Hammersmith & City` |
| `data[].lineStatuses[]` | One or more status entries per line |
| `lineStatuses[].statusSeverity` | Integer severity code |
| `lineStatuses[].statusSeverityDescription` | Status word, for example `Minor Delays` |
| `lineStatuses[].reason` | Disruption sentence. Present only on disrupted entries, absent on good-service entries. Has trailing whitespace |

Severity codes come from `https://api.tfl.gov.uk/Line/Meta/Severity` and are the same for tube, overground, elizabeth-line, dlr and tram.

| Code | Meaning |
|---|---|
| 0 | Special Service |
| 1 | Closed |
| 2 | Suspended |
| 3 | Part Suspended |
| 4 | Planned Closure |
| 5 | Part Closure |
| 6 | Severe Delays |
| 7 | Reduced Service |
| 8 | Bus Service |
| 9 | Minor Delays |
| 10 | Good Service |
| 11 | Part Closed |
| 12 | Exit Only |
| 13 | No Step Free Access |
| 14 | Change of frequency |
| 15 | Diverted |
| 16 | Not Running |
| 17 | Issues Reported |
| 18 | No Issues |
| 19 | Information |
| 20 | Service Closed |

A status entry is disrupted when its severity is not 10, 18 or 20. The old web app used "below 10", which missed 11 to 17 and 19.

Reason text usually starts with a prefix such as `Hammersmith and City Line: `. The template strips everything up to and including the first `": "` before showing the reason. See Rendering for where this applies.

Errors: an unknown mode returns HTTP 400 with a JSON object whose keys include `message` (for example `The following mode is not recognised: notamode`) and `exceptionType`. TRMNL passes non-200 JSON through to the template.

## Files

`simple_tube_status/` with the same shape as `national_rail_departures/`: `settings.yml`, `shared.liquid`, `full.liquid`, `half_horizontal.liquid`, `half_vertical.liquid`, `quadrant.liquid`, `check.py`, and the existing `.env.tpl`.

## Settings

Polling strategy, GET, refresh every 5 minutes, `polling_url: https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status`. Custom fields:

| keyname | type | required | purpose |
|---|---|---|---|
| `modes` | string | yes | Comma-separated TfL mode list, default `tube,elizabeth-line,overground`. Valid extra values include `dlr` and `tram` |

Plus the `author_bio` field like the other plugins.

## Rendering

`shared.liquid` normalises the payload (`data` present or not) and defines one `board` template that all four layouts render with size arguments: table class, head class, cell class, `max_with_reason`, and `max_rows`. This follows the National Rail pattern, including the `.board` flex wrapper with `min-height: 0` so the table limiter measures the right height.

Three states:

- No disrupted entries: "Good service on all lines", centred, large.
- Poll failed, meaning `data` is absent or empty: "Could not fetch TfL status" followed by the API error message when the body carries one. `shared.liquid` reads that message from the top-level `message` field first, since that is where TfL's 400 body normally arrives. It falls back to `data.message` to cover a body that TRMNL wraps under `data`. TfL never returns an empty array for a valid mode, so an empty array is treated as a failure. The heading follows the layout's `head_class`.
- Disruptions present: the number of disrupted lines against the layout's `max_rows` and `max_with_reason` picks one of two shapes.
  - At or below `max_rows`, a two-column table: line name on the left, status word right-aligned. The table has `data-table-limit="true"` as a last-resort row limiter, so a list that still overflows shows "and N more". Each disrupted line gets exactly one row, showing its worst status by the plugin's own worst-first ranking of severity codes: `1, 2, 16, 3, 4, 5, 11, 6, 8, 7, 15, 14, 9, 12, 13, 17, 0, 19`. A status code missing from that list ranks after every listed code, and among entries with an unranked code, or on a tie, the first as TfL lists them wins. At or below `max_with_reason`, each row's name cell also carries that chosen status's disruption reason on a second line, in a `label` span with `data-clamp="2"`. Above `max_with_reason` the table has no reason line, name and status only.
  - Above `max_rows`, the board switches to a compact wrapped list (`flex flex--wrap gap--small`) of line name and inverted status label, one pair per disrupted line showing its worst status by the same ranking, no table and no reason text. "Hammersmith & City" shortens to "H&C" and "Waterloo & City" shortens to "W&C" in this mode only. Unlike the table, this list has no overflow guard, so on a day when nearly every line is disrupted it can run past the bottom of the board on the smaller sizes. That is an accepted trade-off: the compact list never hides a line.
  - Below the table or list: "Good service on all other lines".
  - Per-layout caps: full `max_with_reason` 5, `max_rows` 10. half_vertical 6 and 12. half_horizontal 2 and 4. quadrant 0 and 6, so the quadrant table never shows a reason. `max_with_reason` and `max_rows` are both compared against the same total count of disrupted lines, so either every row shows a reason or none does, and either the table or the compact list is used, never a mix.

Reason text drops everything up to and including its first `": "`, because TfL prefixes every reason with the line name.

Text size classes: full uses `value value--small` for names and status, halves use `value value--xsmall`, quadrant uses `label`. "Good service on all other lines" uses the same class as the table or list rows.

The title bar is a sibling placed after the `layout` element, so the platform renders it as a footer, as in `tfl_bus_times`. It shows the TfL roundel, embedded in `shared.liquid` as a base64 data URI (source file: `docs/tube-status-icon.svg`) because TRMNL's publishing check could not fetch the external Wikimedia URL, and "TfL Line Status". Disrupted lines appear in API order, which is alphabetical by line id.

## Out of scope

Line colours, ordering by severity, listing good-service lines, the per-line `disruptions` array, validity periods, and the "names" toggle from the old app (names are always shown because there is no colour).

## Verification

Done on September 4, 2026 against the live API: the endpoint, field names, severity codes and 400 error shape above are all confirmed.

Also verified on September 4, 2026 in the live TRMNL recipe editor: the poll works with `modes` left at its default (TRMNL applies the custom field's `default:` value), and the disruptions state rendered correctly on all four layout sizes.

`python3 simple_tube_status/check.py` (needs `python-liquid`) renders the templates against six fixtures. `ALL_GOOD` covers the all-good state. `DISRUPTED` covers three disrupted lines, using severities 6, 9, 10, 11, 18 and 20 and prefixed reasons; Piccadilly carries two disrupted entries (9 and 6) that must collapse to one row showing the worse Severe Delays, not Minor Delays. `RANK_ORDER` proves the ranking, not numeric value or TfL's listed order, picks the winner: a line lists Minor Delays (9) before Part Closed (11), and the row must show Part Closed with its reason; a second line carries only an unranked code (42, "Mystery") to prove the fallback still renders it. `MANY` uses a larger set of eight disrupted lines to exercise the compact list. The error body holds a 400 error response. The empty object holds an empty payload. It must print `ok`.

Not yet observed on a device or in the recipe editor: the compact wrapped-list mode, which needs a day with enough disrupted lines to exceed a layout's `max_rows`. So far it has only been checked by `check.py`.
