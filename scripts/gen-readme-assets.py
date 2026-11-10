#!/usr/bin/env python3
"""Generate the README visuals for dsh-bid-qual-check.

Outputs (idempotent overwrite):
  docs/assets/dsh-bid-qual-check-hero-{zh,en}-{light,dark}.webp   (1440x576, Pillow)
  docs/assets/dsh-bid-qual-check-flow-v5-{light,dark}.svg         (1100x660, hand-written SVG)

Design, grounded in the plugin's real pipeline:

  Hero  - one row of a bidder qualification checklist. The four columns the
          checker holds a row to (required / actual / evidence / verdict) are
          linked clockwise into a closed loop; the empty required cell breaks
          the loop and carries BQ-001. The row's pass/fail flag (BQ-005), the
          header (BQ-006), the sequence number (BQ-007) and the placeholder
          check (BQ-008) are all visible, and BQ-004 is drawn as skipped
          because the shipped `values` list is empty. Footer values (issues 1,
          skipped 1, warn 1) are the real output of samples/quickstart.

  Flow  - two sources (material + validated rule pack) merge into the engine,
          which holds the eight rules in three scope lanes (header 1, row 2,
          cell 5); results leave as the two report channels issues[] and
          skipped[], and the conclusion stops at the human-review boundary.
          Grammar: dual-source merge + three-lane scope map + dual-channel
          report + boundary hand-off. Deliberately not a left-to-right node
          chain.

Text inside both images is drawn from tokens the plugin really emits:
rule ids (BQ-001..BQ-008), canonical field names, check kinds
(presenceAny / presence / enum / conditionalPresence / headerPresence /
unique / containsAny), report keys and the real quickstart finding.

Run:  python scripts/gen-readme-assets.py
Needs: Python 3, Pillow (hero), Chrome/Edge only for the manual overflow check.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

F_SANS = r"C:\Windows\Fonts\msyh.ttc"
F_SANS_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
F_MONO = r"C:\Windows\Fonts\consola.ttf"
F_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"

W, H = 1440, 576

# --- palettes (family accent #4B67B4 / dark #8496f5) ----------------------
P = {
    "light": dict(
        bg_top=(249, 246, 253), bg_bot=(228, 234, 248),
        card=(255, 255, 255), node=(251, 250, 253), edge=(226, 222, 239),
        track=(243, 241, 248), ink=(22, 23, 29), sub=(86, 91, 107),
        faint=(128, 133, 150), accent=(75, 103, 180), accent_soft=(236, 235, 249),
        warn=(176, 83, 9), warn_soft=(253, 241, 227), warn_border=(228, 178, 116),
        ok=(31, 122, 74), ok_soft=(233, 246, 238),
    ),
    "dark": dict(
        bg_top=(19, 26, 42), bg_bot=(12, 16, 22),
        card=(26, 34, 51), node=(32, 42, 64), edge=(43, 54, 80),
        track=(21, 28, 44), ink=(233, 237, 249), sub=(154, 166, 196),
        faint=(124, 136, 166), accent=(132, 150, 245), accent_soft=(35, 44, 74),
        warn=(240, 180, 95), warn_soft=(52, 40, 25), warn_border=(122, 91, 45),
        ok=(111, 211, 154), ok_soft=(28, 47, 38),
    ),
}

_FONTS: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]


def sans(size: int):
    return font(F_SANS, size)


def sans_b(size: int):
    return font(F_SANS_BOLD, size)


def mono(size: int):
    return font(F_MONO, size)


def mono_b(size: int):
    return font(F_MONO_BOLD, size)


def blend(c1, c2, t: float):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def lerp(c1, c2, t: float):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def tw(text: str, f: ImageFont.FreeTypeFont) -> float:
    return f.getlength(text)


# --- shared drawing helpers ------------------------------------------------
def add_shadow(img, box, radius, dy=10, blur=18, alpha=38, color=(24, 18, 48)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(
        (box[0], box[1] + dy, box[2], box[3] + dy),
        radius=radius, fill=color + (alpha,),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def draw_bg(theme: str) -> Image.Image:
    p = P[theme]
    small = Image.new("RGB", (72, 72))
    px = small.load()
    top, bot = p["bg_top"], p["bg_bot"]
    for y in range(72):
        for x in range(72):
            t = (0.70 * y + 0.30 * x) / 71.0
            px[x, y] = lerp(top, bot, t)
    img = small.resize((W, H), Image.BICUBIC).convert("RGBA")

    # soft, very faint loop-related decoration: one large disc + two arcs
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    accent = p["accent"]
    if theme == "light":
        dd.ellipse((1090, -160, 1590, 340), fill=blend(p["bg_top"], (255, 255, 255), 0.55) + (90,))
        arc_col = accent + (16,)
    else:
        dd.ellipse((1090, -160, 1590, 340), fill=blend(p["bg_top"], accent, 0.08) + (120,))
        arc_col = accent + (26,)
    cx, cy, r = 90, 560, 210
    for off in (0, 34, 68):
        dd.arc((cx - r - off, cy - r - off, cx + r + off, cy + r + off),
               212, 328, fill=arc_col, width=2)
    deco = deco.filter(ImageFilter.GaussianBlur(28))
    img.alpha_composite(deco)
    return img


def put(d, x, y, s, f, fill, anchor="ls"):
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def put_right(d, x_right, y, s, f, fill, extra=0):
    d.text((x_right - extra, y), s, font=f, fill=fill, anchor="rs")
    return tw(s, f)


def put_center(d, cx, y, s, f, fill):
    d.text((cx, y), s, font=f, fill=fill, anchor="ms")


def pill(d, x, y, h, text, f, fg, bg, padx=11, radius=None, border=None, border_w=1.2):
    w = tw(text, f) + padx * 2
    r = h / 2 if radius is None else radius
    d.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=bg,
                        outline=border, width=int(round(border_w)))
    d.text((x + padx, y + h / 2 + 0.5), text, font=f, fill=fg, anchor="lm")
    return w


def draw_check(d, cx, cy, s, color, width=2.0):
    d.line(
        [(cx - s * 0.55, cy + s * 0.02),
         (cx - s * 0.12, cy + s * 0.42),
         (cx + s * 0.55, cy - s * 0.45)],
        fill=color, width=round(width), joint="curve",
    )


def bez(p0, p1, p2, steps=54):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        ))
    return pts


def arrow_head(d, p_from, p_to, color, size=8.5):
    ang = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])
    left = (p_to[0] - size * math.cos(ang - 0.42), p_to[1] - size * math.sin(ang - 0.42))
    right = (p_to[0] - size * math.cos(ang + 0.42), p_to[1] - size * math.sin(ang + 0.42))
    d.polygon([p_to, left, right], fill=color)


# --- hero text -------------------------------------------------------------
HERO: dict[str, dict] = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 资格核对",
        value=["每一行四栏闭环", "缺哪一栏，指到哪一栏"],
        subtitle=["只列材料内部能逐条指认的差异，", "不判资格、不核原件、不下结论。"],
        meta="BQ-001…BQ-008 · 规则库随包 · skipped 逐条说明",
        footer="Apache-2.0 · PerryLink DSH plugin family",
        card_title="投标人资格条件核对表",
        card_tag="JSON / YAML · 只读",
        header="项目 某某工程施工招标 · 投标人 某某建设有限公司",
        row_prefix="第 1 行 · 否决项 = ", row_flag="是",
        row_right_text="序号 1 唯一",
        center_top="第 1 行",
        center_big="闭环",
        center_gap="缺 1 栏",
        center_rule="否决项三栏同填",
        legend_ok="已留痕",
        legend_gap="! 缺栏",
        legend_skip="- 未执行（skipped）",
        skip_note="BQ-004 跳过：values 未配置（口径由本机构规定）",
        source_note="示例行取自 samples/quickstart（BQ-001-unsafe.json）",
        handoff="结论留给审核人",
        nodes={
            "N": dict(name="要求内容", key="required", value="（空）", state="gap", pills=[("! BQ-001", "gap"), ("BQ-008", "ok")]),
            "E": dict(name="投标人情况", key="actual", value="持有二级资质，证书有效", state="ok", pills=[("BQ-002", "ok")]),
            "S": dict(name="证明材料", key="evidence", value="资质证书复印件 p12", state="ok", pills=[("BQ-003", "ok")]),
            "W": dict(name="核对结论", key="verdict", value="符合", state="skip", pills=[("- BQ-004", "skip")]),
        },
        value_size=40,
        sub_size=20,
        kicker_size=14,
        meta_size=15.5,
        footer_size=14,
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · qualification check",
        value=["Four columns, one loop", "point at the missing one"],
        subtitle=["Lists only the gaps the checklist itself can point to —",
                  "no eligibility finding, no originals, no verdict."],
        meta="BQ-001…BQ-008 · rule pack bundled · every skip explained",
        footer="Apache-2.0 · PerryLink DSH plugin family",
        card_title="Bidder qualification checklist",
        card_tag="JSON / YAML · read-only",
        header="Project Some Works · Bidder Some Construction Co., Ltd.",
        row_prefix="Row 1 · pass/fail = ", row_flag="yes",
        row_right_text="seq 1 unique",
        center_top="Row 1",
        center_big="closed loop",
        center_gap="1 gap",
        center_rule="needs all three",
        legend_ok="recorded",
        legend_gap="! gap",
        legend_skip="- skipped",
        skip_note="BQ-004 skipped: values not configured",
        source_note="Illustrative row; the sample ships in samples/quickstart.",
        handoff="verdict stays with the reviewer",
        nodes={
            "N": dict(name="Requirement", key="required", value="(blank)", state="gap", pills=[("! BQ-001", "gap"), ("BQ-008", "ok")]),
            "E": dict(name="Bidder's position", key="actual", value="Grade-2 licence, valid", state="ok", pills=[("BQ-002", "ok")]),
            "S": dict(name="Evidence", key="evidence", value="Licence copy p12", state="ok", pills=[("BQ-003", "ok")]),
            "W": dict(name="Verdict", key="verdict", value="Meets", state="skip", pills=[("- BQ-004", "skip")]),
        },
        value_size=39,
        sub_size=19.5,
        kicker_size=13.5,
        meta_size=15,
        footer_size=14,
    ),
}

# fixed ring geometry: N/E/S/W cards around a 176px-wide centre
NODE_BOX = {
    "N": (942, 169, 1126, 235),
    "E": (1122, 287, 1306, 353),
    "S": (942, 405, 1126, 471),
    "W": (762, 287, 946, 353),
}
CENTER = (1034, 320)


def hero(locale: str, theme: str) -> Image.Image:
    p = P[theme]
    t = HERO[locale]
    img = draw_bg(theme)
    d = ImageDraw.Draw(img)

    # ---------------- left column ----------------
    kf = sans(t["kicker_size"])
    kw = tw(t["kicker"], kf)
    pill(d, 72, 58, 32, t["kicker"], kf, p["accent"], p["accent_soft"], padx=16)

    title_f = mono_b(58)
    title = "dsh-bid-qual-check"
    # slight tracking so the mono title breathes like the family heroes
    x = 72
    for ch in title:
        d.text((x, 182), ch, font=title_f, fill=p["ink"], anchor="ls")
        x += tw(ch, title_f) + 0.6
    title_w = x - 72 - 0.6
    assert title_w < 610, title_w

    vf = sans_b(t["value_size"])
    for i, line in enumerate(t["value"]):
        assert tw(line, vf) < 608, (line, tw(line, vf))
        put(d, 72, 262 + i * 54, line, vf, p["ink"])

    sf = sans(t["sub_size"])
    for i, line in enumerate(t["subtitle"]):
        assert tw(line, sf) < 608, (line, tw(line, sf))
        put(d, 72, 366 + i * 31, line, sf, p["sub"])

    put(d, 72, 448, t["meta"], sans(t["meta_size"]), p["sub"])

    d.line([(72, 480), (664, 480)], fill=p["edge"], width=1)
    put(d, 72, 512, t["footer"], sans(t["footer_size"]), p["faint"])

    # ---------------- right panel ----------------
    box = (700, 56, 1368, 524)
    add_shadow(img, box, 20, dy=12, blur=24, alpha=34)
    d.rounded_rectangle(box, radius=20, fill=p["card"], outline=p["edge"], width=1)

    # header
    put(d, 726, 94, t["card_title"], sans_b(15.5), p["ink"])
    tag_f = sans(10.5)
    tag_w = tw(t["card_tag"], tag_f) + 22
    d.rounded_rectangle((1342 - tag_w, 80, 1342, 102), radius=11,
                        fill=p["accent_soft"])
    d.text((1342 - tag_w + 11, 91.5), t["card_tag"], font=tag_f,
           fill=p["accent"], anchor="lm")

    # header line + BQ-006
    hf = sans(11.2)
    htext = t["header"]
    hmax = 1342 - 726 - 96
    while tw(htext, hf) > hmax:
        htext = htext[:-2] + "…"
    put(d, 726, 121, htext, hf, p["sub"])
    bq6_f = mono_b(9.6)
    bq6_w = tw("BQ-006", bq6_f) + 30
    d.rounded_rectangle((1342 - bq6_w, 108, 1342, 128), radius=10, fill=p["ok_soft"])
    d.text((1352 - bq6_w, 118.5), "BQ-006", font=bq6_f, fill=p["ok"], anchor="lm")
    draw_check(d, 1342 - 10, 118, 5.2, p["ok"], 1.8)

    # row line + BQ-007
    rf = sans_b(11.8)
    put(d, 726, 148, t["row_prefix"], rf, p["ink"])
    put(d, 726 + tw(t["row_prefix"], rf), 148, t["row_flag"], rf, p["warn"])
    bq7_f = mono_b(9.8)
    bq7_t = sans(9.8)
    bq7_id = "BQ-007"
    bq7_txt = t["row_right_text"]
    bq7_total = tw(bq7_id, bq7_f) + 6 + tw(bq7_txt, bq7_t) + 16
    bq7_x = 1342 - bq7_total
    put(d, bq7_x, 148, bq7_id, bq7_f, p["ok"])
    put(d, bq7_x + tw(bq7_id, bq7_f) + 6, 148, bq7_txt, bq7_t, p["ok"])
    draw_check(d, 1342 - 8, 144, 5.4, p["ok"], 1.8)
    d.line([(726, 158), (1342, 158)], fill=p["edge"], width=1)

    # ring links (behind cards)
    link_col = blend(p["card"], p["accent"], 0.78)
    link_warn = blend(p["card"], p["warn"], 0.88)
    links = [
        ((1120, 240), (1170, 248), (1196, 282), False),
        ((1298, 356), (1245, 428), (1130, 446), False),
        ((940, 442), (830, 428), (772, 356), False),
        ((862, 281), (892, 244), (944, 234), True),
    ]
    for p0, p1, p2, dashed in links:
        pts = bez(p0, p1, p2)
        col = link_warn if dashed else link_col
        if dashed:
            for i in range(0, len(pts) - 2, 6):
                d.line(pts[i:i + 4], fill=col, width=2, joint="curve")
        else:
            d.line(pts, fill=col, width=2, joint="curve")
        arrow_head(d, pts[-3], pts[-1], col, 8.5)

    # centre disc + copy
    disc = blend(p["card"], p["accent"], 0.045)
    d.ellipse((CENTER[0] - 76, CENTER[1] - 76, CENTER[0] + 76, CENTER[1] + 76),
              fill=disc)
    put_center(d, CENTER[0], 292, t["center_top"], sans(10.5), p["faint"])
    put_center(d, CENTER[0], 326, t["center_big"],
               sans_b(26 if locale == "zh" else 23), p["ink"])
    put_center(d, CENTER[0], 350, t["center_gap"], sans_b(12.5), p["warn"])

    cr_f = sans(10.2)
    cr_w = tw(t["center_rule"], cr_f)
    bq5_f = mono_b(9.6)
    bq5_w = tw("BQ-005", bq5_f) + 22
    total = bq5_w + 7 + cr_w
    cx0 = CENTER[0] - total / 2
    d.rounded_rectangle((cx0, 362, cx0 + bq5_w, 382), radius=10, fill=p["ok_soft"])
    d.text((cx0 + 11, 372.5), "BQ-005", font=bq5_f, fill=p["ok"], anchor="lm")
    d.text((cx0 + bq5_w + 7, 372.5), t["center_rule"], font=cr_f,
           fill=p["ok"], anchor="lm")

    # node cards
    for key, (x0, y0, x1, y1) in NODE_BOX.items():
        n = t["nodes"][key]
        gap = n["state"] == "gap"
        fill = p["warn_soft"] if gap else p["node"]
        edge = p["warn_border"] if gap else p["edge"]
        d.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=fill,
                            outline=edge, width=2 if gap else 1)
        key_f = mono(9.6)
        ktext = n["key"]
        while tw(ktext, key_f) > (x1 - x0 - 90):
            ktext = ktext[:-2] + "…"
        put_right(d, x1 - 12, y0 + 38, ktext, key_f, p["faint"])
        put(d, x0 + 14, y0 + 38, n["name"], sans_b(13.8), p["ink"])
        val_col = p["warn"] if gap else p["ink"]
        put(d, x0 + 14, y0 + 58, n["value"], sans(11.2), val_col)

        # status pills sit on the card's top edge
        px = x0 + 13
        for label, state in n["pills"]:
            f = mono_b(9.4)
            bg = p["ok_soft"] if state == "ok" else p["warn_soft"]
            fg = p["ok"] if state == "ok" else p["warn"]
            w = tw(label, f) + 16
            d.rounded_rectangle((px, y0 - 9, px + w, y0 + 9), radius=9, fill=bg)
            d.text((px + 8, y0 + 0.5), label, font=f, fill=fg, anchor="lm")
            px += w + 5

    # panel footer
    fy = 486
    dot_col = p["ok"]
    d.ellipse((726, fy - 6, 733, fy + 1), fill=dot_col)
    lf = sans(10.2)
    x = 738
    put(d, x, fy, t["legend_ok"], lf, p["sub"])
    x += tw(t["legend_ok"], lf) + 14
    put(d, x, fy, t["legend_gap"], lf, p["warn"])
    x += tw(t["legend_gap"], lf) + 14
    put(d, x, fy, t["legend_skip"], lf, p["faint"])
    put_right(d, 1342, fy, t["skip_note"], sans(10.0), p["warn"])
    put(d, 726, 508, t["source_note"], sans(9.7), p["faint"])
    hf = sans(10.6)
    hw = tw(t["handoff"], hf)
    hx = 1342 - 22 - hw
    put(d, hx, 508, t["handoff"], hf, p["ok"])
    counts_f = sans(10.2)
    put_right(d, hx - 14, 508, "issues 1 · skipped 1", counts_f, p["sub"])
    ax0 = 1342 - 18
    d.line([(ax0, 504), (1340, 504)], fill=p["ok"], width=2)
    arrow_head(d, (ax0, 504), (1341, 504), p["ok"], 5.5)

    return img


# --- structure diagram (SVG) ----------------------------------------------
SANS_STACK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
              "'Source Han Sans SC',sans-serif")
MONO_STACK = "'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace"

T = {
    "light": dict(
        bg1="#f9f6fd", bg2="#e4eaf8", card="#ffffff", node="#fbfafd",
        edge="#e6e2ef", track="#f3f1f8", ink="#16171d", sub="#565b6b",
        faint="#83879a", accent="#4B67B4", accent_soft="#ecebf9",
        warn="#b45309", warn_soft="#fdf1e3", ok="#1f7a4a", ok_soft="#e9f6ee",
        shadow="#16122c", shadow_op="0.10",
    ),
    "dark": dict(
        bg1="#131a2a", bg2="#0c1016", card="#1a2233", node="#202a40",
        edge="#2b3650", track="#151c2c", ink="#e9edf9", sub="#9aa6c4",
        faint="#7e8aab", accent="#8496f5", accent_soft="#232c4a",
        warn="#f0b45f", warn_soft="#3a2d1c", ok="#6fd39a", ok_soft="#1c2f26",
        shadow="#000000", shadow_op="0.45",
    ),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def stext(x, y, s, size, fill, *, weight=400, family="sans", anchor="start",
          opacity=None, italic=False):
    fam = SANS_STACK if family == "sans" else MONO_STACK
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"',
             f'font-family="{fam}"', f'font-size="{size:g}"']
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{esc(s)}</text>'


def tlen(s, size, *, bold=False, mono_=False) -> float:
    f = mono_b(size) if (mono_ and bold) else (
        mono(size) if mono_ else (sans_b(size) if bold else sans(size)))
    return tw(s, f)


def fit(s, size, maxw, *, bold=False, mono_=False) -> str:
    if tlen(s, size, bold=bold, mono_=mono_) <= maxw:
        return s
    s = s.rstrip()
    while s and tlen(s + "…", size, bold=bold, mono_=mono_) > maxw:
        s = s[:-1]
    return s + "…"


def pillw(s, size, *, mono_=False, bold=True, padx=9, dot=False, check=False):
    return tlen(s, size, bold=bold, mono_=mono_) * 1.03 + padx * 2 + (11 if dot else 0) + (12 if check else 0)


def spath(d, stroke, width=1.4, opacity=None, fill="none", dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round"{op}{extra}/>')


def srect(x0, y0, x1, y1, fill, stroke=None, r=12, sw=1.2, shadow=False, op=None):
    extra = ' filter="url(#soft)"' if shadow else ""
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    o = f' opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" '
            f'height="{y1 - y0:g}" rx="{r:g}" fill="{fill}"{st}{o}{extra}/>')


def sput(x, y, s, size, fill, *, bold=False, mono_=False, anchor="start", op=None):
    return stext(x, y, s, size, fill,
                 weight=700 if bold else 400,
                 family="mono" if mono_ else "sans",
                 anchor=anchor, opacity=op)


def sput_pill(x, y, h, s, size, fg, bg, *, mono_=True, bold=True, padx=8,
              stroke=None, dot=None, check=False):
    w = tlen(s, size, bold=bold, mono_=mono_) * 1.03 + padx * 2 + (11 if dot else 0) + (12 if check else 0)
    out = [f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
           f'rx="{h / 2:g}" fill="{bg}"'
           + (f' stroke="{stroke}" stroke-width="1"' if stroke else "") + "/>"]
    tx = x + padx + (11 if dot else 0)
    if dot:
        out.append(f'<circle cx="{x + padx + 3:g}" cy="{y + h / 2:g}" r="2.6" fill="{dot}"/>')
    out.append(stext(tx, y + h / 2 + 3.2, s, size, fg,
                     weight=700 if bold else 400,
                     family="mono" if mono_ else "sans"))
    if check:
        cx = tx + tlen(s, size, bold=bold, mono_=mono_) + 7
        cy = y + h / 2
        out.append(spath(f"M{cx - 3.6:g} {cy + 0.2:g} L{cx - 1.0:g} {cy + 2.8:g} L{cx + 4.0:g} {cy - 3.4:g}",
                         fg, 1.8))
    return "".join(out), w


def flow_svg(theme: str) -> str:
    c = T[theme]
    parts: list[str] = []
    A = parts.append

    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
      f'viewBox="0 0 1100 660" role="img" aria-labelledby="fig-title fig-desc">')
    A('<title id="fig-title">dsh-bid-qual-check 结构：两条输入、三层检查、两条报告通道</title>')
    A('<desc id="fig-desc">材料（JSON/YAML 核对表）与规则库（8 条，加载期校验）汇入检查引擎；'
      '规则分三层——表头 BQ-006，行 BQ-005/BQ-007，栏 BQ-001/BQ-002/BQ-003/BQ-004/BQ-008；'
      '结果分成 issues[] 与 skipped[] 两条通道，BQ-004 因 values 未配置进入 skipped；'
      '报告交给人工复核，不判资格、不核原件、不判否决。</desc>')
    A('<defs>')
    A(f'<linearGradient id="bg" x1="0" y1="0" x2="0.30" y2="1">'
      f'<stop offset="0" stop-color="{c["bg1"]}"/>'
      f'<stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>')
    A(f'<filter id="soft" x="-8%" y="-14%" width="116%" height="140%">'
      f'<feDropShadow dx="0" dy="7" stdDeviation="9" flood-color="{c["shadow"]}" '
      f'flood-opacity="{c["shadow_op"]}"/></filter>')
    A(f'<marker id="arr" viewBox="0 0 10 10" refX="8.2" refY="5" '
      f'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
      f'<path d="M0 1.8 L9 5 L0 8.2 z" fill="{c["accent"]}"/></marker>')
    A(f'<marker id="arrWarn" viewBox="0 0 10 10" refX="8.2" refY="5" '
      f'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
      f'<path d="M0 1.8 L9 5 L0 8.2 z" fill="{c["warn"]}"/></marker>')
    A('</defs>')
    A(f'<rect width="1100" height="660" fill="url(#bg)"/>')
    # faint decorative arcs, echoing the per-row loop in the hero
    A(f'<g opacity="0.16">')
    for r in (150, 186, 222):
        A(f'<circle cx="1050" cy="636" r="{r}" fill="none" stroke="{c["accent"]}" stroke-width="1.6"/>')
    A('</g>')

    # ---------- header ----------
    A(sput(44, 52, "dsh-bid-qual-check", 26, c["ink"], bold=True, mono_=True))
    A(sput(44, 80, "8 条规则分三层读同一张核对表：表头 1、行 2、栏 5；能执行的出 issues，不能执行的出 skipped。",
           13.2, c["sub"]))
    bw = pillw("规则包 2026.1 · 8 条", 11, mono_=False, padx=10)
    badge, _ = sput_pill(1056 - bw, 30, 26, "规则包 2026.1 · 8 条", 11,
                         c["accent"], c["accent_soft"], mono_=False, padx=10)
    A(badge)

    # ---------- sources ----------
    # material card
    A(srect(44, 100, 604, 246, c["card"], c["edge"], 18, 1.2, shadow=True))
    A(sput(64, 127, "材料 · 投标人资格条件核对表", 13.6, c["ink"], bold=True))
    tw_ = pillw("JSON / YAML · 只读", 11, mono_=False, bold=False, padx=9)
    tag, _ = sput_pill(604 - 26 - tw_, 106, 24, "JSON / YAML · 只读", 11,
                       c["accent"], c["accent_soft"], mono_=False, bold=False, padx=9)
    A(tag)
    A(sput(64, 150, fit("项目 某某工程施工招标 · 招标编号 ZB-2026-018 · 投标人 某某建设有限公司",
                        11, 500), 11, c["sub"]))
    # mini table
    cols = [(64, "序号"), (108, "要求内容"), (236, "投标人情况"), (372, "证明材料"), (490, "核对结论")]
    for x, label in cols:
        A(sput(x, 179, label, 11, c["faint"], bold=True))
    A(srect(56, 186, 592, 212, c["track"], r=7))
    A(sput(64, 203, "1", 11, c["ink"], mono_=True, bold=True))
    A(sput(108, 203, "（空）", 11, c["warn"], bold=True))
    A(sput(236, 203, "持有二级资质", 11, c["ink"]))
    A(sput(372, 203, "资质证书 p12", 11, c["ink"]))
    A(sput(490, 203, "符合", 11, c["ink"]))
    A(sput(64, 232, "列名忽略大小写 / 空白 / 下划线；报告保留材料原列名", 11, c["faint"]))

    # rule pack card
    A(srect(624, 100, 1056, 246, c["card"], c["edge"], 18, 1.2, shadow=True))
    A(sput(644, 127, "规则库 · bid-qual-check.yaml", 13.6, c["ink"], bold=True))
    tw_ = pillw("加载期校验", 11, mono_=False, bold=False, padx=9)
    tag, _ = sput_pill(1056 - 26 - tw_, 106, 24, "加载期校验", 11,
                       c["accent"], c["accent_soft"], mono_=False, bold=False, padx=9)
    A(tag)
    bullets = [
        "· 8 条规则；id 唯一，excerpt ≥ 8 字",
        "· severity 上限：direct→error · 原则→warn · 本机构→info",
        "· 规则是数据：换 YAML 即换规则集，报告带版本 2026.1",
        "· 加载失败直接抛错，绝不静默回退到错误规则库",
    ]
    for i, b in enumerate(bullets):
        A(sput(644, 152 + i * 21, fit(b, 11, 386), 11, c["sub"]))
    A(sput(644, 238, "BQ-001 … BQ-008 · 规则库版本随报告返回", 11, c["faint"]))

    # source arrows into the engine
    for x in (324, 840):
        A(spath(f"M{x} 246 L{x} 259", c["accent"], 2, opacity="0.8"))
        A(spath(f"M{x - 4} 255 L{x} 260 L{x + 4} 255", c["accent"], 2))

    # ---------- engine panel ----------
    A(srect(44, 262, 1056, 536, c["card"], c["edge"], 18, 1.2, shadow=True))
    A(sput(64, 288, "检查引擎 · runTableCheck", 13.6, c["ink"], bold=True))
    A(sput(64, 307, "列名归一 → 逐条执行；前置缺失的规则进 skipped 并写明原因", 11, c["sub"]))
    tw_ = pillw("8 条 · 3 层", 11, mono_=False, bold=False, padx=9)
    tag, _ = sput_pill(1056 - 26 - tw_, 274, 24, "8 条 · 3 层", 11,
                       c["accent"], c["accent_soft"], mono_=False, bold=False, padx=9)
    A(tag)

    # lane helper
    def lane(y0, y1, name, count):
        A(srect(60, y0, 1040, y1, c["track"], r=10))
        A(sput(74, y0 + 20, name, 13, c["ink"], bold=True))
        A(sput(74, y0 + 36, count, 11, c["faint"]))

    # lane 1: header
    lane(326, 370, "表头", "1 条")
    A(srect(150, 332, 1028, 364, c["card"], c["edge"], 9, 1.0))
    pill1, _ = sput_pill(162, 339, 18, "BQ-006", 11, c["ok"], c["ok_soft"], padx=7)
    A(pill1)
    A(sput(230, 352, fit("表头声明 project · bidder；缺项按缺失字段报出", 11, 700), 11, c["sub"]))
    A(sput(1016, 352, "headerPresence", 11, c["faint"], mono_=True, anchor="end"))

    # lane 2: row
    lane(376, 420, "行", "2 条")
    A(srect(150, 382, 586, 414, c["card"], c["edge"], 9, 1.0))
    pill2, _ = sput_pill(162, 389, 18, "BQ-005", 11, c["warn"], c["warn_soft"], padx=7)
    A(pill2)
    A(sput(230, 402, fit("否决项 = 是 → actual · evidence · verdict 三栏同填", 11, 350), 11, c["sub"]))

    A(srect(596, 382, 1028, 414, c["card"], c["edge"], 9, 1.0))
    pill3, _ = sput_pill(608, 389, 18, "BQ-007", 11, c["warn"], c["warn_soft"], padx=7)
    A(pill3)
    A(sput(676, 402, fit("序号唯一（忽略空白）；整表无序号 → skipped", 11, 320), 11, c["sub"]))
    A(sput(1016, 402, "unique", 11, c["faint"], mono_=True, anchor="end"))

    # lane 3: cell / field map
    lane(426, 530, "栏", "5 条")
    fields = [
        (150, "要求内容", "required",
         [("BQ-001", "至少填一项"), ("BQ-008", "无占位符")], None),
        (374, "投标人情况", "actual",
         [("BQ-002", "是否记录")], "空栏 → 逐行报"),
        (598, "证明材料", "evidence",
         [("BQ-003", "是否填写")], "空栏 → 逐行报"),
        (822, "核对结论", "verdict",
         [("BQ-004", "是否在册")], "values 空 → skipped"),
    ]
    for x0, name, key, rules_, note in fields:
        A(srect(x0, 434, x0 + 216, 524, c["card"], c["edge"], 11, 1.0))
        A(sput(x0 + 12, 470, name, 13.2, c["ink"], bold=True))
        A(sput(x0 + 12 + tlen(name, 13.2, bold=True) + 8, 470, key, 11, c["faint"], mono_=True))
        yy = 492
        for rid, desc in rules_:
            A(sput(x0 + 12, yy, rid, 11, c["accent"], mono_=True, bold=True))
            A(sput(x0 + 12 + tlen(rid, 11, bold=True, mono_=True) + 6, yy,
                   fit(desc, 11, 196 - tlen(rid, 11, bold=True, mono_=True)), 11, c["sub"]))
            yy += 17
        if note:
            A(sput(x0 + 12, yy, fit(note, 11, 196), 11, c["warn"]))

    # engine -> report arrow
    A(spath('M550 536 L550 546', c["accent"], 2, opacity="0.8"))
    A(spath('M546 542 L550 547 L554 542', c["accent"], 2))

    # ---------- report + boundary ----------
    A(srect(44, 548, 822, 630, c["card"], c["edge"], 18, 1.2, shadow=True))
    A(sput(64, 568, "报告 · buildView", 13, c["ink"], bold=True))
    A(sput(802, 568, "markdown + reportJson", 11, c["faint"], mono_=True, anchor="end"))
    A(sput(64, 588, "issues[] 1", 11, c["accent"], mono_=True, bold=True))
    A(sput(132, 588, "· warn 1 · error 0 · info 0", 11, c["faint"]))
    A(sput(802, 588, "BQ-001 · 第 1 行 · required", 11, c["accent"], anchor="end"))
    A(sput(64, 606, fit("required、criterion 都为空 → 补填资格条件与要求内容；不判断该条件是否应当设置", 11, 730), 11, c["sub"]))
    A(sput(64, 624, fit("skipped[] 1 · BQ-004：values 未配置 —— 「verdict」口径由本机构规定", 11, 730), 11, c["warn"]))

    # dashed boundary + review card
    A(f'<line x1="830" y1="552" x2="830" y2="624" stroke="{c["edge"]}" '
      f'stroke-width="1.4" stroke-dasharray="4 5"/>')
    A(spath("M824 598 L834 598", c["accent"], 2, opacity="0.9"))
    A(spath("M830 594 L835 598 L830 602", c["accent"], 2))
    A(srect(838, 548, 1056, 630, c["node"], c["edge"], 18, 1.2, shadow=True))
    A(sput(856, 568, "人工复核", 13, c["ink"], bold=True))
    A(sput(856, 588, "结论不在报告里", 11, c["ok"], bold=True))
    A(sput(856, 606, "不判资格 · 不核原件", 11, c["sub"]))
    A(sput(856, 624, "不判否决", 11, c["sub"]))

    # footer
    A(sput(44, 648, "network: none · model: none · writes: none", 11, c["faint"], mono_=True))
    A(sput(1056, 648, "samples/quickstart · rules/bid-qual-check.yaml · 2026.1", 11, c["faint"], mono_=True, anchor="end"))
    A('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for locale in ("zh", "en"):
        for theme in ("light", "dark"):
            img = hero(locale, theme)
            path = os.path.join(OUT, f"dsh-bid-qual-check-hero-{locale}-{theme}.webp")
            img.convert("RGB").save(path, "WEBP", quality=92, method=6)
            print(f"wrote {os.path.relpath(path, ROOT)}")
    for theme in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-bid-qual-check-flow-v5-{theme}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(theme))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
