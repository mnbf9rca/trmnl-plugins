"""Render check: python3 check.py (needs python-liquid). Fails if the board logic breaks."""
import re, sys
from liquid import Environment, DictLoader

shared = open("shared.liquid").read()
m = re.search(r"{% template board %}(.*?){% endtemplate %}", shared, re.S)
head = shared[: m.start()]
env = Environment(loader=DictLoader({"board": m.group(1)}))

svc = lambda std, etd, dest, plat="4", cancelled=False, via=None: {
    "std": std, "etd": etd, "platform": plat, "isCancelled": cancelled,
    "destination": [{"locationName": dest, "crs": "XXX", "via": via}],
}
payload = {
    "locationName": "Wimbledon",
    "trainServices": [svc("10:32", "On time", "London Waterloo"),
                      svc("10:41", "10:47", "London Waterloo", via="via Clapham Junction"),
                      svc("10:50", "Cancelled", "London Waterloo", plat=None, cancelled=True)],
    "nrccMessages": [{"Value": "<p>Delays between <a href='#'>Wimbledon</a> and Waterloo.</p>"}],
}

def render(layout, data):
    return env.from_string(head + open(layout).read()).render(**data)

out = render("full.liquid", payload)
for s in ["Wimbledon", "10:32", "On time", "Exp 10:47", "via Clapham Junction", "Cancelled", ">-<",
          "Delays between Wimbledon and Waterloo.", "<th"]:
    assert s in out, f"missing {s!r}"
assert "<a href" not in out, "html not stripped"
assert "lg:value--large" in out and "lg:portrait:value--base" in out, "TRMNL X sizing"
assert out.count("label--inverted") == 2, "only late/cancelled get inverted"
assert 'class="instance"' in out and "data:image/svg+xml;base64," in out, "documented title bar with embedded icon"
assert "icons8" not in out and "gap--distribute" not in out, "no external icon, no nested title bar"

assert "Plat" not in render("quadrant.liquid", payload), "quadrant must hide platform"
assert " via London" not in out, "no filter, no via in title"
assert "Wimbledon via London Waterloo" in render("full.liquid", dict(payload, filterLocationName="London Waterloo")), "filtered title"
assert "10:32" in render("full.liquid", {"data": payload}), "wrapped payload"

empty = dict(payload, trainServices=[])
out = render("half_vertical.liquid", empty)
assert "<table" not in out and "Delays between" in out
out = render("half_horizontal.liquid", dict(empty, nrccMessages=[]))
assert "No departures in the next 2 hours" in out
out = render("full.liquid", {})
assert "Could not fetch departures" in out and "<table" not in out, "failed poll"
assert "Train departures" in out, "empty-state title"
assert "Check the API key" in out, "generic error without api body"
assert "Invalid ApiKey" in render("full.liquid", {"fault": {"faultstring": "Invalid ApiKey"}}), "401 fault text"
assert "Invalid crs code supplied" in render("full.liquid", {"Message": "Invalid crs code supplied"}), "400 message text"
assert 'style="' not in out, "no inline styles"
print("ok")
