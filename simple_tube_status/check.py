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
    "full.liquid": {"col_class": "value value--small lg:value--base lg:portrait:value--small", "col_badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                     "cell_class": "value value--base lg:value--large lg:portrait:value--base",
                     "badge_class": "value value--base lg:value--base lg:portrait:value--small bg--black text--white rounded--xsmall px--1",
                     "foot_class": "value value--base lg:value--base lg:portrait:value--base",
                     "max_with_reason": 5, "max_rows": 7, "max_with_reason_lg": 6, "max_rows_lg": 9, "max_name_chars": 99},
    "half_vertical.liquid": {"col_class": "value value--xsmall lg:value--base lg:portrait:value--small", "col_badge_class": "label label--inverted lg:label--large lg:portrait:label--base",
                     "cell_class": "value value--small lg:value--base lg:portrait:value--small",
                              "badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                              "foot_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall",
                              "max_with_reason": 6, "max_rows": 11, "max_with_reason_lg": 6, "max_rows_lg": 11, "max_name_chars": 13},
    "half_horizontal.liquid": {"col_class": "value value--small lg:value--base lg:portrait:value--small", "col_badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                     "cell_class": "value value--small lg:value--base lg:portrait:value--small",
                              "badge_class": "value value--xsmall lg:value--small lg:portrait:value--xsmall bg--black text--white rounded--xsmall px--1",
                              "foot_class": "value value--small lg:value--base lg:portrait:value--small",
                                "max_with_reason": 2, "max_rows": 3, "max_with_reason_lg": 3, "max_rows_lg": 6, "max_name_chars": 13},
    "quadrant.liquid": {"col_class": "label lg:label--large lg:portrait:label--base", "col_badge_class": "label label--inverted lg:label--large lg:portrait:label--base",
                     "cell_class": "label lg:label--large lg:portrait:label--base",
                         "badge_class": "label label--inverted lg:label--large lg:portrait:label--base",
                         "foot_class": "label lg:label--large lg:portrait:label--base",
                         "max_with_reason": 0, "max_rows": 6, "max_with_reason_lg": 2, "max_rows_lg": 7, "max_name_chars": 99},
}

def badges(out, cfg):
    """Count status badges: one per disrupted line per rendered block, whatever class builds them."""
    classes = {cfg["badge_class"], cfg["col_badge_class"]}
    return sum(out.count(f'class="{c}"') for c in classes)

def render(layout, data, show_disruptions="true"):
    """show_disruptions defaults on so the reason-cap checks below still bite; the box is off by default in settings.yml.
    TRMNL exposes custom field values only under trmnl.plugin_settings.custom_fields_values (confirmed in the editor
    on September 7, 2026: a top-level show_disruptions never rendered a reason), as "true"/"false" strings."""
    trmnl = {"plugin_settings": {"custom_fields_values": {"show_disruptions": show_disruptions}}}
    return env.from_string(head + open(os.path.join(here, layout)).read()).render(trmnl=trmnl, **data)

def reason_state(n, cfg):
    """Where n falls relative to the reason-line caps."""
    if n <= cfg["max_with_reason"]:
        return "block"
    elif n <= cfg["max_with_reason_lg"]:
        return "hidden"
    return "absent"

def table_state(n, cfg):
    """Where n falls relative to the table/two-column caps."""
    if n <= cfg["max_rows"]:
        return "table_only"
    elif n <= cfg["max_rows_lg"]:
        return "both"
    return "compact_only"

def assert_lg_cell(out, layout, cfg, ctx):
    lg_tokens = [t for t in cfg["cell_class"].split() if t.startswith("lg:")]
    assert lg_tokens, f"{layout}: cell_class has no lg: variant"
    for t in lg_tokens:
        assert t in out, f"{layout}: {t} missing from render ({ctx})"

def assert_reason_class(out, layout, state, ctx):
    if state == "block":
        assert 'class="label lg:label--xxlarge lg:portrait:label--large block"' in out, \
            f"{layout}: reason must render with block class ({ctx})"
    elif state == "hidden":
        assert 'class="label lg:label--xxlarge lg:portrait:label--large hidden lg:visible"' in out, \
            f"{layout}: reason must render with hidden lg:visible class ({ctx})"

def assert_stretch_y(out, layout, ctx):
    assert out.count('class="grow w--full"') == 1, f"{layout}: grow w--full wrapper must appear exactly once ({ctx})"
    assert out.index('class="grow w--full"') < out.index("Good service on all other lines"), \
        f"{layout}: grow w--full wrapper must come before the footer text ({ctx})"

def assert_table_state(out, layout, state, ctx):
    assert "data-table-limit" not in out, f"{layout}: row limiter must be absent ({ctx})"
    if state == "table_only":
        assert "<table" in out, f"{layout}: table expected ({ctx})"
        assert '<div class="columns">' not in out, f"{layout}: no columns block expected ({ctx})"
    elif state == "both":
        assert out.count('<div class="columns">') == 1, f"{layout}: exactly one columns block expected ({ctx})"
        assert re.search(r'class="hidden lg:visible">\s*<table', out), \
            f"{layout}: table must be wrapped in class=\"hidden lg:visible\" ({ctx})"
        assert re.search(r'class="lg:hidden">\s*<div class="columns">', out), \
            f"{layout}: columns block must be wrapped in class=\"lg:hidden\" ({ctx})"
    else:
        assert '<div class="columns">' in out, f"{layout}: columns block expected ({ctx})"

def compact_tables(out):
    """Split out the two <table> blocks inside the columns block."""
    idx = out.index('<div class="columns">')
    tail = out[idx:]
    first_idx = tail.find("<table")
    second_idx = tail.find("<table", first_idx + 1)
    return tail[first_idx:second_idx], tail[second_idx:]

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
# More than full's max_rows (7), so full must also exercise compact mode, not just quadrant/half_horizontal.
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
# Five lines, each with exactly one disrupted status and a prefixed reason. Sits strictly between
# half_horizontal's max_rows (3) and max_rows_lg (6): exercises the "between the caps" branch that
# ALL_GOOD/DISRUPTED/MANY miss. On full it lands exactly on max_with_reason (5).
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
    cell_class = cfg["cell_class"]
    badge_lg = [t for t in cfg["badge_class"].split() if t.startswith("lg:")][0]

    out = render(layout, ALL_GOOD)
    assert "Good service on all lines" in out, f"{layout}: all-good text"
    assert "other lines" not in out and "<table" not in out, f"{layout}: all-good must not render a table"
    assert "value--large" in out and "flex--center-x" in out, f"{layout}: all-good text large and centred"
    assert "lg:value--xlarge" in out, f"{layout}: all-good headline must carry lg:value--xlarge"
    assert "lg:value--base" not in out and "lg:label--large" not in out, \
        f"{layout}: all-good render must not carry cell_class's lg: tokens"

    # DISRUPTED: 3 disrupted lines (Piccadilly's two entries collapse to one row, its worst).
    # Table mode everywhere except half_horizontal, whose max_rows of 2 puts it in "both" mode
    # (every line rendered twice: hidden table for the X, columns for the original device).
    out = render(layout, DISRUPTED)
    mult = 2 if table_state(3, cfg) == "both" else 1
    long_ok = cfg["max_name_chars"] >= 18
    hc = "Hammersmith &amp; City" if long_ok else "H&amp;C"
    assert ("Hammersmith &amp; City" in out) == long_ok, f"{layout}: long name only within the character budget"
    for s in [hc, "Piccadilly", "District", "Part Closed", "Severe Delays",
              "Good service on all other lines", "<th"]:
        assert s in out, f"{layout}: missing {s!r}"
    for s in ["Service Closed", "Victoria", "Good service on all lines", "No Issues", "Waterloo"]:
        assert s not in out, f"{layout}: must not show {s!r}"
    assert out.count("Minor Delays") == mult, \
        f"{layout}: only Hammersmith & City shows Minor Delays; Piccadilly must show its worse Severe Delays instead"
    assert badges(out, cfg) == 3 * mult, f"{layout}: one status badge per disrupted line, not per entry"
    assert "data-table-limit" not in out, f"{layout}: no row limiter"
    if mult == 1:
        assert 'class="hidden lg:visible"' not in out, f"{layout}: table_only render must have no wrapper"
    assert "Reason" not in out, f"{layout}: no Reason header anywhere"
    assert f'<span class="{cfg["foot_class"]} px--1">Good service on all other lines</span>' in out, \
        f"{layout}: footer text must use foot_class"
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (DISRUPTED)"
    assert_lg_cell(out, layout, cfg, "DISRUPTED")
    assert_table_state(out, layout, table_state(3, cfg), "DISRUPTED n=3")
    assert_stretch_y(out, layout, "DISRUPTED n=3")
    if layout == "full.liquid":
        assert "value value--base" in out and "value value--small" not in out, f"{layout}: full uses base text"
        assert f'class="{cfg["badge_class"]}"' in out, f"{layout}: badge uses the utility-built value--base badge"
    elif layout == "half_vertical.liquid":
        assert "value value--small" in out and f'class="{cfg["badge_class"]}"' in out, f"{layout}: half vertical uses small text and the utility badge"
    elif layout == "half_horizontal.liquid":
        assert "value value--small" in out and f'class="{cfg["badge_class"]}"' in out, f"{layout}: half horizontal uses small text and the utility badge"
    else:
        assert "label--xxlarge" not in out and 'class="label label--inverted' in out, f"{layout}: quadrant keeps the base badge"

    state = reason_state(3, cfg)
    if state in ("block", "hidden"):
        assert "Minor delays due to train cancellations" in out, f"{layout}: reason text"
        assert 'data-clamp="1"' in out, f"{layout}: reason clamped"
        assert "cancellations. <" not in out, f"{layout}: reason trailing space stripped"
        assert "&lt;rail replacement&gt;" in out, f"{layout}: reason escaped"
        for prefix in ["Hammersmith and City Line: ", "Piccadilly Line: ", "District Line: "]:
            assert prefix not in out, f"{layout}: line-name prefix {prefix!r} must be stripped from reason"
        assert "signal failure at Rayners Lane: expect disruption" in out, \
            f"{layout}: remainder including its own inner ': ' must survive"
        assert "Minor delays between Acton Town and Heathrow" not in out, \
            f"{layout}: Piccadilly's non-chosen Minor Delays reason must not appear"
        assert_reason_class(out, layout, state, "DISRUPTED n=3")
    else:
        assert "Minor delays due to train cancellations" not in out, f"{layout}: reason text must be hidden"
        assert 'data-clamp="1"' not in out, f"{layout}: no reason column, no clamp"

    # RANK_ORDER: rank beats both numeric order (9 < 11) and TfL's listed order (9 listed first).
    # Checkbox off (missing, "false" or False): rows drop the reason line but keep name and status.
    for off in (None, "false", False):
        out = render(layout, DISRUPTED, show_disruptions=off)
        assert "signal failure" not in out and "data-clamp" not in out, f"{layout}: reason must be absent when show_disruptions={off!r}"
        assert "Piccadilly" in out and "Severe Delays" in out, f"{layout}: name and status still render when show_disruptions={off!r}"
    out = render(layout, DISRUPTED, show_disruptions=True)
    assert "data-clamp" in out or cfg["max_with_reason_lg"] < 3, f"{layout}: boolean True must enable the reason line"

    out = render(layout, RANK_ORDER)
    assert badges(out, cfg) == 2, f"{layout}: one status badge per disrupted line (RANK_ORDER)"
    assert "Part Closed" in out and "Mystery" in out, f"{layout}: RANK_ORDER labels missing"
    assert "Minor Delays" not in out, \
        f"{layout}: Northern's non-chosen Minor Delays must not win over Part Closed"
    assert_lg_cell(out, layout, cfg, "RANK_ORDER")
    assert_table_state(out, layout, table_state(2, cfg), "RANK_ORDER n=2")
    assert_stretch_y(out, layout, "RANK_ORDER n=2")
    state = reason_state(2, cfg)
    if state in ("block", "hidden"):
        assert "planned engineering works" in out, f"{layout}: Northern's chosen Part Closed reason must show"
        assert "signal failure" not in out, \
            f"{layout}: Northern's non-chosen Minor Delays reason must not show"
        assert_reason_class(out, layout, state, "RANK_ORDER n=2")

    # MANY: 9 disrupted entries, one per line.
    out = render(layout, MANY)
    assert "Reason" not in out, f"{layout}: no Reason header anywhere (MANY)"
    assert f'<span class="{cfg["foot_class"]} px--1">Good service on all other lines</span>' in out, \
        f"{layout}: footer text must use foot_class (MANY)"
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (MANY)"
    assert_lg_cell(out, layout, cfg, "MANY")
    t_state = table_state(9, cfg)
    assert_table_state(out, layout, t_state, "MANY n=9")
    assert_stretch_y(out, layout, "MANY n=9")
    # "both" mode renders every line twice (once in the table, once in the columns).
    expected_inverted = 18 if t_state == "both" else 9
    assert badges(out, cfg) == expected_inverted, \
        f"{layout}: expected {expected_inverted} inverted statuses for MANY ({t_state})"
    r_state = reason_state(9, cfg)

    if t_state == "table_only":
        assert "flex--wrap" not in out, f"{layout}: MANY table mode must not be compact"
        if long_ok:
            assert "Hammersmith &amp; City" in out and "Waterloo &amp; City" in out and "Metropolitan" in out, \
                f"{layout}: MANY table mode shows full line names"
            assert "H&amp;C" not in out and "W&amp;C" not in out, f"{layout}: MANY table mode must not shorten names"
        else:
            assert "H&amp;C" in out and "W&amp;C" in out and "Metropolitan" in out, \
                f"{layout}: MANY table mode shortens only names over the budget (Metropolitan is 12 chars)"
        if r_state == "absent":
            assert "engineering works" not in out, f"{layout}: MANY table mode hides reason text (over max_with_reason_lg)"
    elif t_state == "compact_only":
        assert out.count("<table") == 2, f"{layout}: MANY compact mode renders exactly two tables"
        assert "<thead" not in out, f"{layout}: MANY compact mode has no table header"
        assert "flex--wrap" not in out, f"{layout}: MANY compact mode must not use the old wrapped-chip layout"
        assert "H&amp;C" in out and "W&amp;C" in out, f"{layout}: MANY compact mode shortens H&C/W&C names"
        assert f'<span class="{cfg["col_class"]}">H&amp;C' in out and f'<span class="{cfg["col_badge_class"]}">' in out, \
            f"{layout}: MANY compact rows use col_class and col_badge_class"
        first_table, second_table = compact_tables(out)
        first_names = ["Bakerloo", "Central", "Circle", "District", "H&amp;C"]
        second_names = ["Jubilee", "W&amp;C", "Victoria", "Met"]
        for name in first_names:
            assert name in first_table, f"{layout}: MANY first column missing {name!r}"
            assert name not in second_table, f"{layout}: MANY second column must not contain {name!r}"
        for name in second_names:
            assert name in second_table, f"{layout}: MANY second column missing {name!r}"
            assert name not in first_table, f"{layout}: MANY first column must not contain {name!r}"
    else:  # both: table and columns render together (X caps give room for the table too)
        assert out.count("<table") == 3, f"{layout}: MANY both mode renders one table plus two column tables"
        if long_ok:
            assert "Hammersmith &amp; City" in out and "Waterloo &amp; City" in out, \
                f"{layout}: MANY both mode table keeps full line names"
        assert "Metropolitan" in out, f"{layout}: MANY both mode table keeps Metropolitan (within budget)"
        assert "H&amp;C" in out and "W&amp;C" in out, f"{layout}: MANY both mode columns shorten H&C/W&C names"
        assert f'<span class="{cfg["col_class"]}">H&amp;C' in out, f"{layout}: MANY both mode columns use col_class"
        if r_state == "absent":
            assert "engineering works" not in out, f"{layout}: MANY both mode hides reason text (over max_with_reason_lg)"
        first_table, second_table = compact_tables(out)
        first_names = ["Bakerloo", "Central", "Circle", "District", "H&amp;C"]
        second_names = ["Jubilee", "W&amp;C", "Victoria", "Met"]
        for name in first_names:
            assert name in first_table, f"{layout}: MANY first column missing {name!r}"
            assert name not in second_table, f"{layout}: MANY second column must not contain {name!r}"
        for name in second_names:
            assert name in second_table, f"{layout}: MANY second column missing {name!r}"
            assert name not in first_table, f"{layout}: MANY first column must not contain {name!r}"

    # FIVE: 5 disrupted entries, exercises the "between the caps" branches.
    out = render(layout, FIVE)
    assert badge_lg in out, f"{layout}: status labels must carry {badge_lg} (FIVE)"
    assert_lg_cell(out, layout, cfg, "FIVE")
    t_state = table_state(5, cfg)
    assert_table_state(out, layout, t_state, "FIVE n=5")
    assert_stretch_y(out, layout, "FIVE n=5")
    expected_inverted = 10 if t_state == "both" else 5
    assert badges(out, cfg) == expected_inverted, \
        f"{layout}: expected {expected_inverted} inverted statuses for FIVE ({t_state})"
    r_state = reason_state(5, cfg)
    if r_state in ("block", "hidden") and t_state in ("table_only", "both"):
        assert "broken down train" in out, f"{layout}: FIVE reason text"
        assert_reason_class(out, layout, r_state, "FIVE n=5")
    elif r_state == "absent":
        assert 'data-clamp="1"' not in out, f"{layout}: FIVE no reason column, no clamp"
    if layout == "full.liquid":
        assert t_state == "table_only" and r_state == "block", \
            "full: FIVE must land exactly on max_with_reason (5) and inside max_rows (7)"
        assert out.count('data-clamp="1"') == 5, "full: FIVE shows five one-line reasons"
    if layout == "half_horizontal.liquid":
        assert t_state == "both", "half_horizontal: FIVE must exercise the between-max_rows branch (3 < 5 <= 6)"

    out = render(layout, ERROR)
    assert "Could not fetch TfL status" in out and "notamode" in out and "<table" not in out, f"{layout}: 400 body"

    out = render(layout, {})
    assert "Could not fetch TfL status" in out and "<table" not in out, f"{layout}: empty payload"
    assert "TfL Line Status" in out and 'style="' not in out, f"{layout}: title bar present, no inline styles"
    assert "<style" not in out, f"{layout}: shared head must carry no <style> block"
    assert "data:image/svg+xml;base64," in out, f"{layout}: roundel must be an embedded base64 data URI"

print("ok")
