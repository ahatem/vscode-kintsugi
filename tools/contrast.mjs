/**
 * Reports the contrast ratio of every syntax colour against the editor background it is drawn on.
 *
 * Whether a light theme "works" tends to be argued in adjectives. It does not have to be: contrast
 * is measurable, and a light palette derived from a dark one fails in a specific, predictable way —
 * mid-tone accents keep their hue but lose their separation, because they were chosen against
 * near-black and are now on cream.
 *
 * WCAG floors: 4.5 for body text, 3.0 for large. Code is small, so 4.5 is the number that matters,
 * with comments allowed to sit lower since they are meant to recede.
 *
 * Usage:  node tools/contrast.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const themesDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'themes');

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
    if (ch === '"') { inString = true; out += ch; continue; }
    if (ch === '/' && next === '/') { while (i < text.length && text[i] !== '\n') i++; out += '\n'; continue; }
    if (ch === '/' && next === '*') { i += 2; while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) i++; i++; continue; }
    out += ch;
  }
  return JSON.parse(out.replace(/,(\s*[}\]])/g, '$1'));
}

const toLinear = (c) => {
  const v = c / 255;
  return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
};

function luminance(hex) {
  const h = hex.replace('#', '').slice(0, 6);
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

function contrast(fg, bg) {
  const a = luminance(fg);
  const b = luminance(bg);
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100;
}

/** Scopes meant to recede, held to the large-text floor instead of body text. */
const RELAXED = /comment|punctuation\.definition\.comment/;

const files = readdirSync(themesDir).filter((f) => f.endsWith('-color-theme.json')).sort();
let failures = 0;

for (const file of files) {
  const theme = parseJsonc(readFileSync(join(themesDir, file), 'utf8'));
  const bg = theme.colors['editor.background'];
  const rows = [];

  for (const tc of theme.tokenColors ?? []) {
    const fg = tc.settings?.foreground;
    if (!fg) continue;
    const scope = Array.isArray(tc.scope) ? tc.scope.join(', ') : String(tc.scope ?? '');
    const floor = RELAXED.test(scope) ? 3.0 : 4.5;
    const ratio = contrast(fg, bg);
    if (ratio < floor) {
      rows.push({ fg, ratio, floor, scope: scope.slice(0, 58) });
      failures++;
    }
  }

  console.log(`\n${theme.name}   background ${bg}`);
  if (rows.length === 0) {
    console.log('  every token meets its floor');
  } else {
    for (const r of rows) {
      console.log(`  ${r.fg}  ${String(r.ratio).padStart(5)} < ${r.floor}   ${r.scope}`);
    }
  }
}

console.log(`\n${failures} token${failures === 1 ? '' : 's'} below floor across ${files.length} themes.`);
