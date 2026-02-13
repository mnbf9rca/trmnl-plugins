# TRMNL Framework v2 CSS Reference (Comprehensive Cheat Sheet)

## What is this?

A complete reference of every CSS class, data attribute, and component available in the [TRMNL](https://usetrmnl.com) e-ink display framework (v2). Compiled from the official docs at https://trmnl.com/framework/docs and verified against the actual plugin CSS source.

## Who is this for?

- **Plugin/recipe developers** building TRMNL templates (Liquid/HTML)
- **AI agents** assisting with TRMNL plugin development (this doc is optimised for LLM context)
- **Code reviewers** checking that templates use native framework classes instead of inline styles

## When to use this

- When writing or editing `.liquid` template markup for TRMNL plugins
- When replacing inline `style="..."` attributes with framework utility classes
- When you need the exact class name, pixel value, or responsive variant for a TRMNL component
- When debugging layout issues on e-ink displays (1-bit, 2-bit, 4-bit)

## How to use this

1. **Start with [Key Gotchas](#key-gotchas--warnings)** — common mistakes that waste time
2. **Find the relevant section** via the Table of Contents below
3. **Use the exact class names shown** — the framework does NOT support arbitrary/invented classes
4. **Follow the [Template Structure](#template-structure)** at the bottom for correct plugin scaffolding

> **Important:** The TRMNL markup editor wraps your content in a `view` container automatically. Do NOT add `<div class="view">` yourself. Your top-level element should be `<div class="layout ...">` with a sibling `<div class="title_bar">`.

## Sources

- Official docs: https://trmnl.com/framework/docs
- Plugin CSS: `https://trmnl.com/css/latest/plugins.css` (~7MB, ~219K lines)
- Plugin JS: `https://trmnl.com/js/latest/plugins.js`
- Best practices: https://help.trmnl.com/en/articles/11395668-recipe-best-practices
- Last updated: 2026-02-13

---

## Table of Contents

1. [Key Gotchas & Warnings](#key-gotchas--warnings)
2. [Responsive Prefixes](#responsive-prefixes)
3. [Screen Container](#screen-container)
4. [View](#view)
5. [Layout](#layout)
6. [Flex](#flex)
7. [Grid](#grid)
8. [Columns](#columns)
9. [Mashup](#mashup)
10. [Size (Width & Height)](#size-width--height)
11. [Spacing (Padding & Margin)](#spacing-padding--margin)
12. [Gap](#gap)
13. [Text](#text)
14. [Title](#title)
15. [Value](#value)
16. [Label](#label)
17. [Description](#description)
18. [Title Bar](#title-bar)
19. [Table](#table)
20. [Item](#item)
21. [Divider](#divider)
22. [Border](#border)
23. [Rounded](#rounded)
24. [Outline](#outline)
25. [Background](#background)
26. [Image](#image)
27. [Image Stroke](#image-stroke)
28. [Text Stroke](#text-stroke)
29. [Visibility](#visibility)
30. [Overflow](#overflow)
31. [Clamp](#clamp)
32. [Scale](#scale)
33. [Aspect Ratio](#aspect-ratio)
34. [Progress](#progress)
35. [Rich Text](#rich-text)
36. [Chart](#chart)
37. [Data Attributes (JS Runtime)](#data-attributes-js-runtime)
38. [Upgrade Guide (v1 to v2)](#upgrade-guide-v1-to-v2)
39. [Best Practices](#best-practices)
40. [Template Structure](#template-structure)

---

## Key Gotchas & Warnings

- **NO bracket syntax for spacing**: `p--[2px]`, `pl--[6px]` DO NOT EXIST. Spacing uses a scale: `p--{N}` where value = N * 4px.
- **`gap--distribute`** = actual `space-between`. **`gap--space-between`** = `space-evenly` (misleading name!).
- **`gap--auto`** = `space-evenly`.
- Table cells have `padding: 0` by default -- use explicit spacing utilities like `pl--1`, `pr--1`.
- `title_bar` must be a **sibling** of `layout`, not nested inside it. The platform positions it at the bottom.
- In the markup editor, do NOT wrap content in `view` -- the platform provides that automatically.
- `.view` is already `display: flex; flex-direction: column` -- don't add `flex flex--col` redundantly.
- **Clamping is NOT automatic in v2.** Title, Label, Description are unclamped by default. You must explicitly add `data-clamp="N"` or `clamp--N`.
- **Border classes changed in v2.** Re-evaluate intensity levels if upgrading from v1.
- Arbitrary gap values (`gap--[Npx]`) do NOT support responsive variants.
- Arbitrary rounded values (`rounded--[Npx]`) do NOT support responsive variants.
- Scale utility is only available on 4-bit devices.
- Aspect Ratio is currently in Beta.

---

## Responsive Prefixes

All prefixes follow the pattern: `{prefix}:{class}`. Multiple prefixes chain: `md:portrait:text--center`.

### Size Breakpoints (mobile-first, progressive)

| Prefix | Min Width | Devices |
|--------|-----------|---------|
| `sm:` | 600px | Kindle 2024 |
| `md:` | 800px | TRMNL OG, TRMNL OG V2 |
| `lg:` | 1024px | TRMNL V2 |

### Bit-Depth (NOT progressive -- each targets only its specific depth)

| Prefix | Color Support | Devices |
|--------|---------------|---------|
| `1bit:` | Monochrome (2 shades) | TRMNL OG |
| `2bit:` | Grayscale (4 shades) | TRMNL OG V2 |
| `4bit:` | Grayscale (16 shades) | TRMNL V2, Kindle 2024 |

### Orientation

| Prefix | Application |
|--------|-------------|
| `portrait:` | Portrait orientation only (landscape is default) |

### Combined Pattern Order

`size:orientation:bit-depth:utility`

Examples:
- `md:portrait:text--center`
- `lg:2bit:value--xlarge`
- `md:portrait:4bit:gap--large`

---

## Screen Container

The outermost wrapper. Sets viewport dimensions and cascading CSS variables.

### Classes

| Class | Purpose |
|-------|---------|
| `screen` | Base container (800x480px landscape default) |
| `screen--portrait` | Swaps width/height (480x800) |
| `screen--no-bleed` | Removes default padding (edge-to-edge content) |
| `screen--dark-mode` | Inverts colors (images preserved) |
| `screen--backdrop` | Patterned bg (1-bit) or solid gray (2/4-bit) with plain white views |

### Device Variants

| Class | Resolution | Bit Depth |
|-------|------------|-----------|
| `screen--og` | 800x480 | 1-bit |
| `screen--v2` | 1040x780 | 4-bit |
| `screen--amazon_kindle_2024` | 718x540 | 4-bit |
| `screen--1bit` | -- | 1-bit depth modifier |
| `screen--2bit` | -- | 2-bit depth modifier |
| `screen--4bit` | -- | 4-bit depth modifier |

Additional device variants: `screen--amazon_kindle_7`, `screen--amazon_kindle_oasis_2`, various PaperWhite, Kobo, Inkplate, Waveshare, Onyx Boox, Nook, Seeed, Xteink models.

### CSS Variables Provided by `screen`

| Variable | Purpose | Default |
|----------|---------|---------|
| `--screen-w` | Screen width | 800px |
| `--screen-h` | Screen height | 480px |
| `--full-w` | Width minus padding | `calc(--screen-w - --gap * 2)` |
| `--full-h` | Height minus padding | `calc(--screen-h - --gap * 2)` |
| `--ui-scale` | UI scaling factor | 1 |
| `--gap-scale` | Gap scaling factor | 1 |
| `--color-depth` | Color depth in bits | 1 |

---

## View

Container for content within a Layout. The platform auto-wraps your markup -- do NOT add manually in markup editor.

| Class | Purpose |
|-------|---------|
| `view` | Base container (`display: flex; flex-direction: column`) |
| `view--full` | Full-width view |
| `view--half_horizontal` | Half-width horizontal layout |
| `view--half_vertical` | Half-width vertical layout |
| `view--quadrant` | Quarter-screen layout |

---

## Layout

Flex-based layout container with built-in centering and gap.

```css
.layout {
  container-type: size;
  display: flex;
  overflow: hidden;
  justify-content: center;
  align-items: center;
  gap: 10px;
}
```

### Direction

| Class | Effect |
|-------|--------|
| `layout layout--row` | Horizontal (left to right) |
| `layout layout--col` | Vertical (top to bottom) |

### Horizontal Alignment

| Class | CSS |
|-------|-----|
| `layout--left` | `justify-content: flex-start` |
| `layout--center-x` | `justify-content: center` |
| `layout--right` | `justify-content: flex-end` |

### Vertical Alignment

| Class | CSS |
|-------|-----|
| `layout--top` | `align-items: flex-start` |
| `layout--center-y` | `align-items: center` |
| `layout--bottom` | `align-items: flex-end` |

### Combined Centering

| Class | Effect |
|-------|--------|
| `layout--center` | Centers both axes |

### Stretch Modifiers (Container)

| Class | Effect |
|-------|--------|
| `layout--stretch` | All children stretch both directions |
| `layout--stretch-x` | Children stretch horizontally |
| `layout--stretch-y` | Children stretch vertically (`flex: 1 1 0%`) |

### Stretch Modifiers (Child)

| Class | Effect |
|-------|--------|
| `stretch-x` | Individual element stretches horizontally (`flex: 1; width: 100%`) |
| `stretch-y` | Individual element stretches vertically (`flex: 1; height: 100%`) |

---

## Flex

Lower-level flex utilities (compared to `layout` which is higher-level).

### Direction

| Class | CSS |
|-------|-----|
| `flex flex--row` | `display: flex; flex-direction: row` |
| `flex flex--col` | `display: flex; flex-direction: column` |
| `flex--row-reverse` | `flex-direction: row-reverse` |
| `flex--col-reverse` | `flex-direction: column-reverse` |

### Alignment

| Class | Purpose |
|-------|---------|
| `flex--left` | Align items left |
| `flex--center-x` | Center horizontally |
| `flex--right` | Align items right |
| `flex--top` | Align items top |
| `flex--center-y` | Center vertically |
| `flex--bottom` | Align items bottom |

### Container Stretch

| Class | Effect |
|-------|--------|
| `flex--stretch` | Stretches children in cross-axis |
| `flex--stretch-x` | Stretch children horizontally |
| `flex--stretch-y` | Stretch children vertically |

### Individual Item Classes

| Class | Effect |
|-------|--------|
| `stretch` | Stretches in cross-axis |
| `stretch-x` | Stretches horizontally |
| `stretch-y` | Stretches vertically |
| `no-shrink` | Prevents shrinking |

### Wrapping

| Class | Effect |
|-------|--------|
| `flex--wrap` | Enable line wrapping |
| `flex--nowrap` | Prevent wrapping |
| `flex--wrap-reverse` | Wrap with reversed line order |

### Multi-Line Alignment (align-content)

| Class | Effect |
|-------|--------|
| `flex--content-start` | Lines at start |
| `flex--content-center` | Lines centered |
| `flex--content-end` | Lines at end |
| `flex--content-between` | Space between lines |
| `flex--content-around` | Space around lines |
| `flex--content-evenly` | Equal space distribution |
| `flex--content-stretch` | Lines stretch |

### Main-Axis Distribution (justify-content)

| Class | Effect |
|-------|--------|
| `flex--between` | `space-between` |
| `flex--around` | `space-around` |
| `flex--evenly` | `space-evenly` |

### Item-Level Controls

| Class | CSS |
|-------|-----|
| `self--start` | `align-self: flex-start` |
| `self--center` | `align-self: center` |
| `self--end` | `align-self: flex-end` |
| `self--stretch` | `align-self: stretch` |
| `grow` | `flex-grow` enabled |
| `shrink-0` | `flex-shrink: 0` |
| `flex-none` | `flex: none` |
| `flex-initial` | `flex: initial` |
| `basis--[value]` | `flex-basis` with size |
| `order--first` | `order: 9999` |
| `order--last` | `order: -9999` |
| `order--[n]` | `order: [number]` |

### Display Variants

| Class | Effect |
|-------|--------|
| `inline-flex` | Inline-level flex container |

### Responsive

`portrait:flex--col`, `portrait:flex--row`, etc.

---

## Grid

CSS Grid utilities.

### Container

| Class | Effect |
|-------|--------|
| `grid` | Base grid container |
| `grid--cols-1` | 1 equal column |
| `grid--cols-3` | 3 equal columns |
| `grid--cols-4` | 4 equal columns |
| `grid--cols-{N}` | N equal columns |

### Column Spanning

| Class | CSS |
|-------|-----|
| `col--span-1` | `grid-column: span 1` |
| `col--span-2` | `grid-column: span 2` |
| `col--span-3` | `grid-column: span 3` |
| `col--span-6` | `grid-column: span 6` |
| `col--span-{N}` | `grid-column: span N` |

### Column/Row Alignment

| Class | Effect |
|-------|--------|
| `col` | Vertical column layout within grid |
| `col--start` | Align column content at start |
| `col--center` | Center column content |
| `col--end` | Align column content at end |
| `row` | Horizontal row layout within grid |
| `row--start` | Align row content at start |
| `row--center` | Center row content |
| `row--end` | Align row content at end |

### Responsive Wrapping

| Class | Effect |
|-------|--------|
| `grid--wrap` | Enable responsive wrapping |
| `grid--min-{size}` | Min track size for wrapping (e.g., `grid--min-32`, `grid--min-56`) |

---

## Columns

Simple balanced multi-column layout.

| Class | Purpose |
|-------|---------|
| `columns` | Container for column layout |
| `column` | Individual column child |

Add as many `.column` children as needed. Can combine with Grid for complex layouts.

---

## Mashup

Grid-based plugin composition layouts.

| Class | Layout |
|-------|--------|
| `mashup` | Base container |
| `mashup--1Lx1R` | 1 Left + 1 Right (two equal columns) |
| `mashup--1Tx1B` | 1 Top + 1 Bottom (two equal rows) |
| `mashup--1Lx2R` | 1 Left + 2 stacked Right |
| `mashup--2Lx1R` | 2 stacked Left + 1 Right |
| `mashup--2Tx1B` | 2 side-by-side Top + 1 Bottom |
| `mashup--1Tx2B` | 1 Top + 2 side-by-side Bottom |
| `mashup--2x2` | 2x2 Grid (four quadrants) |

Each mashup contains child `.view` elements with sizing: `view--half_vertical`, `view--half_horizontal`, `view--quadrant`.

---

## Size (Width & Height)

### Fixed Size Classes

Format: `w--{size}` and `h--{size}` where value = size * 4px.

Examples: `w--16` = 64px, `h--24` = 96px, `w--32` = 128px. Range: 0-96.

### Arbitrary Size

Format: `w--[Npx]` and `h--[Npx]` where N = 0-800.

Examples: `w--[150px]`, `h--[300px]`.

### Dynamic Size

| Class | CSS |
|-------|-----|
| `w--full` | `width: 100%` |
| `h--full` | `height: 100%` |
| `w--auto` | `width: auto` |
| `h--auto` | `height: auto` |

### Container Query Sizes

Format: `w--[Ncqw]` and `h--[Ncqh]` where N = 0-100.

Examples: `w--[50cqw]` = 50% of container width, `h--[75cqh]` = 75% of container height.

### Min/Max Constraints

| Pattern | Examples |
|---------|----------|
| Fixed: `w--min-{size}`, `w--max-{size}` | `w--min-16`, `w--max-64` |
| Fixed: `h--min-{size}`, `h--max-{size}` | `h--min-16`, `h--max-64` |
| Arbitrary: `w--min-[Npx]`, `w--max-[Npx]` | `w--min-[100px]`, `w--max-[400px]` |
| Arbitrary: `h--min-[Npx]`, `h--max-[Npx]` | `h--min-[100px]`, `h--max-[400px]` |
| Dynamic: `w--min-full`, `w--max-auto` | -- |
| Container: `w--min-[Ncqw]`, `h--max-[Ncqh]` | `w--min-[50cqw]` |

### Responsive Variants

`md:w--16`, `lg:h--24`, `md:w--[50cqw]`, `portrait:w--full`.

---

## Spacing (Padding & Margin)

**Scale:** `{property}--{N}` where value = N * 4px. All have `!important`.

**NO bracket syntax exists** for spacing -- `p--[2px]` is INVALID.

### Padding

| Class | Effect |
|-------|--------|
| `p--{N}` | All sides (N * 4px) |
| `pt--{N}` | Top |
| `pr--{N}` | Right |
| `pb--{N}` | Bottom |
| `pl--{N}` | Left |
| `px--{N}` | Horizontal (left + right) |
| `py--{N}` | Vertical (top + bottom) |

Range: `p--0` (0px) through `p--16` (64px).

### Margin

| Class | Effect |
|-------|--------|
| `m--{N}` | All sides |
| `mt--{N}` | Top |
| `mr--{N}` | Right |
| `mb--{N}` | Bottom |
| `ml--{N}` | Left |
| `mx--{N}` | Horizontal (left + right) |
| `my--{N}` | Vertical (top + bottom) |

### Responsive Variants

`sm:p--2`, `md:py--4`, `lg:mt--6`, `portrait:mx--2`, `lg:portrait:mt--4`.

---

## Gap

Controls spacing between flex/grid children.

### Named Sizes

| Class | Value |
|-------|-------|
| `gap--none` | 0px |
| `gap--xsmall` | 5px |
| `gap--small` | 7px |
| `gap` / `gap--base` | 10px |
| `gap--medium` | 16px |
| `gap--large` | 20px |
| `gap--xlarge` | 30px |
| `gap--xxlarge` | 40px |

### Arbitrary Pixel Gap

`gap--[Npx]` where N = 0-50. Example: `gap--[15px]`.

**WARNING:** Arbitrary gap values do NOT support responsive variants.

### Distribution Modifiers

| Class | CSS | Notes |
|-------|-----|-------|
| `gap--distribute` | `justify-content: space-between` | **THE ONE YOU USUALLY WANT** |
| `gap--auto` | `justify-content: space-evenly` | |
| `gap--space-between` | `justify-content: space-evenly` | **MISLEADING NAME** -- kept for backwards compat, same as `gap--auto` |

### Responsive Variants

`md:gap--large`, `lg:gap--xlarge`, `portrait:gap--medium`, `md:portrait:gap--xlarge`.

**Note:** Gap utilities only support size-based responsive variants. Bit-depth variants (`1bit:`, `4bit:`) are NOT available for gap.

---

## Text

### Text Color (Dithered Grayscale)

| Class | Shade |
|-------|-------|
| `text--black` | Solid black |
| `text--gray-10` | 10% gray (dithered) |
| `text--gray-15` | 15% gray |
| `text--gray-20` | 20% gray |
| `text--gray-25` | 25% gray |
| `text--gray-30` | 30% gray |
| `text--gray-35` | 35% gray |
| `text--gray-40` | 40% gray |
| `text--gray-45` | 45% gray |
| `text--gray-50` | 50% gray |
| `text--gray-55` | 55% gray |
| `text--gray-60` | 60% gray |
| `text--gray-65` | 65% gray |
| `text--gray-70` | 70% gray |
| `text--gray-75` | 75% gray |
| `text--white` | Solid white |

Legacy (deprecated, still supported): `text--gray-1` through `text--gray-7`.

### Text Alignment (all `!important`)

| Class | CSS |
|-------|-----|
| `text--left` | `text-align: left` |
| `text--center` | `text-align: center` |
| `text--right` | `text-align: right` |
| `text--justify` | `text-align: justify` |

### Responsive Variants

Breakpoints: `sm:text--center`, `md:text--right`, `lg:text--left`.
Orientation: `portrait:text--center`.
Bit-depth (alignment only): `1bit:text--right`, `2bit:text--center`, `4bit:text--left`.
Combined: `md:portrait:text--right`.

---

## Title

Heading text element.

| Class | Size |
|-------|------|
| `title` | Base size (default) |
| `title--small` | Compact |
| `title--base` | Explicit base (for responsive) |
| `title--large` | Prominent |
| `title--xlarge` | Extra large |
| `title--xxlarge` | Maximum impact |

### Responsive

`sm:title--small`, `md:title--large`, `lg:title--xlarge`, `portrait:title--small`.

### Usage

```html
<span class="title title--large">Section Heading</span>
```

---

## Value

Numerical/textual value display.

| Class | Size |
|-------|------|
| `value` | Base size |
| `value--xxsmall` | Smallest |
| `value--xsmall` | Extra small |
| `value--small` | Small |
| `value--base` | Base (explicit) |
| `value--large` | Large |
| `value--xlarge` | Extra large |
| `value--xxlarge` | Very large |
| `value--xxxlarge` | Very large variant |
| `value--mega` | Extremely large |
| `value--giga` | Massive |
| `value--tera` | Colossal |
| `value--peta` | Largest available |

### Modifier

| Class | Effect |
|-------|--------|
| `value--tnums` | Tabular numbers (monospace digits for alignment) |

### Responsive

`sm:value--small`, `md:value--large`, `lg:value--xlarge`, `portrait:value--base`.

### Usage

```html
<span class="value value--xlarge value--tnums">42,195</span>
```

---

## Label

Text label element.

### Size Modifiers

| Class | Size |
|-------|------|
| `label` | Base |
| `label--small` | Compact |
| `label--base` | Explicit base |
| `label--large` | Large |
| `label--xlarge` | Extra large |
| `label--xxlarge` | Double extra large |

### Style Variants

| Class | Effect |
|-------|--------|
| `label--outline` | Bordered label |
| `label--underline` | Underlined text |
| `label--gray` | Muted/secondary |
| `label--gray-out` | Legacy (deprecated, maps to `--gray`) |
| `label--inverted` | High contrast (inverted colors) |

### Responsive

`sm:label--small`, `md:label--large`, `lg:label--xlarge`, `portrait:label--small`.
Bit-depth: `1bit:label--small`, `2bit:label--base`, `4bit:label--large`.

### Usage

```html
<span class="label label--outline">Status</span>
<span class="label label--small" data-clamp="1">Truncated label</span>
```

---

## Description

Descriptive text element.

| Class | Size |
|-------|------|
| `description` | Base |
| `description--large` | Large |
| `description--xlarge` | Extra large |
| `description--xxlarge` | Double extra large |

### Responsive

`sm:description--base`, `md:description--large`, `lg:description--xlarge`, `portrait:description--base`.

### Usage

```html
<span class="description" data-clamp="2">Long description text...</span>
```

---

## Title Bar

Consistent header component positioned at the bottom by the platform.

### Structure

```html
<div class="title_bar">
  <img class="image" src="/images/plugins/trmnl--render.svg">
  <span class="title">Plugin Name</span>
  <span class="instance">Production</span>  <!-- optional -->
</div>
```

### Classes

| Class | Element | Purpose |
|-------|---------|---------|
| `title_bar` | Container | Wrapper with horizontal layout |
| `image` | `<img>` | Icon/logo (dithered for 1-bit) |
| `title` | `<span>` | Main heading text |
| `instance` | `<span>` | Optional context label |

**Important:** `title_bar` must be a SIBLING of `layout`, not inside it.

---

## Table

### Size Variants

| Class | thead height | tbody height | Alias |
|-------|-------------|-------------|-------|
| `table` / `table--base` | 36px | 46px | -- |
| `table--large` | 44px | 56px | -- |
| `table--small` | 24px | 31px | `table--condensed` (legacy) |
| `table--xsmall` | 18px | 22px | -- |

### Indexed Tables

| Class | Effect |
|-------|--------|
| `table--indexed` | Adds index column support |

Requires `<span class="meta"><span class="index">1</span></span>` inside `<td>`.

### Related Element Classes

| Class | Context |
|-------|---------|
| `title` / `title--small` | `<th>` header text |
| `label` / `label--small` | `<td>` cell text |
| `meta` | Index wrapper |
| `index` | Index number |

### Table Overflow

Uses data attributes (see [Data Attributes](#data-attributes-js-runtime)):
- `data-table-limit="true"` -- enable overflow with "and X more" row
- `data-table-max-height="auto"` or `data-table-max-height="240"` -- height constraint

### Usage

```html
<table class="table table--small table--indexed" data-table-limit="true" data-table-max-height="auto">
  <thead>
    <tr><th><span class="title title--small">#</span></th><th><span class="title title--small">Name</span></th></tr>
  </thead>
  <tbody>
    <tr><td><span class="meta"><span class="index">1</span></span></td><td><span class="label label--small" data-clamp="1">Item</span></td></tr>
  </tbody>
</table>
```

---

## Item

Content block with optional metadata, indexing, and icons.

### Core Classes

| Class | Purpose |
|-------|---------|
| `item` | Base container |
| `meta` | Metadata section |
| `content` | Main content area |
| `index` | Numeric index badge |
| `icon` | Optional icon section |

### Emphasis Modifiers

| Class | Effect |
|-------|--------|
| `item--emphasis-1` | Light emphasis (default) |
| `item--emphasis-2` | Medium emphasis |
| `item--emphasis-3` | High emphasis (darkest) |

### Nested Elements

Items use standard framework elements: `.title`, `.title--small`, `.description`, `.label`, `.label--small`, `.label--underline`, `.flex`, `.gap--small`.

### Usage

```html
<div class="item item--emphasis-2">
  <div class="meta"><span class="index">1</span></div>
  <div class="content">
    <span class="title title--small">Item Title</span>
    <span class="description" data-clamp="2">Description text</span>
  </div>
</div>
```

---

## Divider

Visual separators.

### Classes

| Class | Effect |
|-------|--------|
| `divider` | Horizontal separator (auto-detects background) |
| `divider--h` | Explicit horizontal (same as `divider`) |
| `divider--v` | Vertical separator |

### Background-Specific Variants

| Class | For Background | Darkness Level |
|-------|---------------|---------------|
| `divider--on-white` | White / gray-70 to gray-75 | Level 7 (darkest) |
| `divider--on-light` | Light gray (gray-50 to gray-65) | Level 6 |
| `divider--on-dark` | Dark gray (gray-30 to gray-45) | Level 3 |
| `divider--on-black` | Black / gray-10 to gray-25 | Level 1 (lightest) |

### Usage

```html
<div class="divider"></div>
<div class="divider--v divider--on-white"></div>
```

---

## Border

Dithered border patterns for 1-bit rendering. Intensity scale: 1 (black) to 7 (white).

### Horizontal Borders

`border--h-1` through `border--h-7`

### Vertical Borders

`border--v-1` through `border--v-7`

**v2 Breaking Change:** Border utility is NOT backward compatible with v1. Re-evaluate intensity values when upgrading.

---

## Rounded

Border-radius utilities.

### Named Sizes

| Class | Radius |
|-------|--------|
| `rounded--none` | 0px |
| `rounded--xsmall` | 5px |
| `rounded--small` | 7px |
| `rounded` / `rounded--base` | 10px |
| `rounded--medium` | 15px |
| `rounded--large` | 20px |
| `rounded--xlarge` | 25px |
| `rounded--xxlarge` | 30px |
| `rounded--full` | 9999px (pill) |

### Arbitrary

`rounded--[Npx]` where N = 0-50. Example: `rounded--[15px]`. **No responsive support.**

### Corner-Specific

Individual corners: `rounded-tl--{size}`, `rounded-tr--{size}`, `rounded-br--{size}`, `rounded-bl--{size}`.

Side rounding: `rounded-t--{size}`, `rounded-r--{size}`, `rounded-b--{size}`, `rounded-l--{size}`.

Where `{size}` = `none`, `xsmall`, `small`, (base), `medium`, `large`, `xlarge`, `xxlarge`, or `[Npx]`.

### Responsive

`md:rounded--large`, `portrait:rounded--small`, `md:portrait:rounded--xsmall`.

---

## Outline

Pixel-perfect rounded border using 9-slice PNG technique.

### Classes

| Class | Implementation |
|-------|---------------|
| `outline` | `border: 10px solid transparent; border-image-source: [9-slice PNG]; border-image-slice: 10 fill` |

### Bit-Depth Behavior

- **1-bit:** Uses border-image for crisp pixel-perfect corners.
- **2-bit / 4-bit:** Falls back to `border: 1px solid var(--black); border-radius: 10px`.

### Screen Modifier

`screen--backdrop` on `.screen` element changes mashup appearance (patterned bg instead of bordered views).

---

## Background

Dithered grayscale backgrounds for e-ink displays.

### Classes

| Class | Shade |
|-------|-------|
| `bg--black` | Pure black (solid) |
| `bg--gray-10` | 10% gray (dithered) |
| `bg--gray-15` | 15% gray |
| `bg--gray-20` | 20% gray |
| `bg--gray-25` | 25% gray |
| `bg--gray-30` | 30% gray |
| `bg--gray-35` | 35% gray |
| `bg--gray-40` | 40% gray |
| `bg--gray-45` | 45% gray |
| `bg--gray-50` | 50% gray |
| `bg--gray-55` | 55% gray |
| `bg--gray-60` | 60% gray |
| `bg--gray-65` | 65% gray |
| `bg--gray-70` | 70% gray |
| `bg--gray-75` | 75% gray |
| `bg--white` | Pure white (solid) |

Legacy (deprecated, still supported): `bg--gray-1` through `bg--gray-7`.

**Dark Mode Note:** Palette appears inverted because dark mode inverts the entire screen (except images).

---

## Image

### Classes

| Class | Effect |
|-------|--------|
| `image` | Base image class |
| `image-dither` | Applies dithering for 1-bit grayscale simulation |
| `image--fill` | `object-fit: fill` (stretches/squishes) |
| `image--contain` | `object-fit: contain` (fits within, maintains ratio) |
| `image--cover` | `object-fit: cover` (fills, clips excess, maintains ratio) |

Commonly combined with `rounded`: `class="image image-dither rounded"`.

---

## Image Stroke

Outlines for vector/transparent raster images.

### Size Modifiers

| Class | Stroke Width |
|-------|-------------|
| `image-stroke` | 1.5px (default) |
| `image-stroke--small` | 1px |
| `image-stroke--base` | 1.5px (explicit) |
| `image-stroke--medium` | 2px |
| `image-stroke--large` | 2.5px |
| `image-stroke--xlarge` | 3px |

### Color Modifier

| Class | Effect |
|-------|--------|
| `image-stroke--black` | Black stroke (default is white) |

### Usage

```html
<img class="image-stroke image-stroke--medium" src="/images/icon.svg">
<img class="image-stroke image-stroke--black image-stroke--large" src="/images/dark-icon.svg">
```

---

## Text Stroke

Outlined text rendering.

### Width Modifiers

| Class | Stroke Width |
|-------|-------------|
| `text-stroke` | 3.5px (default, white) |
| `text-stroke--small` | 2px |
| `text-stroke--base` | 3.5px (explicit) |
| `text-stroke--medium` | 4.5px |
| `text-stroke--large` | 6px |
| `text-stroke--xlarge` | 7.5px |

### Color/Shade Modifiers

`text-stroke--black`, `text-stroke--gray-10` through `text-stroke--gray-75`, `text-stroke--white`.

**Limitation:** Only works with solid black or white text fills. Does NOT work on dithered gray text.

### Usage

```html
<span class="text-stroke text-stroke--large text-stroke--black">Outlined Text</span>
```

---

## Visibility

### Core Display Classes

| Class | CSS |
|-------|-----|
| `hidden` | `display: none` |
| `visible` | `display: block` |
| `block` | `display: block` |
| `inline` | `display: inline` |
| `inline-block` | `display: inline-block` |
| `flex` | `display: flex` |
| `grid` | `display: grid` |
| `table` | `display: table` |
| `table-row` | `display: table-row` |

### Responsive Size Prefixes

`sm:hidden`, `md:flex`, `lg:grid`, etc.

### Bit-Depth Prefixes

`1bit:hidden`, `2bit:flex`, `4bit:grid`.

### Combined

Pattern: `size:bit-depth:display`. Examples: `md:1bit:block`, `md:2bit:flex`, `lg:4bit:grid`.

---

## Overflow

Attribute-driven layout engine for smart column planning and content overflow.

### Data Attributes

| Attribute | Purpose | Values |
|-----------|---------|--------|
| `data-overflow="true"` | Enable overflow engine | `true`/`false` |
| `data-overflow-max-height` | Height budget | pixel value or `auto` |
| `data-overflow-counter="true"` | Show "and N more" label | `true`/`false` |
| `data-overflow-max-cols` | Best-fit columns up to N | numeric |
| `data-overflow-cols` | Force exact column count | numeric |
| `data-group-header="true"` | Mark grouped headers (avoid orphaning) | `true` |

### Responsive Modifiers for Column Attributes

Suffix with: `-sm`, `-md`, `-lg`, `-portrait`, `-md-portrait`.

Example: `data-overflow-max-cols="2" data-overflow-max-cols-lg="4"`.

### Usage

```html
<div class="columns" data-overflow="true" data-overflow-max-cols="3" data-overflow-counter="true">
  <div class="column">
    <div class="item">...</div>
  </div>
</div>
```

---

## Clamp

Text truncation to N lines with word-based ellipsis.

### Data Attributes (Preferred)

| Attribute | Purpose |
|-----------|---------|
| `data-clamp="N"` | Truncate to N lines |
| `data-clamp-sm="N"` | At sm breakpoint |
| `data-clamp-md="N"` | At md breakpoint |
| `data-clamp-lg="N"` | At lg breakpoint |
| `data-clamp-portrait="N"` | In portrait orientation |
| `data-clamp-md-portrait="N"` | At md + portrait |

### Legacy Classes (Backward Compatible)

`clamp--none` (disables), `clamp--1` through `clamp--50`.

### Usage

```html
<span class="label" data-clamp="1">Single line truncated text...</span>
<span class="description" data-clamp="2" data-clamp-md="4" data-clamp-portrait="1">Responsive clamping</span>
```

---

## Scale

UI scaling for the entire screen. **Only available on 4-bit devices.**

| Class | Scale Factor | CSS Variable |
|-------|-------------|-------------|
| `screen--scale-xsmall` | 0.75 (75%) | `--ui-scale: 0.75` |
| `screen--scale-small` | 0.875 (87.5%) | `--ui-scale: 0.875` |
| `screen--scale-regular` | 1.0 (100%) | `--ui-scale: 1.0` |
| `screen--scale-large` | 1.125 (112.5%) | `--ui-scale: 1.125` |
| `screen--scale-xlarge` | 1.25 (125%) | `--ui-scale: 1.25` |
| `screen--scale-xxlarge` | 1.5 (150%) | `--ui-scale: 1.5` |

Affects: font sizes, line heights, component dimensions, spacing, custom properties using `var(--ui-scale)`.

### Usage

```html
<div class="screen screen--scale-large">
  <!-- All content scales to 112.5% -->
</div>
```

---

## Aspect Ratio

**Beta Feature.** Uses native CSS `aspect-ratio` property.

| Class | Ratio |
|-------|-------|
| `aspect--auto` | No constraint |
| `aspect--1/1` | Square |
| `aspect--4/3` | Standard |
| `aspect--3/2` | Photo |
| `aspect--16/9` | Widescreen |
| `aspect--21/9` | Ultrawide |
| `aspect--3/4` | Portrait standard |
| `aspect--2/3` | Portrait photo |
| `aspect--9/16` | Vertical video |
| `aspect--9/21` | Ultrawide portrait |

---

## Progress

### Progress Bar

| Class | Purpose |
|-------|---------|
| `progress-bar` | Base container |
| `progress-bar--small` | Compact size |
| `progress-bar--base` | Explicit base (for responsive) |
| `progress-bar--large` | Large variant |
| `progress-bar--emphasis-2` | Medium emphasis |
| `progress-bar--emphasis-3` | High emphasis |

Child elements: `.content` (label + value), `.track` (background), `.fill` (filled portion, width via inline style).

```html
<div class="progress-bar progress-bar--large">
  <div class="content">
    <span class="label">Progress</span>
    <span class="value">75%</span>
  </div>
  <div class="track">
    <div class="fill" style="width: 75%"></div>
  </div>
</div>
```

### Progress Dots

| Class | Purpose |
|-------|---------|
| `progress-dots` | Base container |
| `progress-dots--small` | Compact dots |
| `progress-dots--base` | Explicit base |
| `progress-dots--large` | Larger dots |

Child elements: `.track` (container), `.dot` (empty), `.dot--filled` (completed), `.dot--current` (active).

```html
<div class="progress-dots">
  <div class="track">
    <div class="dot dot--filled"></div>
    <div class="dot dot--current"></div>
    <div class="dot"></div>
  </div>
</div>
```

---

## Rich Text

### Classes

| Class | Purpose |
|-------|---------|
| `richtext` | Base container |
| `richtext--left` | Left-aligned component |
| `richtext--center` | Centered component |
| `richtext--right` | Right-aligned component |

### Content Child

| Class | Purpose |
|-------|---------|
| `content` | Text content container |
| `content--small` through `content--xxxlarge` | Size variants |
| `content--left`, `content--center`, `content--right` | Alignment |

Responsive: `sm:content--small`, `md:content--large`, `lg:content--xxlarge`.
Bit-depth: `1bit:`, `2bit:`, `4bit:` prefixes supported.
Data attributes: `data-content-limiter="true"`, `data-content-max-height`, `data-pixel-perfect="true"`.

---

## Chart

No dedicated chart CSS classes. Charts use Highcharts/Chartkick JS libraries with standard TRMNL utilities (`w--full`, `h--full`, `layout`, `grid`, etc.) for layout.

---

## Data Attributes (JS Runtime)

The Framework Runtime automatically processes these attributes.

### Value Formatting

| Attribute | Purpose |
|-----------|---------|
| `data-value-format="true"` | Auto-format numbers (K, M, B abbreviation) |
| `data-fit-value="true"` / `data-value-fit="true"` | Preserve currency symbol placement |
| `data-value-locale="en-US"` | Regional number formatting (en-US, de-DE, fr-FR, en-GB, ja-JP) |

Supported currency symbols: $, EUR, GBP, JPY, UAH, INR, ILS, KRW, VND, PHP, RUB, BTC.

### Value Fitting

| Attribute | Purpose |
|-----------|---------|
| `data-value-fit="true"` | Auto-resize font/weight/line-height to fit container |
| `data-value-fit-max-height="N"` | Max height constraint in px (required for text, optional for numbers) |

### Content Limiter

| Attribute | Purpose |
|-----------|---------|
| `data-content-limiter="true"` | Auto-limit content height by view type |
| `data-content-max-height="N"` | Custom max height in px |

### Table Overflow

| Attribute | Purpose |
|-----------|---------|
| `data-table-limit="true"` | Enable overflow with "and X more" row |
| `data-table-max-height="auto"` or `"N"` | Height constraint |

### Pixel Perfect

| Attribute | Purpose |
|-----------|---------|
| `data-pixel-perfect="true"` | Align text to pixel grid for crisp 1-bit rendering |

### Runtime Control

| Attribute | Purpose |
|-----------|---------|
| `data-adjust-grid-gaps="false"` | Disable grid gap tweaking |
| `data-adjust-column-gaps="false"` | Disable column gap normalization |
| `data-prefer-model-size="true"` | Use device model dimensions |

### Runtime Execution Order

1. Clamp -- text truncation
2. Overflow -- column planning with counters
3. Value Formatting -- number abbreviation
4. Fit Value -- font size adjustment
5. Grid Gaps -- integer pixel alignment
6. Column Gaps -- column normalization
7. Pixel-Perfect Fonts -- line wrapping for crisp rendering
8. Content Limiter -- height constraints
9. Index Widths -- even badge widths

---

## Upgrade Guide (v1 to v2)

### Borders

- v2 border utility is NOT backward compatible with v1.
- Search for `border--h-*` classes and re-evaluate intensity (1-7 scale now supports 1/2/4-bit displays).

### Clamping

- **v1:** Title, Label, Description auto-clamped to 1 line.
- **v2:** Unclamped by default. Must explicitly add `data-clamp="N"`.
- Legacy `clamp--N` classes still work during transition.

### Migration Pattern

```html
<!-- v1 (auto-clamped) -->
<span class="label">Text</span>

<!-- v2 (explicit clamp) -->
<span class="label" data-clamp="1">Text</span>
```

---

## Best Practices

1. **Use the framework** -- avoid inline styles for display, justify-content, padding, margin, background-color, color, border-radius, text-align, object-fit, font-size.
2. **Use data attributes** for clamp, overflow, value formatting rather than legacy classes.
3. **Test across view sizes** -- full, half_horizontal, half_vertical, quadrant.
4. **Embed links** in custom field descriptions using `<a href="...">` tags.
5. **Use the Chef linting utility** for recipe validation.

---

## Template Structure

Standard template for the markup editor:

```html
<div class="layout layout--col layout--top layout--stretch-x">
  <!-- Your content here -->
</div>
<div class="title_bar">
  <img class="image" src="/images/plugins/your-plugin--icon.svg">
  <span class="title">Plugin Name</span>
</div>
```

The platform wraps this in a `view` container automatically. Do NOT add `view` manually.
