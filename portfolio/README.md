# 포트폴리오 작성 규칙

> 이 폴더는 PDF 포트폴리오의 **원고**다. 설계 문서(`docs/`)가 "무엇을 어떻게 만들지"라면, 여기는 "만들면서 어떤 문제를 어떻게 풀었는지"를 증거와 함께 남긴다.

## 1. PDF 구성

| 페이지 | 원고 | 내용 |
|---|---|---|
| 1 | [00-project-summary.md](00-project-summary.md) | 프로젝트 한 줄 소개, 내 역할, 기술, 전체 구조 그림 |
| 2~5 | `problems/P*.md` 중 **확정 4개** | 문제 해결 경험 1개 = 1페이지 |

## 2. 문제 해결 경험 1개의 구조 (5단계, 모든 항목 동일)

| 단계 | 분량 | 쓰는 법 |
|---|---|---|
| 1. 제목 | 1문장 | **어떤 기능**에서 **어떤 문제**를 **어떻게** 해결했는지. 예: "리포트 수집에서 RSS 50건 제한으로 생기는 누락을 하루 4회 수집과 고정 마감으로 해결" |
| 2. 그림 | 1장 | [STYLE-GUIDE.md](STYLE-GUIDE.md)의 `BA`(개선 전후) 또는 `FLOW` 유형. 한눈에 상황이 보여야 한다 |
| 3. 문제 원인 | 3줄 | 어떻게 발견했고, 어떤 현상이었고, 원인이 무엇이었는지 |
| 4. 해결 과정 | 3~4줄 + 테스트 | **왜 그 방법을 골랐는지** 논리 흐름. 번호는 그림의 단계 번호와 맞춘다. 마지막에 "테스트" 하위 항목 |
| 5. 결과 | 수치 + 조건 | 개선 전 → 후 수치와 **테스트 조건**(기간, 데이터 양, 환경, 측정 방법). 근거 파일 링크 |

템플릿: [problems/_TEMPLATE.md](problems/_TEMPLATE.md)

## 3. 가장 중요한 원칙: 내 경험만 쓴다

- 포트폴리오의 주인은 나다. **Claude Code는 기록하고 정리하는 도구**다.
- 결과 수치는 실제로 측정한 값만 쓴다. 측정 전에는 `측정 예정`으로 둔다.
- 해결 과정의 "왜 그 방법을 골랐는지"는 내가 설계에서 내린 결정(ADR)과 구현 중 판단에서 나온다.
- 그림·테스트 결과 같은 **증거를 댈 수 없는 경험은 항목으로 쓰지 않는다.**

## 4. 역할 분담

| 일 | 누가 | 어디에 |
|---|---|---|
| 기획·설계, 문제를 어떻게 풀지 결정 | 나 | `docs/`, `docs/decisions/` |
| 구현 중 생긴 문제를 그때그때 사실대로 기록 | Claude Code | `portfolio/logs/` |
| 측정 실행과 원본 결과 보관 | Claude Code (측정 방법은 내가 승인) | `portfolio/evidence/`, `experiments/` |
| 증거가 모인 후보를 5단계 초안으로 정리 | Claude Code | `portfolio/problems/P*.md` (상태: 초안) |
| 초안을 내 말로 다시 쓰고 확정 | 나 | 같은 파일 (상태: 확정) |
| 그림 명세 작성·생성 | Claude Code | `portfolio/figures/specs/` |
| 그림 손질·PNG 내보내기 | 나 | `portfolio/figures/` |

## 5. 항목 상태

| 상태 | 뜻 | 다음 단계 |
|---|---|---|
| 후보 | 설계 단계에서 예상한 문제. 측정 계획만 있음 | 구현 중 증거 수집 |
| 증거 수집 중 | 로그·측정이 쌓이는 중 | 측정 완료 후 초안 |
| 초안 | Claude Code가 증거로 5단계를 채움 | 내가 검토 |
| 확정 | 내가 내 말로 고쳐 쓰고 수치를 확인함. **Claude Code는 수정 금지** | PDF에 사용 |
| 제외 | 증거가 부족하거나 덜 중요함 | 이유를 한 줄 남김 |

## 6. 후보 목록

| ID | 가제 | 상태 | 핵심 증거 | 관련 설계 |
|---|---|---|---|---|
| [P1](problems/P1-rss-coverage.md) | RSS 50건 제한 속 하루치 수집 누락 방지 | 후보 | 7일간 누락 글 수 (개선 전 모의 vs 개선 후) | SCH-R1~R7, ADR-004 |
| [P2](problems/P2-gemini-free-tier.md) | Gemini 무료 한도 안에서 50건 요약: Jev 선별 후 1회 호출 | 후보 | 호출 수·429 발생·처리 시간 (기사별 호출 vs 선별 후 1회) | ADR-002, GEM-A |
| [P3](problems/P3-summary-grounding.md) | LLM 요약의 원문 외 내용을 Jev 근거 검증으로 차단 | 후보 | 내가 라벨링한 요약 N건의 원문 외 내용 비율 | JEV-V1~V3 |
| [P4](problems/P4-feedback-personalization.md) | 텍스트 피드백과 기준선 보정으로 Top 적중률 개선 | 후보 | 4주간 주별 Top "좋음" 비율 | FB-*, ADR-003, ADR-006 |
| [R1](problems/R1-jev-order-bias.md) | 판단 모델의 선택지 순서 편향 측정과 고정 | 예비 | 순서를 바꿨을 때 결과가 뒤집히는 비율 | JEV-C6 |
| [R2](problems/R2-actions-delay.md) | 예약 실행 지연 속 18시 전 도착 보장 | 예비 | 14일간 예약 대비 실제 시작 지연 분포 | SCH-R5, ADR-004 |

구현 중 새 문제가 생기면 `logs/`에 먼저 기록하고, 가치가 있으면 새 후보(P5, P6 …)로 올린다. 최종 4개는 증거가 가장 확실한 순서로 내가 고른다.

## 7. PDF 만들기

| 파일 | 역할 |
|---|---|
| [pdf.config.json](pdf.config.json) | PDF에 넣을 항목과 순서 (`problems`), 저장소 주소(`repo_url`, 넣으면 근거 링크가 살아남) |
| 각 원고의 `<!-- PDF:START -->` ~ `<!-- PDF:END -->` | 이 구간만 PDF에 들어간다. 나머지(작성 메모)는 빠진다 |
| 요약 원고의 `<!-- PDF:TOC -->` | 문제 해결 경험 목록을 제목·쪽 번호로 자동 생성 |
| `dist/geeknews-digest-portfolio.pdf` | 결과물 |

```bash
npm --prefix tools/portfolio install      # 처음 한 번
npm --prefix tools/portfolio run setup    # 처음 한 번 (Chromium 설치)
npm --prefix tools/portfolio run figures  # 그림 내보내기
npm --prefix tools/portfolio run pdf      # 초안 PDF: 상태 표시, '측정 예정' 강조, 쪽 아래 '초안'
node tools/portfolio/build-pdf.mjs --final   # 최종 PDF: 모두 '확정'이고 '측정 예정'·'(가제)'·빈 저장소 주소가 없을 때만 만든다
```

- 원고 하나 = 한 쪽이다. 빌드가 쪽마다 높이를 알려 주고, 한 쪽을 넘으면 경고한다.
- 최종 PDF는 **사용자가 요청할 때만** 만든다.

## 8. 흐름 요약

```
구현 중 문제 발생 ─▶ logs/L-날짜-번호.md (사실 기록)
                          │
측정 실행 ─────────▶ evidence/P번호/ (원본 결과 + 조건)
                          │
증거 충분 ─────────▶ problems/P번호.md 초안 + figures/specs 갱신
                          │
내가 검토·재작성 ──▶ 상태 확정 ─▶ PDF
```
