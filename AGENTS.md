# AGENTS.md

Recipe plugins for TRMNL e-ink displays. One directory per plugin, each holding `settings.yml`, `shared.liquid`, and the four layout templates (`full`, `half_horizontal`, `half_vertical`, `quadrant`).

## How to work in this repo

- The main session orchestrates. Delegate research, file writing, and checks to subagents, and relay their results. Do work inline only for one-line edits.
- Build the smallest thing that works. No abstractions, scaffolding, or configuration for needs that do not exist yet.
- Follow the writing-clearly rules for any prose (README, specs, help text).
- Commit only when asked. Match the existing line endings of a file you edit (`README.md` uses CRLF).
- Before a pull request is ready to merge, anything done to verify it that is not already in the repo (a fixture, a measurement pass, a device or editor test method) goes into AGENTS.md and the repo in that same pull request. Nothing about how the change was proven should have to be rediscovered.
- Design specs live in `docs/superpowers/specs/`. Read the relevant spec before changing a plugin.
- `TRMNL_FRAMEWORK_CHEAT_SHEET.md` lists every framework CSS class. Use it instead of guessing class names.

## Secrets

- Secrets live in 1Password, never in the repo or the shell environment. Each plugin folder has a `.env.tpl` that maps environment variable names to `op://` references and holds no values. It always includes that plugin's `TRMNL_MCP_API_KEY`, plus any data-source secrets the plugin needs. `.envrc` loads only a service-account token. All of these files are safe to commit.
- Start Claude with `op_claude <plugin_dir>`. It runs `op run --env-file=<plugin_dir>/.env.tpl -- claude`, so the TRMNL MCP server talks to that one plugin and the secrets exist only inside that process. It also exports `TRMNL_PLUGIN=<plugin_dir>`, and a SessionStart hook in `.claude/settings.json` prints that name into the session, so check it before any MCP write rather than asking which plugin is loaded.
- To run anything else that needs a secret, wrap it the same way: `op run --env-file=<plugin_dir>/.env.tpl -- sh -c '...'` and read the variable inside that child process. Never `op read` a secret into the main shell, write it to a file, or print it.
- To add a new secret, add one line to the plugin's `.env.tpl`. Do not document individual keys here.

## TRMNL facts that matter here

- Polling headers use `key=value` pairs separated by `&`, and can interpolate custom fields, for example `x-apikey={{ api_key }}`.
- Shared markup is prepended to every layout. Define reusable markup with `{% template name %}...{% endtemplate %}` and use it with `{% render "name", arg: value %}`. `render` has an isolated scope, so pass every variable explicitly.
- A JSON object response is exposed at the top level; a JSON array is wrapped as `data` (per TRMNL's `trmnlp` poller source). A non-200 JSON response is passed through to the template like any other (confirmed September 3, 2026: a 401 body rendered as "Invalid ApiKey" on screen). Do not trust the `trmnlp` dev tool on this; it discards them.
- Custom field types include `string`, `password`, `number`, `select`, `boolean`, and `author_bio`. Custom field values are not top-level template variables: they live at `trmnl.plugin_settings.custom_fields_values.<keyname>`, and a boolean field arrives as the string `"true"` or `"false"`. Custom field values cannot be set through the MCP settings tool; only the recipe's settings page can change them.
- The framework source is at https://github.com/usetrmnl/trmnl-framework. Check it when `TRMNL_FRAMEWORK_CHEAT_SHEET.md` names a class or data attribute but not how it behaves, for example how `data-table-limit` measures its container or how `data-clamp` truncates.
- The TRMNL MCP server also carries documentation: `DesignSystemTemplateGuideTool` (sections such as `framework_engines_data_attributes`, `custom_fields_form_builder`, `view_adaptation_strategy`) and `DesignSystemReferenceTool` (example markup per size). Ask those before guessing at framework behaviour.
- `data-table-limit` budgets the table's parent element height minus the `thead`, reserves its own row for "and N more", and runs on window load after images settle. `data-table-max-height` overrides that budget. `data-clamp` is a one-shot JavaScript text cut measured on an offscreen clone; if column widths change afterwards, the text can wrap to more lines again.
- `gap--small` is 7 pixels.
- To test a specific API response in the real renderer, switch the plugin to the Static strategy: `IntegrationsWriteSettingsTool` with `{"strategy": "static"}`, then a second call with `{"static_data": <JSON>}` (static data must be a hash, so wrap an array response as `{"data": [...]}`, which is the shape polling produces; the two writes must be separate because `static_data` is only writable once the strategy is static). The editor renders from the last stored payload, so click "Force Refresh" on the plugin's settings page (a confirm dialog follows) before screenshotting; `MergeVariablesShowTool` shows what is stored. Restore with one call `{"strategy": "polling", "polling_url": "<the plugin's polling URL>", "static_data": ""}` (it warns that `polling_url` is unavailable but applies all three; write `polling_url` again on its own to be sure), then Force Refresh again so the device gets live data. The permission classifier sometimes blocks the strategy write in a subagent, so run those writes from the main session.
- To check all four sizes at once, use the Visual Editor button in the TRMNL markup editor (`/plugin_settings/<id>/markup/edit`); it renders full, half horizontal, half vertical and quadrant together and follows the device selector, so one screenshot per device covers everything. The Pop Out Preview page opens its render in a second browser tab, which confused scripted screenshots.

## Plugins

- `national_rail_departures`: read `national_rail_departures/AGENTS.md` before changing anything in it.
- `simple_tube_status`: read `simple_tube_status/AGENTS.md` before changing anything in it.
- `tfl_bus_times`: read `tfl_bus_times/AGENTS.md` before changing anything in it.
