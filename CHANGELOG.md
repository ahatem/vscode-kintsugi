# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.3.1] - 2026-08-16

### Fixed

- **Syntax colours now meet WCAG contrast against the background they are drawn on.** 48 tokens across the eight themes sat below the readable floor, and they failed in the way a light palette derived from a dark one always does: mid-tone accents keep their hue but lose their separation, because they were chosen against near-black and are now on cream. The signature gold keyword was at 3.76 against a floor of 4.5 — the colour the theme is named for was the least readable thing in it.
- Thirteen colours adjusted, each the smallest hue-preserving move that clears its floor, computed in HSL so a gold stays gold rather than drifting toward brown. Comments are held to 3.0 rather than 4.5, since they are meant to recede.
- Only `tokenColors` changed. The same values appear in the workbench colours, where they sit on different backgrounds and were already fine.

### Added

- Every syntax colour is now checked against the background it is drawn on, rather than judged by eye, so contrast stops being a matter of taste.

## [0.3.0] - 2026-08-16

### Added

- **Kintsugi Dark Clay** and **Kintsugi Light Clay**, plus a Flared twin of each — four new themes, bringing the set to eight. The interface is re-tinted to bronze and parchment in place of neutral grey: a deeper, earthen ground for the dark variant and warm parchment for the light one. Named for the vessel that kintsugi mends.
- A Clay variant keeps its namesake's syntax colours **exactly** — every `tokenColors` entry is identical. Only the interface changes, so switching between a theme and its Clay twin recolours the room around your code and leaves the code itself alone. That is the same relationship Flared has in the other direction, where the syntax changes and the interface does not.

### Changed

- The Clay themes are generated from their namesakes rather than maintained by hand, so the pairs cannot drift — a fix applied to Dark and forgotten on Dark Clay is the kind of thing nobody notices for months.

## [0.2.1] - 2026-04-24

### Changed
- **Light Themes:** Updated background color to warm cream (`#f8f4ea`) for a cozier, easier-on-the-eyes experience.

## [0.2.0] - 2026-04-25

### Added

- **Kintsugi Light Theme:** Introduced the first official light variant of Kintsugi. Built on a warm **washi paper** base (`#f3f1ec`) — named after the traditional Japanese paper used in kintsugi restoration — with gold as the only warm accent, exactly like real kintsugi pottery. Features green strings, indigo numbers, and gilded keywords, faithful to the Kintsugi Dark token philosophy.
- **Kintsugi Light Flared Theme:** Introduced the light counterpart to Kintsugi Dark Flared. Shares the washi paper base but brings the Flared variant's signature orange-red keywords, amber operators, and terracotta strings into a bright, refined light environment.
- **`uiTheme: vs` for light variants:** Both light themes correctly declare `vs` as their UI theme for proper VS Code light mode integration.

### Changed

- **`package.json` description:** Updated to reflect that Kintsugi is now available in both dark and light variants.
- **`package.json` keywords:** Added `light`, `washi`, `ivory`, `japanese`, `ceramic` for improved Marketplace discoverability.
- **`package.json` version:** Bumped from `0.1.1` to `0.2.0` to reflect the addition of new theme variants.

## [0.1.1] - 2024-12-21

### Fixed

- **Theme Logic:** Corrected and simplified several `tokenColors` rules in the `Flared` variant to improve consistency and maintainability.
- **File Organization:** Moved files in `snippets` to `snippets/showcase` and added `snippets/syntax` to easily test syntax highlighting.

### Changed

- **Documentation:** Updated the `README.md` to recommend `editor.cursorSmoothCaretAnimation` for a more polished user experience.

## [0.1.0] - 2024-11-15

### Added

- **Kintsugi Dark Flared Theme:** Introduced a new, official theme variant, `Kintsugi Dark Flared`. This variant shares the same minimalist UI as the original but features a warm, vibrant syntax highlighting alternative with a cozy, autumn-like palette of rich oranges, terracottas, and deep golds.
- **Subtle Indent Guides:** Added new theme colors for file explorer indent guides (`tree.indentGuidesStroke`) to provide a subtle, warm visual structure perfectly aligned with the theme's aesthetic.

### Changed

- **Major `README.md` Overhaul:** Completely rebuilt the documentation for clarity, professionalism, and ease of use.
  - Introduced a new `How to Get the Look` section for a clear, step-by-step setup guide to replicate the screenshot aesthetic.
  - Restructured advanced settings, power-user tips, and the complete `settings.json` into collapsible `<details>` sections to simplify the main view.
  - Added a dedicated showcase section for the new `Flared` variant with language examples.
  - Updated and expanded font and icon recommendations.
  - Added official credits for the themes that inspired Kintsugi and its variants.

## [0.0.2] - 2024-10-08

### Added

- **Punctuation Color:** Introduced a new, unified color for all punctuation (`brackets`, `delimiters`, etc.) to create a more consistent and harmonious syntax highlighting experience.

### Changed

- **Bracket Highlighting:** Overhauled the `editorBracketHighlight` colors to create a subtle, monochromatic fade effect born from and perfectly matching the new base punctuation color.
- **Icon Refinement:** Updated the extension icon with a softer, more rounded design to better reflect the theme's elegant aesthetic.

## [0.0.1] - 2024-09-01

### Added

- Initial release of **Kintsugi Dark**, a sophisticated, warm-toned dark theme.
- Complete UI theming for core VS Code components, including the editor, terminal, sidebars, and status bar.
- Custom syntax highlighting designed for readability and focus.
- Seamless tab and breadcrumb integration for a minimalist feel.
- Official icon and marketplace presence.