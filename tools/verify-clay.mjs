/**
 * Checks that each Clay theme is its namesake with a different interface, and nothing more.
 *
 * Two properties matter, and neither is visible by eye without opening eight files side by side:
 * the syntax must be identical to the namesake's, and the interface must actually have changed.
 * A mapping typo could quietly satisfy one and not the other.
 *
 * Usage:  node tools/verify-clay.mjs
 */

import { readFileSync } from 'node:fs';
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

const load = (n) => parseJsonc(readFileSync(join(themesDir, `${n}-color-theme.json`), 'utf8'));

const pairs = [
  ['Kintsugi-Dark', 'Kintsugi-Dark-Clay'],
  ['Kintsugi-Dark-Flared', 'Kintsugi-Dark-Clay-Flared'],
  ['Kintsugi-Light', 'Kintsugi-Light-Clay'],
  ['Kintsugi-Light-Flared', 'Kintsugi-Light-Clay-Flared'],
];

let failures = 0;

for (const [baseName, clayName] of pairs) {
  const base = load(baseName);
  const clay = load(clayName);

  const syntaxSame = JSON.stringify(base.tokenColors) === JSON.stringify(clay.tokenColors);
  const semanticSame =
    JSON.stringify(base.semanticTokenColors ?? null) === JSON.stringify(clay.semanticTokenColors ?? null);

  const keysSame =
    JSON.stringify(Object.keys(base.colors).sort()) === JSON.stringify(Object.keys(clay.colors).sort());

  const changed = Object.keys(base.colors).filter((k) => base.colors[k] !== clay.colors[k]).length;

  const ok = syntaxSame && semanticSame && keysSame && changed > 0;
  if (!ok) failures++;

  console.log(
    `${ok ? 'ok  ' : 'FAIL'} ${clayName.padEnd(28)} syntax=${syntaxSame ? 'same' : 'DIFFERS'}` +
      ` semantic=${semanticSame ? 'same' : 'DIFFERS'}` +
      ` keys=${keysSame ? 'same' : 'DIFFERS'}` +
      ` chrome changed=${changed}`,
  );

  // A theme that lost its editor background would render over whatever was there before.
  for (const required of ['editor.background', 'editor.foreground']) {
    if (!clay.colors[required]) {
      console.log(`     FAIL ${clayName} has no ${required}`);
      failures++;
    }
  }
}

if (failures) {
  console.error(`\n${failures} problem(s) found.`);
  process.exit(1);
}
console.log('\nAll Clay themes keep their namesake\'s syntax and change only the interface.');
