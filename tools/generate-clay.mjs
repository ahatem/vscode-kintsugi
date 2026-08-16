/**
 * Generates the Clay variants from the base themes.
 *
 * A Clay theme is its namesake with the interface re-tinted to the QTranslate palette — bronze and
 * parchment in place of neutral grey — and the syntax left exactly as it was. So this rewrites only
 * the chrome colours in `colors`, and copies `tokenColors` and `semanticTokenColors` untouched.
 *
 * Mapping the chrome rather than every colour is the point. The base themes use around 60 distinct
 * values, most of them syntax or semantic — diff greens, error reds, the gold accent — which a Clay
 * variant must keep identical or it stops being the same theme.
 *
 * The mappings live in clay-map.json, not here, so the data can be read by anything.
 *
 * Usage:  node tools/generate-clay.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const toolsDir = dirname(fileURLToPath(import.meta.url));
const themesDir = join(toolsDir, '..', 'themes');

const { dark: DARK, light: LIGHT } = JSON.parse(
  readFileSync(join(toolsDir, 'clay-map.json'), 'utf8'),
);

/**
 * Parses a VS Code theme file, which is JSONC rather than JSON.
 *
 * The base themes carry `//` comments — VS Code accepts them, `JSON.parse` does not. Stripping
 * them needs to respect string literals, or a `//` inside a URL or a scope selector would take the
 * rest of the line with it and produce something that still parses but has lost a property.
 */
function parseJsonc(text) {
  let out = '';
  let inString = false;
  let escaped = false;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];

    if (inString) {
      out += ch;
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }

    if (ch === '"') {
      inString = true;
      out += ch;
      continue;
    }
    if (ch === '/' && next === '/') {
      while (i < text.length && text[i] !== '\n') i++;
      out += '\n';
      continue;
    }
    if (ch === '/' && next === '*') {
      i += 2;
      while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) i++;
      i++;
      continue;
    }
    out += ch;
  }

  // Trailing commas are legal in JSONC and are what a stripped comment can leave behind.
  return JSON.parse(out.replace(/,(\s*[}\]])/g, '$1'));
}

/**
 * Rewrites one colour, preserving any alpha suffix.
 *
 * Values here are frequently `#rrggbbaa`. Matching eight digits against a six-digit key would miss
 * them entirely, and rewriting without carrying the alpha across would turn a subtle overlay into
 * a solid block — both silent, and both only visible once the theme is in front of someone.
 */
function remap(value, map) {
  if (typeof value !== 'string' || !value.startsWith('#')) return value;
  const base = value.slice(0, 7).toLowerCase();
  const alpha = value.slice(7);
  const mapped = map[base];
  return mapped ? mapped + alpha : value;
}

function buildClay({ from, to, label, map }) {
  const source = parseJsonc(readFileSync(join(themesDir, from), "utf8"));
  const theme = JSON.parse(JSON.stringify(source));

  theme.name = label;

  let retinted = 0;
  for (const key of Object.keys(theme.colors)) {
    const next = remap(theme.colors[key], map);
    if (next !== theme.colors[key]) retinted++;
    theme.colors[key] = next;
  }
  // tokenColors and semanticTokenColors are deliberately untouched: a Clay variant is the same
  // theme in a different room, not a different theme.

  writeFileSync(join(themesDir, to), JSON.stringify(theme, null, 2) + '\n', 'utf8');
  console.log(`  ${label.padEnd(28)} <- ${from.padEnd(40)} ${retinted} re-tinted`);
}

const variants = [
  { from: 'Kintsugi-Dark-color-theme.json',         to: 'Kintsugi-Dark-Clay-color-theme.json',         label: 'Kintsugi Dark Clay',         map: DARK },
  { from: 'Kintsugi-Dark-Flared-color-theme.json',  to: 'Kintsugi-Dark-Clay-Flared-color-theme.json',  label: 'Kintsugi Dark Clay Flared',  map: DARK },
  { from: 'Kintsugi-Light-color-theme.json',        to: 'Kintsugi-Light-Clay-color-theme.json',        label: 'Kintsugi Light Clay',        map: LIGHT },
  { from: 'Kintsugi-Light-Flared-color-theme.json', to: 'Kintsugi-Light-Clay-Flared-color-theme.json', label: 'Kintsugi Light Clay Flared', map: LIGHT },
];

for (const v of variants) buildClay(v);
console.log('\nDone. Edit clay-map.json, not the generated themes.');
