# Simple Tube Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A TRMNL recipe in `simple_tube_status/` that lists the TfL lines with a disruption and the reason, or says "Good service on all lines", in all four layout sizes, with a local render check that proves the three states.

**Architecture:** Same shape as `national_rail_departures/`. `settings.yml` polls `https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status` every 5 minutes with no key. `shared.liquid` normalises the payload (`data` array or top-level error object) and defines one `board` template; the four layouts each render it with size arguments (table class, head class, cell class, show reason). `check.py` renders every layout against four inline payloads with python-liquid.

**Tech Stack:** TRMNL recipe (YAML settings + Liquid templates using framework v2 classes), Python 3 with `python-liquid` for the local check (run via `uv run --with python-liquid`, which downloads the python-liquid wheel into uv's cache on first use, so the first run needs network; `uv` is on this machine, no install needed).

**Spec:** docs/superpowers/specs/2026-09-04-simple-tube-status-design.md

## Global Constraints

- Do not commit. AGENTS.md: commit only when asked. No task in this plan has a commit step.
- Build the smallest thing that works. No abstractions, scaffolding, or configuration for needs that do not exist yet.
- Use only CSS class names that appear in `TRMNL_FRAMEWORK_CHEAT_SHEET.md`. Every class below was checked against it: `layout`, `layout--col`, `layout--top`, `layout--stretch-x`, `flex`, `flex--center-x`, `flex--center-y`, `stretch-y`, `gap--none`, `title_bar`, `image`, `title`, `title--small`, `value`, `value--small`, `value--large`, `label`, `label--small`, `label--inverted`, `table`, `table--large`, `table--small`, `table--xsmall`, `text--right`, `pl--1`, `pr--1`, `px--1`, plus the attributes `data-table-limit="true"` and `data-clamp="2"`.
- `README.md` uses CRLF line endings. Every line you add to it must end in `\r\n`. `AGENTS.md` uses LF.
- Severity rule: a status entry is disrupted when `statusSeverity` is not 10, 18 or 20.
- Poll every 5 minutes (`refresh_interval: 5`).
- Default modes: `tube,elizabeth-line,overground`.
- `simple_tube_status/.env.tpl` already exists and must not be changed. Do not create any other file in that directory beyond the six named in this plan.
- The `title_bar` is a sibling of the `layout` div, placed after its closing `</div>`, so the platform renders it as a footer at the bottom of the view (`TRMNL_FRAMEWORK_CHEAT_SHEET.md` line 90: "`title_bar` must be a sibling of `layout`, not nested inside it. The platform positions it at the bottom"). It is not nested inside `layout` the way the National Rail layouts do it.
- The `.board` style block stays (AGENTS.md: the row limiter measures the table's parent height, so the wrapper must be flex-sized with `min-height: 0`).
- Run every command from the repo root `/Users/rob/git/trmnl-plugins`. The check command is `uv run --with python-liquid python3 simple_tube_status/check.py`; if `python-liquid` is installed for the system `python3`, plain `python3 simple_tube_status/check.py` also works. (The National Rail check must be run from inside its own directory because it opens `shared.liquid` relative to the cwd; this plugin's `check.py` resolves paths from its own location so the spec's command works from the root.)

---

## Task 1: settings.yml

**Files:**
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/settings.yml`

**Interfaces:**
- Consumes: the `modes` custom field, interpolated into `polling_url`.
- Produces: a TRMNL polling recipe whose GET response (a JSON array) TRMNL exposes to the templates as `data`; a non-200 JSON object is exposed at the top level.

**Steps:**

- [ ] 1. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/settings.yml` with exactly this content. It copies the `tfl_bus_times/settings.yml` structure (no `id` line, empty headers/body/static_data) and the `author_bio` field from that file with a new description.

```yaml
---
strategy: polling
no_screen_padding: 'yes'
dark_mode: 'no'
static_data: ''
polling_verb: get
polling_url: https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status
polling_headers: ''
polling_body: ''
custom_fields:
- keyname: modes
  field_type: string
  name: Modes
  description: TfL modes to check
  default: tube,elizabeth-line,overground
  help_text: Comma-separated TfL mode names. The default <code>tube,elizabeth-line,overground</code> covers the Underground, Elizabeth line and Overground. Add <code>dlr</code> or <code>tram</code> to include those too.
- keyname: about
  name: About This Plugin
  category: travel,news
  field_type: author_bio
  description: Shows which TfL lines are disrupted and why, or that all lines have good service. Not affiliated with TfL but uses their free, public API.
  github_url: https://github.com/mnbf9rca
  learn_more_url: https://blog.cynexia.com
name: TfL Line Status - disruption summary
refresh_interval: 5
```

- [ ] 2. Check that the YAML parses. PyYAML is not installed for the system `python3` on this machine (`import yaml` fails), so the primary check is the ruby one-liner (macOS ruby ships with YAML). Run:

```
ruby -ryaml -e 'y = YAML.load_file("simple_tube_status/settings.yml"); puts y["polling_url"]; puts y["custom_fields"].map { |f| f["keyname"] }.inspect; puts "ok"'
```

Expected output:

```
https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status
["modes", "about"]
ok
```

If you prefer python and PyYAML happens to be available, this is equivalent and prints `ok`:

```
python3 -c "import yaml,sys; yaml.safe_load(open('simple_tube_status/settings.yml')); print('ok')"
```

If neither parser is available, fall back to `cat simple_tube_status/settings.yml` and compare it by eye against the block in step 1; say in your report that the file was only eyeballed.

- [ ] 3. Confirm nothing else in the directory changed:

```
ls -A simple_tube_status
git status --short simple_tube_status
```

Expected: `.env.tpl` and `settings.yml` listed; `git status` shows `?? simple_tube_status/settings.yml` only. The real check is that there is no ` M simple_tube_status/.env.tpl` line: that file is already committed (commit d36b4d5) and must be unchanged.

---

## Task 2: check.py, then shared.liquid

**Files:**
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/check.py`
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/shared.liquid`

**Interfaces:**
- Consumes (shared.liquid): TRMNL merge variables. Success: `data` is the array of line objects, each with `name` and `lineStatuses[]` holding `statusSeverity`, `statusSeverityDescription` and (on disrupted entries only) `reason`. Failure: no `data`; the 400 body's `message` is at the top level.
- Produces (shared.liquid): the `.board` style block, top-level variables `lines` and `api_error`, and a `{% template board %}` that the layouts render with `lines`, `api_error`, `table_class`, `head_class`, `cell_class`, `show_reason`.
- Consumes (check.py): `shared.liquid` and the four layout files, resolved relative to `check.py` itself.
- Produces (check.py): prints `ok`, or raises `AssertionError` naming the layout and the failed expectation.

**How `{% template %}` and `{% render %}` are handled:** python-liquid does not know TRMNL's `{% template %}` tag. `national_rail_departures/check.py` handles this by regex-extracting the body between `{% template board %}` and `{% endtemplate %}`, registering it under the name `board` in a `DictLoader`, and prepending everything before the template block (the style block and the `assign`s) to each layout before rendering. Standard `{% render "board", ... %}` then resolves through the loader. This plan copies that mechanism exactly.

**Steps:**

- [ ] 1. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/check.py` with exactly this content:

```python
"""Render check: python3 simple_tube_status/check.py (needs python-liquid). Fails if the board logic breaks."""
import os, re
from liquid import Environment, DictLoader

here = os.path.dirname(os.path.abspath(__file__))
shared = open(os.path.join(here, "shared.liquid")).read()
m = re.search(r"{% template board %}(.*?){% endtemplate %}", shared, re.S)
head = shared[: m.start()]
env = Environment(loader=DictLoader({"board": m.group(1)}))
LAYOUTS = ["full.liquid", "half_horizontal.liquid", "half_vertical.liquid", "quadrant.liquid"]

def render(layout, data):
    return env.from_string(head + open(os.path.join(here, layout)).read()).render(**data)

good = lambda id_, name: {"id": id_, "name": name, "modeName": "tube",
                          "lineStatuses": [{"statusSeverity": 10, "statusSeverityDescription": "Good Service"}]}
ALL_GOOD = {"data": [good("bakerloo", "Bakerloo"), good("central", "Central")]}
DISRUPTED = {"data": [
    {"id": "hammersmith-city", "name": "Hammersmith & City", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Hammersmith and City Line: Minor delays due to train cancellations. "}]},
    {"id": "piccadilly", "name": "Piccadilly", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Piccadilly Line: Minor delays between Heathrow Airport and Acton Town eastbound only due to an earlier faulty train at Acton Town. GOOD SERVICE on the rest of the line. "}]},
    {"id": "district", "name": "District", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 11, "statusSeverityDescription": "Part Closed",
         "reason": "District Line: No service between Earl's Court and Wimbledon. Use <rail replacement> buses. "}]},
    {"id": "tram", "name": "Tram", "modeName": "tram", "lineStatuses": [
        {"statusSeverity": 20, "statusSeverityDescription": "Service Closed"}]},
    {"id": "waterloo-city", "name": "Waterloo & City", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 18, "statusSeverityDescription": "No Issues"}]},
    {"id": "victoria", "name": "Victoria", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 10, "statusSeverityDescription": "Good Service"}]},
]}
ERROR = {"$type": "Tfl.Api.Presentation.Entities.ApiError, Tfl.Api.Presentation.Entities",
         "timestampUtc": "2026-09-04T16:00:00Z", "exceptionType": "ApiArgumentException",
         "httpStatusCode": "BadRequest", "httpStatus": "BadRequest",
         "relativeUri": "/Line/Mode/notamode/Status",
         "message": "The following mode is not recognised: notamode"}

for layout in LAYOUTS:
    out = render(layout, ALL_GOOD)
    assert "Good service on all lines" in out, f"{layout}: all-good text"
    assert "other lines" not in out and "<table" not in out, f"{layout}: all-good must not render a table"
    assert "value--large" in out and "flex--center-x" in out, f"{layout}: all-good text large and centred"

    out = render(layout, DISRUPTED)
    for s in ["Hammersmith &amp; City", "Piccadilly", "District", "Part Closed", "Good service on all other lines", "<th"]:
        assert s in out, f"{layout}: missing {s!r}"
    for s in ["Service Closed", "Victoria", "Good service on all lines", "No Issues", "Waterloo"]:
        assert s not in out, f"{layout}: must not show {s!r}"
    assert out.count("label--inverted") == 3, f"{layout}: one inverted status per disrupted entry"
    assert 'class="board"' in out and 'data-table-limit="true"' in out, f"{layout}: board wrapper and row limiter"
    if layout == "quadrant.liquid":
        assert "train cancellations" not in out and "Reason" not in out, "quadrant must hide the reason column"
    else:
        assert "Minor delays due to train cancellations" in out, f"{layout}: reason text"
        assert 'data-clamp="2"' in out, f"{layout}: reason clamped"
        assert "cancellations. <" not in out, f"{layout}: reason trailing space stripped"
        assert "&lt;rail replacement&gt;" in out, f"{layout}: reason escaped"

    out = render(layout, ERROR)
    assert "Could not fetch TfL status" in out and "notamode" in out and "<table" not in out, f"{layout}: 400 body"

    out = render(layout, {})
    assert "Could not fetch TfL status" in out and "<table" not in out, f"{layout}: empty payload"
    assert "TfL Line Status" in out and 'style="' not in out, f"{layout}: title bar present, no inline styles"

print("ok")
```

Notes on the assertions: the template uses the `escape` filter on line names and reasons, so the ampersand in "Hammersmith & City" renders as `&amp;` and the check asserts that form. `label--inverted` count 3 = Hammersmith & City (9), Piccadilly (9), District (11); Tram (20), Waterloo & City (18) and Victoria (10) are excluded by the severity rule, and the `"No Issues"`/`"Waterloo"` must-not-show entries prove severity 18 is treated as good service. The `"cancellations. <"` assertion proves the trailing space in `reason` is stripped. The `&lt;rail replacement&gt;` assertion proves `reason` is escaped. `class="board"` and `data-table-limit="true"` prove the row-limiter wrapper is present in every disrupted render. `value--large` and `flex--center-x` prove the good-service text is large and centred.

- [ ] 2. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/shared.liquid` with exactly this content:

```liquid
<style>
  /* Sized by flexbox to the space above the title bar, so the table row limiter measures the right height. */
  .board { flex: 1 1 0; min-height: 0; width: 100%; }
</style>
{% assign lines = data %}
{% assign api_error = message | default: data.message %}

{% template board %}
{% assign n_lines = lines | size %}
{% if n_lines == 0 %}
<span class="title px--1">Could not fetch TfL status</span>
{% if api_error %}<span class="{{ cell_class }} px--1">{{ api_error | escape }}</span>{% endif %}
{% else %}
{% assign disrupted = 0 %}
{% capture rows %}
{% for line in lines %}
{% for status in line.lineStatuses %}
{% if status.statusSeverity != 10 and status.statusSeverity != 18 and status.statusSeverity != 20 %}
{% assign disrupted = disrupted | plus: 1 %}
    <tr>
      <td class="pl--1"><span class="{{ cell_class }}">{{ line.name | escape }}</span></td>
      <td{% unless show_reason %} class="text--right pr--1"{% endunless %}><span class="label label--inverted">{{ status.statusSeverityDescription | escape }}</span></td>
      {% if show_reason %}<td class="pr--1"><span class="{{ cell_class }}" data-clamp="2">{{ status.reason | strip | escape }}</span></td>{% endif %}
    </tr>
{% endif %}
{% endfor %}
{% endfor %}
{% endcapture %}
{% if disrupted == 0 %}
<div class="flex flex--center-x flex--center-y stretch-y">
  <span class="value value--large">Good service on all lines</span>
</div>
{% else %}
<div class="board">
<table class="table {{ table_class }}" data-table-limit="true">
  <thead>
    <tr>
      <th class="pl--1"><span class="title {{ head_class }}">Line</span></th>
      <th{% unless show_reason %} class="text--right pr--1"{% endunless %}><span class="title {{ head_class }}">Status</span></th>
      {% if show_reason %}<th class="pr--1"><span class="title {{ head_class }}">Reason</span></th>{% endif %}
    </tr>
  </thead>
  <tbody>
{{ rows }}
  </tbody>
</table>
</div>
<span class="label label--small px--1">Good service on all other lines</span>
{% endif %}
{% endif %}
{% endtemplate %}
```

How it works, so you do not "improve" it:
- `lines = data`: TRMNL wraps the array response as `data`. On a failed poll `data` is absent, `lines | size` is 0, and the error branch shows. `api_error` comes from the top-level `message` (the real 400 shape), with `data.message` as the National Rail style fallback.
- One loop, not two: rows are captured into `rows` while `disrupted` counts them, so the severity condition appears exactly once. If the count is zero the capture is discarded and the good-service branch shows.
- `escape` on `name`, `statusSeverityDescription`, `reason` and `api_error` because the ampersand in "Hammersmith & City" is real and the reason text is free text from the API.
- When `show_reason` is false (quadrant) the Status column is the last column, so it gets `text--right pr--1` like National Rail's last column.
- `data` present but an empty array renders the fetch error; TfL never returns an empty array for a valid mode, so this is accepted.
- The guard is for `data` absent, not malformed. If `data` were ever an object, `size` returns its key count and the loop yields nothing, so the good-service text would show. TRMNL only wraps arrays, so this does not occur.

Do not run the check yet: the layouts do not exist until Task 3, and the check runs once at Task 3 step 5.

---

## Task 3: the four layouts

**Files:**
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/full.liquid`
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/half_horizontal.liquid`
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/half_vertical.liquid`
- Create: `/Users/rob/git/trmnl-plugins/simple_tube_status/quadrant.liquid`

**Interfaces:**
- Consumes: `lines` and `api_error` from `shared.liquid` (shared markup is prepended to every layout by TRMNL), and the `board` template.
- Produces: the outer `layout` shell holding one `{% render "board", ... %}` with the size arguments for that layout, then a sibling `title_bar` (TfL roundel image and "TfL Line Status") placed after the layout so the platform renders it as a footer. `render` has an isolated scope, so every variable is passed explicitly.

The outer shell, `gap--none` on half_horizontal, and the `table_class`/`head_class`/`cell_class` values are copied from the matching `national_rail_departures/*.liquid` file. The title bar is not copied: it is a sibling `<div class="title_bar">` placed after the closing `</div>` of the layout, as `tfl_bus_times/full.liquid` does and as `TRMNL_FRAMEWORK_CHEAT_SHEET.md` line 90 requires ("`title_bar` must be a sibling of `layout`, not nested inside it. The platform positions it at the bottom"). The other differences from National Rail: the image is the TfL roundel URL (same as `tfl_bus_times`) without `image-dither`, the title is fixed text, there is no `instance` span, and `platform:` becomes `show_reason:`.

**Steps:**

- [ ] 1. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/full.liquid` with exactly this content (`table--large`, `cell_class: "value"`, `show_reason: true`):

```liquid
<div class="layout layout--col layout--top layout--stretch-x">
  {% render "board", lines: lines, api_error: api_error, table_class: "table--large", head_class: "", cell_class: "value", show_reason: true %}
</div>

<div class="title_bar">
  <img class="image" src="https://upload.wikimedia.org/wikipedia/commons/3/3e/TfL_roundel_%28no_text%29.svg" />
  <span class="title">TfL Line Status</span>
</div>
```

- [ ] 2. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/half_horizontal.liquid` with exactly this content (`table--small`, `cell_class: "value value--small"` as National Rail's half_horizontal uses, `show_reason: true`):

```liquid
<div class="layout layout--col layout--top layout--stretch-x gap--none">
  {% render "board", lines: lines, api_error: api_error, table_class: "table--small", head_class: "title--small", cell_class: "value value--small", show_reason: true %}
</div>

<div class="title_bar">
  <img class="image" src="https://upload.wikimedia.org/wikipedia/commons/3/3e/TfL_roundel_%28no_text%29.svg" />
  <span class="title">TfL Line Status</span>
</div>
```

- [ ] 3. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/half_vertical.liquid` with exactly this content (same sizes as National Rail's half_vertical, `show_reason: true`):

```liquid
<div class="layout layout--col layout--top layout--stretch-x">
  {% render "board", lines: lines, api_error: api_error, table_class: "table--small", head_class: "title--small", cell_class: "value value--small", show_reason: true %}
</div>

<div class="title_bar">
  <img class="image" src="https://upload.wikimedia.org/wikipedia/commons/3/3e/TfL_roundel_%28no_text%29.svg" />
  <span class="title">TfL Line Status</span>
</div>
```

- [ ] 4. Write `/Users/rob/git/trmnl-plugins/simple_tube_status/quadrant.liquid` with exactly this content (`table--xsmall`, `head_class: "title--small"`, `cell_class: "label"`, `show_reason: false`, and `title--small` on the sibling title bar's title):

```liquid
<div class="layout layout--col layout--top layout--stretch-x">
  {% render "board", lines: lines, api_error: api_error, table_class: "table--xsmall", head_class: "title--small", cell_class: "label", show_reason: false %}
</div>

<div class="title_bar">
  <img class="image" src="https://upload.wikimedia.org/wikipedia/commons/3/3e/TfL_roundel_%28no_text%29.svg" />
  <span class="title title--small">TfL Line Status</span>
</div>
```

- [ ] 5. Run the check:

```
uv run --with python-liquid python3 simple_tube_status/check.py
```

Expected output, exactly:

```
ok
```

- [ ] 6. Confirm the directory holds exactly the seven expected files and `.env.tpl` is untouched:

```
ls -A simple_tube_status
git status --short simple_tube_status
```

Expected `ls`: `.env.tpl check.py full.liquid half_horizontal.liquid half_vertical.liquid quadrant.liquid settings.yml shared.liquid`. Expected `git status`: one `??` line per new file: `?? simple_tube_status/check.py`, `?? simple_tube_status/full.liquid`, `?? simple_tube_status/half_horizontal.liquid`, `?? simple_tube_status/half_vertical.liquid`, `?? simple_tube_status/quadrant.liquid`, `?? simple_tube_status/settings.yml`, `?? simple_tube_status/shared.liquid`. The real check is that there is no ` M simple_tube_status/.env.tpl` line.

---

## Task 4: README section and AGENTS.md section

**Files:**
- Modify: `/Users/rob/git/trmnl-plugins/README.md` (CRLF; insert a section between the National Rail section and `## Framework cheat sheet`)
- Modify: `/Users/rob/git/trmnl-plugins/AGENTS.md` (LF; insert a section between the National Rail section and `## Decisions the TRMNL automated reviewer keeps questioning`)

**Interfaces:**
- Consumes: the existing files; each has its marker heading exactly once.
- Produces: `README.md` with 28 new CRLF lines (70 CR-terminated lines before, 98 after) and `AGENTS.md` with a new `## Simple Tube Status plugin` section.

**Steps:**

- [ ] 1. First run `git diff --quiet README.md && echo clean` and expect `clean` (this decides the rollback path in step 2). Then insert the README section by running this from the repo root. It reads and writes bytes, builds the section with `\r\n` joins, and inserts it immediately before the `## Framework cheat sheet` heading. Do not edit README.md with a text editor or the Edit tool; they may write LF.

```
python3 - <<'EOF'
p = "README.md"
s = open(p, "rb").read()
marker = b"## Framework cheat sheet"
assert s.count(marker) == 1, "marker must appear exactly once"
section = "\r\n".join([
    "## Simple Tube Status",
    "",
    "Which TfL lines are disrupted right now and why, or \"Good service on all lines\" when nothing is. Polls the TfL status feed every 5 minutes for the modes you choose (tube, Elizabeth line and Overground by default).",
    "",
    "Works across all four TRMNL layout sizes.",
    "",
    "### Setup",
    "",
    "1. In the TRMNL recipe editor, create a new recipe using the files in `simple_tube_status/`.",
    "2. Leave `modes` as `tube,elizabeth-line,overground`, or edit the comma-separated list. `dlr` and `tram` are valid additions.",
    "",
    "### Files",
    "",
    "```",
    "simple_tube_status/",
    "  settings.yml          # API config and custom fields",
    "  shared.liquid         # Normalises the payload and defines the shared board template",
    "  full.liquid           # Full-screen layout",
    "  half_horizontal.liquid",
    "  half_vertical.liquid",
    "  quadrant.liquid",
    "  check.py              # Local render check: python3 simple_tube_status/check.py (needs python-liquid)",
    "```",
    "",
    "### Data source",
    "",
    "Uses the [TfL Unified API](https://api.tfl.gov.uk/) (free, no key required). Not affiliated with TfL.",
    "",
    "",
]).encode()
open(p, "wb").write(s.replace(marker, section + marker))
EOF
```

Expected: no output.

- [ ] 2. Check the README line endings and placement:

```
grep -c $'\r' README.md
file README.md
grep -n '^## ' README.md | tr -d '\r'
```

Expected output:

```
98
README.md: ASCII text, with CRLF line terminators
5:## TfL Bus Stops
35:## National Rail Departures
68:## Simple Tube Status
96:## Framework cheat sheet
```

The `grep -c` count was 70 before this task and must be 98 now (28 added lines, every one CRLF). `file` must say only "CRLF line terminators"; if it says "CRLF, LF line terminators" a LF-only line crept in: if README.md had no uncommitted changes before this task (the `git diff --quiet README.md` check in step 1 printed `clean`), run `git checkout README.md` and redo step 1; otherwise remove the inserted section by hand.

- [ ] 3. Insert the AGENTS.md section by running this from the repo root:

```
python3 - <<'EOF'
p = "AGENTS.md"
s = open(p).read()
marker = "## Decisions the TRMNL automated reviewer keeps questioning"
assert s.count(marker) == 1, "marker must appear exactly once"
section = """## Simple Tube Status plugin

- Data source: TfL Unified API, `GET https://api.tfl.gov.uk/Line/Mode/{{ modes }}/Status`. Free, no key. The array response arrives as `data`; a 400 for an unknown mode arrives as a top-level object with `message`.
- Severity rule: a `lineStatuses` entry is disrupted when `statusSeverity` is not 10, 18 or 20. Do not use "below 10"; it misses 11 to 17 and 19.
- Verified against the live API on September 4, 2026: endpoint, field names, severity codes and the 400 error shape.
- Local render check: `python3 simple_tube_status/check.py` (requires the `python-liquid` package; `uv run --with python-liquid python3 simple_tube_status/check.py` works without installing it). It renders all four layouts against all-good, disrupted (severities 9, 11, 18 and 20 present), 400-error and empty payloads and must print `ok`.
- The title bar is a sibling placed after `layout`, so it renders as a footer, unlike National Rail which nests it. The good-service state uses `flex flex--center-x flex--center-y stretch-y`, not a nested `layout`.

"""
open(p, "w").write(s.replace(marker, section + marker))
EOF
```

Expected: no output.

- [ ] 4. Check AGENTS.md placement and line endings:

```
grep -n '^## ' AGENTS.md
file AGENTS.md
```

Expected output:

```
5:## How to work in this repo
14:## Secrets
21:## TRMNL facts that matter here
28:## National Rail Departures plugin
34:## Simple Tube Status plugin
42:## Decisions the TRMNL automated reviewer keeps questioning
AGENTS.md: ASCII text, with very long lines (373)
```

(`file` must not mention CRLF.)

- [ ] 5. Run the render check once more to prove nothing in the plugin changed:

```
uv run --with python-liquid python3 simple_tube_status/check.py
```

Expected output, exactly:

```
ok
```

- [ ] 6. Final working-tree check:

```
git status --short
```

Expected: ` M AGENTS.md`, ` M README.md`, and one `??` line per plugin file (`?? simple_tube_status/check.py`, `?? simple_tube_status/full.liquid`, `?? simple_tube_status/half_horizontal.liquid`, `?? simple_tube_status/half_vertical.liquid`, `?? simple_tube_status/quadrant.liquid`, `?? simple_tube_status/settings.yml`, `?? simple_tube_status/shared.liquid`). The real check is that there is no ` M simple_tube_status/.env.tpl` line. `?? docs/superpowers/plans/` and `?? docs/superpowers/specs/2026-09-04-simple-tube-status-design.md` are also untracked and may show; they are expected. Nothing else should be caused by this plan. Do not commit.

---

## Task 5: manual verification in the TRMNL recipe editor

**Files:** none.

**Interfaces:**
- Consumes: the recipe files from Tasks 1 to 3, loaded into a TRMNL recipe via the TRMNL MCP tools (`mcp__trmnl__IntegrationsWriteSettingsTool`, `mcp__trmnl__MarkupsWriteTool`, `mcp__trmnl__MergeVariablesShowTool`, `mcp__trmnl__IntegrationsLogsTool`).
- Produces: a pass/fail note per item below, relayed back to the main session.

**Note:** the main session performs this task with the TRMNL MCP tools. The executor does not do this task; it stops after Task 4 and reports.

**Checklist:**

1. Write `settings.yml` to the recipe and confirm the poll succeeds with `modes` left at the default `tube,elizabeth-line,overground`: the merge variables show `data` as an array of line objects with `name` and `lineStatuses`.
2. Confirm `{{ modes }}` interpolates in `polling_url`: set `modes` to `notamode`, poll, and confirm the merge variables show a top-level `message` of `The following mode is not recognised: notamode`. Set `modes` back to the default afterwards.
3. Write `shared.liquid` and the four layouts, then render each of full, half_horizontal, half_vertical and quadrant in the current live state. Note which state it is (good on all lines, or disruptions).
4. Disruptions state, all four layouts: one row per disrupted status entry, line name and inverted status label visible, reason column present and clamped to two lines on full and both halves, reason column absent on quadrant, "Good service on all other lines" under the table, "and N more" row appears only when rows overflow.
5. Good-service state, all four layouts: "Good service on all lines" centred and large, no table. If the live feed has disruptions, temporarily set `modes` to a single mode with good service (check the live merge variables to pick one). This state must be seen in the editor.
6. Error state, all four layouts: with `modes` set to `notamode`, the screen shows "Could not fetch TfL status" and the API message. Set `modes` back to the default afterwards.
7. Title bar on all four layouts: TfL roundel visible, "TfL Line Status" not truncated, `title--small` on quadrant, and the title bar sits at the bottom of the view, below the table.
8. Half vertical and quadrant at 390 pixels wide: line names such as "Hammersmith & City" and the inverted status label fit on one row without overlapping.
9. Record the verification date and any deviation in the spec's Verification section if the main session asks for it; otherwise report the results in the reply.
