#!/usr/bin/env node
// 포트폴리오 원고(md) → PDF
//
// portfolio/pdf.config.json 순서대로
//   1쪽: 프로젝트 요약 (00-project-summary.md)
//   2쪽~: 문제 해결 경험 (problems/P*.md 의 <!-- PDF:START --> ~ <!-- PDF:END --> 구간)
// 을 한 PDF로 만든다. 그림은 portfolio/figures/*.png (npm run figures 로 먼저 내보낸다).
//
// 사용법 (tools/portfolio 에서)
//   npm run pdf              초안: 상태 표시, "측정 예정" 강조, 쪽 아래 "초안" 표기
//   node build-pdf.mjs --final   최종: 모든 항목이 '확정'이고 '측정 예정'이 없을 때만 만든다
import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { marked } from "marked";
import { launchBrowser } from "./browser.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "../..");
const PF = join(ROOT, "portfolio");
const FINAL = process.argv.includes("--final");
const cfg = JSON.parse(readFileSync(join(PF, "pdf.config.json"), "utf8"));
const today = new Date().toISOString().slice(0, 10);

const PDF_RE = /<!--\s*PDF:START\s*-->([\s\S]*?)<!--\s*PDF:END\s*-->/;

function pdfPart(md, file) {
  const m = md.match(PDF_RE);
  if (!m) throw new Error(`${file}: <!-- PDF:START --> / <!-- PDF:END --> 구간이 없습니다`);
  return m[1];
}

function status(md) {
  const m = md.match(/^>\s*상태:\s*([^·\n]+)/m);
  return m ? m[1].trim() : "알 수 없음";
}

function findProblem(id) {
  const dir = join(PF, "problems");
  const f = readdirSync(dir).find((n) => n.startsWith(`${id}-`) && n.endsWith(".md"));
  if (!f) throw new Error(`problems/ 에서 ${id}-*.md 를 찾지 못했습니다`);
  return join(dir, f);
}

// 마크다운 → HTML. 상대 경로 이미지는 file:// 로, 상대 경로 링크는 저장소 주소(있으면) 또는 글자로.
function render(md, baseDir) {
  let html = marked.parse(md, { gfm: true });
  // 같은 이름의 .svg가 있으면 벡터로 넣는다 (PDF를 확대해도 선명). 없으면 원고에 적힌 파일(.png)
  html = html.replace(/<img src="([^"]+)"/g, (all, src) => {
    if (/^(https?:|data:|file:)/.test(src)) return all;
    let abs = resolve(baseDir, src);
    const svg = abs.replace(/\.png$/i, ".svg");
    if (svg !== abs && existsSync(svg)) abs = svg;
    if (!existsSync(abs)) console.warn(`  그림 없음: ${abs.slice(ROOT.length + 1)} (npm run figures 먼저)`);
    return `<img src="${pathToFileURL(abs).href}"`;
  });
  html = html.replace(/<a href="([^"]+)">([\s\S]*?)<\/a>/g, (all, href, text) => {
    if (/^https?:/.test(href)) return all;
    if (cfg.repo_url) {
      const rel = resolve(baseDir, href).slice(ROOT.length + 1);
      return `<a href="${cfg.repo_url.replace(/\/$/, "")}/blob/main/${rel}">${text}</a>`;
    }
    return `<code>${text}</code>`;
  });
  html = html.replace(/측정 예정/g, '<span class="todo">측정 예정</span>');
  return html;
}

function chip(text) {
  return FINAL ? "" : `<div class="meta"><span class="chip">${text}</span></div>`;
}

// ---- 원고 읽기 ----
const problems = cfg.problems.map((id, i) => {
  const file = findProblem(id);
  const md = readFileSync(file, "utf8");
  const h1 = md.match(/^#\s+(.+)$/m)?.[1] ?? id;
  const title = h1.replace(/^[PR]\d+\.\s*/, "").replace(/\s*\(가제\)\s*$/, "");
  return { id, no: i + 1, file, md, title, draftTitle: /\(가제\)\s*$/.test(h1), status: status(md), dir: dirname(file) };
});

const sumFile = join(PF, cfg.summary);
const sumMd = readFileSync(sumFile, "utf8");
const toc = problems.map((p) => `${p.no}. ${p.title} — p.${p.no + 1}`).join("\n");
const summaryHtml = render(pdfPart(sumMd, cfg.summary).replace(/<!--\s*PDF:TOC\s*-->/, toc), dirname(sumFile));
const projectName = sumMd.match(/^#\s+(.+)$/m)?.[1] ?? "프로젝트";

// ---- 최종 모드 검사 ----
const problemsHtml = problems.map((p) => render(pdfPart(p.md, p.file), p.dir));
if (FINAL) {
  const errs = [];
  problems.forEach((p, i) => {
    if (p.status !== "확정") errs.push(`${p.id}: 상태가 '${p.status}' (확정이어야 함)`);
    if (p.draftTitle) errs.push(`${p.id}: 제목에 (가제)가 남아 있음`);
    if (problemsHtml[i].includes("측정 예정")) errs.push(`${p.id}: '측정 예정'이 남아 있음`);
  });
  if (summaryHtml.includes("(저장소 주소)")) errs.push("요약: 저장소 주소가 비어 있음");
  if (errs.length) {
    console.error("최종 PDF를 만들 수 없습니다:\n  " + errs.join("\n  "));
    process.exit(1);
  }
}

// ---- HTML 조립 ----
const css = `
@page { size: A4; margin: 15mm 16mm 16mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Pretendard", "Noto Sans CJK KR", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
       font-size: 9.6pt; line-height: 1.58; color: #212529; margin: 0; }
.page { break-after: page; position: relative; }
.page:last-child { break-after: auto; }
h1 { font-size: 20pt; margin: 0 0 4mm; letter-spacing: -0.3px; }
h1.ptitle { font-size: 13.5pt; line-height: 1.4; margin: 0 0 3mm; }
h3 { font-size: 10.5pt; color: #1971c2; margin: 3.2mm 0 1.2mm; }
h3::before { content: "•"; margin-right: 6px; }
ul { margin: 0 0 0 7mm; padding-left: 4mm; }
ul ul { margin-left: 0; list-style: circle; }
li { margin: 0.6mm 0; }
p { margin: 1.5mm 0; }
img { display: block; width: 100%; max-height: 78mm; object-fit: contain; margin: 3mm auto 3mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 1mm; font-size: 9pt; }
th, td { border: 1px solid #dee2e6; padding: 1.4mm 2.4mm; vertical-align: top; text-align: left; }
th { display: none; }
td:first-child { width: 20mm; background: #f8f9fa; font-weight: 600; white-space: nowrap; }
code { font-family: "Noto Sans Mono CJK KR", monospace; font-size: 8.6pt; background: #f1f3f5; padding: 0 3px; border-radius: 3px; }
strong { font-weight: 700; }
a { color: #1971c2; text-decoration: none; }
.todo { background: #fff3bf; color: #e8590c; padding: 0 3px; border-radius: 3px; font-weight: 700; }
.meta { text-align: right; height: 5mm; margin-bottom: 1mm; }
.chip { display: inline-block; font-size: 7.5pt; color: #e8590c; background: #fff3bf;
        border: 1px solid #ffd43b; border-radius: 10px; padding: 0 7px; line-height: 1.7; }
.summary ol { margin: 1mm 0 0 7mm; padding-left: 5mm; }
.summary ol li { margin: 1mm 0; }
.summary h3 + ul { margin-top: 1mm; }
.summary img { max-height: 92mm; }
`;

const pages = [
  `<section class="page summary">${chip(`요약 · ${status(sumMd)}`)}<h1>${projectName}</h1>${summaryHtml}</section>`,
  ...problems.map((p, i) =>
    `<section class="page problem">${chip(`${p.id} · ${p.status}${p.draftTitle ? " · 가제" : ""}`)}` +
    `<h1 class="ptitle">${p.no}. ${p.title}</h1>${problemsHtml[i]}</section>`),
];
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>${cfg.title}</title>
<style>${css}</style></head><body>${pages.join("\n")}</body></html>`;

const buildDir = join(HERE, ".build");
mkdirSync(buildDir, { recursive: true });
const htmlPath = join(buildDir, "portfolio.html");
writeFileSync(htmlPath, html);

// ---- PDF ----
const out = join(PF, cfg.output);
mkdirSync(dirname(out), { recursive: true });
const browser = await launchBrowser();
// 뷰포트 폭 = A4 본문 폭(210 - 좌우 여백 32mm)이어야 높이 측정이 인쇄와 맞는다
const page = await browser.newPage({ viewport: { width: Math.round((178 * 96) / 25.4), height: 1100 } });
await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
await page.emulateMedia({ media: "print" });

// 한 원고 = 한 쪽 확인 (A4 297mm - 위아래 여백 31mm = 266mm)
const over = await page.evaluate(() => {
  const mm = 96 / 25.4;
  return [...document.querySelectorAll(".page")].map((s) => Math.round(s.scrollHeight / mm)).map((h, i) => [i + 1, h]);
});
const footer = FINAL
  ? `${projectName} · <span class="pageNumber"></span> / <span class="totalPages"></span>`
  : `${projectName} · 포트폴리오 초안 ${today} · <span class="pageNumber"></span> / <span class="totalPages"></span>`;
await page.pdf({
  path: out, format: "A4", printBackground: true, preferCSSPageSize: true,
  displayHeaderFooter: true, headerTemplate: "<span></span>",
  footerTemplate: `<div style="width:100%;font-size:7.5pt;color:#868e96;text-align:center;font-family:'Noto Sans CJK KR',sans-serif">${footer}</div>`,
});
await browser.close();

const actual = (readFileSync(out, "latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
console.log(`PDF: ${out.slice(ROOT.length + 1)} (${FINAL ? "최종" : "초안"}, ${actual}쪽 / 목표 ${pages.length}쪽)`);
if (actual !== pages.length) console.log("  경고: 원고 하나가 한 쪽을 넘었습니다. 아래 높이를 확인하세요.");
for (const [n, h] of over) {
  const flag = h > 266 ? "  ← 한 쪽을 넘음: 그림 높이나 문장 분량을 줄이세요" : "";
  console.log(`  ${n}쪽 원고 높이 약 ${h}mm${flag}`);
}
