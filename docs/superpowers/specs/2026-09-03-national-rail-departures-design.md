# National Rail Departures plugin

A TRMNL recipe that shows the next trains from one station, optionally only those calling at a second station, with their live status. It answers "are my trains towards work running normally?"

## Data source

Rail Data Marketplace product **Live Departure Board** (`P-d81d6eaf-8060-4467-a339-1c833e50cbbe`), a JSON REST wrapper over the National Rail Darwin Live Departure Board Web Service (LDBWS).

- Operation: `GetDepartureBoard/{crs}`
- Auth: `x-apikey` header
- Query parameters used: `numRows=10`, `timeWindow=120`, and when a filter station is set, `filterCrs={code}&filterType=to`. The filter matches any service that calls at that station, so it doubles as a "direction" filter. The API also accepts an empty `filterCrs=` as no filter (verified September 3, 2026).
- Licence terms require attribution to Rail Delivery Group.

Response fields used:

| Field | Use |
|---|---|
| `locationName` | Title bar |
| `trainServices[]` | One row each, already in departure order |
| `trainServices[].std` | Scheduled time |
| `trainServices[].etd` | `On time`, `Delayed`, `Cancelled`, `No report`, or a revised `HH:MM` |
| `trainServices[].isCancelled` | Overrides `etd` |
| `trainServices[].platform` | Platform column (may be null) |
| `trainServices[].destination[0].locationName`, `.via` | Destination column |
| `nrccMessages[].Value` | Station disruption notices, HTML |

## Files

`national_rail_departures/` with the same shape as `tfl_bus_times/`: `settings.yml`, `shared.liquid`, `full.liquid`, `half_horizontal.liquid`, `half_vertical.liquid`, `quadrant.liquid`.

## Settings

Polling strategy, GET, refresh every 5 minutes. Custom fields:

| keyname | type | required | purpose |
|---|---|---|---|
| `api_key` | password | yes | Rail Data Marketplace key, sent as `x-apikey` |
| `crs` | string (3 chars) | yes | Departure station, for example `WIM` |
| `filter_crs` | string (3 chars) | no | Only show trains calling here, for example `WAT` |

## Rendering

`shared.liquid` normalises the payload (top-level or wrapped in `data`) and defines one `board` template that all four layouts render with size and column arguments.

Per service the status text is: `Cancelled` if `isCancelled`; otherwise `etd` when it is one of the fixed words; otherwise `Exp HH:MM`.

- Services present: table with Time, Destination, Platform, Status. Quadrant omits Platform. Below the table, the first disruption notice, HTML stripped and truncated to one line, when one exists.
- No services: the table is replaced by the disruption notices in full, or "No departures in the next 2 hours" if there are none.
- No station name at all (the poll failed): "Could not fetch departures" followed by the API error text when the body carries one (`fault.faultstring` on 401, `Message` on 400). Confirmed in TRMNL on September 3, 2026.

Footer attributes Rail Delivery Group.

## Out of scope

Delay and cancellation reason text per row, operator, calling points, configurable time window, the Next Departures and Fastest Departures products.

## Verification

Done on September 3, 2026 against the live API: the URL in `polling_url` is correct, `x-apikey` is accepted, all field names match, and `nrccMessages` items use `Value`. Remaining checks happen inside the TRMNL recipe editor:

1. ~~Base URL~~ Confirmed.
2. ~~Top level vs `data`~~ Confirmed top level (TRMNL's `trmnlp` poller wraps only arrays as `data`).
3. ~~Liquid `{% if %}` in `polling_url`~~ Confirmed evaluated (filtered board rendered in TRMNL on September 3, 2026).
4. ~~`nrccMessages` casing~~ Confirmed `Value`.
5. Check all four layouts with a filtered and an unfiltered station, and observe one delayed or cancelled service.
