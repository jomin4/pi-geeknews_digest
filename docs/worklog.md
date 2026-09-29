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

## 2026-09-29 · T01 RSS 수집
- 환경: 클라우드 세션 (Claude Code). 사용자가 환경 네트워크를 Custom(`news.hada.io` + 기본 패키지 저장소)으로 바꿔 피드를 받음
- 기준 문서 ID: ARCH-02, DATA-01, DATA-06, DATA-R1, DATA-R2, DATA-R7, SCH-R1, SCH-R4, OPEN-4
- 한 일:
  - `tests/fixtures/rss_sample.xml`: 2026-09-29 21:51 KST 실제 피드 원문 (50건)
  - `rss.py`: `fetch_feed`(httpx, User-Agent, HTTP 오류·시간 초과를 RssError로), `parse_feed`(feedparser, 제목 엔터티 풀기, HTML 제거, id·type 추출, KST 변환, ISO가 아니면 published_parsed 사용), `select_new`(SCH-R4), `collect`(지표 필드 계산)
  - `models.py`: Article, ArticlesFile (KST aware datetime만 허용, 모르는 필드 거부)
  - `storage.py`: `read_model`(없으면 기본값, 깨졌으면 멈춤), `write_model`(임시 파일 → fsync → os.replace)
  - `window.py`: `initial_last_cutoff`(DATA-02 첫 실행: 어제 17:30)만. state.json 연결은 T02
  - `cli.py`: `collect` 구현. `--dry-run`이면 `out/articles.json`, `out/metrics.jsonl`에만 쓴다. `--feed-file`로 저장본 사용. 실패도 지표에 `error`로 기록
- 바뀐 파일: `src/gndigest/{rss,models,storage,window,cli,config}.py`, `tests/test_{rss,storage,collect_cli,cli}.py`, `tests/fixtures/rss_sample.xml`, `pyproject.toml`, `uv.lock`, `docs/01`, `04`, `08`, `docs/README.md`, `portfolio/logs/L-20260929-1·2`, `portfolio/evidence/P1/`, `portfolio/problems/P1`, `README.md`
- 테스트: `uv run pytest` 통과 79 / 실패 0. 네트워크 없는 환경(`unshare -rn`)에서도 79 통과. 피드가 아니거나 항목이 0건인 응답은 수집 실패로 처리 (봇 확인 화면을 "0건 수집"으로 넘기지 않기 위해)
- 확인: `uv run gndigest collect --dry-run --feed-file tests/fixtures/rss_sample.xml` → `RSS 50건 · 새 글 50건 · 수집함 50건 → out/articles.json`. 실제 피드로 한 `collect --dry-run`도 같은 결과
- 문서와 다르게 한 것:
  - `collect --feed-file` 옵션 추가 (완료 조건 "fixture로 dry-run"을 위해). 01 §5, 08 T01에 반영
  - 제목 엔터티 풀기와 요약의 블록 태그 → 공백 처리를 DATA-01 표에 추가 (L-20260929-2)
  - `last_cutoff`는 T02 전까지 첫 실행 규칙(어제 17:30)을 쓴다
- 미결 사항(OPEN) 결과: OPEN-4 → 50건 모두 `published = updated`. `published`만 쓴다 (docs/README.md §5)
- 지표: `rss_items`, `new_items`, `rss_oldest_published`, `rss_newest_published` (P1)
- 문제 해결 로그: L-20260929-1 (OPEN-4, 피드 범위 22시간 33분, 원문 요약 최대 186자), L-20260929-2 (제목 이중 이스케이프)
- 사용자에게 알린 설계 관찰: RSS 원문 요약이 중앙값 152자라 Gemini 요약 목표(150자)와 거의 같다 (GEM-A). 설계는 바꾸지 않음
- 다음 작업: T02 범위 · 상태

## 2026-09-29 · T00 저장소 · 환경 · CLI 뼈대
- 환경: 클라우드 세션 (Claude Code)
- 기준 문서 ID: 01 §3~5, ARCH-S1, REQ-14, SCH-R8, DATA-02, DATA-06, DATA-R7, JEV-C2
- 한 일:
  - `pyproject.toml`(uv, Python 3.12, uv_build), `.python-version`, `uv.lock`. 의존성은 지금 쓰는 pydantic, pytest만 넣고, 나머지(feedparser, httpx, respx, google-genai)는 쓰는 작업(T01, T05)에서 추가
  - `cli.py`: collect / report / tune / show-profile 빈 명령, 모든 명령에 `--dry-run`, report에 `--cutoff`(시간대 없으면 거부, KST로 변환)
  - `config.py`: 환경변수 읽기(명령마다 필요한 이름을 `require`로 지정, 빠진 이름을 모두 담은 오류), 비밀값을 가리는 repr, 기본 기준선(DATA-02), `JEV_MODEL` 기본값 `typesafe/jev-1.13`, KST
  - `metrics.py`: DATA-06 한 줄 모델(`RunMetric`, 공통 필드 + 작업별 필드는 extra), `make_run_id`, `record_run`
  - `storage.py`: `append_jsonl`만 먼저 만듦 (CLAUDE.md 7절 "data/는 storage.py로만"을 지키기 위해). 원자적 저장·검증은 T01
  - `tests/conftest.py`: 모든 테스트에서 외부 소켓 연결·이름 조회를 막고, gndigest 환경변수를 비움 (REQ-14)
  - `.env.example`, `data/` 초기 파일(`profile.json` 관심 분야 4개, 빈 `articles.json`·`feedback.json`, `reports/`). `state.json`은 DATA-02대로 첫 실행 때 만든다
  - 포트폴리오 도구 확인: `figgen.py --all`, `npm install`, `npm run figures`, `npm run pdf`(초안 5쪽, 쪽 넘침 경고 없음). 그림 파일은 그대로였고 PDF만 바이너리가 달라져 되돌림
- 바뀐 파일: `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `src/gndigest/*`, `tests/*`, `data/*`, `README.md`, `docs/SETUP.md`, `docs/worklog.md`
- 테스트: `uv run pytest` 통과 34 / 실패 0. 네트워크 인터페이스가 없는 환경(`unshare -rn`)에서도 34 통과
- 문서와 다르게 한 것:
  - 작업 환경: ADR-007은 T00~T10을 로컬로 정했지만, 키·봇 설정이 필요 없는 T00~T02는 사용자 결정으로 클라우드 세션에서 진행한다. T03부터는 실제 API 확인이 있어 로컬에서 한다
  - `storage.py`를 T01보다 먼저 만들었다 (위 이유). 동작 변경은 없음
  - `npm run setup`(Chromium 설치)은 건너뜀: 이 환경에 Chromium이 이미 있고 `browser.mjs`가 찾아 씀
- 지표: T00에는 기록할 지표 필드 없음 (`metrics.py` 뼈대만)
- 미결 사항(OPEN) 결과: 해당 없음
- 다음 작업: T01 RSS 수집

## 2026-09-29 · 설계 검토 결과 반영 (전송 실패·중복 전송 규칙 보완)
- 환경: 클라우드 세션 (Claude Code)
- 기준 문서 ID: SCH-R6, SCH-R9(신규), DSC-09, DSC-10, DATA-01, DATA-05, DATA-06, ARCH-01, REQ-03
- 한 일: 설계 문서 검토에서 찾은 빈틈을 사용자 합의대로 문서에 반영 (코드 없음)
  - 수집함은 전송 성공 시에만 비운다. 전송 성공 = 메시지 1 성공 (SCH-R6, DATA-01)
  - 메시지 1은 성공하고 메시지 2만 실패하면 보낸 것으로 처리하고, `msg2_failed`를 기록해 다음 리포트 안내 카드에 알린다 (DSC-10, DSC-09, DATA-05)
  - 예약 실행이 빠지는 날을 위해 17:50 백업 리포트 실행을 둔다. 이미 보냈으면 건너뛰고 `skipped`를 기록한다 (SCH-R9, DATA-06)
  - SCH-D2의 판단 대상을 "수집함 전체"에서 "범위 안 기사"로 고쳤다 (SCH-R2·R7과 맞춤)
  - 02 §3: GitHub concurrency는 대기 실행을 하나만 두는 동작과 실행 시작 시 `pull --rebase` 추가
  - docs/README.md ID 표의 작업 범위 `T00~T12` → `T00~T14`
- 바뀐 파일: `docs/00`, `01`, `02`, `04`, `06`, `08`, `docs/README.md`, `portfolio/problems/R2-actions-delay.md`
- 다이어그램: ARCH-D1, SCH-D1, SCH-D2, DSC-D1, DATA-D1 갱신·문법 확인
- 테스트: 해당 없음 (코드 없음)
- 문서와 다르게 한 것: 없음 (문서 자체 보완)
- 포트폴리오 그림: 영향 없음 (수집은 여전히 하루 4회, 백업 실행은 그림 범위 밖)
- 다음 작업: T00

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
