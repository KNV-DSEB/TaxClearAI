"""Dựng toàn bộ tài sản thương hiệu Tax Clear AI từ một định nghĩa hình học.

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


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    ra, ga, ba = _hex(a)
    rb, gb, bb = _hex(b)
    return "#{:02x}{:02x}{:02x}".format(
        round(ra + (rb - ra) * t), round(ga + (gb - ga) * t), round(ba + (bb - ba) * t)
    )


# ---------------------------------------------------------------- C pha lê
CX = CY = 32.0
R_OUT, R_IN = 28.0, 13.5
ANGLES = [22.5 + 45 * k for k in range(8)]  # SVG: y hướng xuống, 22.5° = dưới phải
LIGHT_FROM = 225.0  # ánh sáng từ góc trên trái


def _pt(r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return round(CX + r * math.cos(a), 2), round(CY + r * math.sin(a), 2)


def _lightness(mid: float) -> float:
    return (math.cos(math.radians(mid - LIGHT_FROM)) + 1) / 2


# Mỗi bảng màu: (mặt ngoài tối, mặt ngoài sáng, mặt trong tối, mặt trong sáng)
PALETTES = {
    "light": ("#0f5a4c", "#8fe0c4", "#0a3a33", "#2fae8a"),
    "dark": ("#1f8f73", "#c9f0e2", "#15705c", "#4cc39f"),
}
WARM = {"light": ("#f6b04c", "#e07f1f"), "dark": ("#f8bd63", "#ea8c2a")}


def facets(variant: str = "light", simple: bool = False) -> list[dict]:
    """Danh sách mặt cắt: {points, fill, role}. simple=True: 7 mặt cho cỡ nhỏ."""
    o_dark, o_light, i_dark, i_light = PALETTES[variant]
    warm_outer, warm_inner = WARM[variant]
    out = []
    for i in range(7):
        a0, a1 = ANGLES[i], ANGLES[i + 1]
        o0, o1, i0, i1 = _pt(R_OUT, a0), _pt(R_OUT, a1), _pt(R_IN, a0), _pt(R_IN, a1)
        light = _lightness((a0 + a1) / 2)
        warm = i == 6  # mép trên của khe mở bắt ánh sáng ấm
        if simple:
            fill = warm_outer if warm else mix(o_dark, o_light, light * 0.85)
            out.append({"points": [o0, o1, i1, i0], "fill": fill, "role": "warm" if warm else "facet"})
            continue
        outer = warm_outer if warm else mix(o_dark, o_light, light)
        inner = warm_inner if warm else mix(i_dark, i_light, light)
        role = "warm" if warm else "facet"
        out.append({"points": [o0, o1, i0], "fill": outer, "role": role})
        out.append({"points": [o1, i1, i0], "fill": inner, "role": role})
    return out


def _d(points) -> str:
    return "M" + "L".join(f"{x:g} {y:g}" for x, y in points) + "Z"


def mark_body(variant="light", simple=False, mono: str | None = None, gap_color: str | None = None) -> str:
    parts = []
    for f in facets(variant, simple):
        fill = mono or f["fill"]
        if mono and gap_color:
            parts.append(
                f'<path d="{_d(f["points"])}" fill="{fill}" stroke="{gap_color}" '
                f'stroke-width="1.4" stroke-linejoin="round"/>'
            )
        else:
            parts.append(f'<path d="{_d(f["points"])}" fill="{fill}"/>')
    return "".join(parts)


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
    """'Tax Clear' + chữ x vẽ riêng (một nét vàng nghệ) + 'AI' nhỏ. Trả (svg, width, cap_height)."""
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
    x2 = x1 + w2 + size * 0.2
    d3, w3 = text_path("AI", "Medium", size * 0.6, x2, baseline, tracking=size * 0.02)
    body = (
        f'<path d="{d1}" fill="{ink}"/>{xs}<path d="{d2}" fill="{ink}"/>'
        f'<path d="{d3}" fill="{ink if mono else accent}"/>'
    )
    return body, x2 + w3 - x, cap


# ---------------------------------------------------------------- lockups
THEMES = {
    "color": dict(variant="light", ink=COLORS["ink"], accent=COLORS["teal-700"], warm=COLORS["saffron-500"]),
    "on-dark": dict(variant="dark", ink=COLORS["white"], accent=COLORS["teal-300"], warm=COLORS["saffron-500"]),
    "mono-dark": dict(variant="light", ink=COLORS["ink"], accent=COLORS["ink"], warm=COLORS["ink"], mono=COLORS["ink"]),
    "mono-white": dict(variant="dark", ink=COLORS["white"], accent=COLORS["white"], warm=COLORS["white"], mono=COLORS["white"]),
}


def _mark_for(theme: dict, simple=False, gap="#ffffff") -> str:
    mono = theme.get("mono")
    return mark_body(theme["variant"], simple, mono=mono, gap_color=(gap if mono else None))


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
    paths = []
    for idx, f in enumerate(facets("light")):
        cls = "f warm" if f["role"] == "warm" else "f"
        paths.append(
            f'<path class="{cls}" style="animation-delay:{idx * 45}ms" d="{_d(f["points"])}" fill="{f["fill"]}"/>'
        )
    style = (
        "<style>.f{transform-box:fill-box;transform-origin:center;animation:in .7s cubic-bezier(.2,.8,.2,1) both}"
        ".warm{animation:in .7s cubic-bezier(.2,.8,.2,1) both,glint 1.2s ease-in-out .9s both}"
        "@keyframes in{from{opacity:0;transform:scale(.4) rotate(-20deg)}to{opacity:1;transform:none}}"
        "@keyframes glint{0%,100%{filter:none}45%{filter:brightness(1.35) drop-shadow(0 0 2px #f6b04c)}}"
        "@media (prefers-reduced-motion:reduce){.f,.warm{animation:none}}</style>"
    )
    return svg_doc(style + "".join(paths), 64, 64, "Tax Clear AI")


# ---------------------------------------------------------------- web geometry (TS)
def write_geometry() -> None:
    def facet_list(variant, simple):
        rows = [
            f"  {{ d: '{_d(f['points'])}', fill: '{f['fill']}', warm: {str(f['role'] == 'warm').lower()} }},"
            for f in facets(variant, simple)
        ]
        return "[\n" + "\n".join(rows) + "\n]"

    def words(theme):
        t = THEMES[theme]
        size = 31.0
        _, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=76, baseline=0)
        body, ww, cap = wordmark(t["ink"], t["accent"], t["warm"], size, x=76, baseline=32 + cap / 2)
        return body, 76 + ww + 2

    color_words, width = words("color")
    dark_words, _ = words("on-dark")
    ts = (
        "// Tệp sinh tự động bởi docs/brand/tools/build_brand.py — không sửa tay.\n\n"
        "export interface Facet {\n  d: string;\n  fill: string;\n  warm: boolean;\n}\n\n"
        f"export const FACETS: Facet[] = {facet_list('light', False)};\n\n"
        f"export const FACETS_ON_DARK: Facet[] = {facet_list('dark', False)};\n\n"
        f"export const FACETS_SMALL: Facet[] = {facet_list('light', True)};\n\n"
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
            write(p, svg_doc(body, round(w, 1), round(h, 1), "Tax Clear AI"))
            out[p.stem] = p
        mark = svg_doc(_mark_for(THEMES[theme], gap=gap), 64, 64, "Tax Clear AI")
        p = logo / f"tax-clear-ai-mark-{theme}.svg"
        write(p, mark)
        out[p.stem] = p
    small = svg_doc(mark_body("light", simple=True), 64, 64, "Tax Clear AI")
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
        <h1 style="font-size:64px;line-height:1.08;letter-spacing:-.03em;margin:22px 0 0;max-width:1040px">Gỡ rối hồ sơ.<br><span style="color:#17705f">Biết bước chuẩn bị tiếp theo.</span></h1></div>
        <p style="margin:0;font-size:22px;color:#4d6764">Khảo sát 11 câu · Checklist giấy tờ · Hỏi đáp có trích dẫn văn bản</p></div>""",
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
        <p style="margin:0;font-size:40px;font-weight:600;letter-spacing:-.02em;max-width:820px">Gỡ rối hồ sơ giải thể. <span class="saffron">Từng bước, rõ ràng.</span></p></div>
        {sized(mark_dark, 380, 380)}</div>""",
    )
    shot(
        "linkedin-banner-1584x396",
        1584,
        396,
        f"""<div class="canvas light" style="padding:0 96px;display:flex;align-items:center">
        {sized(mark, 560, 560).replace('<svg ', '<svg style="position:absolute;right:-90px;top:-82px" ', 1)}
        <div style="display:grid;gap:16px;max-width:980px">{fit(logo_h, 300)}
        <p style="margin:0;font-size:46px;font-weight:600;letter-spacing:-.02em;line-height:1.15">Chuẩn bị hồ sơ giải thể, <span class="saffron">rõ ràng từng bước.</span></p></div></div>""",
    )
    shot(
        "slide-cover-1920x1080",
        1920,
        1080,
        f"""<div class="canvas dark" style="padding:120px 140px;display:grid;align-content:space-between">
        {sized(mark_dark, 1400, 1400).replace('<svg ', '<svg style="position:absolute;right:-420px;top:-160px;opacity:.16" ', 1)}
        {fit(logo_h_dark, 560)}
        <div style="display:grid;gap:30px"><span class="tag" style="font-size:26px;justify-self:start">Giới thiệu sản phẩm</span>
        <h1 style="margin:0;font-size:120px;line-height:1;letter-spacing:-.04em;max-width:1300px">Gỡ rối hồ sơ.<br><span class="saffron">Biết bước tiếp theo.</span></h1></div>
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
