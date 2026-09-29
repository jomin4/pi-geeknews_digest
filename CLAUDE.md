# CLAUDE.md — geeknews-digest 작업 규칙

GeekNews RSS를 수집해 Jev(판단)와 Gemini(요약)로 리포트를 만들고 Discord로 보내는 프로젝트다. **포트폴리오용 프로젝트**이며 역할이 나뉘어 있다.

| 누가 | 맡는 일 |
|---|---|
| 사용자 | 기획·설계 (`docs/`), 결정 (`docs/decisions/`), 포트폴리오 문장 확정 |
| Claude Code | 설계 문서대로 구현, 테스트, **문서 최신화**, 문제 해결 기록, 측정, 포트폴리오 초안 |

시작점: 설계는 `docs/README.md`, 포트폴리오는 `portfolio/README.md`.

---

## 1. 문서가 기준이다

- `docs/`가 설계의 기준이다. 코드는 문서를 따른다.
- 작업 전에 `docs/README.md`와 작업에 해당하는 문서를 **반드시 먼저 읽는다**.
- 문서에 없는 동작을 추가하거나 문서와 다르게 구현해야 하면, **코드를 쓰기 전에 멈추고 사용자에게 알린다.** 합의되면 문서를 먼저 고친다. 설계 방향이 바뀌는 수준이면 ADR 초안을 제안한다 (채택은 사용자가 한다).
- 상태가 `초안` 또는 `변경 중`인 설계 문서의 내용은 구현하지 않는다.

## 2. 작업 절차 (작업 하나마다)

1. 작업 번호(T00~T14)와 기준 문서 ID를 확인한다 (`docs/08-implementation-plan.md`).
2. 해당 문서와 다이어그램을 읽고, **구현할 규칙 ID 목록과 기록할 지표**를 먼저 사용자에게 보여준다.
3. 테스트를 먼저 쓰고 구현한다. 테스트 이름에 규칙 ID를 넣는다 (`test_sch_r3_cutoff_is_fixed`).
4. 규칙을 구현한 함수 위에 `# spec: SCH-R3` 주석을 단다.
5. 작업의 지표 필드를 `metrics.py`로 기록한다 (DATA-06, 08 문서의 각 작업 "지표" 줄).
6. `uv run pytest`가 통과해야 끝난다.
7. 아래 **3. 문서 최신화 체크리스트**를 모두 처리한다.
8. 커밋 메시지는 `[T03][JEV-Q1] 설명` 형식. PR은 `.github/pull_request_template.md`를 채운다.

## 3. 문서 최신화 체크리스트 (작업 끝날 때마다)

설계 문서
- [ ] 구현이 끝난 문서의 상태를 `구현됨`으로 바꾸고 하단 **변경 이력**에 한 줄 추가
- [ ] 동작이 달라졌다면 해당 Mermaid 다이어그램을 같은 커밋에서 고친다
- [ ] 미결 사항(OPEN-n)을 확인했다면 `docs/README.md` §5 표에 결과를 적는다
- [ ] `docs/worklog.md` 맨 위에 템플릿대로 기록한다

포트폴리오
- [ ] 이번 작업에서 문제가 있었다면 `portfolio/logs/L-날짜-번호.md`를 남겼다 (4절)
- [ ] 관련 후보(P/R)의 "필요한 증거" 체크박스와 상태를 갱신했다
- [ ] 설계 변경으로 포트폴리오 그림이 틀려졌다면 `portfolio/figures/README.md`의 상태를 `갱신 필요`로 바꾸고 명세를 고쳤다
- [ ] 루트 `README.md`의 진행 상황 표를 갱신했다

## 4. 문제 해결 기록 규칙 (portfolio/logs)

다음 중 하나가 생기면 **그 자리에서** `portfolio/logs/_TEMPLATE.md`로 로그를 만든다.
- 설계대로 했는데 예상과 다르게 동작했다 (외부 API 응답 형식, 한도, 시간대 등)
- 테스트가 실패해 원인을 찾았다 (단순 오타 제외)
- 설계 문서와 다르게 구현해야 했다
- 성능·비용·안정성 수치가 눈에 띄게 달라졌다
- 미결 사항(OPEN-n)을 확인했다

작성 규칙
- 현상은 **로그·에러·수치 원문**을 붙인다. 추측으로 채우지 않는다.
- 원인은 **어떻게 확인했는지**(재현 명령, 본 파일)까지 쓴다.
- `## 내 메모` 칸은 비워 둔다. 사용자가 쓴다.
- 포트폴리오 후보와 연결되면 해당 `portfolio/problems/P?.md`의 관련 로그에 ID를 추가한다. 새 후보감이면 사용자에게 제안만 한다.

## 5. 측정과 포트폴리오 규칙

- **수치를 지어내지 않는다.** 포트폴리오·로그·문서의 모든 결과 수치는 실제 실행 결과여야 하고, `portfolio/evidence/`의 원본 파일로 되돌아갈 수 있어야 한다. 측정 전에는 `측정 예정`으로 둔다.
- 측정 스크립트는 `experiments/`에 둔다. 테스트가 아니므로 CI에서 돌리지 않는다. **실제 API를 부르는 실험은 사용자 승인 후 실행**한다.
- 원본 결과 파일은 수정하지 않는다. 다시 측정하면 새 날짜 파일을 만든다 (`portfolio/evidence/README.md`).
- `portfolio/problems/`의 항목은 증거가 모이면 5단계(제목·그림·문제 원인·해결 과정·결과)로 **초안**까지만 쓴다. 상태가 `확정`인 항목의 문장은 고치지 않는다 (수치가 틀렸으면 사용자에게 알린다).
- 해결 과정의 "왜 그 방법인지"는 ADR과 로그에 있는 근거만 쓴다.
- P3 라벨처럼 사용자의 판단이 필요한 데이터는 빈 칸으로 만들어 두고 채우지 않는다.

## 6. 그림 규칙

| 용도 | 도구 | 규칙 |
|---|---|---|
| 설계 문서 `docs/` | Mermaid (문서 안 코드블록) | 이미지 파일을 따로 만들지 않는다 |
| 포트폴리오 `portfolio/` | Excalidraw | `portfolio/STYLE-GUIDE.md`를 따르고, 명세 JSON → `python tools/figgen.py 명세.json`으로 생성 |

- 포트폴리오 그림은 명세(`portfolio/figures/specs/`)를 고치고 다시 생성한다. `.excalidraw`를 직접 손으로 편집하지 않는다 (사용자가 손질한 파일은 덮어쓰기 전에 묻는다).
- 스타일 가이드에 없는 색·도형을 쓰지 않는다. 필요하면 스타일 가이드 변경을 사용자에게 제안한다.
- 명세를 고쳤으면 `python tools/figgen.py 명세.json` → `npm --prefix tools/portfolio run figures -- FIG-ID`로 SVG·PNG까지 다시 만들고, 결과 PNG를 직접 열어 겹침이 없는지 확인한다.
- `figures/README.md`에서 상태가 `손질함`인 그림은 명세로 다시 생성하지 않는다 (사용자가 excalidraw.com에서 고친 것). 먼저 묻는다.
- 포트폴리오 원고나 그림이 바뀌면 `npm run pdf`로 **초안 PDF**를 다시 만들고, 빌드 출력의 쪽 높이 경고를 확인한다. 최종 PDF(`--final`)는 사용자가 요청할 때만 만든다.

## 7. 코드 규칙

- Python 3.12, uv, pytest. 구조는 `docs/01-architecture.md` §5를 따른다.
- 모든 외부 호출(RSS, OpenRouter, Gemini, Discord)은 한 모듈을 거치고, 테스트에서는 `tests/fixtures/`의 가짜 응답을 쓴다. **테스트가 인터넷에 접속하면 안 된다.**
- 비밀값은 환경변수로만 읽는다. `data/`, 코드, 테스트, 로그, 증거 파일에 키를 쓰지 않는다.
- `data/`의 JSON은 `storage.py`로만 읽고 쓴다 (원자적 저장, pydantic 검증).
- 시각은 항상 KST(`Asia/Seoul`) 기준 aware datetime으로 다룬다.
- 기준선 숫자를 코드에 하드코딩하지 않는다. `state.json`의 `thresholds`를 읽는다 (기본값만 `config.py`).
- 프롬프트 원문은 `src/gndigest/prompts/`에 두고 `docs/05-gemini-prompts.md`와 내용을 같게 유지한다.

## 8. 하지 말 것

- 문서를 읽지 않고 구현 시작
- 테스트에서 실제 API 호출
- `data/` 파일을 검증 없이 덮어쓰기
- 문서 변경 없이 동작 변경
- 측정하지 않은 수치를 문서·포트폴리오에 쓰기
- `확정` 상태의 포트폴리오 문장 수정, `## 내 메모` 칸 작성
- 설계 문서 그림을 이미지 파일로 만들기, 포트폴리오 그림을 스타일 가이드 밖으로 그리기

## 9. 자주 쓰는 명령

```bash
uv run pytest
uv run gndigest collect --dry-run
uv run gndigest report --dry-run --cutoff 2026-09-28T17:30:00+09:00
uv run gndigest show-profile
python tools/figgen.py portfolio/figures/specs/FIG-P0-architecture.json
npm --prefix tools/portfolio install          # 처음 한 번 (포트폴리오 도구)
npm --prefix tools/portfolio run setup        # 처음 한 번 (Chromium 설치)
npm --prefix tools/portfolio run figures      # Excalidraw → SVG·PNG (전부, 또는 -- FIG-P1)
npm --prefix tools/portfolio run pdf          # 초안 PDF → portfolio/dist/
```
