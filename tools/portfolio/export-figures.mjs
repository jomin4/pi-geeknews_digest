#!/usr/bin/env node
// Excalidraw 파일 → SVG · PNG 내보내기
//
// excalidraw.com의 "Export image"와 같은 엔진(@excalidraw/excalidraw exportToSvg / exportToBlob)을
// 헤드리스 Chromium에서 실행한다. 폰트도 패키지에 들어 있는 파일을 그대로 쓴다.
//
// 사용법 (tools/portfolio 에서)
//   npm run figures                 portfolio/figures/*.excalidraw 전부
//   node export-figures.mjs FIG-P1-rss-coverage   특정 그림만
//
// 결과: portfolio/figures/FIG-*.svg, FIG-*.png (2배율, 흰 배경)
import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { dirname, join, resolve, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { launchBrowser } from "./browser.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "../..");
const FIG_DIR = join(ROOT, "portfolio/figures");
const BUNDLE = join(HERE, ".build/excalidraw-bundle.js");
const ASSETS = join(HERE, "node_modules/@excalidraw/excalidraw/dist/prod");
const ORIGIN = "http://gndigest.local";

function ensureBundle() {
  const entry = join(HERE, "excalidraw-entry.js");
  if (existsSync(BUNDLE) && statSync(BUNDLE).mtimeMs > statSync(entry).mtimeMs) return;
  console.log("Excalidraw 번들 생성 중 (처음 한 번)...");
  execFileSync(
    join(HERE, "node_modules/.bin/esbuild"),
    [entry, "--bundle", "--format=iife", `--outfile=${BUNDLE}`, "--minify",
     "--define:process.env.NODE_ENV=\"production\"", "--loader:.css=empty", "--log-level=warning"],
    { stdio: "inherit" },
  );
}

const MIME = { ".woff2": "font/woff2", ".ttf": "font/ttf", ".js": "text/javascript", ".wasm": "application/wasm" };

async function main() {
  ensureBundle();
  const only = process.argv.slice(2);
  const files = readdirSync(FIG_DIR)
    .filter((f) => f.endsWith(".excalidraw"))
    .filter((f) => only.length === 0 || only.some((o) => f.startsWith(o)))
    .sort();
  if (files.length === 0) {
    console.error("내보낼 .excalidraw 파일이 없습니다:", FIG_DIR);
    process.exit(1);
  }

  const browser = await launchBrowser();
  const page = await browser.newPage();
  const blocked = new Set();
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== ORIGIN) {
      blocked.add(url.origin);
      return route.abort();
    }
    if (url.pathname === "/") {
      return route.fulfill({
        contentType: "text/html",
        body: `<!doctype html><meta charset="utf-8"><body>
<script>window.EXCALIDRAW_ASSET_PATH = "${ORIGIN}/assets/";</script>
<script src="/bundle.js"></script></body>`,
      });
    }
    if (url.pathname === "/bundle.js") return route.fulfill({ path: BUNDLE, contentType: "text/javascript" });
    if (url.pathname.startsWith("/assets/")) {
      const p = join(ASSETS, decodeURIComponent(url.pathname.slice("/assets/".length)));
      if (existsSync(p)) return route.fulfill({ path: p, contentType: MIME[extname(p)] || "application/octet-stream" });
    }
    return route.fulfill({ status: 404, body: "" });
  });
  page.on("pageerror", (e) => console.error("페이지 오류:", e.message));
  await page.goto(ORIGIN + "/");
  await page.waitForFunction(() => window.ExcalidrawLib);

  for (const f of files) {
    const id = f.replace(/\.excalidraw$/, "");
    const scene = JSON.parse(readFileSync(join(FIG_DIR, f), "utf8"));
    const out = await page.evaluate(async (scene) => {
      const { exportToSvg, exportToBlob, restoreElements } = window.ExcalidrawLib;
      const elements = restoreElements(scene.elements, null, { refreshDimensions: false });
      const appState = {
        exportBackground: true,
        viewBackgroundColor: scene.appState?.viewBackgroundColor || "#ffffff",
        exportWithDarkMode: false,
        exportEmbedScene: false,
      };
      const svg = await exportToSvg({ elements, appState, files: scene.files || {}, exportPadding: 24 });
      const blob = await exportToBlob({
        elements, appState, files: scene.files || {}, exportPadding: 24, mimeType: "image/png",
        getDimensions: (w, h) => ({ width: w * 2, height: h * 2, scale: 2 }),
      });
      const buf = new Uint8Array(await blob.arrayBuffer());
      let bin = "";
      for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode(...buf.subarray(i, i + 0x8000));
      return { svg: svg.outerHTML, png: btoa(bin), w: svg.getAttribute("width"), h: svg.getAttribute("height") };
    }, scene);
    writeFileSync(join(FIG_DIR, `${id}.svg`), out.svg);
    writeFileSync(join(FIG_DIR, `${id}.png`), Buffer.from(out.png, "base64"));
    console.log(`${id}: svg ${out.w}x${out.h}, png 2x`);
  }
  if (blocked.size) console.log("차단한 외부 요청:", [...blocked].join(", "));
  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
