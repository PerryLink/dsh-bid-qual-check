#!/usr/bin/env python3
"""Generate the README hero diagram for dsh-bid-qual-check (docs/assets/).

Outputs (idempotent overwrite):
  docs/assets/dsh-bid-qual-check-flow-light.svg
  docs/assets/dsh-bid-qual-check-flow-dark.svg

This repository has no UI screenshots and no benchmark table, so the only
README asset is a vector flow diagram. SVG is written directly: Pillow cannot
rasterise SVG, and a vector image stays crisp on GitHub. Text inside the
diagram is command-surface tokens only (tool name, rule ids, config path,
report keys), so all five README languages share one light/dark pair.

The palette follows the family generator in dsh-mask/scripts/gen-readme-assets.py:
family accent #4B67B4, GitHub light #ffffff, GitHub dark #0d1117.

Run once:  python scripts/gen-readme-assets.py
Requires:  Python 3 (standard library only; no Pillow needed for SVG)
"""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", track="#eaeef2"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", track="#21262d"),
}

# --- the pipeline: material -> rule pack -> report -> human review ---------
FLOW_NODES = [
    ("material", "JSON / YAML · rows[]"),
    ("ruleset", "BQ-001 … BQ-008"),
    ("report", "issues[] + skipped[]"),
    ("reviewer", "human review"),
]

NOTE = "bid_qual_check · rules/bid-qual-check.yaml"
FOOTNOTE = "network: none · model: none · writes: none"
STATS = "summary.error · summary.warn · summary.info · skipped[]"


def flow_svg(skin: str) -> str:
    """Render one theme of the flow diagram as an SVG document."""
    s = SKIN[skin]
    w, h = 1200, 400
    nw, nh, gap = 220, 100, 50
    x0, y0 = 85, 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-bid-qual-check flow: material to rule pack to report to reviewer">',
        '<title>dsh-bid-qual-check flow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" '
        f'font-family="ui-sans-serif,system-ui,sans-serif" font-size="30" '
        f'font-weight="700">dsh-bid-qual-check</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" '
        f'font-family="ui-monospace,monospace" font-size="16">{NOTE}</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]

    for i, (label, sub) in enumerate(FLOW_NODES):
        x = x0 + i * (nw + gap)
        accent = FAMILY if i == 1 else (GREEN[skin] if i == 2 else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 42}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="17" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 72}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 8
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 16}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 18} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')

    # summary strip under the pipeline
    bx, bw, by, bh = x0, nw * 4 + gap * 3, 292, 46
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        f'fill="{s["track"]}" stroke="{s["border"]}"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 29}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="13">{STATS}</text>')
    parts.append(
        f'<text x="60" y="378" fill="{s["sub"]}" '
        f'font-family="ui-monospace,monospace" font-size="13">{FOOTNOTE}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-bid-qual-check-flow-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
