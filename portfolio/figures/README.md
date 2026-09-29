# 그림 목록

모든 그림은 [STYLE-GUIDE.md](../STYLE-GUIDE.md)를 따른다.

| ID | 유형 | 쓰는 곳 | 명세 | Excalidraw | SVG · PNG | 상태 |
|---|---|---|---|---|---|---|
| FIG-P0-architecture | 전체 구조 | 00-project-summary, README | [specs](specs/FIG-P0-architecture.json) | [열기](FIG-P0-architecture.excalidraw) | [svg](FIG-P0-architecture.svg) · [png](FIG-P0-architecture.png) | 내보내기 최신 |
| FIG-P1-rss-coverage | 구조 + 문제 지점 | P1 | [specs](specs/FIG-P1-rss-coverage.json) | [열기](FIG-P1-rss-coverage.excalidraw) | [svg](FIG-P1-rss-coverage.svg) · [png](FIG-P1-rss-coverage.png) | 내보내기 최신 |
| FIG-P2-gemini-calls | 개선 전후 | P2 | [specs](specs/FIG-P2-gemini-calls.json) | [열기](FIG-P2-gemini-calls.excalidraw) | [svg](FIG-P2-gemini-calls.svg) · [png](FIG-P2-gemini-calls.png) | 내보내기 최신 |
| FIG-P3-summary-grounding | 구조 + 문제 지점 | P3 | [specs](specs/FIG-P3-summary-grounding.json) | [열기](FIG-P3-summary-grounding.excalidraw) | [svg](FIG-P3-summary-grounding.svg) · [png](FIG-P3-summary-grounding.png) | 내보내기 최신 |
| FIG-P4-feedback-loop | 구조 + 문제 지점 | P4 | [specs](specs/FIG-P4-feedback-loop.json) | [열기](FIG-P4-feedback-loop.excalidraw) | [svg](FIG-P4-feedback-loop.svg) · [png](FIG-P4-feedback-loop.png) | 내보내기 최신 |

**상태 값**: 명세만 · 생성됨 · 내보내기 최신 · 손질함(사람이 excalidraw.com에서 고침) · **갱신 필요**(설계나 수치가 바뀌어 그림이 틀림)

## 만드는 순서

```bash
# 1) 명세 → .excalidraw  (저장소 루트에서)
python tools/figgen.py portfolio/figures/specs/FIG-P1-rss-coverage.json   # 하나
python tools/figgen.py --all                                               # 전부

# 2) .excalidraw → .svg + .png  (처음 한 번: npm --prefix tools/portfolio install && npm --prefix tools/portfolio run setup)
npm --prefix tools/portfolio run figures            # 전부
npm --prefix tools/portfolio run figures -- FIG-P1  # 하나만

# 3) PDF 다시 만들기
npm --prefix tools/portfolio run pdf
```

- 2단계는 excalidraw.com의 "Export image"와 **같은 엔진**(`@excalidraw/excalidraw` 0.18.1)을 헤드리스 Chromium에서 돌린다. 그래서 excalidraw.com에서 직접 내보낸 것과 모양이 같다.
- **SVG**: 영문 글꼴(Excalidraw Normal)을 파일 안에 넣는다. 한글은 보는 기기의 기본 글꼴로 나온다 (excalidraw.com도 같다). PDF는 SVG를 우선 쓴다 (확대해도 선명).
- **PNG**: 2배율, 흰 배경. README·슬라이드처럼 이미지가 필요한 곳에 쓴다. 한글 글꼴이 이미지에 고정된다.

## 사람이 손질한 그림

excalidraw.com에서 `.excalidraw`를 열어 위치를 손으로 고쳤다면:
1. 같은 파일에 덮어쓰고 상태를 `손질함`으로 바꾼다.
2. 이후 명세로 다시 생성하면 손질이 사라진다. **손질함 상태인 그림은 명세로 다시 생성하지 않는다** (Claude Code는 먼저 묻는다). 내보내기(2단계)는 해도 된다.

## 명세(spec) 형식

```json
{
  "id": "FIG-P1-rss-coverage",
  "nodes": [
    {"id": "rss", "kind": "start", "label": "GeekNews RSS", "x": 10, "y": 245, "w": 150, "h": 80},
    {"id": "srv", "kind": "server", "label": "수집 · 리포트 실행\n(GitHub Actions)", "x": 290, "y": 180, "h": 210},
    {"id": "art", "label": "articles.json", "color": "green", "x": 590, "y": 240}
  ],
  "edges": [
    {"from": "rss", "to": "srv", "n": 1, "label": "하루 4회", "note": "최신 50건만"},
    {"from": "srv", "to": "art", "n": 3}
  ],
  "brackets": [{"nodes": ["st", "art"], "label": "git"}],
  "texts": [{"text": "개선 전", "x": 0, "y": 52}],
  "dividers": [{"x1": 0, "x2": 990, "y": 145}]
}
```

| 필드 | 값 |
|---|---|
| `kind` | start(타원), server(큰 사각형), box(기본), decision(마름모) |
| `color` | white(기본), green, red, purple, orange — 한 그림에 2가지까지 |
| `n` / `label` / `note` | 화살표 번호 / 6자 이내 라벨 / 빨간 문제 주석(한 그림에 한 곳) |
| `dashed` | 다음 실행으로 넘어가는 흐름 |
| `from_side` / `to_side` / `from_at` / `to_at` | 선이 붙는 변(right·left·top·bottom)과 그 변 위 위치(0~1) |
| `via` | 꺾이는 점 목록 |
| `seg` / `flip` | 번호·라벨을 붙일 구간 / 선의 반대편에 붙이기 (주석은 항상 반대편) |
| `brackets` | 박스 묶음 괄호 + 한 단어 (`side`: right 기본, bottom) |
| `texts` / `dividers` | 행 이름(회색) / 개선 전후 사이 회색 점선 |

글자가 선과 겹치면 박스 사이 간격을 넓힌다 (최소 90px).
