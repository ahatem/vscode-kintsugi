# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.2.0] - 2025-04-25

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