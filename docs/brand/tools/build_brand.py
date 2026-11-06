"""Dựng toàn bộ tài sản thương hiệu Tax Clear (khiên hồ sơ + chữ C vàng nghệ).

Chạy: python docs/brand/tools/build_brand.py
Cần: fontTools, Pillow, Playwright (Chromium) trong Python hệ thống.
Sinh: docs/brand/{logo,png,social,animated}, frontend/public/brand, frontend/src/app icon files,
      frontend/src/components/features/brand/brand-geometry.ts
"""

import base64
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[3]
BRAND = ROOT / "docs" / "brand"
FONTS = BRAND / "fonts"
WEB_PUBLIC = ROOT / "frontend" / "public" / "brand"
WEB_APP = ROOT / "frontend" / "src" / "app"
WEB_GEOMETRY = ROOT / "frontend" / "src" / "components" / "features" / "brand" / "brand-geometry.ts"

# ---------------------------------------------------------------- màu
COLORS = {
    "teal-950": "#0a3a33",
    "teal-900": "#0f5a4c",
    "teal-700": "#17705f",
    "teal-600": "#1f8f73",
    "teal-500": "#2fae8a",
    "teal-300": "#7fd6bb",
    "teal-100": "#c9f0e2",
    "saffron-500": "#f4a23c",
    "saffron-700": "#e07f1f",
    "saffron-text": "#a3550c",
    "ink": "#123a35",
    "mint": "#eef7f3",
    "white": "#ffffff",
}


# ---------------------------------------------------------------- Khiên hồ sơ + chữ C vàng nghệ
# Thiết kế trên lưới 128, thu về 64 khi ghép lockup.
SHIELD = "M64 8L90 15.5L108 33V60C108 90 90 109 64 120C38 109 20 90 20 60V21Z"
FOLD = "M90 15.5L108 33L93 31Z"
TICK = "M52 64L61 73L84 50"


def c_shape(cx=62.0, cy=66.0, R=37.0, r=20.0, a_open=42.0) -> str:
    """Chữ C dạng khối, hai đầu cắt vát song song nếp gấp giấy."""
    a0, a1 = math.radians(a_open), math.radians(360 - a_open)

    def po(rr, a):
        return cx + rr * math.cos(a), cy + rr * math.sin(a)

    o0, o1, i0, i1 = po(R, a0), po(R, a1), po(r, a0), po(r, a1)
    cut = (R - r) * 0.55
    i0 = (i0[0] + cut, i0[1] + cut * 0.15)
    i1 = (i1[0] + cut, i1[1] - cut * 0.15)
    return (
        f"M{o1[0]:.2f} {o1[1]:.2f}A{R:g} {R:g} 0 1 0 {o0[0]:.2f} {o0[1]:.2f}"
        f"L{i0[0]:.2f} {i0[1]:.2f}A{r:g} {r:g} 0 1 1 {i1[0]:.2f} {i1[1]:.2f}Z"
    )


C_PATH = c_shape()
C_PATH_SMALL = c_shape(R=38.0, r=18.5)


def mark_design(uid: str, small: bool = False, mono: str | None = None, gap: str | None = None) -> str:
    """Biểu tượng trên lưới 128. mono: khiên một màu, chữ C và tick bằng màu gap (khoét rỗng)."""
    c_path = C_PATH_SMALL if small else C_PATH
    tick_w = 11 if small else 9
    if mono:
        return (
            f'<path d="{SHIELD}" fill="{mono}"/>'
            f'<path d="M90 15.5L93 31L108 33" fill="none" stroke="{gap}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<path d="{c_path}" fill="{gap}"/>'
            # Viền cùng màu khiên tách dấu tick khỏi chữ C khi cả hai cùng màu khoét
            f'<path d="{TICK}" fill="none" stroke="{mono}" stroke-width="{tick_w + 6}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{TICK}" fill="none" stroke="{gap}" stroke-width="{tick_w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    shadow = "" if small else f' filter="url(#{uid}-sh)"'
    return (
        "<defs>"
        f'<linearGradient id="{uid}-d" x1="20" y1="8" x2="64" y2="120" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#18a885"/><stop offset="1" stop-color="#0a3a33"/></linearGradient>'
        f'<linearGradient id="{uid}-l" x1="64" y1="8" x2="108" y2="120" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#5ff0c0"/><stop offset="1" stop-color="#128c71"/></linearGradient>'
        f'<linearGradient id="{uid}-y" x1="30" y1="30" x2="100" y2="100" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffd987"/><stop offset=".55" stop-color="#f7a535"/>'
        '<stop offset="1" stop-color="#e2771a"/></linearGradient>'
        f'<clipPath id="{uid}-c"><path d="{SHIELD}"/></clipPath>'
        f'<filter id="{uid}-sh" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#06302a" flood-opacity=".45"/></filter>'
        "</defs>"
        f'<path class="mk-shield" d="{SHIELD}" fill="url(#{uid}-d)"/>'
        f'<g class="mk-shield" clip-path="url(#{uid}-c)"><rect x="64" y="0" width="64" height="128" fill="url(#{uid}-l)"/></g>'
        f'<path class="mk-fold" d="{FOLD}" fill="#c9f0e2"/>'
        f'<path class="mk-c" d="{c_path}" fill="url(#{uid}-y)"{shadow}/>'
        f'<path class="mk-tick" d="{TICK}" pathLength="1" fill="none" stroke="#ffffff" '
        f'stroke-width="{tick_w}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def mark_body(uid: str = "tc", small: bool = False, mono: str | None = None, gap_color: str | None = None) -> str:
    """Biểu tượng thu về hệ toạ độ 64×64 để ghép lockup."""
    return f'<g transform="scale(.5)">{mark_design(uid, small, mono, gap_color)}</g>'


# ---------------------------------------------------------------- wordmark
_fonts: dict[str, TTFont] = {}


def _font(weight: str) -> TTFont:
    if weight not in _fonts:
        _fonts[weight] = TTFont(FONTS / f"BeVietnamPro-{weight}.ttf")
    return _fonts[weight]


def text_path(text, weight, size, x, baseline, tracking=0.0, kern=None):
    f = _font(weight)
    scale = size / f["head"].unitsPerEm
    cmap, glyphs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    pen = SVGPathPen(glyphs)
    cursor = x
    for idx, ch in enumerate(text):
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
        cursor += hmtx[name][0] * scale + tracking
        if kern and idx < len(text) - 1:
            cursor += kern.get(text[idx : idx + 2], 0) * size
    return pen.getCommands(), cursor - x - tracking


KERN = {"Ta": -0.07, "Cl": -0.01}


def wordmark(ink, accent, warm, size=30.0, x=0.0, baseline=0.0, mono=False):
    """'Tax Clear' + chữ x vẽ riêng (một nét vàng nghệ). Trả (svg, width, cap_height)."""
    f = _font("SemiBold")
    upm = f["head"].unitsPerEm
    xh = f["OS/2"].sxHeight * size / upm
    cap = f["OS/2"].sCapHeight * size / upm
    d1, w1 = text_path("Ta", "SemiBold", size, x, baseline, tracking=-0.4, kern=KERN)
    x0 = x + w1 + size * 0.035
    xw, sw = size * 0.5, size * 0.135
    p = sw / 2
    second = ink if mono else warm
    xs = (
        f'<path d="M{x0 + p:.2f} {baseline - xh + p:.2f}L{x0 + xw - p:.2f} {baseline - p:.2f}" '
        f'stroke="{ink}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
        f'<path d="M{x0 + xw - p:.2f} {baseline - xh + p:.2f}L{x0 + p:.2f} {baseline - p:.2f}" '
        f'stroke="{second}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
    )
    x1 = x0 + xw + size * 0.27
    d2, w2 = text_path("Clear", "SemiBold", size, x1, baseline, tracking=-0.4, kern=KERN)
    body = f'<path d="{d1}" fill="{ink}"/>{xs}<path d="{d2}" fill="{ink}"/>'
    return body, x1 + w2 - x, cap


# ---------------------------------------------------------------- lockups
THEMES = {
    "color": dict(ink=COLORS["ink"], accent=COLORS["teal-700"], warm=COLORS["saffron-500"]),
    "on-dark": dict(ink=COLORS["white"], accent=COLORS["teal-300"], warm=COLORS["saffron-500"]),
    "mono-dark": dict(ink=COLORS["ink"], accent=COLORS["ink"], warm=COLORS["ink"], mono=COLORS["ink"]),
    "mono-white": dict(ink=COLORS["white"], accent=COLORS["white"], warm=COLORS["white"], mono=COLORS["white"]),
}


def _mark_for(theme: dict, simple=False, gap="#ffffff", uid="tc") -> str:
    mono = theme.get("mono")
    return mark_body(uid, simple, mono=mono, gap_color=(gap if mono else None))


def svg_doc(body: str, w: float, h: float, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" '
        f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n'
    )


def horizontal(theme_name: str) -> tuple[str, float, float]:
    t = THEMES[theme_name]
    gap = "#123a35" if theme_name == "mono-white" else "#ffffff"
    mark_h = 64.0
    size = 31.0
    words, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=mark_h + 12, baseline=0, mono="mono" in t)
    baseline = 32 + cap / 2
    words, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=mark_h + 12, baseline=baseline, mono="mono" in t)
    w = mark_h + 12 + ww + 2
    return f"{_mark_wrap(t, gap)}{words}", w, 64.0


def _mark_wrap(t, gap, scale=1.0, dx=0.0, dy=0.0) -> str:
    return f'<g transform="translate({dx:g} {dy:g}) scale({scale:g})">{_mark_for(t, gap=gap)}</g>'


def vertical(theme_name: str) -> tuple[str, float, float]:
    t = THEMES[theme_name]
    gap = "#123a35" if theme_name == "mono-white" else "#ffffff"
    size = 30.0
    words, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=0, baseline=0, mono="mono" in t)
    w = max(ww, 96.0) + 8
    mark = _mark_wrap(t, gap, scale=1.5, dx=(w - 96) / 2, dy=0)
    words, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=(w - ww) / 2, baseline=96 + 18 + cap, mono="mono" in t)
    return mark + words, w, 96 + 18 + cap + 8


def wordmark_only(theme_name: str) -> tuple[str, float, float]:
    t = THEMES[theme_name]
    size = 31.0
    _, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=0, baseline=0, mono="mono" in t)
    words, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=2, baseline=cap + 4, mono="mono" in t)
    return words, ww + 4, cap + 8


# ---------------------------------------------------------------- animated
def animated_svg() -> str:
    style = (
        "<style>.mk-shield,.mk-fold{transform-box:fill-box;transform-origin:center bottom;"
        "animation:shield .6s cubic-bezier(.2,.8,.2,1) both}"
        ".mk-c{transform-box:fill-box;transform-origin:center;animation:sweep .7s cubic-bezier(.2,.8,.2,1) .25s both}"
        ".mk-tick{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .45s ease-out .8s forwards}"
        "@keyframes shield{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}"
        "@keyframes sweep{from{opacity:0;transform:rotate(-120deg) scale(.6)}to{opacity:1;transform:none}}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        "@media (prefers-reduced-motion:reduce){.mk-shield,.mk-fold,.mk-c{animation:none}"
        ".mk-tick{animation:none;stroke-dashoffset:0}}</style>"
    )
    return svg_doc(style + mark_body("tca"), 64, 64, "Tax Clear")


# ---------------------------------------------------------------- web geometry (TS)
def write_geometry() -> None:
    def words(theme):
        t = THEMES[theme]
        size = 31.0
        _, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=76, baseline=0)
        body, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=76, baseline=32 + cap / 2)
        return body, 76 + ww + 2

    color_words, width = words("color")
    dark_words, _ = words("on-dark")
    ts = (
        "// Tệp sinh tự động bởi docs/brand/tools/build_brand.py — không sửa tay.\n"
        "// Markup biểu tượng trên lưới 128; __ID__ được thay bằng mã riêng của mỗi lần hiển thị.\n\n"
        f"export const MARK_SVG = `{mark_design('__ID__')}`;\n\n"
        f"export const MARK_SMALL_SVG = `{mark_design('__ID__', small=True)}`;\n\n"
        f"export const LOGO_WIDTH = {width:.1f};\n\n"
        f"export const WORDMARK_SVG = `{color_words}`;\n\n"
        f"export const WORDMARK_ON_DARK_SVG = `{dark_words}`;\n"
    )
    WEB_GEOMETRY.parent.mkdir(parents=True, exist_ok=True)
    WEB_GEOMETRY.write_text(ts, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- xuất file
def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_svgs() -> dict[str, Path]:
    out: dict[str, Path] = {}
    logo = BRAND / "logo"
    for theme in THEMES:
        gap = "#123a35" if theme == "mono-white" else "#ffffff"
        for kind, fn in (("horizontal", horizontal), ("vertical", vertical), ("wordmark", wordmark_only)):
            body, w, h = fn(theme)
            p = logo / f"tax-clear-ai-{kind}-{theme}.svg"
            write(p, svg_doc(body, round(w, 1), round(h, 1), "Tax Clear"))
            out[p.stem] = p
        mark = svg_doc(_mark_for(THEMES[theme], gap=gap), 64, 64, "Tax Clear")
        p = logo / f"tax-clear-ai-mark-{theme}.svg"
        write(p, mark)
        out[p.stem] = p
    small = svg_doc(mark_body("tcs", small=True), 64, 64, "Tax Clear")
    write(logo / "tax-clear-ai-mark-small.svg", small)
    out["tax-clear-ai-mark-small"] = logo / "tax-clear-ai-mark-small.svg"
    write(BRAND / "animated" / "tax-clear-ai-mark-animated.svg", animated_svg())
    return out


def render_png(page, svg_text: str, w: int, h: int, path: Path, bg: str | None = None, scale: float = 1) -> None:
    background = f"background:{bg};" if bg else "background:transparent;"
    html = (
        f"<html><body style='margin:0;{background}width:{w}px;height:{h}px;display:grid;place-items:center'>"
        f"{svg_text}</body></html>"
    )
    page.set_viewport_size({"width": w, "height": h})
    page.set_content(html)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), omit_background=bg is None, clip={"x": 0, "y": 0, "width": w, "height": h})


def sized(svg_text: str, width: float, height: float) -> str:
    return svg_text.replace('width="', 'data-w="', 1).replace('height="', 'data-h="', 1).replace(
        "<svg ", f'<svg width="{width:g}" height="{height:g}" ', 1
    )


def dims(svg_text: str) -> tuple[float, float]:
    w = float(svg_text.split('width="')[1].split('"')[0])
    h = float(svg_text.split('height="')[1].split('"')[0])
    return w, h


def fit(svg_text: str, width: float) -> str:
    w, h = dims(svg_text)
    return sized(svg_text, width, width * h / w)


def font_face() -> str:
    faces = ""
    for weight, num in (("Medium", 500), ("SemiBold", 600), ("Bold", 700)):
        # set_content chạy trên about:blank nên không nạp được file://; nhúng font dạng data URI
        data = base64.b64encode((FONTS / f"BeVietnamPro-{weight}.ttf").read_bytes()).decode()
        faces += (
            f"@font-face{{font-family:'Be Vietnam Pro';src:url(data:font/ttf;base64,{data}) "
            f"format('truetype');font-weight:{num}}}"
        )
    return faces


def social(page, svgs: dict[str, Path]) -> None:
    mark = svgs["tax-clear-ai-mark-color"].read_text(encoding="utf-8")
    mark_dark = svgs["tax-clear-ai-mark-on-dark"].read_text(encoding="utf-8")
    logo_h = svgs["tax-clear-ai-horizontal-color"].read_text(encoding="utf-8")
    logo_h_dark = svgs["tax-clear-ai-horizontal-on-dark"].read_text(encoding="utf-8")
    base_css = (
        font_face()
        + "body{margin:0;font-family:'Be Vietnam Pro',sans-serif;color:#123a35}"
        ".canvas{position:relative;overflow:hidden;width:100%;height:100%;box-sizing:border-box}"
        ".light{background:radial-gradient(120% 90% at 85% 10%,#dcf0e7 0%,transparent 60%),#eef7f3}"
        ".dark{background:radial-gradient(90% 90% at 80% 20%,#17705f 0%,transparent 55%),#0a3a33;color:#fff}"
        ".tag{display:inline-block;padding:.35em .9em;border-radius:99px;background:#e3f2ec;color:#17705f;font-weight:600}"
        ".dark .tag{background:rgba(255,255,255,.1);color:#c9f0e2}"
        ".saffron{color:#a3550c}.dark .saffron{color:#f8bd63}"
    )

    def shot(name: str, w: int, h: int, body: str, extra_css: str = "") -> None:
        page.set_viewport_size({"width": w, "height": h})
        page.set_content(f"<html><head><style>{base_css}{extra_css}</style></head><body style='width:{w}px;height:{h}px'>{body}</body></html>")
        page.wait_for_timeout(150)
        (BRAND / "social").mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(BRAND / "social" / f"{name}.png"), clip={"x": 0, "y": 0, "width": w, "height": h})

    big_ghost = sized(mark, 900, 900).replace("<svg ", '<svg style="position:absolute;right:-180px;top:-150px;opacity:.12" ', 1)
    shot(
        "og-image-1200x630",
        1200,
        630,
        f"""<div class="canvas light" style="padding:72px 80px;display:grid;align-content:space-between">
        {big_ghost}{fit(logo_h, 430)}
        <div><span class="tag" style="font-size:22px">Trợ lý chuẩn bị hồ sơ giải thể</span>
        <h1 style="font-size:64px;line-height:1.08;letter-spacing:-.03em;margin:22px 0 0;max-width:1040px">Giải thể gọn gàng.<br><span style="color:#17705f">An tâm sang trang.</span></h1></div>
        <p style="margin:0;font-size:22px;color:#4d6764">Khảo sát ngắn · Checklist giấy tờ · Hỏi đáp có trích dẫn văn bản</p></div>""",
    )
    shot(
        "avatar-1080",
        1080,
        1080,
        f'<div class="canvas light" style="display:grid;place-items:center">{sized(mark, 640, 640)}</div>',
    )
    shot(
        "avatar-dark-1080",
        1080,
        1080,
        f'<div class="canvas dark" style="display:grid;place-items:center">{sized(mark_dark, 640, 640)}</div>',
    )
    shot(
        "facebook-cover-1640x624",
        1640,
        624,
        f"""<div class="canvas dark" style="padding:0 120px;display:flex;align-items:center;justify-content:space-between">
        <div style="display:grid;gap:26px">{fit(logo_h_dark, 520)}
        <p style="margin:0;font-size:40px;font-weight:600;letter-spacing:-.02em;max-width:820px">Giải thể gọn gàng. <span class="saffron">An tâm sang trang.</span></p></div>
        {sized(mark_dark, 380, 380)}</div>""",
    )
    shot(
        "linkedin-banner-1584x396",
        1584,
        396,
        f"""<div class="canvas light" style="padding:0 96px;display:flex;align-items:center">
        {sized(mark, 560, 560).replace('<svg ', '<svg style="position:absolute;right:-90px;top:-82px" ', 1)}
        <div style="display:grid;gap:16px;max-width:980px">{fit(logo_h, 300)}
        <p style="margin:0;font-size:46px;font-weight:600;letter-spacing:-.02em;line-height:1.15">Giải thể gọn gàng. <span class="saffron">An tâm sang trang.</span></p></div></div>""",
    )
    shot(
        "slide-cover-1920x1080",
        1920,
        1080,
        f"""<div class="canvas dark" style="padding:120px 140px;display:grid;align-content:space-between">
        {sized(mark_dark, 1400, 1400).replace('<svg ', '<svg style="position:absolute;right:-420px;top:-160px;opacity:.16" ', 1)}
        {fit(logo_h_dark, 560)}
        <div style="display:grid;gap:30px"><span class="tag" style="font-size:26px;justify-self:start">Giới thiệu sản phẩm</span>
        <h1 style="margin:0;font-size:120px;line-height:1;letter-spacing:-.04em;max-width:1300px">Giải thể gọn gàng.<br><span class="saffron">An tâm sang trang.</span></h1></div>
        <p style="margin:0;font-size:28px;color:#c9f0e2">Trợ lý chuẩn bị hồ sơ giải thể cho doanh nghiệp · Bản thử nghiệm</p></div>""",
    )


def build_pngs(svgs: dict[str, Path]) -> None:
    from PIL import Image
    from playwright.sync_api import sync_playwright

    png = BRAND / "png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        mark = svgs["tax-clear-ai-mark-color"].read_text(encoding="utf-8")
        small = svgs["tax-clear-ai-mark-small"].read_text(encoding="utf-8")
        for size in (512, 256, 128):
            render_png(page, sized(mark, size, size), size, size, png / f"mark-{size}.png")
        for size in (16, 32, 48):
            render_png(page, sized(small, size, size), size, size, png / f"favicon-{size}.png")
        # icon ứng dụng: nền trắng, biểu tượng chiếm ~68%
        for size, name in ((180, "apple-touch-icon"), (192, "icon-192"), (512, "icon-512")):
            inner = round(size * 0.68)
            render_png(page, sized(mark, inner, inner), size, size, png / f"{name}.png", bg="#ffffff")
        for name, path in svgs.items():
            if "horizontal" in name or "vertical" in name:
                text = path.read_text(encoding="utf-8")
                w = float(text.split('width="')[1].split('"')[0])
                h = float(text.split('height="')[1].split('"')[0])
                scale = 4
                bg = "#123a35" if ("on-dark" in name or "mono-white" in name) else None
                render_png(page, sized(text, w * scale, h * scale), round(w * scale), round(h * scale), png / f"{name}.png", bg=bg)
        social(page, svgs)
        browser.close()
    icons = [Image.open(png / f"favicon-{s}.png").convert("RGBA") for s in (16, 32, 48)]
    icons[2].save(png / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=icons[:2])


def publish_to_web(svgs: dict[str, Path]) -> None:
    import shutil

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in ("tax-clear-ai-horizontal-color", "tax-clear-ai-horizontal-on-dark", "tax-clear-ai-mark-color"):
        shutil.copy(svgs[name], WEB_PUBLIC / f"{name}.svg")
    shutil.copy(BRAND / "png" / "icon-192.png", WEB_PUBLIC / "icon-192.png")
    shutil.copy(BRAND / "png" / "icon-512.png", WEB_PUBLIC / "icon-512.png")
    shutil.copy(svgs["tax-clear-ai-mark-small"], WEB_APP / "icon.svg")
    shutil.copy(BRAND / "png" / "apple-touch-icon.png", WEB_APP / "apple-icon.png")
    shutil.copy(BRAND / "png" / "favicon.ico", WEB_APP / "favicon.ico")
    shutil.copy(BRAND / "social" / "og-image-1200x630.png", WEB_APP / "opengraph-image.png")


if __name__ == "__main__":
    built = build_svgs()
    build_pngs(built)
    write_geometry()
    publish_to_web(built)
    print(f"Đã dựng {len(built)} SVG, PNG, ấn phẩm và tài sản web.")
