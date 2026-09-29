# 작업 기록 (worklog)

Claude Code 세션이 끝날 때마다 **맨 위에** 항목을 추가한다. 이 파일만 읽어도 지금까지 무엇이 왜 바뀌었는지 알 수 있어야 한다.

## 템플릿

```markdown
## YYYY-MM-DD · T번호 작업 이름
- 환경: 로컬 | 클라우드 세션
- 기준 문서 ID: JEV-Q1, JEV-C6 …
- 한 일:
  - …
- 바뀐 파일: `src/…`, `tests/…`, `docs/…`
- 테스트: `uv run pytest` 결과 (통과 n / 실패 0)
- 문서와 다르게 한 것: 없음 | 있음 → 어떤 문서를 어떻게 고쳤는지
- 미결 사항(OPEN) 결과: …
- 다음 작업: T번호
```

---

## 2026-09-29 · 로컬 세팅 준비와 첫 업로드
- 환경: claude.ai 설계 대화
- 한 일:
  - `docs/SETUP.md` 작성: Ubuntu 기준 설치, 레포 받기, 포트폴리오 도구 확인, Claude Code 첫 지시문(T00), 작업별 계정·키 준비 시점, Discord 봇 만들기
  - `.claude/settings.json`: 자주 쓰는 명령 허용, `.env` 읽기 차단
  - 포트폴리오 도구가 어느 컴퓨터에서든 Chromium을 찾도록 `tools/portfolio/browser.mjs` 추가, `npm run setup`(Chromium 설치) 추가, 문서의 명령을 `npm --prefix tools/portfolio run …`으로 통일
  - GitHub `jomin4/pi-geeknews_digest` main에 첫 커밋
- 다음 작업: T00 (로컬, Claude Code)

## 2026-09-29 · 저장소 주소 반영
- 환경: claude.ai 설계 대화
- 한 일: 저장소 `https://github.com/jomin4/pi-geeknews_digest`를 포트폴리오 요약 쪽 '저장소' 칸과 `pdf.config.json`의 `repo_url`에 넣고 초안 PDF를 다시 만듦. 이제 PDF의 근거 파일 링크도 GitHub 주소로 연결된다
- 다음 작업: 저장소에 올리기 → T00

## 2026-09-29 · 포트폴리오 시각화 방식 변경 (구조만 보여주는 최소 그림)
- 환경: claude.ai 설계 대화
- 기준 문서 ID: portfolio/STYLE-GUIDE.md (전면 개정)
- 한 일:
  - 사용자가 참고 이미지 기준으로 시각화 방식을 확정: 그림은 구조만, 설명은 본문이 맡는다
  - 그림 제목·구역 박스·범례·결과 수치 박스 제거, 박스는 이름만 한 줄, 화살표 번호는 본문 해결 과정 번호와 일치, 빨간 문제 주석은 한 곳, 괄호 묶음, 직선·일반 글꼴, 색은 최대 2가지
  - `tools/figgen.py` 새 명세 형식으로 재작성 (`kind`, `color`, `n`/`label`/`note`, `brackets`, `dividers`, `--all`), 색 2개 초과 경고
  - 그림 5개(P0~P4) 다시 그리고 내보내기, PDF 그림 높이 78mm(요약 92mm)로 조정 → 원고마다 한 쪽에 여유
- 다음 작업: 저장소 연결 → T00

## 2026-09-29 · 포트폴리오 PDF 기초틀과 그림 내보내기
- 환경: claude.ai 설계 대화
- 기준 문서 ID: portfolio/README.md §7, STYLE-GUIDE §1, T14
- 한 일:
  - `tools/portfolio/export-figures.mjs`: Excalidraw 공식 엔진(@excalidraw/excalidraw 0.18.1)을 헤드리스 Chromium에서 돌려 `.excalidraw` → SVG·PNG
  - `tools/portfolio/build-pdf.mjs`: 원고의 PDF 구간 → A4 PDF (요약 1쪽 + 경험 4쪽), 초안/최종 모드, 쪽 넘침 경고
  - 그림 FIG-P2·P3·P4 추가, FIG-P0 화살표 경로 정리. `figgen.py`에 직각 꺾은선·라벨 위치·구역 이름 정렬·도형 모양 범례 추가
  - 원고 PDF 구간 표시를 `<!-- PDF:START -->` / `<!-- PDF:END -->`로 통일, 요약 쪽 목록 자동 생성(`<!-- PDF:TOC -->`)
  - 초안 PDF `portfolio/dist/geeknews-digest-portfolio.pdf` 5쪽 생성·확인
- 알게 된 것: SVG에는 영문 손글씨 글꼴만 내장되고 한글은 보는 기기의 글꼴로 나온다 (excalidraw.com 내보내기도 같음). PDF는 SVG를 넣어 벡터로 선명하게, README에는 PNG를 쓴다
- 다음 작업: 저장소 연결 → T00

## 2026-09-28 · 포트폴리오 구조 세팅
- 환경: claude.ai 설계 대화
- 기준 문서 ID: ADR-008, DATA-06, ARCH-12, T13, T14
- 한 일:
  - 포트폴리오 5단계 형식(제목·그림·문제 원인·해결 과정·결과)에 맞춘 `portfolio/` 구성: 작성 규칙, 프로젝트 요약, 후보 P1~P4·예비 R1~R2, 로그·증거 템플릿
  - Excalidraw 스타일 가이드와 그림 생성기 `tools/figgen.py`, 그림 FIG-P0·FIG-P1 생성
  - 포트폴리오 증거용 실행 지표(DATA-06) 설계, 구현 계획에 작업별 지표와 Phase 4 추가, PLAN-D1·DATA-D1 갱신·문법 확인
  - CLAUDE.md에 문서 최신화 체크리스트·문제 해결 기록·측정 규칙 추가, 루트 README를 포트폴리오 첫 화면으로 재작성
- 문서와 다르게 한 것: 없음
- 다음 작업: 저장소 연결 → T00

## 2026-09-28 · 설계 문서 초안
- 환경: claude.ai 설계 대화
- 기준 문서 ID: 전체
- 한 일:
  - 요구사항, 아키텍처, 수집 범위, Jev 판단, 데이터 구조, Gemini 프롬프트, Discord 양식, 피드백 구조, 구현 계획 문서화
  - Mermaid 다이어그램 8개 작성·문법 확인 (ARCH-D1, SCH-D1, SCH-D2, JEV-D1, DATA-D1, DSC-D1, FB-D1, PLAN-D1)
  - ADR-001~007 작성
- 문서와 다르게 한 것: 설계 중 충돌한 "Top 채우기" 규칙을 ADR-006으로 정리
- 미결 사항: OPEN-1~5 (docs/README.md §5)
- 다음 작업: T00
