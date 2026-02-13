# TRMNL plugins

Recipe plugins for [TRMNL](https://usetrmnl.com) e-ink displays.

## TfL Bus Stops

Live bus arrival times from Transport for London. Polls the TfL API every 5 minutes and shows the next buses at your stop, sorted by arrival time.

![a screen shot showing bus arrivals](docs/bus-times.png)

Works across all four TRMNL layout sizes (full, half horizontal, half vertical, quadrant).

### Setup

1. In the TRMNL recipe editor, create a new recipe using the files in `tfl_bus_times/`
2. Set the `stoppoint` custom field to your TfL StopPoint ID
3. To find your StopPoint ID: search for your bus stop on the [TfL website](https://tfl.gov.uk) and grab the code from the URL

### Files

```
tfl_bus_times/
  settings.yml          # API config and custom fields
  shared.liquid         # Sorts buses by arrival time
  full.liquid           # Full-screen layout
  half_horizontal.liquid
  half_vertical.liquid
  quadrant.liquid
```

### Data source

Uses the [TfL Unified API](https://api.tfl.gov.uk/) (free, no key required). Not affiliated with TfL.

## Framework cheat sheet

`TRMNL_FRAMEWORK_CHEAT_SHEET.md` is a complete reference of every CSS class in the TRMNL framework v2. Useful if you're building your own plugins or if you're an AI agent helping someone build one. Compiled from the [official docs](https://trmnl.com/framework/docs).
