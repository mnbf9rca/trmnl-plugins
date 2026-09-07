# TfL Bus Times plugin
Read the root `AGENTS.md` first for repo-wide rules, secrets and TRMNL platform facts. Data source: TfL Unified API, `GET https://api.tfl.gov.uk/StopPoint/{{ stoppoint }}/Arrivals` (free, no key; `stoppoint` is a string custom field); `shared.liquid` sorts `data` by `timeToStation`, the layouts use `data-table-limit`, and there is no `check.py` for this plugin.
