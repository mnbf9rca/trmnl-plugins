"""Render check: python3 simple_tube_status/check.py (needs python-liquid). Fails if the board logic breaks."""
import os, re
from liquid import Environment, DictLoader

here = os.path.dirname(os.path.abspath(__file__))
shared = open(os.path.join(here, "shared.liquid")).read()
m = re.search(r"{% template board %}(.*?){% endtemplate %}", shared, re.S)
head = shared[: m.start()]
env = Environment(loader=DictLoader({"board": m.group(1)}))
LAYOUTS = ["full.liquid", "half_horizontal.liquid", "half_vertical.liquid", "quadrant.liquid"]
LAYOUT_CFG = {
    "full.liquid": {"cell_class": "value value--small", "max_with_reason": 5, "max_rows": 10},
    "half_vertical.liquid": {"cell_class": "value value--xsmall", "max_with_reason": 6, "max_rows": 12},
    "half_horizontal.liquid": {"cell_class": "value value--xsmall", "max_with_reason": 2, "max_rows": 4},
    "quadrant.liquid": {"cell_class": "label", "max_with_reason": 0, "max_rows": 6},
}

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
# Eight lines, each with exactly one disrupted status; mixed severities and a prefixed reason each.
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
]}
ERROR = {"$type": "Tfl.Api.Presentation.Entities.ApiError, Tfl.Api.Presentation.Entities",
         "timestampUtc": "2026-09-04T16:00:00Z", "exceptionType": "ApiArgumentException",
         "httpStatusCode": "BadRequest", "httpStatus": "BadRequest",
         "relativeUri": "/Line/Mode/notamode/Status",
         "message": "The following mode is not recognised: notamode"}

for layout in LAYOUTS:
    cfg = LAYOUT_CFG[layout]
    cell_class = cfg["cell_class"]

    out = render(layout, ALL_GOOD)
    assert "Good service on all lines" in out, f"{layout}: all-good text"
    assert "other lines" not in out and "<table" not in out, f"{layout}: all-good must not render a table"
    assert "value--large" in out and "flex--center-x" in out, f"{layout}: all-good text large and centred"

    # DISRUPTED: 3 disrupted lines (Piccadilly's two entries collapse to one row, its worst),
    # table mode on every layout (3 <= every layout's max_rows).
    out = render(layout, DISRUPTED)
    for s in ["Hammersmith &amp; City", "Piccadilly", "District", "Part Closed", "Severe Delays",
              "Good service on all other lines", "<th"]:
        assert s in out, f"{layout}: missing {s!r}"
    for s in ["Service Closed", "Victoria", "Good service on all lines", "No Issues", "Waterloo"]:
        assert s not in out, f"{layout}: must not show {s!r}"
    assert out.count("Minor Delays") == 1, \
        f"{layout}: only Hammersmith & City shows Minor Delays; Piccadilly must show its worse Severe Delays instead"
    assert out.count("label--inverted") == 3, f"{layout}: one inverted status per disrupted line, not per entry"
    assert 'class="board"' in out and 'data-table-limit="true"' in out, f"{layout}: board wrapper and row limiter"
    assert "Reason" not in out, f"{layout}: no Reason header anywhere"
    assert f'<span class="{cell_class} px--1">Good service on all other lines</span>' in out, \
        f"{layout}: footer text must use cell_class {cell_class!r}"
    if layout == "full.liquid":
        assert "value value--small" in out, f"{layout}: full uses small text"
    elif layout in ("half_horizontal.liquid", "half_vertical.liquid"):
        assert "value--xsmall" in out, f"{layout}: half uses xsmall text"

    if 3 <= cfg["max_with_reason"]:
        assert "Minor delays due to train cancellations" in out, f"{layout}: reason text"
        assert 'data-clamp="2"' in out, f"{layout}: reason clamped"
        assert "cancellations. <" not in out, f"{layout}: reason trailing space stripped"
        assert "&lt;rail replacement&gt;" in out, f"{layout}: reason escaped"
        for prefix in ["Hammersmith and City Line: ", "Piccadilly Line: ", "District Line: "]:
            assert prefix not in out, f"{layout}: line-name prefix {prefix!r} must be stripped from reason"
        assert "signal failure at Rayners Lane: expect disruption" in out, \
            f"{layout}: remainder including its own inner ': ' must survive"
        assert "Minor delays between Acton Town and Heathrow" not in out, \
            f"{layout}: Piccadilly's non-chosen Minor Delays reason must not appear"
    else:
        assert "Minor delays due to train cancellations" not in out, f"{layout}: reason text must be hidden"
        assert 'data-clamp="2"' not in out, f"{layout}: no reason column, no clamp"

    # RANK_ORDER: rank beats both numeric order (9 < 11) and TfL's listed order (9 listed first).
    out = render(layout, RANK_ORDER)
    assert out.count("label--inverted") == 2, f"{layout}: one inverted status per disrupted line (RANK_ORDER)"
    assert "Part Closed" in out and "Mystery" in out, f"{layout}: RANK_ORDER labels missing"
    assert "Minor Delays" not in out, \
        f"{layout}: Northern's non-chosen Minor Delays must not win over Part Closed"
    if 2 <= cfg["max_with_reason"]:
        assert "planned engineering works" in out, f"{layout}: Northern's chosen Part Closed reason must show"
        assert "signal failure" not in out, \
            f"{layout}: Northern's non-chosen Minor Delays reason must not show"

    # MANY: 8 disrupted entries, one per line.
    out = render(layout, MANY)
    assert "Reason" not in out, f"{layout}: no Reason header anywhere (MANY)"
    assert out.count("label--inverted") == 8, f"{layout}: one inverted status per MANY line"
    assert f'<span class="{cell_class} px--1">Good service on all other lines</span>' in out, \
        f"{layout}: footer text must use cell_class {cell_class!r} (MANY)"
    if 8 <= cfg["max_rows"]:
        assert "<table" in out, f"{layout}: MANY still fits a table"
        assert "flex--wrap" not in out, f"{layout}: MANY table mode must not be compact"
        assert "Hammersmith &amp; City" in out and "Waterloo &amp; City" in out, \
            f"{layout}: MANY table mode shows full line names"
        assert "H&amp;C" not in out and "W&amp;C" not in out, f"{layout}: MANY table mode must not shorten names"
        assert "engineering works" not in out, f"{layout}: MANY table mode hides reason text (over max_with_reason)"
    else:
        assert "flex--wrap" in out, f"{layout}: MANY compact mode wraps"
        assert "<table" not in out, f"{layout}: MANY compact mode has no table"
        assert "H&amp;C" in out and "W&amp;C" in out, f"{layout}: MANY compact mode shortens H&C/W&C names"

    out = render(layout, ERROR)
    assert "Could not fetch TfL status" in out and "notamode" in out and "<table" not in out, f"{layout}: 400 body"

    out = render(layout, {})
    assert "Could not fetch TfL status" in out and "<table" not in out, f"{layout}: empty payload"
    assert "TfL Line Status" in out and 'style="' not in out, f"{layout}: title bar present, no inline styles"
    assert "data:image/svg+xml;base64," in out, f"{layout}: roundel must be an embedded base64 data URI"

print("ok")
