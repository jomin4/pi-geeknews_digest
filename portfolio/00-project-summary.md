# GeekNews Digest

> 상태: 초안 · PDF 1페이지 원고 · 문제 해결 경험 목록은 빌드할 때 `pdf.config.json` 순서대로 자동 생성된다

<!-- PDF:START -->

**매일 올라오는 기술 뉴스를 내 관심사 기준으로 골라 요약해 주는 개인 리포트 봇**

GeekNews의 하루치 글(약 50건)을 판단 모델 Jev로 선별하고 Gemini로 요약해 매일 18시 전에 Discord로 보내며, 텍스트 피드백으로 취향과 선별 기준을 계속 조정하는 자동화 서비스.

| 항목 | 내용 |
|---|---|
| 기간 | 2026.09 ~ (진행 중) |
| 인원 | 1명 |
| 역할 | **기획·설계 전담** — 요구사항, 아키텍처, 판단 규칙, 데이터 구조, 프롬프트, 측정 설계. 구현은 설계 문서를 기준으로 Claude Code에 맡기고 문서·테스트로 검증 |
| 기술 | Python 3.12 · GitHub Actions · OpenRouter(Jev) · Gemini API · Discord REST · pytest |
| 저장소 | [github.com/jomin4/pi-geeknews_digest](https://github.com/jomin4/pi-geeknews_digest) |

### 전체적인 아키텍처

![FIG-P0](figures/FIG-P0-architecture.png)

- **수집**: RSS가 최신 50건만 보여줘 하루 4회 수집하고 17:30에 마감한다.
- **선별·요약**: Jev가 기사마다 분야·관심도·실무 활용·제외 여부를 확률로 판단하고, Gemini는 Top 최대 8개만 한 번에 요약한다. 요약은 Jev가 원문 근거를 다시 검증한다.
- **전달·피드백**: Discord로 번호 붙은 리포트를 보내고, 피드백 채널의 텍스트를 해석해 다음 날 판단에 반영한다.

### 문제 해결 경험

<!-- PDF:TOC -->

<!-- PDF:END -->
