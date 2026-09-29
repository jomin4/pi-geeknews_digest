# GeekNews Digest 문서 지도

> 이 폴더가 프로젝트의 **기준(Source of Truth)** 이다. 코드는 문서를 따르고, 동작을 바꾸려면 문서를 먼저 고친다.

## 1. 한눈에 보기

GeekNews RSS를 하루 4번 수집하고, 매일 17:30(KST)에 **Jev가 판단**하고 **Gemini가 요약**한 리포트를 Discord로 보낸다. 나는 18~20시에 읽고, 피드백 채널에 텍스트로 의견을 남기면 다음 리포트부터 반영된다.

## 2. 읽는 순서

| 순서 | 문서 | 내용 | 상태 |
|---|---|---|---|
| 1 | [00-overview.md](00-overview.md) | 목적, 요구사항(REQ), 용어집 | 확정 |
| 2 | [01-architecture.md](01-architecture.md) | 전체 구조, 컴포넌트, 코드 배치 | 확정 |
| 3 | [02-schedule-and-range.md](02-schedule-and-range.md) | 실행 시각, 수집 범위 경계, 실행 순서 | 확정 |
| 4 | [03-jev-decisions.md](03-jev-decisions.md) | Jev 질문 설계, 선별 규칙, 요약 검증 | 확정 |
| 5 | [04-data-model.md](04-data-model.md) | data 폴더 JSON 구조, 보관 규칙 | 확정 |
| 6 | [05-gemini-prompts.md](05-gemini-prompts.md) | 리포트 요약·피드백 해석 프롬프트 | 확정 |
| 7 | [06-discord-report.md](06-discord-report.md) | 리포트 양식, 메시지 분할 | 확정 |
| 8 | [07-feedback-loop.md](07-feedback-loop.md) | 피드백 → 취향·기준선 반영 | 확정 |
| 9 | [08-implementation-plan.md](08-implementation-plan.md) | 작업 단위 T00~T14, 로컬→클라우드→포트폴리오 | 확정 |
| - | [../portfolio/](../portfolio/README.md) | 포트폴리오 원고·그림(Excalidraw)·측정 증거 | 계속 갱신 |
| - | [SETUP.md](SETUP.md) | 로컬 세팅, Claude Code 시작, 계정·키 준비 시점 | 확정 |
| - | [decisions/](decisions/) | 결정 기록(ADR): 왜 그렇게 정했는지 | - |
| - | [worklog.md](worklog.md) | 세션별 작업 기록 | 계속 갱신 |

## 3. 다이어그램 목록

모든 다이어그램은 각 문서 안에 Mermaid 코드블록으로 들어 있다. GitHub(모바일 포함)에서 바로 그림으로 보인다.

| ID | 다이어그램 | 위치 | 이걸 보면 알 수 있는 것 |
|---|---|---|---|
| ARCH-D1 | 전체 아키텍처 | [01](01-architecture.md#arch-d1-전체-아키텍처) | 어떤 부품이 어떤 순서로 연결되는지 |
| SCH-D1 | 수집 범위 타임라인 | [02](02-schedule-and-range.md#sch-d1-수집-범위-타임라인) | 어느 글이 어느 날 리포트에 들어가는지 |
| SCH-D2 | 17:30 실행 순서 | [02](02-schedule-and-range.md#sch-d2-1730-리포트-실행-순서) | 리포트 실행 한 번에 일어나는 일 |
| JEV-D1 | 기사 선별 흐름 | [03](03-jev-decisions.md#jev-d1-기사-선별-흐름) | 한 기사가 Top/확인/기타/제외로 갈리는 규칙 |
| DATA-D1 | 데이터 모델 | [04](04-data-model.md#data-d1-데이터-모델) | JSON 파일 사이의 관계 |
| DSC-D1 | Discord 리포트 구성 | [06](06-discord-report.md#dsc-d1-리포트-구성) | 메시지 두 개에 무엇이 들어가는지 |
| FB-D1 | 피드백 반영 흐름 | [07](07-feedback-loop.md#fb-d1-피드백-반영-흐름) | 피드백이 다음 리포트에 반영되는 두 경로 |
| PLAN-D1 | 구현 로드맵 | [08](08-implementation-plan.md#plan-d1-구현-로드맵) | 작업 순서와 로컬→클라우드 전환 시점 |

## 4. 문서 관리 규칙

### 4.1 ID 체계

설계 항목마다 ID가 있고, 코드·커밋·작업기록이 모두 같은 ID를 가리킨다.

| 접두어 | 대상 | 예시 |
|---|---|---|
| `REQ-` | 요구사항 | REQ-03 18시 전 도착 |
| `ARCH-` | 컴포넌트 | ARCH-06 선별기 |
| `SCH-` | 스케줄·범위 규칙 | SCH-R3 마감 시각 고정 |
| `JEV-Q` / `JEV-R` / `JEV-V` | Jev 질문 / 선별 규칙 / 검증 | JEV-Q2 관심도 |
| `DATA-` | 데이터 파일 | DATA-03 profile.json |
| `GEM-A` / `GEM-B` | 요약 / 피드백 해석 프롬프트 | GEM-A1 원문 외 내용 금지 |
| `DSC-` | Discord 양식 | DSC-04 메시지 분할 |
| `FB-` | 피드백 규칙 | FB-06 60일 정리 |
| `T00`~`T14` | 구현 작업 | T03 Jev 판단 |
| `ADR-` | 결정 기록 | ADR-006 Top 채우지 않기 |
| `P` / `R` | 포트폴리오 문제 해결 후보 / 예비 | P2 Gemini 호출 절감 |
| `L-날짜-번호` | 문제 해결 로그 | L-20261002-1 |
| `FIG-` | 포트폴리오 그림 (Excalidraw) | FIG-P1-rss-coverage |
| `*-D숫자` | 다이어그램 | JEV-D1 |

**추적 방법**
- 코드 주석: `# spec: JEV-Q2` (규칙을 구현한 함수 바로 위)
- 커밋 메시지: `[T03][JEV-Q1] topic 질문 구현`
- 테스트 이름: `test_jev_r4_top_requires_interest_and_confidence`
- worklog: 작업마다 참조한 ID 기록

### 4.2 문서 상태

각 문서 맨 위에 상태를 적는다.

| 상태 | 의미 |
|---|---|
| 초안 | 아직 논의 중. 구현하지 않는다 |
| 확정 | 설계 합의 완료. 구현해도 된다 |
| 구현됨 | 코드와 테스트가 문서와 일치한다 |
| 변경 중 | 문서를 고치는 중. 해당 부분 구현 보류 |

### 4.3 변경 절차

1. 동작을 바꾸고 싶으면 **문서를 먼저** 고친다 (상태: 변경 중).
2. 이유가 설계 방향을 바꾸는 수준이면 ADR을 새로 쓴다.
3. 다이어그램이 달라지면 같은 커밋에서 함께 고친다.
4. 구현하고 테스트가 통과하면 상태를 `구현됨`으로 바꾸고 문서 하단 **변경 이력**에 한 줄 추가한다.
5. worklog.md에 세션 기록을 남긴다.

### 4.4 다이어그램 규칙

그림은 용도에 따라 두 가지로 나눈다.

| 용도 | 도구 | 위치 | 규칙 |
|---|---|---|---|
| 설계 문서 (`docs/`) | Mermaid | 각 문서 안 코드블록 | 아래 규칙 |
| 포트폴리오 (`portfolio/`) | Excalidraw | `portfolio/figures/` | [STYLE-GUIDE.md](../portfolio/STYLE-GUIDE.md) |

설계가 바뀌어 같은 내용을 담은 포트폴리오 그림(예: ARCH-D1 ↔ FIG-P0)이 틀려지면, 그 그림의 상태를 `갱신 필요`로 바꾼다.

- 설계 문서의 그림은 Mermaid로 통일한다. 이미지 파일을 따로 두지 않는다.
- 제목 앞에 ID를 붙인다 (`### ARCH-D1 전체 아키텍처`).
- 다이어그램 안의 이름은 문서 본문의 용어·ID와 같게 쓴다.
- 고친 다이어그램은 Mermaid 렌더러에서 문법을 확인한 뒤 커밋한다.

## 5. 미결·확인 필요 사항

구현 중 확인해서 결과를 해당 문서와 이 표에 반영한다.

| ID | 내용 | 확인 시점 | 결과 |
|---|---|---|---|
| OPEN-1 | Jev criteria를 한국어로 써도 정확한가? 영어 기준과 10건 비교 | T03 | - |
| OPEN-2 | Gemini 무료 티어에서 쓸 Flash 모델 이름과 현재 한도 (AI Studio에서 확인) | T05 | - |
| OPEN-3 | Discord 봇이 REST만으로 메시지를 보내기 전에 게이트웨이 1회 연결이 필요한지 | T07 | - |
| OPEN-4 | RSS의 `published`와 `updated`가 다른 글이 있는지 (수정된 글 처리) | T01 | - |
| OPEN-5 | OpenRouter Decisions API가 `alpha` 경로라 형식이 바뀔 수 있음. 응답 검증으로 대비 | T03 | - |
