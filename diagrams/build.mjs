#!/usr/bin/env node
// Gera SVG/PNG com identidade INF-UFRGS a partir de blocos ```mermaid em arquivos markdown.
//
// Uso:
//   node diagrams/build.mjs                     # todos os fontes, svg claro
//   node diagrams/build.mjs -f svg,png          # formatos
//   node diagrams/build.mjs -v claro,escuro     # variantes de tema
//   node diagrams/build.mjs diagrams/src/x.md   # apenas um fonte
//
// Cada bloco recebe o nome definido em `<!-- diagrama: nome -->` na linha anterior.

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(fileURLToPath(import.meta.url), '..', '..');
const DIR = {
  src: path.join(ROOT, 'diagrams', 'src'),
  out: path.join(ROOT, 'diagrams', 'out'),
  theme: path.join(ROOT, 'diagrams', 'theme'),
  tmp: path.join(ROOT, 'diagrams', '.cache'),
};

const VARIANTS = {
  claro: { config: 'inf-ufrgs.mermaid.json', css: 'inf-ufrgs.mermaid.css', bg: '#FFFFFF', suffix: '' },
  escuro: { config: 'inf-ufrgs-dark.mermaid.json', css: 'inf-ufrgs-dark.mermaid.css', bg: '#111111', suffix: '-escuro' },
};

function parseArgs(argv) {
  const opts = { formats: ['svg'], variants: ['claro'], scale: 3, transparent: false, files: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-f' || a === '--format') opts.formats = argv[++i].split(',');
    else if (a === '-v' || a === '--variant') opts.variants = argv[++i].split(',');
    else if (a === '-s' || a === '--scale') opts.scale = Number(argv[++i]);
    else if (a === '--transparent') opts.transparent = true;
    else if (a.startsWith('-')) throw new Error(`Opção desconhecida: ${a}`);
    else opts.files.push(a);
  }
  for (const v of opts.variants) if (!VARIANTS[v]) throw new Error(`Variante inválida: ${v} (use claro|escuro)`);
  return opts;
}

// Extrai os blocos ```mermaid e o nome declarado no comentário anterior.
function extractBlocks(markdown, fallbackBase) {
  const lines = markdown.split(/\r?\n/);
  const blocks = [];
  let pendingName = null;

  for (let i = 0; i < lines.length; i++) {
    const nameMatch = lines[i].match(/<!--\s*diagrama:\s*([A-Za-z0-9._-]+)\s*-->/i);
    if (nameMatch) { pendingName = nameMatch[1].replace(/\.(svg|png)$/i, ''); continue; }

    if (!/^\s*```+\s*mermaid\s*$/i.test(lines[i])) continue;
    const body = [];
    let j = i + 1;
    while (j < lines.length && !/^\s*```+\s*$/.test(lines[j])) body.push(lines[j++]);
    blocks.push({ name: pendingName || `${fallbackBase}-${blocks.length + 1}`, code: body.join('\n') });
    pendingName = null;
    i = j;
  }
  return blocks;
}

function mmdc(args) {
  const bin = path.join(ROOT, 'node_modules', '.bin', process.platform === 'win32' ? 'mmdc.cmd' : 'mmdc');
  execFileSync(bin, args, { stdio: ['ignore', 'pipe', 'inherit'], shell: process.platform === 'win32' });
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const sources = opts.files.length
    ? opts.files.map((f) => path.resolve(ROOT, f))
    : fs.existsSync(DIR.src)
      ? fs.readdirSync(DIR.src).filter((f) => f.endsWith('.md')).map((f) => path.join(DIR.src, f))
      : [];

  if (!sources.length) { console.error(`Nenhum fonte encontrado em ${DIR.src}`); process.exit(1); }

  fs.mkdirSync(DIR.out, { recursive: true });
  fs.mkdirSync(DIR.tmp, { recursive: true });
  let total = 0;

  for (const src of sources) {
    const base = path.basename(src, '.md');
    const blocks = extractBlocks(fs.readFileSync(src, 'utf8'), base);
    if (!blocks.length) { console.warn(`- ${base}: nenhum bloco mermaid`); continue; }

    // Um único markdown temporário por fonte: o mermaid-cli abre o navegador uma vez só.
    const tmpMd = path.join(DIR.tmp, `${base}.md`);
    fs.writeFileSync(tmpMd, blocks.map((b) => '```mermaid\n' + b.code + '\n```').join('\n\n') + '\n');

    for (const variant of opts.variants) {
      const v = VARIANTS[variant];
      for (const format of opts.formats) {
        const stage = path.join(DIR.tmp, `${base}-${variant}-${format}.md`);
        fs.copyFileSync(tmpMd, stage);
        mmdc([
          '-i', stage,
          '-o', stage,
          '-e', format,
          '-c', path.join(DIR.theme, v.config),
          '-C', path.join(DIR.theme, v.css),
          '-p', path.join(DIR.theme, 'puppeteer.json'),
          '-b', opts.transparent ? 'transparent' : v.bg,
          '-s', String(opts.scale),
          '-q',
        ]);

        blocks.forEach((block, idx) => {
          const generated = path.join(DIR.tmp, `${base}-${variant}-${format}-${idx + 1}.${format}`);
          const target = path.join(DIR.out, `${block.name}${v.suffix}.${format}`);
          fs.renameSync(generated, target);
          total++;
          console.log(`  ${path.relative(ROOT, target)}`);
        });
      }
    }
  }

  fs.rmSync(DIR.tmp, { recursive: true, force: true });
  console.log(`\n${total} arquivo(s) gerado(s) em ${path.relative(ROOT, DIR.out)}/`);
}

main();
