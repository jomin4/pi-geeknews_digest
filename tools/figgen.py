#!/usr/bin/env python3
"""figgen: 그림 명세(JSON) -> Excalidraw 파일 생성기.

portfolio/STYLE-GUIDE.md의 규칙(구조만 보여주는 최소 그림)을 코드로 고정해,
누가 만들어도 같은 모양이 나오게 한다.

사용법 (저장소 루트에서)
  python tools/figgen.py portfolio/figures/specs/FIG-P1-rss-coverage.json
      -> portfolio/figures/FIG-P1-rss-coverage.excalidraw
  python tools/figgen.py --all
      -> specs/ 의 모든 명세

이미지(SVG·PNG)는 tools/portfolio 에서 `npm run figures`로 내보낸다.
명세 형식은 portfolio/figures/README.md 참고. 표준 라이브러리만 사용한다.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

# ---- STYLE-GUIDE §3 색 -------------------------------------------------------
FILLS = {
    "white": "#ffffff",
    "green": "#b2f2bb",   # 해결된 부분 · 바뀐 부분
    "red": "#ffc9c9",     # 문제 지점
    "purple": "#d0bfff",  # 구조도 강조 A (전후가 없는 그림에서만)
    "orange": "#ffd8a8",  # 구조도 강조 B
}
INK = "#1e1e1e"          # 선 · 글자
PROBLEM_INK = "#e03131"  # 문제 주석
GRAY = "#868e96"         # 점선 · 괄호 · 구분선
GRAY_TEXT = "#495057"    # 행 이름 · 괄호 이름

# ---- §4 모양 ----------------------------------------------------------------
SHAPES = {"start": "ellipse", "server": "rectangle", "box": "rectangle", "decision": "diamond"}
DEFAULT_SIZE = {"start": (150, 70), "server": (200, 200), "box": (150, 56), "decision": (140, 80)}

# ---- §6 글자 ----------------------------------------------------------------
FONT = 6            # Excalidraw "Normal"(Nunito). 한글은 보는 기기의 기본 글꼴
SIZE_NODE = 18
SIZE_EDGE = 17
SIZE_LABEL = 17
UPDATED = 1759000000000  # 고정: 같은 명세 -> 같은 파일 (git diff 최소화)
MAX_COLORS = 2


def _seed(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest()[:8], 16)


def text_size(text: str, size: int) -> tuple[float, float]:
    """글자 폭 추정: 한글·전각 1.0em, 그 외 0.56em."""
    lines = text.split("\n")
    width = max(sum(size * (1.0 if ord(ch) > 0x2E80 else 0.56) for ch in line) for line in lines)
    return round(width + 2, 1), round(len(lines) * size * 1.25, 1)


def base(eid, etype, x, y, w, h, stroke, bg="transparent", **kw) -> dict:
    el = {
        "id": eid, "type": etype, "x": round(x, 1), "y": round(y, 1),
        "width": round(w, 1), "height": round(h, 1), "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg, "fillStyle": "solid",
        "strokeWidth": kw.pop("strokeWidth", 1), "strokeStyle": kw.pop("strokeStyle", "solid"),
        "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
        "roundness": kw.pop("roundness", None), "seed": _seed(eid), "version": 1,
        "versionNonce": _seed(eid + "#"), "isDeleted": False, "boundElements": [],
        "updated": UPDATED, "link": None, "locked": False,
    }
    el.update(kw)
    return el


def text_el(eid, text, x, y, size, color=INK, center=None) -> dict:
    w, h = text_size(text, size)
    align = "left"
    if center is not None:
        x, y, align = center[0] - w / 2, center[1] - h / 2, "center"
    return base(eid, "text", x, y, w, h, color, text=text, fontSize=size, fontFamily=FONT,
                textAlign=align, verticalAlign="middle" if center else "top",
                containerId=None, originalText=text, autoResize=True, lineHeight=1.25)


def clip(n: dict, tx: float, ty: float) -> tuple[float, float]:
    """도형 중심에서 (tx, ty) 쪽으로 나가는 선이 테두리와 만나는 점."""
    cx, cy = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    hw, hh = n["w"] / 2, n["h"] / 2
    if n["shape"] == "diamond":
        t = 1 / (abs(dx) / hw + abs(dy) / hh)
    elif n["shape"] == "ellipse":
        t = 1 / math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
    else:
        t = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
    return cx + dx * t, cy + dy * t


SIDES = {"right": (1, 0.5), "left": (0, 0.5), "top": (0.5, 0), "bottom": (0.5, 1)}


def anchor(n: dict, side, toward, at=None):
    """side: 도형의 어느 변에서 나갈지, at: 그 변 위의 위치(0~1).
    타원·마름모는 그 위치에서 실제 테두리 위의 점을 쓴다 (선이 곡선에 정확히 닿게)."""
    if not side:
        return clip(n, *toward)
    fx, fy = SIDES[side]
    if at is not None:
        if side in ("top", "bottom"):
            fx = at
        else:
            fy = at
    x, y = n["x"] + n["w"] * fx, n["y"] + n["h"] * fy
    if n["shape"] in ("ellipse", "diamond"):
        cx, cy, hw, hh = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2, n["w"] / 2, n["h"] / 2
        if side in ("left", "right"):
            r = min(abs(y - cy) / hh, 1)
            k = math.sqrt(1 - r * r) if n["shape"] == "ellipse" else 1 - r
            x = cx + (hw * k if side == "right" else -hw * k)
        else:
            r = min(abs(x - cx) / hw, 1)
            k = math.sqrt(1 - r * r) if n["shape"] == "ellipse" else 1 - r
            y = cy + (hh * k if side == "bottom" else -hh * k)
    return x, y


def place(mx, my, nx, ny, text, size, color, eid):
    """선의 한쪽(법선 방향)에 겹치지 않게 글자를 놓는다."""
    w, h = text_size(text, size)
    gap = 6 + abs(nx) * w / 2 + abs(ny) * h / 2
    return text_el(eid, text, mx + nx * gap - w / 2, my + ny * gap - h / 2, size, color)


# ---------------------------------------------------------------------------
def build(spec: dict) -> list[dict]:
    els: list[dict] = []
    fid = spec["id"]

    # 행 이름·구분선 (가장 뒤에)
    for i, d in enumerate(spec.get("dividers", [])):
        els.append(base(f"dv{i}", "line", d["x1"], d["y"], d["x2"] - d["x1"], 0, GRAY,
                        strokeStyle="dashed", points=[[0, 0], [d["x2"] - d["x1"], 0]],
                        lastCommittedPoint=None, startBinding=None, endBinding=None,
                        startArrowhead=None, endArrowhead=None))

    # 노드
    nodes: dict[str, dict] = {}
    colors = set()
    for n in spec["nodes"]:
        kind = n.get("kind", "box")
        shape = SHAPES[kind]
        dw, dh = DEFAULT_SIZE[kind]
        node = {"x": n["x"], "y": n["y"], "w": n.get("w", dw), "h": n.get("h", dh), "shape": shape}
        color = n.get("color", "white")
        if color != "white":
            colors.add(color)
        eid = f"n-{n['id']}"
        rnd = {"type": 3} if shape == "rectangle" else ({"type": 2} if shape == "diamond" else None)
        el = base(eid, shape, node["x"], node["y"], node["w"], node["h"], INK, FILLS[color], roundness=rnd)
        t = text_el(f"{eid}-t", n["label"], 0, 0, SIZE_NODE,
                    center=(node["x"] + node["w"] / 2, node["y"] + node["h"] / 2))
        t["containerId"] = eid
        el["boundElements"].append({"id": t["id"], "type": "text"})
        node["el"] = el
        nodes[n["id"]] = node
        els += [el, t]
    if len(colors) > MAX_COLORS:
        print(f"  경고: {fid} 색 {len(colors)}개 사용 ({', '.join(sorted(colors))}). 규칙은 최대 {MAX_COLORS}개",
              file=sys.stderr)

    # 화살표
    for i, e in enumerate(spec.get("edges", [])):
        a, b = nodes[e["from"]], nodes[e["to"]]
        via = [tuple(p) for p in e.get("via", [])]
        ac = (a["x"] + a["w"] / 2, a["y"] + a["h"] / 2)
        bc = (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)
        start = anchor(a, e.get("from_side"), via[0] if via else bc, e.get("from_at"))
        end = anchor(b, e.get("to_side"), via[-1] if via else ac, e.get("to_at"))
        pts_abs = [start, *via, end]
        sx, sy = pts_abs[0]
        pts = [[round(px - sx, 1), round(py - sy, 1)] for px, py in pts_abs]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        dashed = e.get("dashed", False)
        aid = f"e{i}"
        arrow = base(aid, "arrow", sx, sy, max(xs) - min(xs), max(ys) - min(ys),
                     GRAY if dashed else INK, strokeStyle="dashed" if dashed else "solid",
                     roundness=None, points=pts, lastCommittedPoint=None,
                     startBinding={"elementId": a["el"]["id"], "focus": 0, "gap": 3},
                     endBinding={"elementId": b["el"]["id"], "focus": 0, "gap": 3},
                     startArrowhead=None, endArrowhead="arrow", elbowed=False)
        a["el"]["boundElements"].append({"id": aid, "type": "arrow"})
        b["el"]["boundElements"].append({"id": aid, "type": "arrow"})
        els.append(arrow)

        seg = e.get("seg")
        if seg is None:
            seg = max(range(len(pts_abs) - 1), key=lambda k: math.dist(pts_abs[k], pts_abs[k + 1]))
        (x1, y1), (x2, y2) = pts_abs[seg], pts_abs[seg + 1]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L = math.dist((x1, y1), (x2, y2)) or 1
        nx, ny = (y2 - y1) / L, -(x2 - x1) / L  # 오른쪽으로 가는 선이면 위쪽
        if e.get("flip"):
            nx, ny = -nx, -ny
        # 번호 + 짧은 라벨: 한쪽, 문제 주석: 반대쪽
        head = "  ".join(str(v) for v in (e.get("n"), e.get("label")) if v)
        if head:
            els.append(place(mx, my, nx, ny, head, SIZE_EDGE, GRAY if dashed else INK, f"{aid}-l"))
        if e.get("note"):
            els.append(place(mx, my, -nx, -ny, e["note"], SIZE_EDGE, PROBLEM_INK, f"{aid}-p"))

    # 괄호 묶음 (참고 그림의 "동기화")
    for i, br in enumerate(spec.get("brackets", [])):
        group = [nodes[k] for k in br["nodes"]]
        side = br.get("side", "right")
        tick = 12
        if side == "right":
            x = max(g["x"] + g["w"] for g in group) + br.get("gap", 14)
            y1, y2 = min(g["y"] for g in group), max(g["y"] + g["h"] for g in group)
            pts = [[0, 0], [tick, 0], [tick, y2 - y1], [0, y2 - y1]]
            els.append(base(f"br{i}", "line", x, y1, tick, y2 - y1, GRAY, points=pts,
                            lastCommittedPoint=None, startBinding=None, endBinding=None,
                            startArrowhead=None, endArrowhead=None))
            w, h = text_size(br["label"], SIZE_LABEL)
            els.append(text_el(f"br{i}-t", br["label"], x + tick + 8, (y1 + y2) / 2 - h / 2, SIZE_LABEL, GRAY_TEXT))
        else:  # bottom
            y = max(g["y"] + g["h"] for g in group) + br.get("gap", 14)
            x1, x2 = min(g["x"] for g in group), max(g["x"] + g["w"] for g in group)
            pts = [[0, 0], [0, tick], [x2 - x1, tick], [x2 - x1, 0]]
            els.append(base(f"br{i}", "line", x1, y, x2 - x1, tick, GRAY, points=pts,
                            lastCommittedPoint=None, startBinding=None, endBinding=None,
                            startArrowhead=None, endArrowhead=None))
            els.append(text_el(f"br{i}-t", br["label"], 0, 0, SIZE_LABEL, GRAY_TEXT,
                               center=((x1 + x2) / 2, y + tick + 14)))

    # 행 이름 등 짧은 글자
    for i, t in enumerate(spec.get("texts", [])):
        color = PROBLEM_INK if t.get("problem") else GRAY_TEXT
        els.append(text_el(f"tx{i}", t["text"], t["x"], t["y"], t.get("size", SIZE_LABEL), color))
    return els


def write(spec_path: Path) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    els = build(spec)
    doc = {"type": "excalidraw", "version": 2, "source": "geeknews-digest/tools/figgen.py",
           "elements": els, "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}
    out = spec_path.parent.parent / f"{spec['id']}.excalidraw"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(els)} elements)")
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    if argv[1] == "--all":
        specs = sorted(Path(__file__).resolve().parent.parent.glob("portfolio/figures/specs/FIG-*.json"))
    else:
        specs = [Path(p) for p in argv[1:]]
    for p in specs:
        write(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
