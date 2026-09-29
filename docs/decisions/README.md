# 결정 기록 (ADR)

설계 방향을 정한 이유를 남긴다. 한 번 쓴 ADR은 고치지 않고, 결정을 바꿀 때는 새 ADR을 쓰고 이전 것의 상태를 `대체됨 (ADR-xxx)`으로 바꾼다.

| ID | 제목 | 상태 | 날짜 |
|---|---|---|---|
| [ADR-001](ADR-001-rss-source.md) | 크롤링 대신 RSS로 수집 | 채택 | 2026-09-28 |
| [ADR-002](ADR-002-jev-gemini-roles.md) | Jev는 판단, Gemini는 글쓰기 | 채택 | 2026-09-28 |
| [ADR-003](ADR-003-discord-text-feedback.md) | Discord 전달 + 텍스트 피드백 | 채택 | 2026-09-28 |
| [ADR-004](ADR-004-cutoff-1730.md) | 17:30 고정 마감 + 하루 4회 수집 | 채택 | 2026-09-28 |
| [ADR-005](ADR-005-json-in-git.md) | DB 없이 JSON을 git에 저장 | 채택 | 2026-09-28 |
| [ADR-006](ADR-006-no-top-filling.md) | Top이 부족해도 채우지 않음 | 채택 | 2026-09-28 |
| [ADR-007](ADR-007-local-first.md) | 로컬 구현·테스트 후 클라우드 이관 | 채택 | 2026-09-28 |
| [ADR-008](ADR-008-metrics-for-evidence.md) | 포트폴리오 증거를 위해 실행 지표를 처음부터 기록 | 채택 | 2026-09-28 |

## 템플릿

```markdown
# ADR-000 제목

- 상태: 제안 | 채택 | 대체됨 (ADR-xxx)
- 날짜: YYYY-MM-DD
- 관련: 문서 ID

## 맥락
무엇이 문제였나

## 결정
무엇을 하기로 했나

## 검토한 대안
- 대안 A: 버린 이유

## 결과
좋아지는 점 / 감수하는 점
```
