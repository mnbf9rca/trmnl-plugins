"""Render check: python3 simple_tube_status/check.py (needs python-liquid). Fails if the board logic breaks.

python3 simple_tube_status/check.py dump <three|five|nine> prints that fixture as TRMNL static data
({"data": [...]}, the shape the polling strategy produces) for pasting into the plugin's Static Data box."""
import os, re, sys, json
from liquid import Environment, DictLoader

here = os.path.dirname(os.path.abspath(__file__))
shared = open(os.path.join(here, "shared.liquid")).read()
m = re.search(r"{% template board %}(.*?){% endtemplate %}", shared, re.S)
head = shared[: m.start()]
env = Environment(loader=DictLoader({"board": m.group(1)}))
LAYOUTS = ["full.liquid", "half_horizontal.liquid", "half_vertical.liquid", "quadrant.liquid"]
LAYOUT_CFG = {
    "full.liquid": {"col_class": "value value--small portrait:label--small lg:value--base lg:portrait:value--small", "col_badge_class": "value value--xsmall portrait:label--small lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                     "cell_class": "value value--base portrait:value--small lg:value--large lg:portrait:value--base",
                     "badge_class": "value value--base portrait:value--xsmall lg:value--base lg:portrait:value--small bg--black text--white rounded--xsmall px--1",
                     "foot_class": "value value--base portrait:value--small lg:value--base lg:portrait:value--base", "max_name_chars": 99},
    "half_vertical.liquid": {"col_class": "value value--xsmall portrait:label--small lg:value--base lg:portrait:value--small", "col_badge_class": "label label--inverted portrait:label--small lg:label--large lg:portrait:label--base",
                     "cell_class": "value value--small portrait:label--small lg:value--base lg:portrait:value--small",
                              "badge_class": "value value--xsmall portrait:label--small lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                              "foot_class": "value value--xsmall portrait:label--small lg:value--small lg:portrait:value--xsmall", "max_name_chars": 13},
    "half_horizontal.liquid": {"col_class": "value value--small lg:value--base lg:portrait:value--small", "col_badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                     "cell_class": "value value--small lg:value--base lg:portrait:value--small",
                              "badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                              "foot_class": "value value--small lg:value--base lg:portrait:value--small", "max_name_chars": 13},
    "quadrant.liquid": {"col_class": "label label--small lg:label--base lg:portrait:label--small", "col_badge_class": "label label--small label--inverted lg:label--base lg:portrait:label--small",
                     "cell_class": "label portrait:label--small lg:label--large lg:portrait:label--base",
                         "badge_class": "label label--inverted portrait:label--small lg:label--large lg:portrait:label--base",
                         "foot_class": "label portrait:label--small lg:label--large lg:portrait:label--base", "max_name_chars": 13},
}

def badges(out, cfg):
    """Count status badges: one per disrupted line per rendered block, whatever class builds them."""
    classes = {cfg["badge_class"], cfg["col_badge_class"]}
    return sum(out.count(f'class="{c}"') for c in classes)

def render(layout, data, show_disruptions="true"):
    """show_disruptions defaults on so reason rendering is checked; the box is off by default in settings.yml.
    TRMNL exposes custom field values only under trmnl.plugin_settings.custom_fields_values (confirmed in the editor
    on September 7, 2026: a top-level show_disruptions never rendered a reason), as "true"/"false" strings."""
    values = {} if show_disruptions is None else {"show_disruptions": show_disruptions}
    trmnl = {"plugin_settings": {"custom_fields_values": values}}
    return env.from_string(head + open(os.path.join(here, layout)).read()).render(trmnl=trmnl, **data)

def assert_lg_cell(out, layout, cfg, ctx):
    lg_tokens = [t for t in cfg["cell_class"].split() if t.startswith("lg:")]
    assert lg_tokens, f"{layout}: cell_class has no lg: variant"
    for t in lg_tokens:
        assert t in out, f"{layout}: {t} missing from render ({ctx})"

def assert_stretch_y(out, layout, ctx):
    assert out.count('class="grow w--full"') == 1, f"{layout}: grow w--full wrapper must appear exactly once ({ctx})"
    assert out.index('class="grow w--full"') < out.index("Good service on all other lines"), \
        f"{layout}: grow w--full wrapper must come before the footer text ({ctx})"

def short_name(name):
    return {"Hammersmith & City": "H&C", "Waterloo & City": "W&C",
            "Elizabeth line": "Elizabeth", "Metropolitan": "Met"}.get(name, name).replace("&", "&amp;")

def disrupted_names(data):
    return [line["name"] for line in data["data"]
            if any(status["statusSeverity"] not in (10, 18, 20) for status in line["lineStatuses"])]

def row_names(rows):
    return [re.search(r"<td[^>]*>\s*<span[^>]*>(.*?)</span>", row, re.S).group(1).strip() for row in rows]

def assert_board(out, layout, cfg, data, ctx, reasons=True):
    names = disrupted_names(data)
    assert out.count('<div data-board="table">') == 1, f"{layout}: exactly one table board ({ctx})"
    assert out.count('<div class="hidden" data-board="columns">') == 1, \
        f"{layout}: exactly one initially hidden columns board ({ctx})"
    assert len(re.findall(r'<div class="hidden" data-board="columns">\s*<div class="columns">', out)) == 1, \
        f"{layout}: columns block must be directly inside its hidden wrapper ({ctx})"
    table_start = out.index('<div data-board="table">')
    columns_start = out.index('<div class="hidden" data-board="columns">')
    foot_start = out.index('data-board="foot"')
    table_body = re.search(r"<tbody>(.*?)</tbody>", out[table_start:columns_start], re.S).group(1)
    table_rows = re.findall(r"<tr>.*?</tr>", table_body, re.S)
    assert len(table_rows) == len(names), f"{layout}: table row count ({ctx})"
    expected_table_names = [short_name(name) if len(name) > cfg["max_name_chars"] else name.replace("&", "&amp;") for name in names]
    assert row_names(table_rows) == expected_table_names, f"{layout}: table row order/names ({ctx})"
    for row in table_rows:
        reason_spans = re.findall(r'<span\b[^>]*\bdata-board="reason"[^>]*>', row)
        assert len(reason_spans) == reasons, f"{layout}: one reason span per table row iff enabled ({ctx})"
        if reasons:
            assert 'class="label lg:label--xxlarge lg:portrait:label--large block"' in reason_spans[0], \
                f"{layout}: reason span class ({ctx})"
            assert reason_spans[0].count('data-clamp="1"') == 1, \
                f"{layout}: reason span must carry one-line clamp ({ctx})"
        else:
            assert 'data-clamp="1"' not in row, f"{layout}: disabled row must not carry a clamp ({ctx})"

    columns = out[columns_start:foot_start]
    bodies = re.findall(r"<tbody>(.*?)</tbody>", columns, re.S)
    assert len(bodies) == 2, f"{layout}: hidden columns must contain two tables ({ctx})"
    column_names = [row_names(re.findall(r"<tr>.*?</tr>", body, re.S)) for body in bodies]
    half = (len(names) + 1) // 2
    expected = [list(map(short_name, names[:half])), list(map(short_name, names[half:]))]
    assert column_names == expected, f"{layout}: columns must split column-major in source order ({ctx})"

    scripts = re.findall(r"<script>(.*?)</script>", out, re.S)
    assert len(scripts) == 1, f"{layout}: exactly one inline script ({ctx})"
    for selector in ("foot", "reason", "table", "columns"):
        assert f"[data-board={selector}]" in scripts[0], f"{layout}: script missing data-board={selector} ({ctx})"
    assert "document.currentScript" in scripts[0], f"{layout}: script must scope itself from document.currentScript ({ctx})"

def assert_toggles(layout, cfg, data, ctx):
    for value in ("true", True):
        assert_board(render(layout, data, value), layout, cfg, data, f"{ctx} show_disruptions={value!r}")
    for value in (None, "false", False):
        out = render(layout, data, value)
        assert_board(out, layout, cfg, data, f"{ctx} show_disruptions={value!r}", reasons=False)
        assert "data-clamp" not in out, f"{layout}: reason must be absent when show_disruptions={value!r} ({ctx})"

good = lambda id_, name: {"id": id_, "name": name, "modeName": "tube",
                          "lineStatuses": [{"statusSeverity": 10, "statusSeverityDescription": "Good Service"}]}
ALL_GOOD = {"data": [good("bakerloo", "Bakerloo"), good("central", "Central")]}
DISRUPTED = {"data": [
    {"id": "hammersmith-city", "name": "Hammersmith & City", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Hammersmith and City Line: Minor delays due to train cancellations. "}]},
    {"id": "piccadilly", "name": "Piccadilly", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Piccadilly Line: Minor delays between Acton Town and Heathrow: allow extra time. "},
        {"statusSeverity": 6, "statusSeverityDescription": "Severe Delays",
         "reason": "Piccadilly Line: Severe delays between Acton Town and Uxbridge due to a signal failure at Rayners Lane: expect disruption until end of service. "}]},
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
# Rank order beats both numeric order and TfL's listed order: 9 (Minor Delays) listed first,
# 11 (Part Closed) listed second; 11 ranks worse in severity_rank, so it must win the row.
RANK_ORDER = {"data": [
    {"id": "northern", "name": "Northern", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Northern Line: Minor delays due to a signal failure. "},
        {"statusSeverity": 11, "statusSeverityDescription": "Part Closed",
         "reason": "Northern Line: Part closure between Camden Town and Kennington due to planned engineering works. "}]},
    {"id": "elizabeth", "name": "Elizabeth line", "modeName": "elizabeth-line", "lineStatuses": [
        {"statusSeverity": 42, "statusSeverityDescription": "Mystery",
         "reason": "Elizabeth line: Mystery status code for testing the unranked fallback. "}]},
]}
# Nine lines, each with exactly one disrupted status; mixed severities and a prefixed reason each.
# Large enough to exercise an uneven column-major split and all short-name replacements.
MANY = {"data": [
    {"id": "bakerloo", "name": "Bakerloo", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Bakerloo Line: Minor delays due to a broken down train. "}]},
    {"id": "central", "name": "Central", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 6, "statusSeverityDescription": "Severe Delays",
         "reason": "Central Line: Severe delays due to a signal failure. "}]},
    {"id": "circle", "name": "Circle", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 11, "statusSeverityDescription": "Part Closed",
         "reason": "Circle Line: Part closure between Edgware Road and Aldgate. "}]},
    {"id": "district2", "name": "District", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 16, "statusSeverityDescription": "Not Running",
         "reason": "District Line: Reduced service due to staff shortage. "}]},
    {"id": "hammersmith-city2", "name": "Hammersmith & City", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Hammersmith and City Line: Minor delays due to engineering works. "}]},
    {"id": "jubilee", "name": "Jubilee", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 6, "statusSeverityDescription": "Severe Delays",
         "reason": "Jubilee Line: Severe delays due to a person ill on a train. "}]},
    {"id": "waterloo-city2", "name": "Waterloo & City", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 11, "statusSeverityDescription": "Part Closed",
         "reason": "Waterloo and City Line: Part closure for planned engineering works. "}]},
    {"id": "victoria2", "name": "Victoria", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 16, "statusSeverityDescription": "Not Running",
         "reason": "Victoria Line: Reduced service due to a technical issue. "}]},
    {"id": "metropolitan", "name": "Metropolitan", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Metropolitan Line: Minor delays due to a fire alert. "}]},
]}
# Five lines, each with exactly one disrupted status and a prefixed reason; exercises an uneven split.
FIVE = {"data": [
    {"id": "bakerloo", "name": "Bakerloo", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 9, "statusSeverityDescription": "Minor Delays",
         "reason": "Bakerloo Line: Minor delays due to a broken down train. "}]},
    {"id": "central", "name": "Central", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 6, "statusSeverityDescription": "Severe Delays",
         "reason": "Central Line: Severe delays due to a signal failure. "}]},
    {"id": "circle", "name": "Circle", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 11, "statusSeverityDescription": "Part Closed",
         "reason": "Circle Line: Part closure between Edgware Road and Aldgate. "}]},
    {"id": "district2", "name": "District", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 16, "statusSeverityDescription": "Not Running",
         "reason": "District Line: Reduced service due to staff shortage. "}]},
    {"id": "jubilee", "name": "Jubilee", "modeName": "tube", "lineStatuses": [
        {"statusSeverity": 6, "statusSeverityDescription": "Severe Delays",
         "reason": "Jubilee Line: Severe delays due to a person ill on a train. "}]},
]}
ERROR = {"$type": "Tfl.Api.Presentation.Entities.ApiError, Tfl.Api.Presentation.Entities",
         "timestampUtc": "2026-09-04T16:00:00Z", "exceptionType": "ApiArgumentException",
         "httpStatusCode": "BadRequest", "httpStatus": "BadRequest",
         "relativeUri": "/Line/Mode/notamode/Status",
         "message": "The following mode is not recognised: notamode"}

STATIC = {"three": lambda: DISRUPTED["data"],
          "five": lambda: FIVE["data"] + [good("northern", "Northern")],
          "nine": lambda: MANY["data"] + [good("northern", "Northern")]}
if sys.argv[1:2] == ["dump"]:
    print(json.dumps({"data": STATIC[sys.argv[2]]()}, separators=(",", ":")))
    sys.exit(0)

for layout in LAYOUTS:
    cfg = LAYOUT_CFG[layout]
    badge_lg = [t for t in cfg["badge_class"].split() if t.startswith("lg:")][0]

    out = render(layout, ALL_GOOD)
    assert "Good service on all lines" in out, f"{layout}: all-good text"
    assert "other lines" not in out and "<table" not in out, f"{layout}: all-good must not render a table"
    assert "value--large" in out and "flex--center-x" in out, f"{layout}: all-good text large and centred"
    assert "lg:value--xlarge" in out, f"{layout}: all-good headline must carry lg:value--xlarge"
    assert "lg:value--base" not in out and "lg:label--large" not in out, \
        f"{layout}: all-good render must not carry cell_class's lg: tokens"

    # DISRUPTED: severity 20/18/10 are not disruptions, and Piccadilly's two
    # disrupted entries collapse to one row showing the worse Severe Delays.
    out = render(layout, DISRUPTED)
    assert_board(out, layout, cfg, DISRUPTED, "DISRUPTED")
    for s in ["Piccadilly", "District", "Part Closed", "Severe Delays",
              "Good service on all other lines", "<th"]:
        assert s in out, f"{layout}: missing {s!r}"
    for s in ["Service Closed", "Victoria", "Good service on all lines", "No Issues", "Waterloo"]:
        assert s not in out, f"{layout}: must not show {s!r}"
    assert out.count("Minor Delays") == 2, \
        f"{layout}: only Hammersmith & City shows Minor Delays in the table and columns"
    assert badges(out, cfg) == 6, f"{layout}: one status badge per disrupted line in each board"
    assert "data-table-limit" not in out and "Reason" not in out, f"{layout}: no limiter or Reason header"
    assert f'<span class="{cfg["foot_class"]} px--1" data-board="foot">Good service on all other lines</span>' in out, \
        f"{layout}: footer text must use foot_class"
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (DISRUPTED)"
    assert_lg_cell(out, layout, cfg, "DISRUPTED")
    assert_stretch_y(out, layout, "DISRUPTED")
    assert f'class="{cfg["cell_class"]}"' in out, f"{layout}: table rows use cell_class"
    assert f'class="{cfg["badge_class"]}"' in out, f"{layout}: table rows use badge_class"
    assert f'class="{cfg["col_class"]}"' in out, f"{layout}: compact rows use col_class"
    assert f'class="{cfg["col_badge_class"]}"' in out, f"{layout}: compact rows use col_badge_class"
    assert "Minor delays due to train cancellations" in out, f"{layout}: reason text"
    assert "cancellations. <" not in out, f"{layout}: reason trailing space stripped"
    assert "&lt;rail replacement&gt;" in out, f"{layout}: reason escaped"
    for prefix in ["Hammersmith and City Line: ", "Piccadilly Line: ", "District Line: "]:
        assert prefix not in out, f"{layout}: line-name prefix {prefix!r} must be stripped from reason"
    assert "signal failure at Rayners Lane: expect disruption" in out, \
        f"{layout}: remainder including its own inner ': ' must survive"
    assert "Minor delays between Acton Town and Heathrow" not in out, \
        f"{layout}: Piccadilly's non-chosen Minor Delays reason must not appear"

    # Missing, string false and boolean False hide reasons; string true and
    # boolean True show one clamped reason in every table row.
    assert_toggles(layout, cfg, DISRUPTED, "DISRUPTED")

    # Rank order beats numeric/listed order; an unranked disruption still renders.
    out = render(layout, RANK_ORDER)
    assert_board(out, layout, cfg, RANK_ORDER, "RANK_ORDER")
    assert badges(out, cfg) == 4, f"{layout}: one status badge per disrupted line in each board (RANK_ORDER)"
    assert out.count("Part Closed") == 2 and out.count("Mystery") >= 2, f"{layout}: RANK_ORDER labels missing"
    assert "Minor Delays" not in out, f"{layout}: Northern's earlier numeric-lower status must not win"
    assert "planned engineering works" in out and "signal failure" not in out, \
        f"{layout}: only Northern's chosen Part Closed reason must show"
    assert_lg_cell(out, layout, cfg, "RANK_ORDER")
    assert_stretch_y(out, layout, "RANK_ORDER")
    assert_toggles(layout, cfg, RANK_ORDER, "RANK_ORDER")

    out = render(layout, MANY)
    assert_board(out, layout, cfg, MANY, "MANY")
    assert out.count("<table") == 3 and out.count("<thead") == 1, \
        f"{layout}: MANY renders one table and two initially hidden column tables"
    assert badges(out, cfg) == 18, f"{layout}: MANY renders each status in the table and columns"
    assert f'<span class="{cfg["col_class"]}">H&amp;C' in out, f"{layout}: MANY compact rows use short names"
    assert f'<span class="{cfg["col_badge_class"]}">' in out, f"{layout}: MANY compact rows use col_badge_class"
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (MANY)"
    assert_lg_cell(out, layout, cfg, "MANY")
    assert_stretch_y(out, layout, "MANY")
    assert_toggles(layout, cfg, MANY, "MANY")

    out = render(layout, FIVE)
    assert_board(out, layout, cfg, FIVE, "FIVE")
    assert badges(out, cfg) == 10, f"{layout}: FIVE renders each status in the table and columns"
    assert out.count('data-board="reason"') == 5, f"{layout}: FIVE shows five one-line table reasons"
    assert "broken down train" in out, f"{layout}: FIVE reason text"
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (FIVE)"
    assert_lg_cell(out, layout, cfg, "FIVE")
    assert_stretch_y(out, layout, "FIVE")
    assert_toggles(layout, cfg, FIVE, "FIVE")

    out = render(layout, ERROR)
    assert "Could not fetch TfL status" in out and "notamode" in out and "<table" not in out, f"{layout}: 400 body"

    out = render(layout, {})
    assert "Could not fetch TfL status" in out and "<table" not in out, f"{layout}: empty payload"
    assert "TfL Line Status" in out and 'style="' not in out, f"{layout}: title bar present, no inline styles"
    assert "<style" not in out, f"{layout}: shared head must carry no <style> block"
    assert "data:image/svg+xml;base64," in out, f"{layout}: roundel must be an embedded base64 data URI"

print("ok")
