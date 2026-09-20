#!/usr/bin/env python3
"""Deterministically migrate every Kintsugi VS Code theme to a fully populated Zed theme.

The converter intentionally does more than Zed's generic VS Code importer:
- package.json is the source of truth for the complete variant set;
- every current Zed syntax capture known to the official importer is populated;
- current Zed runtime theme fields are populated where a meaningful VS Code source exists;
- missing UI surfaces are derived from the nearest Kintsugi semantic color instead of left to defaults;
- terminal ANSI colors, statuses, version-control colors, diff colors, Vim colors, accents,
  multiplayer colors, font styles, and token backgrounds are preserved/derived;
- outputs are structurally validated and can also be checked against Zed's published JSON schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA_URL = "https://zed.dev/schema/themes/v0.2.0.json"
REPO_ROOT = Path(__file__).resolve().parents[1]
COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# Current capture set used by Zed's official VS Code theme importer.
ZED_SYNTAX_TOKENS = [
    "attribute",
    "boolean",
    "comment",
    "comment.doc",
    "constant",
    "constructor",
    "embedded",
    "emphasis",
    "emphasis.strong",
    "enum",
    "function",
    "hint",
    "keyword",
    "label",
    "link_text",
    "link_uri",
    "number",
    "operator",
    "predictive",
    "preproc",
    "primary",
    "property",
    "punctuation",
    "punctuation.bracket",
    "punctuation.delimiter",
    "punctuation.list_marker",
    "punctuation.special",
    "string",
    "string.escape",
    "string.regex",
    "string.special",
    "string.special.symbol",
    "tag",
    "text.literal",
    "title",
    "type",
    "variable",
    "variable.special",
    "variant",
]

# Ordered from most semantically useful to broader fallbacks. This starts with the
# official importer mapping and expands it for common TextMate scopes used by real VS Code themes.
SYNTAX_SCOPE_MAP: dict[str, list[str]] = {
    "attribute": [
        "entity.other.attribute-name",
        "entity.other.attribute-name.html",
        "entity.other.attribute-name.xml",
        "support.type.property-name",
    ],
    "boolean": ["constant.language.boolean", "constant.language"],
    "comment": ["comment", "comment.line", "comment.block"],
    "comment.doc": [
        "comment.block.documentation",
        "comment.line.documentation",
        "comment.documentation",
    ],
    "constant": [
        "constant",
        "constant.language",
        "constant.character",
        "constant.other",
        "variable.other.constant",
    ],
    "constructor": [
        "entity.name.function.definition.special.constructor",
        "entity.name.function.constructor",
        "entity.name.type.class",
        "entity.name.tag",
    ],
    "embedded": ["meta.embedded", "source.embedded", "text.html.embedded"],
    "emphasis": ["markup.italic", "markup.italic.markdown"],
    "emphasis.strong": ["markup.bold", "markup.bold.markdown"],
    "enum": ["support.type.enum", "entity.name.type.enum", "storage.type.enum"],
    "function": [
        "entity.name.function",
        "entity.name.function.definition",
        "entity.function",
        "variable.function",
        "support.function",
        "meta.function-call",
    ],
    "hint": ["meta.inlay-hint", "meta.hint"],
    "keyword": [
        "keyword.control",
        "keyword.control.flow",
        "keyword.control.import",
        "keyword.control.export",
        "keyword.other.fn.rust",
        "keyword.other",
        "keyword",
        "storage.type",
        "storage.modifier",
        "storage",
        "punctuation.accessor",
    ],
    "label": [
        "entity.name.label",
        "entity.name.import",
        "entity.name.package",
        "entity.name.namespace",
        "entity.name",
        "label",
    ],
    "link_text": [
        "markup.underline.link",
        "markup.link.label",
        "string.other.link.title",
        "string.other.link",
    ],
    "link_uri": [
        "markup.underline.link",
        "markup.link.url",
        "markup.underline.link.image",
        "string.other.link.description",
        "string.other.link",
    ],
    "number": ["constant.numeric", "constant.numeric.integer", "constant.numeric.float", "number"],
    "operator": ["keyword.operator", "keyword.operator.assignment", "operator"],
    "predictive": ["meta.inline-completion", "meta.predictive"],
    "preproc": [
        "meta.preprocessor",
        "keyword.control.directive",
        "keyword.control.directive.define",
        "punctuation.definition.preprocessor",
        "entity.name.function.preprocessor",
        "preproc",
    ],
    "primary": ["markup.heading", "entity.name.type", "entity.name.function"],
    "property": [
        "variable.other.property",
        "variable.object.property",
        "variable.other.field",
        "variable.member",
        "support.type.property-name",
        "meta.object-literal.key",
    ],
    "punctuation": [
        "punctuation",
        "punctuation.section",
        "punctuation.accessor",
        "punctuation.separator",
        "punctuation.definition.tag",
    ],
    "punctuation.bracket": [
        "punctuation.bracket",
        "punctuation.section.braces",
        "punctuation.section.brackets",
        "punctuation.section.parens",
        "punctuation.definition.tag.begin",
        "punctuation.definition.tag.end",
    ],
    "punctuation.delimiter": [
        "punctuation.delimiter",
        "punctuation.separator",
        "punctuation.separator.comma",
        "punctuation.terminator",
    ],
    "punctuation.list_marker": [
        "markup.list punctuation.definition.list.begin",
        "punctuation.definition.list.begin",
        "markup.list.bullet",
        "markup.list.numbered",
    ],
    "punctuation.special": [
        "punctuation.special",
        "punctuation.definition.template-expression",
        "punctuation.definition.interpolation",
    ],
    "string": ["string.quoted", "string.template", "string"],
    "string.escape": [
        "constant.character.escape",
        "string.escape",
        "constant.character",
        "constant.other",
    ],
    "string.regex": ["string.regexp", "string.regex", "constant.regexp"],
    "string.special": [
        "string.special",
        "string.interpolated",
        "constant.other.symbol",
    ],
    "string.special.symbol": [
        "constant.other.symbol",
        "string.special.symbol",
        "constant.language.symbol",
    ],
    "tag": ["entity.name.tag", "meta.tag.sgml", "entity.name.tag.custom", "tag"],
    "text.literal": [
        "markup.raw",
        "markup.inline.raw",
        "text.literal",
        "string",
    ],
    "title": [
        "markup.heading",
        "entity.name.section",
        "entity.name.type.module",
        "entity.name",
        "title",
    ],
    "type": [
        "entity.name.type.class",
        "entity.name.type.interface",
        "entity.name.type.struct",
        "entity.name.type.enum",
        "entity.name.type",
        "entity.name.type.primitive",
        "entity.name.type.numeric",
        "keyword.type",
        "support.type.primitive",
        "support.type",
        "support.class",
        "storage.type",
    ],
    "variable": [
        "variable.parameter",
        "variable.other.readwrite",
        "variable.other",
        "variable.language",
        "variable",
    ],
    "variable.special": [
        "variable.language.this",
        "variable.language.self",
        "variable.language.super",
        "variable.annotation",
        "variable.special",
        "variable.language",
    ],
    "variant": [
        "variable.other.enummember",
        "constant.other.enum",
        "constant.language.enum",
        "entity.name.constant",
        "variant",
    ],
}

SEMANTIC_TOKEN_MAP: dict[str, list[str]] = {
    "attribute": ["decorator"],
    "boolean": ["boolean"],
    "comment": ["comment"],
    "constant": ["enumMember", "variable.readonly", "property.readonly"],
    "constructor": ["class", "struct"],
    "enum": ["enum"],
    "function": ["function", "method"],
    "keyword": ["keyword", "modifier"],
    "label": ["label", "namespace"],
    "number": ["number"],
    "operator": ["operator"],
    "preproc": ["macro"],
    "property": ["property"],
    "string": ["string"],
    "string.regex": ["regexp"],
    "type": ["type", "class", "interface", "struct", "typeParameter"],
    "variable": ["parameter", "variable"],
    "variant": ["enumMember"],
}

SYNTAX_FALLBACKS: dict[str, list[str]] = {
    "comment.doc": ["comment"],
    "boolean": ["constant"],
    "constructor": ["type", "function"],
    "embedded": ["text.literal", "variable"],
    "emphasis": ["text.literal"],
    "emphasis.strong": ["emphasis", "text.literal"],
    "enum": ["type"],
    "hint": ["comment"],
    "label": ["variable"],
    "link_text": ["string"],
    "link_uri": ["link_text", "string"],
    "number": ["constant"],
    "predictive": ["comment"],
    "preproc": ["keyword"],
    "primary": ["keyword", "type"],
    "property": ["variable"],
    "punctuation.bracket": ["punctuation"],
    "punctuation.delimiter": ["punctuation"],
    "punctuation.list_marker": ["punctuation"],
    "punctuation.special": ["punctuation"],
    "string.escape": ["string"],
    "string.regex": ["string"],
    "string.special": ["string"],
    "string.special.symbol": ["string.special", "constant", "string"],
    "tag": ["type", "keyword"],
    "text.literal": ["string"],
    "title": ["type", "primary"],
    "variable.special": ["variable"],
    "variant": ["constant", "enum"],
}

# Current Zed runtime color keys that this migration deliberately populates.
# Some keys are newer than the published v0.2.0 schema; Zed supports them in runtime,
# and v0.2.0 allows additional properties.
REQUIRED_STYLE_KEYS = {
    "background.appearance",
    "background",
    "surface.background",
    "elevated_surface.background",
    "border",
    "border.variant",
    "border.focused",
    "border.selected",
    "border.transparent",
    "border.disabled",
    "element.background",
    "element.hover",
    "element.active",
    "element.selected",
    "element.disabled",
    "element.selection_background",
    "drop_target.background",
    "drop_target.border",
    "ghost_element.background",
    "ghost_element.hover",
    "ghost_element.active",
    "ghost_element.selected",
    "ghost_element.disabled",
    "text",
    "text.muted",
    "text.placeholder",
    "text.disabled",
    "text.accent",
    "icon",
    "icon.muted",
    "icon.placeholder",
    "icon.disabled",
    "icon.accent",
    "debugger.accent",
    "status_bar.background",
    "title_bar.background",
    "title_bar.inactive_background",
    "toolbar.background",
    "tab_bar.background",
    "tab.active_background",
    "tab.inactive_background",
    "search.match_background",
    "search.active_match_background",
    "panel.background",
    "panel.focused_border",
    "panel.indent_guide",
    "panel.indent_guide_hover",
    "panel.indent_guide_active",
    "panel.overlay_background",
    "panel.overlay_hover",
    "pane.focused_border",
    "pane_group.border",
    "scrollbar.thumb.background",
    "scrollbar.thumb.hover_background",
    "scrollbar.thumb.active_background",
    "scrollbar.thumb.border",
    "scrollbar.track.background",
    "scrollbar.track.border",
    "minimap.thumb.background",
    "minimap.thumb.hover_background",
    "minimap.thumb.active_background",
    "minimap.thumb.border",
    "editor.foreground",
    "editor.code_lens.foreground",
    "editor.background",
    "editor.gutter.background",
    "editor.subheader.background",
    "editor.active_line.background",
    "editor.highlighted_line.background",
    "editor.debugger_active_line.background",
    "editor.line_number",
    "editor.active_line_number",
    "editor.hover_line_number",
    "editor.invisible",
    "editor.wrap_guide",
    "editor.active_wrap_guide",
    "editor.indent_guide",
    "editor.indent_guide_active",
    "editor.document_highlight.read_background",
    "editor.document_highlight.write_background",
    "editor.document_highlight.bracket_background",
    "editor.diff_hunk.added.background",
    "editor.diff_hunk.added.hollow_background",
    "editor.diff_hunk.added.hollow_border",
    "editor.diff_hunk.deleted.background",
    "editor.diff_hunk.deleted.hollow_background",
    "editor.diff_hunk.deleted.hollow_border",
    "terminal.background",
    "terminal.foreground",
    "terminal.ansi.background",
    "terminal.bright_foreground",
    "terminal.dim_foreground",
    "terminal.ansi.black",
    "terminal.ansi.bright_black",
    "terminal.ansi.dim_black",
    "terminal.ansi.red",
    "terminal.ansi.bright_red",
    "terminal.ansi.dim_red",
    "terminal.ansi.green",
    "terminal.ansi.bright_green",
    "terminal.ansi.dim_green",
    "terminal.ansi.yellow",
    "terminal.ansi.bright_yellow",
    "terminal.ansi.dim_yellow",
    "terminal.ansi.blue",
    "terminal.ansi.bright_blue",
    "terminal.ansi.dim_blue",
    "terminal.ansi.magenta",
    "terminal.ansi.bright_magenta",
    "terminal.ansi.dim_magenta",
    "terminal.ansi.cyan",
    "terminal.ansi.bright_cyan",
    "terminal.ansi.dim_cyan",
    "terminal.ansi.white",
    "terminal.ansi.bright_white",
    "terminal.ansi.dim_white",
    "link_text.hover",
    "version_control.added",
    "version_control.deleted",
    "version_control.modified",
    "version_control.renamed",
    "version_control.conflict",
    "version_control.ignored",
    "version_control.word_added",
    "version_control.word_deleted",
    "version_control.conflict_marker.ours",
    "version_control.conflict_marker.theirs",
    "vim.normal.background",
    "vim.insert.background",
    "vim.replace.background",
    "vim.visual.background",
    "vim.visual_line.background",
    "vim.visual_block.background",
    "vim.yank.background",
    "vim.helix_jump_label.foreground",
    "vim.helix_normal.background",
    "vim.helix_select.background",
    "vim.normal.foreground",
    "vim.insert.foreground",
    "vim.replace.foreground",
    "vim.visual.foreground",
    "vim.visual_line.foreground",
    "vim.visual_block.foreground",
    "vim.helix_normal.foreground",
    "vim.helix_select.foreground",
    "conflict",
    "conflict.background",
    "conflict.border",
    "created",
    "created.background",
    "created.border",
    "deleted",
    "deleted.background",
    "deleted.border",
    "error",
    "error.background",
    "error.border",
    "hidden",
    "hidden.background",
    "hidden.border",
    "hint",
    "hint.background",
    "hint.border",
    "ignored",
    "ignored.background",
    "ignored.border",
    "info",
    "info.background",
    "info.border",
    "modified",
    "modified.background",
    "modified.border",
    "predictive",
    "predictive.background",
    "predictive.border",
    "renamed",
    "renamed.background",
    "renamed.border",
    "success",
    "success.background",
    "success.border",
    "unreachable",
    "unreachable.background",
    "unreachable.border",
    "warning",
    "warning.background",
    "warning.border",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_color(value: Any) -> bool:
    return isinstance(value, str) and COLOR_RE.fullmatch(value) is not None


def normalize_color(value: str) -> str:
    return value.lower()


def expand_rgb(value: str) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    if len(value) in (3, 4):
        value = "".join(ch * 2 for ch in value)
    if len(value) == 6:
        value += "ff"
    if len(value) != 8:
        raise ValueError(f"Invalid color: #{value}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4, 6))  # type: ignore[return-value]


def with_alpha(value: str, alpha: int) -> str:
    r, g, b, _ = expand_rgb(value)
    return f"#{r:02x}{g:02x}{b:02x}{max(0, min(255, alpha)):02x}"


def first_color(colors: dict[str, Any], *keys: str, fallback: str | None = None) -> str | None:
    for key in keys:
        value = colors.get(key)
        if is_color(value):
            return normalize_color(value)
    if fallback is not None:
        if not is_color(fallback):
            raise ValueError(f"Fallback is not a color: {fallback}")
        return normalize_color(fallback)
    return None


def dedupe_colors(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value is None or not is_color(value):
            continue
        value = normalize_color(value)
        rgb = value[:7] if len(value) in (7, 9) else value
        if rgb not in seen:
            seen.add(rgb)
            out.append(value)
    return out


def token_default_foreground(theme: dict[str, Any]) -> str | None:
    for rule in theme.get("tokenColors", []):
        if rule.get("scope") is None:
            value = rule.get("settings", {}).get("foreground")
            if is_color(value):
                return normalize_color(value)
    return None


def split_scope(scope: str) -> list[str]:
    # TextMate selectors may be comma-separated and/or contextual selectors separated by spaces.
    return [part.strip() for chunk in scope.split(",") for part in chunk.split() if part.strip()]


def rule_scopes(rule: dict[str, Any]) -> list[str]:
    scope = rule.get("scope")
    if isinstance(scope, str):
        return split_scope(scope)
    if isinstance(scope, list):
        return [part for item in scope if isinstance(item, str) for part in split_scope(item)]
    return []


def scope_similarity(candidate: str, target: str) -> int:
    if candidate == target:
        return 1000 + candidate.count(".") * 5
    if candidate.startswith(target + "."):
        return 850 + candidate.count(".") * 5
    if target.startswith(candidate + "."):
        return 700 + candidate.count(".") * 5
    return 0


def best_textmate_rule(theme: dict[str, Any], targets: list[str]) -> dict[str, Any] | None:
    best: tuple[int, int, dict[str, Any]] | None = None
    rules = theme.get("tokenColors", [])
    for index, rule in enumerate(rules):
        settings = rule.get("settings", {})
        if not any(settings.get(k) for k in ("foreground", "background", "fontStyle")):
            continue
        scopes = rule_scopes(rule)
        if not scopes:
            continue
        for priority, target in enumerate(targets):
            for candidate in scopes:
                score = scope_similarity(candidate, target)
                if not score:
                    continue
                # Earlier targets carry more semantic priority; later VS Code rules win ties.
                total = score + (len(targets) - priority) * 100 + index
                if best is None or total > best[0]:
                    best = (total, index, rule)
    return best[2] if best else None


def parse_highlight_settings(settings: Any) -> dict[str, Any] | None:
    if isinstance(settings, str):
        if is_color(settings):
            return {"color": normalize_color(settings)}
        return None
    if not isinstance(settings, dict):
        return None
    style: dict[str, Any] = {}
    foreground = settings.get("foreground")
    background = settings.get("background")
    font_style = settings.get("fontStyle", "")
    if is_color(foreground):
        style["color"] = normalize_color(foreground)
    if is_color(background):
        style["background_color"] = normalize_color(background)
    if isinstance(font_style, str):
        if "italic" in font_style:
            style["font_style"] = "italic"
        elif "oblique" in font_style:
            style["font_style"] = "oblique"
        if "bold" in font_style:
            style["font_weight"] = 700
    return style or None


def semantic_style(theme: dict[str, Any], candidates: list[str]) -> dict[str, Any] | None:
    semantic = theme.get("semanticTokenColors", {})
    if not isinstance(semantic, dict):
        return None
    for candidate in candidates:
        if candidate in semantic:
            style = parse_highlight_settings(semantic[candidate])
            if style:
                return style
        # Accept a semantic token with modifiers when the base token is requested.
        for selector, settings in semantic.items():
            if isinstance(selector, str) and selector.split(".", 1)[0] == candidate:
                style = parse_highlight_settings(settings)
                if style:
                    return style
    return None


def build_syntax(theme: dict[str, Any], base_fg: str, muted: str, accent: str) -> tuple[dict[str, Any], dict[str, int]]:
    syntax: dict[str, Any] = {}
    stats = {"textmate": 0, "semantic": 0, "fallback": 0, "derived": 0}

    for token in ZED_SYNTAX_TOKENS:
        rule = best_textmate_rule(theme, SYNTAX_SCOPE_MAP[token])
        if rule:
            style = parse_highlight_settings(rule.get("settings", {}))
            if style:
                syntax[token] = style
                stats["textmate"] += 1
                continue
        style = semantic_style(theme, SEMANTIC_TOKEN_MAP.get(token, []))
        if style:
            syntax[token] = style
            stats["semantic"] += 1

    # Fill semantic relatives after all direct matches have been collected.
    changed = True
    while changed:
        changed = False
        for token in ZED_SYNTAX_TOKENS:
            if token in syntax:
                continue
            for fallback in SYNTAX_FALLBACKS.get(token, []):
                if fallback in syntax:
                    syntax[token] = dict(syntax[fallback])
                    stats["fallback"] += 1
                    changed = True
                    break

    # Zed supports these captures even when VS Code has no direct equivalent. Give every capture
    # a deterministic Kintsugi value instead of relying on a Zed default from another theme.
    default_colors = {
        "comment": muted,
        "comment.doc": muted,
        "hint": muted,
        "predictive": muted,
        "punctuation": muted,
        "punctuation.bracket": muted,
        "punctuation.delimiter": muted,
        "punctuation.list_marker": muted,
        "punctuation.special": accent,
        "primary": accent,
        "link_text": accent,
        "link_uri": accent,
    }
    for token in ZED_SYNTAX_TOKENS:
        if token not in syntax:
            syntax[token] = {"color": default_colors.get(token, base_fg)}
            stats["derived"] += 1

    return syntax, stats


def set_status_triplet(style: dict[str, Any], name: str, fg: str, bg: str | None = None, border: str | None = None) -> None:
    style[name] = fg
    style[f"{name}.background"] = bg or with_alpha(fg, 0x18)
    style[f"{name}.border"] = border or with_alpha(fg, 0x70)


def build_style(theme: dict[str, Any], appearance: str) -> dict[str, Any]:
    c = theme.get("colors", {})
    if not isinstance(c, dict):
        raise ValueError("theme.colors must be an object")

    base_bg = first_color(c, "editor.background", "background") or ("#161618" if appearance == "dark" else "#f8f4ea")
    base_fg = first_color(c, "editor.foreground", "foreground", fallback=token_default_foreground(theme) or ("#dddddd" if appearance == "dark" else "#3d392f"))
    panel_bg = first_color(c, "sideBar.background", "panel.background", "activityBar.background", fallback=base_bg) or base_bg
    surface = first_color(c, "panel.background", "sideBar.background", "tab.inactiveBackground", fallback=panel_bg) or panel_bg
    elevated = first_color(c, "dropdown.background", "editorWidget.background", "menu.background", "quickInput.background", fallback=surface) or surface
    border = first_color(c, "panel.border", "sideBar.border", "editorGroup.border", "input.border", fallback=with_alpha(base_fg, 0x22)) or with_alpha(base_fg, 0x22)
    accent = first_color(c, "focusBorder", "activityBar.activeBorder", "editorCursor.foreground", "textLink.foreground", "notificationLink.foreground", fallback=base_fg) or base_fg
    muted = first_color(c, "tab.inactiveForeground", "sideBarTitle.foreground", "breadcrumb.foreground", "descriptionForeground", fallback=with_alpha(base_fg, 0x99)) or with_alpha(base_fg, 0x99)
    placeholder = first_color(c, "input.placeholderForeground", fallback=with_alpha(muted, 0x99)) or with_alpha(muted, 0x99)

    selected = first_color(c, "list.activeSelectionBackground", "editor.selectionBackground", fallback=with_alpha(accent, 0x33)) or with_alpha(accent, 0x33)
    hover = first_color(c, "list.hoverBackground", "button.hoverBackground", fallback=with_alpha(base_fg, 0x10)) or with_alpha(base_fg, 0x10)
    active = first_color(c, "list.focusBackground", "list.activeSelectionBackground", fallback=selected) or selected
    disabled_bg = first_color(c, "button.secondaryBackground", "settings.checkboxBackground", fallback=with_alpha(muted, 0x18)) or with_alpha(muted, 0x18)
    transparent = with_alpha(border, 0x00)

    error = first_color(c, "editorError.foreground", "problemsErrorIcon.foreground", "notificationsErrorIcon.foreground", fallback="#b85c5c") or "#b85c5c"
    warning = first_color(c, "editorWarning.foreground", "problemsWarningIcon.foreground", "notificationsWarningIcon.foreground", fallback=accent) or accent
    info = first_color(c, "editorInfo.foreground", "problemsInfoIcon.foreground", "notificationsInfoIcon.foreground", fallback=accent) or accent
    hint = first_color(c, "editorHint.foreground", "editorInlayHint.foreground", fallback=muted) or muted
    success = first_color(c, "gitDecoration.addedResourceForeground", "editorGutter.addedBackground", fallback=hint) or hint
    modified = first_color(c, "gitDecoration.modifiedResourceForeground", "editorGutter.modifiedBackground", fallback=warning) or warning
    deleted = first_color(c, "gitDecoration.deletedResourceForeground", "editorGutter.deletedBackground", fallback=error) or error
    conflict = first_color(c, "gitDecoration.conflictingResourceForeground", fallback=error) or error
    ignored = first_color(c, "gitDecoration.ignoredResourceForeground", fallback=muted) or muted
    renamed = first_color(c, "gitDecoration.renamedResourceForeground", fallback=info) or info
    predictive = first_color(c, "editorGhostText.foreground", fallback=muted) or muted

    editor_line = first_color(c, "editor.lineHighlightBackground", fallback=with_alpha(base_fg, 0x08)) or with_alpha(base_fg, 0x08)
    line_number = first_color(c, "editorLineNumber.foreground", fallback=muted) or muted
    active_line_number = first_color(c, "editorLineNumber.activeForeground", "editor.foreground", fallback=base_fg) or base_fg
    indent = first_color(c, "editorIndentGuide.background1", "tree.indentGuidesStroke", fallback=with_alpha(border, 0x70)) or with_alpha(border, 0x70)
    indent_active = first_color(c, "editorIndentGuide.activeBackground1", fallback=with_alpha(accent, 0x60)) or with_alpha(accent, 0x60)
    scrollbar = first_color(c, "scrollbarSlider.background", fallback=with_alpha(muted, 0x55)) or with_alpha(muted, 0x55)
    scrollbar_hover = first_color(c, "scrollbarSlider.hoverBackground", fallback=with_alpha(muted, 0x88)) or with_alpha(muted, 0x88)
    scrollbar_active = first_color(c, "scrollbarSlider.activeBackground", fallback=with_alpha(accent, 0x88)) or with_alpha(accent, 0x88)

    style: dict[str, Any] = {
        "background.appearance": "opaque",
        "background": base_bg,
        "surface.background": surface,
        "elevated_surface.background": elevated,
        "border": border,
        "border.variant": first_color(c, "editorGroupHeader.tabsBorder", "panelSection.border", fallback=border),
        "border.focused": first_color(c, "focusBorder", "sash.hoverBorder", fallback=accent),
        "border.selected": first_color(c, "inputOption.activeBorder", "focusBorder", fallback=accent),
        "border.transparent": transparent,
        "border.disabled": with_alpha(border, 0x70),
        "element.background": first_color(c, "button.background", "input.background", fallback=surface),
        "element.hover": hover,
        "element.active": active,
        "element.selected": selected,
        "element.disabled": disabled_bg,
        "element.selection_background": selected,
        "drop_target.background": first_color(c, "list.dropBackground", "editorGroup.dropBackground", fallback=with_alpha(accent, 0x30)),
        "drop_target.border": first_color(c, "list.dropBetweenBackground", "focusBorder", fallback=accent),
        "ghost_element.background": surface,
        "ghost_element.hover": hover,
        "ghost_element.active": active,
        "ghost_element.selected": selected,
        "ghost_element.disabled": with_alpha(disabled_bg, 0x80),
        "text": first_color(c, "foreground", "editor.foreground", fallback=base_fg),
        "text.muted": muted,
        "text.placeholder": placeholder,
        "text.disabled": with_alpha(muted, 0x80),
        "text.accent": first_color(c, "textLink.foreground", "notificationLink.foreground", fallback=accent),
        "icon": first_color(c, "activityBar.foreground", "sideBar.foreground", fallback=base_fg),
        "icon.muted": first_color(c, "activityBar.inactiveForeground", "sideBarTitle.foreground", fallback=muted),
        "icon.placeholder": placeholder,
        "icon.disabled": with_alpha(muted, 0x80),
        "icon.accent": accent,
        "debugger.accent": first_color(c, "debugIcon.breakpointForeground", "statusBar.debuggingBackground", fallback=accent),
        "status_bar.background": first_color(c, "statusBar.background", fallback=panel_bg),
        "title_bar.background": first_color(c, "titleBar.activeBackground", "activityBar.background", fallback=panel_bg),
        "title_bar.inactive_background": first_color(c, "titleBar.inactiveBackground", "activityBar.background", fallback=panel_bg),
        "toolbar.background": first_color(c, "breadcrumb.background", "editor.background", fallback=base_bg),
        "tab_bar.background": first_color(c, "editorGroupHeader.tabsBackground", "editorGroupHeader.noTabsBackground", fallback=panel_bg),
        "tab.active_background": first_color(c, "tab.activeBackground", fallback=base_bg),
        "tab.inactive_background": first_color(c, "tab.inactiveBackground", fallback=surface),
        "search.match_background": first_color(c, "editor.findMatchHighlightBackground", "editor.findMatchBackground", fallback=with_alpha(accent, 0x30)),
        "search.active_match_background": first_color(c, "editor.findMatchBackground", fallback=with_alpha(accent, 0x55)),
        "panel.background": first_color(c, "panel.background", "sideBar.background", fallback=panel_bg),
        "panel.focused_border": first_color(c, "panelTitle.activeBorder", "focusBorder", fallback=accent),
        "panel.indent_guide": indent,
        "panel.indent_guide_hover": first_color(c, "tree.indentGuidesStroke", fallback=indent_active),
        "panel.indent_guide_active": indent_active,
        "panel.overlay_background": first_color(c, "quickInput.background", "editorWidget.background", fallback=elevated),
        "panel.overlay_hover": first_color(c, "quickInputList.focusBackground", "list.hoverBackground", fallback=hover),
        "pane.focused_border": first_color(c, "focusBorder", fallback=accent),
        "pane_group.border": first_color(c, "editorGroup.border", fallback=border),
        "scrollbar.thumb.background": scrollbar,
        "scrollbar.thumb.hover_background": scrollbar_hover,
        "scrollbar.thumb.active_background": scrollbar_active,
        "scrollbar.thumb.border": with_alpha(scrollbar, 0x00),
        "scrollbar.track.background": first_color(c, "editor.background", fallback=base_bg),
        "scrollbar.track.border": first_color(c, "editorOverviewRuler.border", fallback=transparent),
        "minimap.thumb.background": first_color(c, "minimapSlider.background", fallback=scrollbar),
        "minimap.thumb.hover_background": first_color(c, "minimapSlider.hoverBackground", fallback=scrollbar_hover),
        "minimap.thumb.active_background": first_color(c, "minimapSlider.activeBackground", fallback=scrollbar_active),
        "minimap.thumb.border": transparent,
        "editor.foreground": base_fg,
        "editor.code_lens.foreground": first_color(c, "editorCodeLens.foreground", fallback=muted),
        "editor.background": base_bg,
        "editor.gutter.background": first_color(c, "editorGutter.background", "editor.background", fallback=base_bg),
        "editor.subheader.background": first_color(c, "editorGroupHeader.tabsBackground", "breadcrumb.background", fallback=surface),
        "editor.active_line.background": editor_line,
        "editor.highlighted_line.background": first_color(c, "editor.rangeHighlightBackground", "editor.lineHighlightBackground", fallback=editor_line),
        "editor.debugger_active_line.background": first_color(c, "editor.stackFrameHighlightBackground", "editor.lineHighlightBackground", fallback=editor_line),
        "editor.line_number": line_number,
        "editor.active_line_number": active_line_number,
        "editor.hover_line_number": first_color(c, "editorLineNumber.activeForeground", fallback=active_line_number),
        "editor.invisible": first_color(c, "editorWhitespace.foreground", fallback=with_alpha(muted, 0x70)),
        "editor.wrap_guide": first_color(c, "editorRuler.foreground", fallback=indent),
        "editor.active_wrap_guide": first_color(c, "editorIndentGuide.activeBackground1", fallback=indent_active),
        "editor.indent_guide": indent,
        "editor.indent_guide_active": indent_active,
        "editor.document_highlight.read_background": first_color(c, "editor.wordHighlightTextBackground", "editor.wordHighlightBackground", fallback=with_alpha(info, 0x22)),
        "editor.document_highlight.write_background": first_color(c, "editor.wordHighlightStrongBackground", fallback=with_alpha(accent, 0x30)),
        "editor.document_highlight.bracket_background": first_color(c, "editorBracketMatch.background", fallback=with_alpha(accent, 0x30)),
        "editor.diff_hunk.added.background": first_color(c, "diffEditor.insertedLineBackground", "diffEditorGutter.insertedLineBackground", fallback=with_alpha(success, 0x18)),
        "editor.diff_hunk.added.hollow_background": first_color(c, "diffEditor.insertedTextBackground", fallback=with_alpha(success, 0x12)),
        "editor.diff_hunk.added.hollow_border": first_color(c, "editorGutter.addedBackground", fallback=success),
        "editor.diff_hunk.deleted.background": first_color(c, "diffEditor.removedLineBackground", "diffEditorGutter.removedLineBackground", fallback=with_alpha(deleted, 0x18)),
        "editor.diff_hunk.deleted.hollow_background": first_color(c, "diffEditor.removedTextBackground", fallback=with_alpha(deleted, 0x12)),
        "editor.diff_hunk.deleted.hollow_border": first_color(c, "editorGutter.deletedBackground", fallback=deleted),
        "terminal.background": first_color(c, "terminal.background", fallback=panel_bg),
        "terminal.foreground": first_color(c, "terminal.foreground", "editor.foreground", fallback=base_fg),
        "terminal.ansi.background": first_color(c, "terminal.background", fallback=panel_bg),
        "terminal.bright_foreground": first_color(c, "terminal.ansiBrightWhite", "terminal.foreground", fallback=base_fg),
        "terminal.dim_foreground": with_alpha(first_color(c, "terminal.foreground", fallback=base_fg) or base_fg, 0x99),
        "link_text.hover": first_color(c, "textLink.activeForeground", "textLink.foreground", "notificationLink.foreground", fallback=accent),
        "version_control.added": success,
        "version_control.deleted": deleted,
        "version_control.modified": modified,
        "version_control.renamed": renamed,
        "version_control.conflict": conflict,
        "version_control.ignored": ignored,
        "version_control.word_added": first_color(c, "diffEditor.insertedTextBackground", fallback=with_alpha(success, 0x35)),
        "version_control.word_deleted": first_color(c, "diffEditor.removedTextBackground", fallback=with_alpha(deleted, 0x35)),
        "version_control.conflict_marker.ours": first_color(c, "merge.currentHeaderBackground", fallback=with_alpha(success, 0x20)),
        "version_control.conflict_marker.theirs": first_color(c, "merge.incomingHeaderBackground", fallback=with_alpha(info, 0x20)),
    }

    ansi_names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    for name in ansi_names:
        lower = name.lower()
        normal = first_color(c, f"terminal.ansi{name}", fallback=base_fg if name == "White" else muted) or muted
        bright = first_color(c, f"terminal.ansiBright{name}", fallback=normal) or normal
        style[f"terminal.ansi.{lower}"] = normal
        style[f"terminal.ansi.bright_{lower}"] = bright
        style[f"terminal.ansi.dim_{lower}"] = with_alpha(normal, 0x99)

    # Complete status palette. Backgrounds and borders prefer original diagnostic/validation colors.
    set_status_triplet(
        style,
        "error",
        error,
        first_color(c, "inputValidation.errorBackground", "editorError.background", fallback=with_alpha(error, 0x18)),
        first_color(c, "inputValidation.errorBorder", "editorError.border", fallback=with_alpha(error, 0x70)),
    )
    set_status_triplet(
        style,
        "warning",
        warning,
        first_color(c, "inputValidation.warningBackground", "editorWarning.background", fallback=with_alpha(warning, 0x18)),
        first_color(c, "inputValidation.warningBorder", "editorWarning.border", fallback=with_alpha(warning, 0x70)),
    )
    set_status_triplet(
        style,
        "info",
        info,
        first_color(c, "inputValidation.infoBackground", "editorInfo.background", fallback=with_alpha(info, 0x18)),
        first_color(c, "inputValidation.infoBorder", "editorInfo.border", fallback=with_alpha(info, 0x70)),
    )
    set_status_triplet(style, "hint", hint)
    set_status_triplet(style, "success", success)
    set_status_triplet(style, "created", success)
    set_status_triplet(style, "modified", modified)
    set_status_triplet(style, "deleted", deleted)
    set_status_triplet(style, "conflict", conflict)
    set_status_triplet(style, "ignored", ignored)
    set_status_triplet(style, "renamed", renamed)
    set_status_triplet(style, "predictive", predictive)
    set_status_triplet(style, "hidden", muted, with_alpha(muted, 0x0c), with_alpha(muted, 0x50))
    set_status_triplet(style, "unreachable", muted, with_alpha(muted, 0x0c), with_alpha(muted, 0x50))

    visual_bg = first_color(c, "editor.selectionBackground", fallback=with_alpha(accent, 0x35)) or with_alpha(accent, 0x35)
    normal_bg = first_color(c, "statusBar.background", fallback=panel_bg) or panel_bg
    style.update(
        {
            "vim.normal.background": normal_bg,
            "vim.insert.background": with_alpha(success, 0x28),
            "vim.replace.background": with_alpha(error, 0x28),
            "vim.visual.background": visual_bg,
            "vim.visual_line.background": visual_bg,
            "vim.visual_block.background": visual_bg,
            "vim.yank.background": first_color(c, "editor.rangeHighlightBackground", fallback=with_alpha(accent, 0x30)),
            "vim.helix_jump_label.foreground": accent,
            "vim.helix_normal.background": normal_bg,
            "vim.helix_select.background": visual_bg,
            "vim.normal.foreground": base_fg,
            "vim.insert.foreground": base_fg,
            "vim.replace.foreground": base_fg,
            "vim.visual.foreground": base_fg,
            "vim.visual_line.foreground": base_fg,
            "vim.visual_block.foreground": base_fg,
            "vim.helix_normal.foreground": base_fg,
            "vim.helix_select.foreground": base_fg,
        }
    )

    accents = dedupe_colors(
        [
            accent,
            first_color(c, "activityBarBadge.background"),
            success,
            modified,
            deleted,
            info,
            first_color(c, "terminal.ansiBlue"),
            first_color(c, "terminal.ansiMagenta"),
            first_color(c, "terminal.ansiCyan"),
        ]
    )
    while len(accents) < 6:
        accents.append(with_alpha(accent, max(0x55, 0xFF - len(accents) * 0x18)))
    style["accents"] = accents
    style["players"] = [
        {
            "cursor": color,
            "background": with_alpha(color, 0x14),
            "selection": with_alpha(color, 0x38),
        }
        for color in accents[:8]
    ]

    syntax, _ = build_syntax(theme, base_fg, muted, accent)
    style["syntax"] = syntax
    return style


def assert_theme_complete(theme: dict[str, Any]) -> None:
    if theme.get("appearance") not in {"light", "dark"}:
        raise AssertionError(f"Invalid appearance: {theme.get('appearance')}")
    style = theme.get("style")
    if not isinstance(style, dict):
        raise AssertionError("Missing style object")
    missing = REQUIRED_STYLE_KEYS - set(style)
    if missing:
        raise AssertionError(f"Missing Zed style keys: {sorted(missing)}")
    syntax = style.get("syntax")
    if not isinstance(syntax, dict):
        raise AssertionError("Missing syntax object")
    missing_syntax = set(ZED_SYNTAX_TOKENS) - set(syntax)
    if missing_syntax:
        raise AssertionError(f"Missing syntax tokens: {sorted(missing_syntax)}")
    if len(style.get("accents", [])) < 6:
        raise AssertionError("Expected at least six accent colors")
    if len(style.get("players", [])) < 4:
        raise AssertionError("Expected at least four player colors")

    def walk(value: Any, path: str = "") -> None:
        if value is None:
            raise AssertionError(f"Null value at {path}")
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f"{path}.{key}" if path else key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]")
        elif isinstance(value, str) and (path.endswith("color") or path.split(".")[-1] in {
            "background", "foreground", "border", "text", "icon", "conflict", "created", "deleted",
            "error", "hidden", "hint", "ignored", "info", "modified", "predictive", "renamed", "success",
            "unreachable", "warning"
        }):
            if value not in {"opaque", "transparent", "blurred", "italic", "oblique", "normal"} and not is_color(value):
                raise AssertionError(f"Invalid color-like value at {path}: {value}")

    walk(style)


def schema_validate(documents: list[Path]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError as exc:
        raise SystemExit("--validate-schema requires the 'jsonschema' package") from exc
    with urllib.request.urlopen(SCHEMA_URL, timeout=30) as response:
        schema = json.load(response)
    validator = jsonschema.Draft7Validator(schema)
    failures: list[str] = []
    for path in documents:
        document = load_json(path)
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
            failures.append(f"{path}: {'/'.join(map(str, error.path))}: {error.message}")
    if failures:
        raise AssertionError("Schema validation failed:\n" + "\n".join(failures))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "dist" / "kintsugi-zed")
    parser.add_argument("--validate-schema", action="store_true")
    args = parser.parse_args()

    package = load_json(REPO_ROOT / "package.json")
    contributions = package.get("contributes", {}).get("themes", [])
    if not isinstance(contributions, list) or not contributions:
        raise AssertionError("package.json contributes.themes is empty")

    listed_paths = {str(item["path"]).removeprefix("./") for item in contributions}
    actual_paths = {str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in (REPO_ROOT / "themes").glob("*-color-theme.json")}
    if listed_paths != actual_paths:
        raise AssertionError(
            "Theme inventory mismatch. package.json and themes/*.json must agree exactly.\n"
            f"Only in package.json: {sorted(listed_paths - actual_paths)}\n"
            f"Only on disk: {sorted(actual_paths - listed_paths)}"
        )
    if len(contributions) != 8:
        raise AssertionError(f"Expected the current Kintsugi set of 8 variants, found {len(contributions)}")

    out = args.output.resolve()
    local_dir = out / "local"
    combined_dir = out / "combined"
    local_dir.mkdir(parents=True, exist_ok=True)
    combined_dir.mkdir(parents=True, exist_ok=True)

    themes: list[dict[str, Any]] = []
    manifest_entries: list[dict[str, Any]] = []
    output_docs: list[Path] = []

    for item in contributions:
        source_rel = str(item["path"]).removeprefix("./")
        source = REPO_ROOT / source_rel
        source_bytes = source.read_bytes()
        source_theme = json.loads(source_bytes)
        label = str(item.get("label") or source_theme.get("name") or source.stem)
        ui_theme = str(item.get("uiTheme", ""))
        appearance = "dark" if "dark" in ui_theme else "light"

        style = build_style(source_theme, appearance)
        zed_theme = {"name": label, "appearance": appearance, "style": style}
        assert_theme_complete(zed_theme)
        themes.append(zed_theme)

        file_name = source.name.replace("-color-theme.json", ".json")
        individual = {
            "$schema": SCHEMA_URL,
            "name": "Kintsugi",
            "author": package.get("author", {}).get("name", "Ahmed Hatem"),
            "themes": [zed_theme],
        }
        target = local_dir / file_name
        write_json(target, individual)
        output_docs.append(target)

        _, syntax_stats = build_syntax(
            source_theme,
            style["editor.foreground"],
            style["text.muted"],
            style["text.accent"],
        )
        manifest_entries.append(
            {
                "source": source_rel,
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "output": str(target.relative_to(out)).replace("\\", "/"),
                "name": label,
                "appearance": appearance,
                "style_key_count": len(style) - 3,  # accents, players, syntax are structured collections
                "syntax_token_count": len(style["syntax"]),
                "syntax_resolution": syntax_stats,
                "accent_count": len(style["accents"]),
                "player_count": len(style["players"]),
            }
        )

    if len({theme["name"] for theme in themes}) != 8:
        raise AssertionError("Duplicate Zed theme names detected")

    combined = {
        "$schema": SCHEMA_URL,
        "name": "Kintsugi",
        "author": package.get("author", {}).get("name", "Ahmed Hatem"),
        "themes": themes,
    }
    combined_path = combined_dir / "Kintsugi.json"
    write_json(combined_path, combined)
    output_docs.append(combined_path)

    manifest = {
        "source_repository": package.get("repository", {}).get("url", "https://github.com/ahatem/vscode-kintsugi.git"),
        "source_version": package.get("version"),
        "zed_schema": SCHEMA_URL,
        "theme_count": len(themes),
        "required_runtime_style_keys": len(REQUIRED_STYLE_KEYS),
        "required_syntax_tokens": len(ZED_SYNTAX_TOKENS),
        "themes": manifest_entries,
    }
    write_json(out / "manifest.json", manifest)

    report_lines = [
        "# Kintsugi → Zed migration report",
        "",
        f"Generated from **{len(themes)} / {len(themes)}** themes declared by `package.json`.",
        "",
        "## What is covered",
        "",
        f"- **{len(REQUIRED_STYLE_KEYS)}** populated Zed UI/status/runtime color keys per theme (no null placeholders).",
        f"- **{len(ZED_SYNTAX_TOKENS)} / {len(ZED_SYNTAX_TOKENS)}** Zed syntax captures populated per theme.",
        "- Original terminal ANSI palettes preserved, with deterministic dim variants.",
        "- Original diagnostic/status colors mapped, plus complete background/border triplets.",
        "- Version-control, diff-hunk, scrollbar/minimap, Vim/Helix, accents and collaboration colors populated.",
        "- TextMate foreground/background and italic/bold styles preserved when Zed can represent them.",
        "- `semanticTokenColors` used as a fallback when a TextMate match is unavailable.",
        "",
        "## Files",
        "",
        "- `local/*.json`: eight standalone files. Copy all of them into Zed's local themes directory.",
        "- `combined/Kintsugi.json`: one Zed theme family containing all eight variants; useful for a Zed theme extension.",
        "- `manifest.json`: source hashes and coverage statistics for every variant.",
        "",
        "On Windows, local Zed themes live under `%USERPROFILE%\\AppData\\Roaming\\Zed\\themes\\`.",
        "",
        "## Important semantic limit",
        "",
        "VS Code/TextMate and Zed/Tree-sitter do not expose identical syntax taxonomies. Some distinctions that exist in a VS Code theme cannot be represented as separate Zed theme captures (for example, certain storage/declaration keyword distinctions). The migration resolves those collisions deterministically using ordered scope priority; it does not silently omit the token. Every Zed capture receives a Kintsugi value.",
        "",
        "## Variant coverage",
        "",
        "| Theme | Appearance | UI keys | Syntax | TextMate | Semantic | Fallback | Derived |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in manifest_entries:
        stats = entry["syntax_resolution"]
        report_lines.append(
            f"| {entry['name']} | {entry['appearance']} | {entry['style_key_count']} | {entry['syntax_token_count']}/{len(ZED_SYNTAX_TOKENS)} | "
            f"{stats['textmate']} | {stats['semantic']} | {stats['fallback']} | {stats['derived']} |"
        )
    (out / "MIGRATION_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if args.validate_schema:
        schema_validate(output_docs)

    print(f"Generated {len(themes)} Zed themes in {out}")
    print(f"Validated {len(REQUIRED_STYLE_KEYS)} required runtime style keys and {len(ZED_SYNTAX_TOKENS)} syntax captures per theme")
    if args.validate_schema:
        print(f"Validated {len(output_docs)} JSON documents against {SCHEMA_URL}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
