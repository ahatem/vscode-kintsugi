/**
 * Proposes the smallest hue-preserving adjustment that brings each failing colour up to its floor.
 *
 * Moves lightness in HSL, holding hue and saturation, so a gold stays gold and only its separation
 * from the background changes. Guessing at replacements drifts the hue and costs the palette the
 * identity it is named for.
 *
 * Each colour is solved against the strictest background it appears on — the base and Clay themes
 * differ slightly, and a value that passes on one and fails on the other by a hundredth is worse
 * than useless, because it looks fixed.
 *
 * Usage:  node tools/suggest-contrast.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const themesDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'themes');

function parseJsonc(text) {
  let out = '', inString = false, escaped = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i], next = text[i + 1];
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

const toLinear = (c) => { const v = c / 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
const rgb = (hex) => { const h = hex.replace('#', '').slice(0, 6); return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)]; };
const lum = (hex) => { const [r,g,b] = rgb(hex); return 0.2126*toLinear(r) + 0.7152*toLinear(g) + 0.0722*toLinear(b); };
const contrast = (fg, bg) => { const a = lum(fg), b = lum(bg); const [hi, lo] = a > b ? [a, b] : [b, a]; return Math.round(((hi+0.05)/(lo+0.05))*100)/100; };

function toHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return [0, 0, l];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h;
  if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  return [h / 6, s, l];
}

const hueToRgb = (p, q, t) => {
  if (t < 0) t += 1;
  if (t > 1) t -= 1;
  if (t < 1/6) return p + (q - p) * 6 * t;
  if (t < 1/2) return q;
  if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
  return p;
};

function toHex(h, s, l) {
  let r, g, b;
  if (s === 0) { r = g = b = l; }
  else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hueToRgb(p, q, h + 1/3); g = hueToRgb(p, q, h); b = hueToRgb(p, q, h - 1/3);
  }
  const to = (v) => Math.round(v * 255).toString(16).padStart(2, '0');
  return `#${to(r)}${to(g)}${to(b)}`;
}

/** Least change that clears the bar; dragging further than needed stops it matching the palette. */
function findAccessible(hex, bg, target) {
  const [h, s, l] = toHsl(...rgb(hex));
  const step = lum(bg) > 0.5 ? -0.005 : 0.005;
  for (let i = 0; i < 200; i++) {
    const candidate = toHex(h, s, Math.max(0, Math.min(1, l + step * i)));
    if (contrast(candidate, bg) >= target) return candidate;
  }
  return hex;
}

const RELAXED = /comment|punctuation\.definition\.comment/;

// colour -> { floor, backgrounds it must work on }
const needs = new Map();

for (const file of readdirSync(themesDir).filter((f) => f.endsWith('-color-theme.json'))) {
  const theme = parseJsonc(readFileSync(join(themesDir, file), 'utf8'));
  const bg = theme.colors['editor.background'];
  for (const tc of theme.tokenColors ?? []) {
    const fg = tc.settings?.foreground;
    if (!fg) continue;
    const scope = Array.isArray(tc.scope) ? tc.scope.join(', ') : String(tc.scope ?? '');
    const floor = RELAXED.test(scope) ? 3.0 : 4.5;
    if (contrast(fg, bg) >= floor) continue;
    const key = fg.toLowerCase();
    const entry = needs.get(key) ?? { floor: 0, backgrounds: new Set() };
    entry.floor = Math.max(entry.floor, floor);
    entry.backgrounds.add(bg);
    needs.set(key, entry);
  }
}

console.log('{');
for (const [hex, { floor, backgrounds }] of [...needs].sort()) {
  // Solve against every background it appears on, and keep the most demanding result.
  let best = hex;
  for (const bg of backgrounds) {
    const candidate = findAccessible(hex, bg, floor);
    if (contrast(candidate, bg) >= floor && contrast(best, bg) < floor) best = candidate;
    else if (Math.abs(lum(candidate) - lum(bg)) > Math.abs(lum(best) - lum(bg))) best = candidate;
  }
  const ratios = [...backgrounds].map((bg) => `${bg}:${contrast(best, bg)}`).join(' ');
  console.log(`  "${hex}": "${best}",   // floor ${floor}  ->  ${ratios}`);
}
console.log('}');
