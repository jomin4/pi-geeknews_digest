# 로컬 세팅과 Claude Code 시작하기 (Ubuntu 기준)

> 상태: 확정 · 최종 수정: 2026-09-30 · 관련: [08 구현 계획](08-implementation-plan.md), [ADR-007](decisions/ADR-007-local-first.md)

순서: **1. 프로그램 설치 → 2. 레포 받기 → 3. 동작 확인 → 4. Claude Code 시작(T03부터)**. 계정과 API 키는 필요한 작업 직전에 준비하면 된다 (5절).

> **현재 상태 (2026-09-30)**: T00~T02는 클라우드 세션에서 끝났다 (키·봇 설정이 필요 없어서, 사용자 결정). 로컬은 **T03 Jev 판단**부터 시작한다. 지금까지 무엇을 왜 했는지는 [worklog.md](worklog.md) 맨 위부터 읽으면 된다.

## 1. 필요한 프로그램

| 프로그램 | 용도 | 설치 (Ubuntu) | 확인 |
|---|---|---|---|
| git | 레포 받기·커밋 | `sudo apt install -y git` | `git --version` |
| uv | Python 3.12와 패키지 관리 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` 후 새 터미널 | `uv --version` |
| Node.js 20 이상 | 포트폴리오 그림·PDF 도구 | 이미 있으면 그대로, 없으면 nvm 또는 NodeSource | `node -v` |
| 한글 글꼴 | PDF의 한글 | `sudo apt install -y fonts-noto-cjk` | `fc-list :lang=ko \| head -1` |
| Claude Code | 구현 담당 | `curl -fsSL https://claude.ai/install.sh \| bash` (또는 `npm install -g @anthropic-ai/claude-code`) | `claude --version` |

Python 3.12는 따로 설치하지 않아도 된다. `uv sync`가 `.python-version`(3.12)에 맞는 버전을 받아 쓴다.

macOS는 `brew install git uv node`, Windows는 WSL(Ubuntu)에서 위 표대로 설치한다.

## 2. 레포 받기와 GitHub 연결

```bash
cd ~
git clone https://github.com/jomin4/pi-geeknews_digest.git
cd pi-geeknews_digest
git log --oneline -5      # 최근 커밋에 [T02] 범위 · 상태가 보이면 최신
```

**이미 같은 이름의 폴더가 있다면** (설계 단계에서 만든 사본 등) 그 폴더에 이어 붙이지 말고 이름을 바꿔 두고 새로 clone한다. 옛 폴더에만 있는 파일이 있으면 새 폴더로 옮긴 뒤 `git status`로 확인한다.

```bash
mv ~/pi-geeknews_digest ~/pi-geeknews_digest.old
```

**push 권한**: clone은 로그인 없이 되지만 push에는 GitHub 인증이 필요하다. GitHub CLI로 한 번 로그인해 두면 git이 그 인증을 쓴다.

```bash
sudo apt install -y gh     # macOS: brew install gh
gh auth login              # GitHub.com → HTTPS → 브라우저로 로그인
gh auth setup-git
git remote -v              # origin https://github.com/jomin4/pi-geeknews_digest.git
```

## 3. 동작 확인 (처음 한 번)

### 3.1 Python 프로젝트

```bash
uv sync                                  # .venv 생성, 의존성 설치
uv run pytest                            # 114 passed (T02 기준). 인터넷 없이도 통과해야 한다
uv run gndigest --help
uv run gndigest collect --dry-run        # 실제 GeekNews 피드 수집 → out/articles.json (data/는 안 바뀜)
```

마지막 명령이 `RSS 50건 · 새 글 …건 · 수집함 …건 → out/articles.json`을 출력하면 성공이다. `out/`은 git에 올라가지 않는다.

### 3.2 포트폴리오 도구

구현과 별개로, 그림과 PDF 도구가 내 컴퓨터에서 도는지 먼저 확인한다.

```bash
npm --prefix tools/portfolio install      # 의존성 (Excalidraw, marked, playwright-core)
npm --prefix tools/portfolio run setup    # 헤드리스 Chromium 설치
python3 tools/figgen.py --all             # 그림 명세 → .excalidraw
npm --prefix tools/portfolio run figures  # .excalidraw → SVG·PNG
npm --prefix tools/portfolio run pdf      # 초안 PDF
```

마지막 명령이 `PDF: portfolio/dist/geeknews-digest-portfolio.pdf (초안, 5쪽 / 목표 5쪽)`을 출력하면 성공이다. 이때 `git status`에 그림·PDF 변경이 보이면, 내 컴퓨터 글꼴로 다시 그려진 것이라 커밋해도 되고 `git checkout -- portfolio/`로 되돌려도 된다.

## 4. Claude Code 시작하기

### 4.1 개인 스킬 넣기 (선택, 추천)

my claude skills 레포의 두 스킬을 Claude Code 개인 스킬 폴더에 넣으면, 다른 프로젝트에서도 같은 포트폴리오 방식이 적용된다.

```bash
mkdir -p ~/.claude/skills
cp -r <my-claude-skills 경로>/portfolio-driven-project ~/.claude/skills/
cp -r <my-claude-skills 경로>/portfolio-diagram-style ~/.claude/skills/
```

이 저장소 안에서는 `CLAUDE.md`와 `portfolio/` 규칙이 이미 같은 내용을 담고 있어서, 스킬이 없어도 동작한다.

### 4.2 첫 로컬 세션 (T03 Jev 판단)

준비: OpenRouter 키 (5절). `.env`에 넣는다.

```bash
cd ~/pi-geeknews_digest
git checkout main && git pull
cp .env.example .env          # OPENROUTER_API_KEY= 뒤에 키 붙여넣기
git checkout -b t03-jev
claude
```

Claude Code는 `CLAUDE.md`를 자동으로 읽는다. 클라우드 세션의 대화 내용은 모르므로, 첫 메시지로 아래를 붙여넣어 worklog부터 읽게 한다.

```
이 저장소는 포트폴리오용 프로젝트다. 나는 기획·설계를 맡았고, 너는 설계 문서대로 구현하면서 문서를 최신으로 유지한다.
T00~T02는 클라우드 세션에서 끝났고, 오늘부터 로컬에서 이어간다.

먼저 읽을 것: docs/README.md → docs/worklog.md (맨 위 4개 항목) → docs/03-jev-decisions.md (JEV-C1~C9, JEV-Q1~Q4) → docs/08-implementation-plan.md의 T03

작업: T03 Jev 판단
1. 코드를 쓰기 전에 구현할 규칙 ID, 만들 파일 목록, 기록할 지표(jev_calls, jev_errors, jev_cost_usd, jev_latency_ms_p50)를 보여주고 내 확인을 받아라.
2. 가짜 응답(tests/fixtures/jev_*.json)으로 단위 테스트를 먼저 만든다. 테스트는 인터넷 없이 돌아야 한다 (tests/conftest.py가 네트워크를 막는다).
3. 실제 API 스모크 테스트(기사 10건)는 실행 전에 내 승인을 받는다. 키는 `uv run --env-file .env ...`로만 넘기고, 키 값을 출력·기록하지 않는다.
4. OPEN-1(한국어 vs 영어 criteria), OPEN-5(응답 형식) 결과를 docs/README.md §5와 portfolio/logs에 남긴다. 스모크 결과는 worklog 표와 portfolio/evidence/R1/에도 남긴다.
5. 실제 응답 형식이 문서와 다르면 fixture를 실제 형식에 맞추고, 문서와 다르게 구현해야 하면 코드 전에 멈추고 물어본다.
6. 끝나면 CLAUDE.md 3절 체크리스트를 모두 처리하고 목록으로 보고한다.
7. 현재 브랜치(t03-jev)에 커밋하고, 커밋 메시지는 [T03][규칙ID] 형식으로 쓴다. push는 내가 확인한 뒤에 한다.
```

### 4.3 이후 작업의 흐름 (작업 하나 = 세션 하나 = 브랜치 하나)

1. 이전 작업 PR이 병합된 뒤 `git checkout main && git pull && git checkout -b t04-selector`
2. `claude` 실행 후 아래 틀로 지시 (`/clear`로 이전 대화를 비우고 시작)

```
작업: T04 선별 · 번호
기준 문서: docs/03-jev-decisions.md (JEV-R1~R9, JEV-D1), docs/06-discord-report.md (DSC-03)
CLAUDE.md의 작업 절차와 3절 체크리스트를 따를 것.
완료 조건은 docs/08-implementation-plan.md의 T04 항목.
시작 전에 규칙 ID·파일 목록·지표를 보여주고, 문서와 다르게 해야 하면 멈추고 물어볼 것.
```

3. 내가 확인할 것: 테스트 통과, `docs/worklog.md` 기록, 바뀐 다이어그램, 문제 해결 로그(`portfolio/logs/`)
4. push 후 GitHub에서 PR을 열고 PR 템플릿의 체크리스트를 확인한 뒤 병합

### 4.4 권한 설정

`.claude/settings.json`에 자주 쓰는 명령(uv, pytest, 그림·PDF 도구, git 조회)이 미리 허용돼 있다. `.env` 읽기는 막혀 있다. push, 파일 삭제, 새 패키지 설치 같은 명령은 매번 확인을 받는다.

## 5. 계정과 API 키: 언제 필요한가

| 작업 | 필요한 것 | 준비 |
|---|---|---|
| T00 ~ T02 | 없음 | 완료 (클라우드 세션, 2026-09-29~30) |
| T03 Jev 판단 | OpenRouter API 키, 소액 충전 | openrouter.ai → Settings → Keys. Jev는 입력 토큰만 과금되며 하루 사용량이 매우 작다 |
| T05 Gemini 요약 | Gemini API 키 (무료 티어) | Google AI Studio → Get API key. 무료 티어 모델 이름과 한도를 확인해 OPEN-2에 기록 |
| T07 Discord 전송 | 봇 토큰, 테스트 서버, 채널 ID 2개, 내 사용자 ID | 아래 5.1 |
| T11 GitHub Actions | 위 값들을 GitHub Secrets에 등록 | 레포 Settings → Secrets and variables → Actions |

키는 `.env`에만 넣는다 (T00에서 `.env.example`이 만들어진다: `cp .env.example .env`). `.env`는 git에 올라가지 않는다.

코드는 `.env` 파일을 직접 읽지 않고 환경변수만 읽는다 (ARCH-S1). 로컬에서 키가 필요한 명령은 `uv run --env-file .env gndigest report --dry-run`처럼 uv가 `.env`를 넘기게 실행한다. 키가 없는 명령(`collect`)과 `uv run pytest`는 `.env` 없이 돈다.

### 5.1 Discord 봇 만들기 (T07 전에)

1. discord.com/developers → New Application → 이름 입력
2. Bot 메뉴 → Reset Token → 토큰 복사해 `.env`의 `DISCORD_BOT_TOKEN`에
3. Bot 메뉴 → Privileged Gateway Intents → **Message Content Intent** 켜기
4. OAuth2 → URL Generator → Scopes: `bot`, Permissions: View Channels, Send Messages, Embed Links, Read Message History → 나온 주소로 **테스트용 서버**에 초대
5. 테스트 서버에 `리포트` 채널과 `피드백` 채널 만들기 (리포트 채널은 나는 읽기 전용)
6. Discord 설정 → 고급 → 개발자 모드 켜기 → 채널 우클릭 "ID 복사"로 두 채널 ID, 내 프로필 우클릭으로 내 사용자 ID를 `.env`에

## 6. 문제가 생기면

| 증상 | 해결 |
|---|---|
| `uv: command not found` | 새 터미널을 열거나 `source ~/.local/bin/env` |
| 그림·PDF 도구가 "Chromium을 찾지 못했습니다" | `npm --prefix tools/portfolio run setup`, 또는 `CHROMIUM_PATH=/usr/bin/google-chrome` 지정 |
| PDF의 한글이 네모로 보임 | `sudo apt install -y fonts-noto-cjk` 후 다시 빌드 |
| Claude Code가 설계와 다르게 구현하려 함 | CLAUDE.md 1절을 다시 읽게 하고, 문서를 먼저 고칠지 결정한다 |

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-09-29 | 최초 작성 (Ubuntu 기준) |
| 2026-09-29 | T00: `.env`를 `uv run --env-file`로 넘기는 방법 추가 |
| 2026-09-30 | 로컬 이관: 현재 상태(T00~T02 완료), 기존 폴더 처리·GitHub 인증(`gh auth login`), 동작 확인(3.1), 첫 로컬 세션을 T03으로 바꿈, 4.3 예시를 T04로 |
