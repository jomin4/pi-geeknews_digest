// 헤드리스 Chromium 찾기 (export-figures.mjs, build-pdf.mjs 공용)
//
// 찾는 순서
//   1. 환경변수 CHROMIUM_PATH
//   2. Playwright가 설치한 Chromium (npm run setup 으로 설치)
//   3. 시스템 브라우저 (google-chrome, chromium)
import { existsSync } from "node:fs";
import { chromium } from "playwright-core";

const SYSTEM = [
  "/opt/pw-browsers/chromium",
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/snap/bin/chromium",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
];

export async function launchBrowser() {
  if (process.env.CHROMIUM_PATH) return chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
  try {
    return await chromium.launch(); // Playwright 기본 설치 위치
  } catch (first) {
    for (const p of SYSTEM) {
      if (!existsSync(p)) continue;
      try {
        return await chromium.launch({ executablePath: p });
      } catch {
        /* 다음 후보 */
      }
    }
    console.error(
      "Chromium을 찾지 못했습니다. tools/portfolio 에서 `npm run setup` 으로 설치하거나,\n" +
        "CHROMIUM_PATH 환경변수에 크롬/크로미움 실행 파일 경로를 지정하세요.",
    );
    throw first;
  }
}
