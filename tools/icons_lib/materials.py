# SPDX-License-Identifier: GPL-2.0-or-later
"""Mac OS X 10.2 "Jaguar" Aqua icon materials, geometry, and base objects.

All palettes and proportions are sampled from Apple's June 2002 *Aqua Human Interface
Guidelines*, Chapter 11 ("Icons", pages 201-220) and Chapter 6/7 dialog figures:
- Finder face (ch11-202-002.png): left #9cbdff->#5272d9->#3052b6, right #d3e4ff->#95a6de
- System Preferences plate (ch11-209-015.png): #f7f7f7->#efefef->#dedede, #808990->#465157
- External drive (ch11-210-017.png): amber anodized top #ec9524..#ffcc4a, bevel #8b500a
- Internal 3.5" drive (ch11-210-017.png): brushed aluminum #d6d5db->#b6b5bb->#9d9ca1
- Network glass globe (ch11-210-017.png): #050239->#367dcb->#8ec3f9->#e7fbff + #dff4ff arcs
- Pinstriped Aqua folder (ch11-212-021.png, al-107-045.png): #e6ffff->#7ab4f5->#5c99df
- Hovered document sheet (ch11-208-012..014.png, Figure 11-11 "Do this")
"""
import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
    QRadialGradient,
    QTransform,
)


def c(hex_or_rgba, a=None):
    col = QColor(hex_or_rgba) if isinstance(hex_or_rgba, str) else QColor(*hex_or_rgba)
    if a is not None:
        col.setAlpha(a)
    return col


def vgrad(y0, y1, *stops, x0=16.0, x1=16.0):
    g = QLinearGradient(QPointF(x0, y0), QPointF(x1, y1))
    for pos, col in stops:
        g.setColorAt(pos, c(col))
    return g


def hgrad(x0, x1, *stops, y0=16.0, y1=16.0):
    g = QLinearGradient(QPointF(x0, y0), QPointF(x1, y1))
    for pos, col in stops:
        g.setColorAt(pos, c(col))
    return g


def rgrad(cx, cy, r, *stops, fx=None, fy=None):
    g = QRadialGradient(
        QPointF(cx, cy), r, QPointF(cx if fx is None else fx, cy if fy is None else fy)
    )
    for pos, col in stops:
        g.setColorAt(pos, c(col))
    return g


# ---- Vector path helpers (work on any canvas coordinate system, default 32x32) ----

def rr(x, y, w, h, r=0.0):
    p = QPainterPath()
    if r <= 0:
        p.addRect(QRectF(x, y, w, h))
    else:
        p.addRoundedRect(QRectF(x, y, w, h), r, r)
    return p


def circ(cx, cy, r):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), r, r)
    return p


def ellipse(cx, cy, rx, ry):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), rx, ry)
    return p


def stroke(path, width, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(width)
    s.setCapStyle(cap)
    s.setJoinStyle(join)
    return s.createStroke(path).simplified()


def poly(*pts, round_=0.0):
    p = QPainterPath()
    p.addPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
    p.closeSubpath()
    if round_:
        p = U(p, stroke(p, round_))
    return p


def line(x1, y1, x2, y2, w=2.0, cap=Qt.RoundCap):
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    return stroke(p, w, cap)


def polyline(pts, w=2.0, cap=Qt.RoundCap, join=Qt.RoundJoin):
    p = QPainterPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    return stroke(p, w, cap, join)


def arc_path(cx, cy, r, start, span, w=2.0, cap=Qt.RoundCap):
    p = QPainterPath()
    rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
    p.arcMoveTo(rect, start)
    p.arcTo(rect, start, span)
    return stroke(p, w, cap)


def ring(cx, cy, r, w):
    return S(circ(cx, cy, r + w / 2.0), circ(cx, cy, r - w / 2.0))


def U(*paths):
    out = QPainterPath()
    for p in paths:
        if p is not None and not p.isEmpty():
            out = out.united(p)
    return out.simplified()


def S(a, *bs):
    for b in bs:
        if b is not None and not b.isEmpty():
            a = a.subtracted(b)
    return a.simplified()


def plus_path(cx=16.0, cy=16.0, s=4.5, w=2.4):
    return U(line(cx - s, cy, cx + s, cy, w), line(cx, cy - s, cx, cy + s, w))


def cross_path(cx=16.0, cy=16.0, s=3.8, w=2.4):
    return U(line(cx - s, cy - s, cx + s, cy + s, w), line(cx + s, cy - s, cx - s, cy + s, w))


def star_path(cx=16.0, cy=16.0, ro=6.5, ri=2.8, pts_n=5, round_=0.4):
    pts = []
    for i in range(pts_n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * (180.0 / pts_n))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(*pts, round_=round_)


def gear_path(cx=16.0, cy=16.0, teeth=8, r_out=7.0, r_in=5.2, hole=2.2):
    g = circ(cx, cy, r_in)
    for i in range(teeth):
        ang = i * 360.0 / teeth
        tooth = rr(cx - 1.3, cy - r_out, 2.6, 3.0, 0.55)
        t = QTransform().translate(cx, cy).rotate(ang).translate(-cx, -cy)
        g = U(g, t.map(tooth))
    return S(g, circ(cx, cy, hole))


def text_path(txt, cx, cy, px=8.0, bold=True, italic=False, serif=False):
    f = QFont("DejaVu Serif" if serif else "Luxi Sans")
    if not serif:
        f.setFamilies(["Lucida Grande", "Luxi Sans", "DejaVu Sans"])
    f.setBold(bold)
    f.setItalic(italic)
    f.setPixelSize(max(4, int(round(px))))
    tp = QPainterPath()
    tp.addText(QPointF(0, 0), f, txt)
    br = tp.boundingRect()
    if not br.isEmpty():
        tp.translate(cx - br.center().x(), cy - br.center().y())
    return tp


# ---- Shadows (overhead lighting, HIG p. 213-217) ----

def floor_shadow(p, cx=16.0, cy=28.5, rx=11.0, ry=2.5, alpha=70):
    p.save()
    p.setPen(Qt.NoPen)
    p.translate(cx, cy)
    p.scale(rx, ry)
    g = QRadialGradient(QPointF(0, 0), 1.0)
    g.setColorAt(0.0, QColor(0, 0, 0, alpha))
    g.setColorAt(0.55, QColor(0, 0, 0, int(alpha * 0.45)))
    g.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.setBrush(g)
    p.drawEllipse(QPointF(0, 0), 1.0, 1.0)
    p.restore()


def drop_shadow_path(p, path, dx=0.0, dy=1.3, alpha=58):
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 10, 28, int(alpha * 0.55)))
    p.drawPath(path.translated(dx, dy + 0.7))
    p.setBrush(QColor(0, 10, 28, alpha))
    p.drawPath(path.translated(dx * 0.6, dy * 0.65))
    p.restore()


# ---- Aqua Gel Palettes & Shapes ----

GEL_PALETTES = {
    "clear":  ("#5c5e63", (0.0, "#dcdedf"), (0.34, "#d2d4d8"), (0.50, "#9e9fa4"), (0.72, "#e8eaed"), (0.90, "#ffffff"), (1.0, "#cfd2d6")),
    "blue":   ("#0d3c82", (0.0, "#b8dcff"), (0.38, "#3e82e8"), (0.50, "#1d5cc9"), (0.75, "#4da0f5"), (0.92, "#94e6ff"), (1.0, "#50b4f8")),
    "red":    ("#660e06", (0.0, "#ffb8b0"), (0.38, "#de3222"), (0.50, "#ad1206"), (0.76, "#e03422"), (0.92, "#ff8b78"), (1.0, "#d42b1c")),
    "green":  ("#1b5c10", (0.0, "#ccf8b4"), (0.38, "#4ec032"), (0.50, "#289214"), (0.76, "#58ca38"), (0.92, "#c8ff9c"), (1.0, "#4eb832")),
    "amber":  ("#7d4908", (0.0, "#fff2b2"), (0.38, "#f4aa24"), (0.50, "#cf7a0c"), (0.76, "#f7b934"), (0.92, "#ffe88a"), (1.0, "#df9618")),
    "purple": ("#3e1b6e", (0.0, "#e6ccff"), (0.38, "#9452de"), (0.50, "#6c2ab8"), (0.76, "#9e5ce8"), (0.92, "#e4b8ff"), (1.0, "#8642d4")),
    "cyan":   ("#0c546e", (0.0, "#c8f8ff"), (0.38, "#28a8cf"), (0.50, "#127ea4"), (0.76, "#36bce2"), (0.92, "#a8f6ff"), (1.0, "#2aa4cc")),
    "graphite": ("#3a3e47", (0.0, "#cfd5df"), (0.38, "#7b8494"), (0.50, "#565e6c"), (0.76, "#838d9e"), (0.92, "#dce2ec"), (1.0, "#6c7585")),
}


def glass_disc(p, cx=16.0, cy=15.5, r=12.0, kind="clear", octagon=False, shadow=True):
    if shadow:
        floor_shadow(p, cx, cy + r * 0.92, r * 0.95, max(1.6, r * 0.22), 76)
    rim, *stops = GEL_PALETTES[kind]
    shape = QPainterPath()
    if octagon:
        pts = [
            QPointF(
                cx + r * 1.05 * math.cos(math.radians(22.5 + i * 45)),
                cy + r * 1.05 * math.sin(math.radians(22.5 + i * 45)),
            )
            for i in range(8)
        ]
        shape.addPolygon(QPolygonF(pts))
        shape.closeSubpath()
    else:
        shape.addEllipse(QPointF(cx, cy), r, r)

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(cy - r, cy + r, *stops, x0=cx, x1=cx))
    p.drawPath(shape)

    p.setClipPath(shape)
    pillow = QRadialGradient(QPointF(cx, cy + r * 0.18), r * 1.04)
    pillow.setColorAt(0.0, QColor(255, 255, 255, 0))
    pillow.setColorAt(0.74, QColor(0, 0, 0, 0))
    pillow.setColorAt(1.0, QColor(0, 0, 0, 56 if kind == "clear" else 74))
    p.setBrush(pillow)
    p.drawRect(QRectF(cx - r - 2, cy - r - 2, 2 * r + 4, 2 * r + 4))

    lens_r = QRectF(cx - r * 0.68, cy - r + r * 0.09, r * 1.36, r * 0.80)
    p.setBrush(
        vgrad(
            lens_r.top(),
            lens_r.bottom(),
            (0.0, (255, 255, 255, 242)),
            (0.55, (255, 255, 255, 132)),
            (1.0, (255, 255, 255, 16)),
            x0=cx,
            x1=cx,
        )
    )
    p.drawEllipse(lens_r)
    p.restore()

    p.setPen(QPen(c(rim), max(0.85, min(1.2, r * 0.095))))
    p.setBrush(Qt.NoBrush)
    p.drawPath(shape)


def draw_disc_glyph(p, path, dark=True):
    p.save()
    p.setPen(Qt.NoPen)
    if dark:
        p.setBrush(QColor(255, 255, 255, 155))
        p.drawPath(path.translated(0, 0.8))
        p.setBrush(c("#16171a"))
        p.drawPath(path)
    else:
        p.setBrush(QColor(0, 0, 0, 105))
        p.drawPath(path.translated(0, 0.9))
        p.setBrush(c("#ffffff"))
        p.drawPath(path)
    p.restore()


def paint_gel_shape(p, path, top_y=None, bot_y=None, kind="blue", shadow=True):
    br = path.boundingRect()
    if top_y is None:
        top_y = br.top()
    if bot_y is None:
        bot_y = br.bottom()
    rim, *stops = GEL_PALETTES[kind]
    p.save()
    if shadow:
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 18, 45, 70))
        p.drawPath(path.translated(0.4, 1.2))
    p.setBrush(vgrad(top_y, max(top_y + 1.0, bot_y), *stops, x0=br.center().x(), x1=br.center().x()))
    p.setPen(QPen(c(rim), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPath(path)
    p.setClipPath(path)
    mid_y = top_y + (bot_y - top_y) * 0.46
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(top_y, max(top_y + 0.5, mid_y), (0.0, (255, 255, 255, 195)), (1.0, (255, 255, 255, 18))))
    p.drawRect(QRectF(br.left() - 1, top_y, br.width() + 2, max(0.5, mid_y - top_y)))
    p.restore()


def bevel_tile(p, x=3.5, y=5.5, w=25.0, h=20.0, r=3.4):
    floor_shadow(p, x + w / 2, y + h + 1.1, w * 0.46, 2.0, 58)
    path = rr(x, y, w, h, r)
    p.setPen(Qt.NoPen)
    p.setBrush(
        vgrad(
            y,
            y + h,
            (0.0, "#ffffff"),
            (0.42, "#e3e5ea"),
            (0.48, "#cfd3da"),
            (0.85, "#f4f5f8"),
            (1.0, "#ffffff"),
        )
    )
    p.drawPath(path)
    lens = rr(x + 1.2, y + 1.0, w - 2.4, h * 0.42, max(0.6, r - 0.8))
    p.setBrush(vgrad(y + 1.0, y + 1.0 + h * 0.42, (0.0, (255, 255, 255, 220)), (1.0, (255, 255, 255, 30))))
    p.drawPath(lens)
    p.setPen(QPen(c("#686b73"), 1.05))
    p.setBrush(Qt.NoBrush)
    p.drawPath(path)


def aqua_arrow_path(cx, cy, r_outer, r_inner, start_deg, span_deg):
    rmid = (r_outer + r_inner) / 2.0
    thick = r_outer - r_inner
    rect = QRectF(cx - rmid, cy - rmid, 2 * rmid, 2 * rmid)
    trim = 18.0 if span_deg > 0 else -18.0
    body_span = span_deg - trim if abs(span_deg) > 40 else span_deg * 0.75
    p = QPainterPath()
    p.arcMoveTo(rect, start_deg)
    p.arcTo(rect, start_deg, body_span)
    st = QPainterPathStroker()
    st.setWidth(thick)
    st.setCapStyle(Qt.FlatCap)
    body = st.createStroke(p)
    sr = math.radians(start_deg)
    tail = circ(cx + rmid * math.cos(sr), cy - rmid * math.sin(sr), thick / 2.0)
    end_deg = start_deg + body_span
    end_rad = math.radians(end_deg)
    ex = cx + rmid * math.cos(end_rad)
    ey = cy - rmid * math.sin(end_rad)
    tan_deg = end_deg + (90 if span_deg > 0 else -90)
    tr = math.radians(tan_deg)
    nr = tr + math.pi / 2
    hw = thick * 1.48
    hl = thick * 2.05
    tip = QPointF(ex + hl * 0.88 * math.cos(tr), ey - hl * 0.88 * math.sin(tr))
    b1 = QPointF(ex - hl * 0.14 * math.cos(tr) + hw * math.cos(nr), ey + hl * 0.14 * math.sin(tr) - hw * math.sin(nr))
    b2 = QPointF(ex - hl * 0.14 * math.cos(tr) - hw * math.cos(nr), ey + hl * 0.14 * math.sin(tr) + hw * math.sin(nr))
    head = QPainterPath()
    head.addPolygon(QPolygonF([tip, b1, b2]))
    head.closeSubpath()
    return body.united(tail).united(head).simplified()


# ---- Reusable 10.2 Corner Badges ----

def plus_badge(p, cx=24.0, cy=8.5, s=5.0, arm=2.1):
    cross_p = U(rr(cx - s, cy - arm / 2, 2 * s, arm, 0.6), rr(cx - arm / 2, cy - s, arm, 2 * s, 0.6))
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 20, 55, 70))
    p.drawPath(cross_p.translated(0.5, 1.0))
    p.setPen(QPen(c("#2f4b7c"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(cy - s, cy + s, (0.0, "#ffffff"), (1.0, "#dceeff"), x0=cx, x1=cx))
    p.drawPath(cross_p)
    p.setPen(Qt.NoPen)
    p.drawPath(cross_p)
    p.restore()


def mini_badge_disc(p, cx=23.6, cy=22.6, r=5.8, kind="blue", glyph=None, dark=False):
    glass_disc(p, cx, cy, r, kind, shadow=False)
    if glyph is not None:
        draw_disc_glyph(p, glyph, dark=dark)


def alias_arrow_badge(p, x=4.0, y=18.5, s=8.2):
    """Classic Mac OS X Finder black-on-white curved alias arrow badge in bottom-left."""
    p.save()
    box = rr(x, y, s, s, 1.4)
    p.setPen(QPen(c("#4e535e"), 0.85))
    p.setBrush(vgrad(y, y + s, (0.0, "#ffffff"), (1.0, "#dfe4ee")))
    p.drawPath(box)
    arr = U(
        arc_path(x + s * 0.52, y + s * 0.68, s * 0.28, 75, 115, 1.5),
        poly((x + s * 0.50, y + s * 0.18), (x + s * 0.84, y + s * 0.42), (x + s * 0.50, y + s * 0.62)),
    )
    p.setPen(Qt.NoPen)
    p.setBrush(c("#14161a"))
    p.drawPath(arr)
    p.restore()


# ---- 10.2 Sky-Blue & Tinted Pinstriped Aqua Folders (ch11-212-021.png, al-107-045.png) ----

FOLDER_TINTS = {
    "blue":   ("#6b7c93", "#dcebfb", "#9abce4", "#476d9e", ("#e6ffff", "#b5dffd", "#7ab4f5", "#5c99df", "#82c2ff"), "#23508c"),
    "cyan":   ("#507b8a", "#d6f6fc", "#8ad2e4", "#316e82", ("#e8ffff", "#a6ecf8", "#5cc2de", "#3da0bf", "#74dcf2"), "#175468"),
    "green":  ("#557a58", "#dcf6de", "#90d296", "#3b7640", ("#ecffea", "#b2f0b6", "#68c870", "#48a650", "#7ae082"), "#1e5c24"),
    "red":    ("#8a5452", "#fde0de", "#e29a96", "#8c3b36", ("#ffecea", "#fcb2ac", "#e66860", "#c8463e", "#f47e76"), "#6e1c16"),
    "orange": ("#8a6842", "#fdedd6", "#e4bc88", "#8e5c24", ("#fff4e2", "#fcd29c", "#ee9e46", "#cf7c22", "#f8b45c"), "#6e3e0c"),
    "yellow": ("#85783c", "#fdf6d2", "#e4d27c", "#8a741c", ("#fffce4", "#fceea2", "#ecd04c", "#caa824", "#f8df66"), "#685208"),
    "violet": ("#6e5c8c", "#ebe0fc", "#b89ce2", "#5c428c", ("#f6ecff", "#d4b8fc", "#9e74e4", "#7c52c6", "#b48cf4"), "#3e2070"),
    "brown":  ("#6e5a48", "#efe2d4", "#bfa082", "#684b30", ("#f8eee4", "#dfc2a4", "#b28860", "#8e6640", "#c49c74"), "#4a3018"),
    "grey":   ("#686d75", "#eaedf2", "#b4bac4", "#585e68", ("#f8fafc", "#d8dde6", "#a8b0bc", "#868e9c", "#bfc6d2"), "#3a3f48"),
    "black":  ("#383c44", "#b8bec8", "#787e8a", "#262930", ("#aeb4c0", "#767c88", "#484d58", "#2e323b", "#5c6270"), "#e6ecf8"),
}


def aqua_folder(p, sm=False, tint="blue", open_flap=False, glyph=None):
    """10.2 sky-blue (or colour-tinted) pinstriped Aqua folder with optional embossed front emblem."""
    back_rim, back_mid, back_bot, front_rim, stops, ink = FOLDER_TINTS.get(tint, FOLDER_TINTS["blue"])
    floor_shadow(p, 16.0, 28.2, 12.2, 2.4, 72)

    back = QPainterPath()
    back.moveTo(4.0, 9.0)
    back.lineTo(4.0, 6.6)
    back.quadTo(4.0, 5.0, 5.8, 5.0)
    back.lineTo(11.6, 5.0)
    back.quadTo(13.0, 5.0, 13.8, 6.6)
    back.lineTo(26.2, 6.6)
    back.quadTo(27.8, 6.6, 27.8, 8.2)
    back.lineTo(27.2, 25.8)
    back.lineTo(4.5, 26.8)
    back.closeSubpath()
    p.setPen(QPen(c(back_rim), 1.05))
    p.setBrush(vgrad(5.0, 26.5, (0.0, "#ffffff" if tint != "black" else "#d8dde6"), (0.35, back_mid), (1.0, back_bot)))
    p.drawPath(back)

    if open_flap:
        sheet = poly((6.2, 9.2), (25.4, 8.2), (25.8, 23.0), (6.0, 24.5))
        p.setPen(QPen(c("#9aa2b0"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawPath(sheet)

    front = QPainterPath()
    if open_flap:
        front.moveTo(2.4, 14.2)
        front.lineTo(28.8, 12.6)
        front.quadTo(29.8, 12.6, 29.4, 14.2)
        front.lineTo(27.2, 25.8)
        front.lineTo(4.5, 26.8)
        front.closeSubpath()
        fy0 = 12.6
    else:
        front.moveTo(4.2, 10.0)
        front.lineTo(27.4, 8.8)
        front.quadTo(28.6, 8.8, 28.4, 10.4)
        front.lineTo(27.2, 25.8)
        front.lineTo(4.5, 26.8)
        front.closeSubpath()
        fy0 = 8.8

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(
        vgrad(
            fy0,
            26.8,
            (0.0, stops[0]),
            (0.28, stops[1]),
            (0.62, stops[2]),
            (0.88, stops[3]),
            (1.0, stops[4]),
        )
    )
    p.drawPath(front)

    p.setClipPath(front)
    for yy in range(int(fy0) + 1, 27, 2):
        p.fillRect(QRectF(2, yy, 29, 0.85), QColor(255, 255, 255, 60 if tint != "black" else 28))
    p.setPen(QPen(QColor(255, 255, 255, 210 if tint != "black" else 120), 1.2))
    if open_flap:
        p.drawLine(QPointF(3.2, 14.8), QPointF(28.5, 13.3))
    else:
        p.drawLine(QPointF(5.0, 10.7), QPointF(27.6, 9.6))

    if glyph is not None:
        # 10.2 recessed Aqua folder emblem (subtle white bottom bevel + deep tint fill)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 140 if tint != "black" else 40))
        p.drawPath(glyph.translated(0.0, 0.75))
        p.setBrush(c(ink, 215))
        p.drawPath(glyph)
    p.restore()

    p.setPen(QPen(c(front_rim), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(front)


# ---- 10.2 Hovered Curled Document Sheet (Figure 11-10, 11-11, 11-12) ----

def aqua_sheet(p, sm=False, x=5.5, y=2.5, w=21.0, h=26.5, label="", band=None, pref_strip=False, lines=False, shadow=True):
    """Hovered 10.2 white document icon with curled dog-ear and integrated bottom label."""
    fold = w * 0.29
    sheet = QPainterPath()
    sheet.moveTo(x, y)
    sheet.lineTo(x + w - fold, y)
    sheet.lineTo(x + w, y + fold)
    sheet.lineTo(x + w, y + h)
    sheet.lineTo(x, y + h)
    sheet.closeSubpath()

    if shadow:
        drop_shadow_path(p, sheet, 0.0, 1.2, 54)

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(y, y + h, (0.0, "#ffffff"), (0.68, "#f7f8fc"), (1.0, "#e5e9f1")))
    p.drawPath(sheet)
    p.setClipPath(sheet)

    if pref_strip:
        # Figure 11-12: Preferences document light-switch strip along the left margin
        sx = x + w * 0.29
        p.fillRect(QRectF(x, y, sx - x, h), vgrad(y, y + h, (0.0, "#f2f3f5"), (1.0, "#dcdfe6")))
        p.setPen(QPen(c("#a0a6b2"), 0.8))
        p.drawLine(QPointF(sx, y), QPointF(sx, y + h))
        # Tiny 3D rocker switch in strip
        sw = QRectF(x + (sx - x) * 0.28, y + h * 0.36, (sx - x) * 0.44, h * 0.24)
        p.setPen(QPen(c("#383b42"), 0.75))
        p.setBrush(vgrad(sw.top(), sw.bottom(), (0.0, "#ffffff"), (0.5, "#dfe3ec"), (1.0, "#9aa0ac")))
        p.drawRoundedRect(sw, 0.6, 0.6)

    if band and not sm:
        p.setPen(Qt.NoPen)
        p.setBrush(c(band, 38))
        p.drawRect(QRectF(x, y + h - 6.6, w, 6.6))

    if lines:
        lx0 = (x + w * 0.35) if pref_strip else (x + 3.2)
        lw_max = (w * 0.52) if pref_strip else (w - 6.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#b8c0ce"))
        for i, f_w in enumerate((0.55, 0.88, 0.88, 0.72)):
            ly = y + fold + 1.8 + i * 2.9
            if ly + 1.3 < y + h - (6.8 if label else 2.5):
                p.drawRoundedRect(QRectF(lx0, ly, lw_max * f_w, 1.25), 0.5, 0.5)

    if label and not sm:
        tp = text_path(label, x + w * (0.64 if pref_strip else 0.50), y + h - 3.4, px=5.2 if len(label) <= 4 else 4.3, bold=True)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#4e545f"))
        p.drawPath(tp)

    # Diagonal shadow cast under the curled dog-ear
    ear_sh = poly(
        (x + w - fold, y + fold),
        (x + w, y + fold),
        (x + w, y + fold + 2.8),
        (x + w - fold - 1.3, y + fold + 1.4),
    )
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 10, 30, 44))
    p.drawPath(ear_sh)
    p.restore()

    p.setPen(QPen(c("#848b98"), 0.95))
    p.setBrush(Qt.NoBrush)
    p.drawPath(sheet)

    ear = QPainterPath()
    ear.moveTo(x + w - fold, y)
    ear.lineTo(x + w, y + fold)
    ear.quadTo(x + w - fold * 0.75, y + fold * 0.92, x + w - fold, y + fold)
    ear.closeSubpath()
    p.setPen(QPen(c("#848b98"), 0.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(y, y + fold, (0.0, "#e6eaf2"), (0.58, "#ffffff"), (1.0, "#cfd4e0")))
    p.drawPath(ear)


# ---- 10.2 Hardware Drives & Optical Media (Figures 11-14, 11-15) ----

def aqua_drive(p, sm=False, kind="internal", glyph=None):
    """Figure 11-14 perspective 3.5-inch internal aluminum or orange external removable drive."""
    floor_shadow(p, 16.0, 28.4, 12.6, 2.4, 76)
    # Perspective trapezoid top + front lip
    top = QPainterPath()
    top.moveTo(6.4, 5.2)
    top.lineTo(25.6, 5.2)
    top.quadTo(26.8, 5.2, 27.1, 6.5)
    top.lineTo(28.8, 22.0)
    top.lineTo(3.2, 22.0)
    top.lineTo(4.9, 6.5)
    top.quadTo(5.2, 5.2, 6.4, 5.2)
    top.closeSubpath()

    front = QPainterPath()
    front.moveTo(3.2, 21.4)
    front.lineTo(28.8, 21.4)
    front.lineTo(28.8, 25.4)
    front.quadTo(28.8, 27.2, 26.8, 27.2)
    front.lineTo(5.2, 27.2)
    front.quadTo(3.2, 27.2, 3.2, 25.4)
    front.closeSubpath()

    if kind == "internal":
        # Sampled ch11-210-017.png: brushed silver #d6d5db -> #b6b5bb -> #9d9ca1
        p.setPen(QPen(c("#585a62"), 1.0))
        p.setBrush(vgrad(5.2, 22.0, (0.0, "#ededf2"), (0.35, "#cfd0d6"), (0.75, "#b4b3ba"), (1.0, "#9d9ca2")))
        p.drawPath(top)
        if not sm:
            # Recessed circular platter stamp + top black spec barcode label + 4 Torx screws
            p.setPen(QPen(QColor(90, 92, 100, 120), 0.9))
            p.setBrush(vgrad(10.5, 19.5, (0.0, "#b8b8c0"), (1.0, "#d8d8e0")))
            p.drawEllipse(QRectF(9.2, 10.6, 13.6, 8.8))
            p.drawEllipse(QRectF(13.6, 13.4, 4.8, 3.2))
            p.setPen(Qt.NoPen)
            p.setBrush(c("#1e2026"))
            p.drawRoundedRect(QRectF(9.4, 6.6, 11.0, 2.4), 0.5, 0.5)
            p.setBrush(c("#585a62"))
            for sx, sy in ((6.6, 6.8), (25.4, 6.8), (5.0, 20.2), (27.0, 20.2)):
                p.drawEllipse(QPointF(sx, sy), 0.75, 0.65)
        # Dark slotted front bezel + vents + lime LED
        p.setPen(QPen(c("#3a3c42"), 1.0))
        p.setBrush(hgrad(3.2, 28.8, (0.0, "#9898a0"), (0.2, "#4a4950"), (0.8, "#34343a"), (1.0, "#8d8c94")))
        p.drawPath(front)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#141418"))
            for vx in range(15, 24, 2):
                p.drawRect(QRectF(vx, 22.6, 1.1, 3.4))
    else:
        # External anodized shell (orange #ec9524..#ffcc4a sampled from ch11-210-017.png, or blue/dark)
        pal = {
            "orange": ("#8b500a", ("#f4961e", "#ffab36", "#ffc448")),
            "blue":   ("#1c4a8c", ("#387ce2", "#5ba0f6", "#86c6ff")),
            "dark":   ("#242830", ("#444b58", "#5e6778", "#7e889a")),
        }[kind]
        p.setPen(QPen(c("#6e727c"), 1.0))
        p.setBrush(vgrad(5.2, 22.0, (0.0, "#f8fafc"), (1.0, "#c8ccd4")))
        p.drawPath(top)
        # Inset coloured anodized top plate
        plate = poly((6.4, 6.0), (25.6, 6.0), (27.2, 20.2), (4.8, 20.2), round_=0.8)
        p.setPen(QPen(c(pal[0]), 0.9))
        p.setBrush(vgrad(6.0, 20.2, (0.0, pal[1][0]), (0.5, pal[1][1]), (1.0, pal[1][2])))
        p.drawPath(plate)
        if glyph is not None:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 238))
            p.drawPath(glyph)
        # Brushed silver front lip
        p.setPen(QPen(c("#686b74"), 1.0))
        p.setBrush(vgrad(21.4, 27.2, (0.0, "#ffffff"), (0.4, "#dcdde4"), (1.0, "#9c9ea8")))
        p.drawPath(front)

    # Glowing lime-yellow activity LED on bottom-right front face
    p.setPen(QPen(c("#3a5210"), 0.6))
    p.setBrush(c("#c8ff38"))
    p.drawEllipse(QPointF(25.4, 24.6), 1.05, 0.95)


def aqua_optical_disc(p, sm=False, label="", tint="silver"):
    """Figure 11-15 front-on iridescent polycarbonate CD/DVD/BD disc."""
    cx, cy, r = 16.0, 15.6, 12.4
    floor_shadow(p, cx, 28.5, 10.8, 2.2, 74)
    outer = circ(cx, cy, r)
    hole = circ(cx, cy, 2.3)
    disc = S(outer, hole)

    base_stops = {
        "silver": ((0.0, "#f8fafc"), (0.45, "#dcdfe8"), (0.75, "#b8beca"), (1.0, "#eef1f7")),
        "dvd":    ((0.0, "#f6f2fc"), (0.45, "#d4cde6"), (0.75, "#aba2c4"), (1.0, "#ece8f6")),
        "bluray": ((0.0, "#e6f4ff"), (0.45, "#9cc6f4"), (0.75, "#6898d8"), (1.0, "#d4ebff")),
        "gold":   ((0.0, "#fff8dc"), (0.45, "#ecd284"), (0.75, "#c49e42"), (1.0, "#faecc0")),
    }[tint]

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(cy - r, cy + r, *base_stops, x0=cx - r * 0.5, x1=cx + r * 0.5))
    p.drawPath(disc)

    # Diagonal rainbow iridescent prism wedges (sampled from ch11-210-018.png bottom row)
    p.setClipPath(disc)
    for base_ang in (132, 312):
        for off, col in ((-16, (110, 225, 255, 130)), (-5, (140, 245, 175, 135)), (6, (255, 230, 130, 125)), (17, (235, 150, 245, 125))):
            wedge = QPainterPath()
            wedge.moveTo(cx, cy)
            wedge.arcTo(QRectF(cx - r - 1, cy - r - 1, 2 * r + 2, 2 * r + 2), base_ang + off, 12)
            wedge.closeSubpath()
            p.setBrush(QColor(*col))
            p.drawPath(wedge)
        # Bright white specular streak
        streak = QPainterPath()
        streak.moveTo(cx, cy)
        streak.arcTo(QRectF(cx - r - 1, cy - r - 1, 2 * r + 2, 2 * r + 2), base_ang - 34, 14)
        streak.closeSubpath()
        p.setBrush(QColor(255, 255, 255, 175))
        p.drawPath(streak)

    # Translucent polycarbonate clamping hub ring
    hub = S(circ(cx, cy, 4.7), hole)
    p.setBrush(QColor(255, 255, 255, 155))
    p.setPen(QPen(QColor(110, 118, 132, 160), 0.75))
    p.drawPath(hub)

    if label and not sm:
        tp = text_path(label, cx, cy + 8.4, px=4.8, bold=True)
        p.setPen(QPen(c("#ffffff"), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(tp)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#1a1d24"))
        p.drawPath(tp)
    p.restore()

    p.setPen(QPen(c("#6c727e"), 1.0))
    p.setBrush(Qt.NoBrush)
    p.drawPath(outer)
    p.drawPath(hole)


# ---- 10.2 Pinstriped Acrylic Monitors & System Preferences Plate ----

def aqua_pinstripe_monitor(p, sm=False, screen_bg=("#1b1e24", "#2e333d"), stand=True):
    """10.2 translucent pinstriped-bezel Studio Display / Terminal frame (ch11-203-003.png)."""
    floor_shadow(p, 16.0, 28.5, 12.2, 2.2, 72)
    if stand:
        # Translucent acrylic pedestal foot
        p.setPen(QPen(c("#787e8a"), 0.9))
        p.setBrush(vgrad(23.5, 28.2, (0.0, "#d4dce8"), (1.0, "#ffffff")))
        p.drawRoundedRect(QRectF(12.2, 23.2, 7.6, 3.4), 1.0, 1.0)
        p.drawRoundedRect(QRectF(8.6, 25.8, 14.8, 2.4), 1.2, 1.2)
        bezel = QRectF(3.5, 3.6, 25.0, 20.6)
    else:
        bezel = QRectF(3.2, 4.2, 25.6, 23.4)

    bp = rr(bezel.x(), bezel.y(), bezel.width(), bezel.height(), 2.6)
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(bezel.top(), bezel.bottom(), (0.0, "#f9fafc"), (0.5, "#eaedf2"), (1.0, "#d4d8e0")))
    p.drawPath(bp)
    p.setClipPath(bp)
    # Fine vertical pinstripes on 10.2 Terminal / Studio Display acrylic bezel
    if not sm:
        for xx in range(int(bezel.left()) + 1, int(bezel.right()), 2):
            p.fillRect(QRectF(xx, bezel.top(), 0.85, bezel.height()), QColor(175, 182, 194, 75))
    p.restore()
    p.setPen(QPen(c("#767c88"), 1.0))
    p.setBrush(Qt.NoBrush)
    p.drawPath(bp)

    scr = bezel.adjusted(2.7, 2.6, -2.7, -3.4 if stand else -3.2)
    p.setPen(QPen(c("#121418"), 1.0))
    p.setBrush(vgrad(scr.top(), scr.bottom(), (0.0, screen_bg[0]), (1.0, screen_bg[1])))
    p.drawRoundedRect(scr, 1.1, 1.1)
    # Subtle diagonal CRT/LCD glass reflection
    refl = poly(
        (scr.left() + 0.6, scr.top() + 0.6),
        (scr.right() - 2.0, scr.top() + 0.6),
        (scr.left() + 5.0, scr.bottom() - 2.0),
        (scr.left() + 0.6, scr.bottom() - 2.0),
    )
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255, 255, 255, 26))
    p.drawPath(refl)
    return scr


def aqua_pref_plate(p, sm=False):
    """Figure 11-12: 10.2 System Preferences brushed-silver light-switch wall plate."""
    plate = rr(3.0, 5.0, 26.0, 22.0, 1.8)
    drop_shadow_path(p, plate, 0.0, 1.3, 62)
    p.setPen(QPen(c("#7a7e86"), 1.0))
    p.setBrush(vgrad(5.0, 27.0, (0.0, "#fafafa"), (0.45, "#eeeeee"), (1.0, "#dcdde0")))
    p.drawPath(plate)
    # Inner white top highlight bevel
    p.setPen(QPen(QColor(255, 255, 255, 210), 0.9))
    p.drawLine(QPointF(4.2, 6.0), QPointF(27.8, 6.0))
    # Vertical seam at x=11.4 separating switch compartment from emblem compartment
    p.setPen(QPen(c("#a8acb4"), 0.9))
    p.drawLine(QPointF(11.4, 5.5), QPointF(11.4, 26.5))
    p.setPen(QPen(QColor(255, 255, 255, 190), 0.8))
    p.drawLine(QPointF(12.2, 5.8), QPointF(12.2, 26.2))

    # 3D recessed dark switch slot + silver/white toggle switch on left
    p.setPen(Qt.NoPen)
    p.setBrush(c("#24282b"))
    p.drawRoundedRect(QRectF(5.7, 11.8, 3.2, 8.4), 0.6, 0.6)
    p.setPen(QPen(c("#585c64"), 0.75))
    p.setBrush(vgrad(12.4, 19.4, (0.0, "#ffffff"), (0.48, "#e6e8ec"), (0.55, "#b4b8c0"), (1.0, "#d8dce4")))
    p.drawRoundedRect(QRectF(6.1, 12.5, 2.4, 6.6), 0.5, 0.5)

    if not sm:
        # 4 slotted corner screw heads (sampled from ch11-209-015.png)
        for sx, sy in ((5.3, 7.4), (5.3, 24.6), (26.6, 7.4), (26.6, 24.6)):
            p.setPen(QPen(c("#6a6e76"), 0.65))
            p.setBrush(c("#cfd3dc"))
            p.drawEllipse(QPointF(sx, sy), 1.05, 1.05)
            p.drawLine(QPointF(sx - 0.7, sy - 0.5), QPointF(sx + 0.7, sy + 0.5))


def aqua_globe(p, cx=16.0, cy=14.8, r=10.8, sm=False, on_stand=False):
    """Figure 11-14: 10.2 glowing sapphire-blue glass network globe with luminous geodesic arcs."""
    if on_stand:
        floor_shadow(p, 16.0, 28.6, 10.6, 2.1, 74)
        # Mini silver drive pedestal underneath globe (sampled ch11-210-017.png bottom-left)
        base_top = poly((7.5, 21.0), (24.5, 21.0), (26.0, 25.0), (6.0, 25.0))
        p.setPen(QPen(c("#585a62"), 0.9))
        p.setBrush(vgrad(21.0, 25.0, (0.0, "#dcdde4"), (1.0, "#9d9ea6")))
        p.drawPath(base_top)
        p.setBrush(c("#3c3d44"))
        p.drawRoundedRect(QRectF(6.0, 24.4, 20.0, 3.2), 1.0, 1.0)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#c8ff38"))
        p.drawEllipse(QPointF(23.6, 26.0), 0.85, 0.85)
        cy, r = 13.0, 9.6
    else:
        floor_shadow(p, cx, cy + r + 1.4, r * 0.92, 2.2, 72)

    sph = circ(cx, cy, r)
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(
        vgrad(
            cy - r,
            cy + r,
            (0.0, "#070a4a"),
            (0.28, "#1844b0"),
            (0.62, "#3c88dc"),
            (0.86, "#88d0ff"),
            (1.0, "#e6fbff"),
            x0=cx,
            x1=cx,
        )
    )
    p.drawPath(sph)
    p.setClipPath(sph)

    # Bottom internal cyan glow
    p.setBrush(rgrad(cx, cy + r * 0.72, r * 0.85, (0.0, (230, 252, 255, 220)), (1.0, (80, 175, 250, 0))))
    p.drawEllipse(QPointF(cx, cy + r * 0.65), r * 0.9, r * 0.7)

    # Luminous white geodesic network arcs & glowing vertex nodes
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor(225, 246, 255, 195), 0.95 if not sm else 1.2))
    for rx, ry, ang in ((r * 1.05, r * 0.42, -24), (r * 1.05, r * 0.48, 32), (r * 0.52, r * 1.05, 12)):
        p.save()
        p.translate(cx, cy)
        p.rotate(ang)
        p.drawEllipse(QPointF(0, 0), rx, ry)
        p.restore()
    if not sm:
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 235))
        for nx, ny in ((cx - r * 0.35, cy - r * 0.12), (cx + r * 0.28, cy + r * 0.18), (cx - r * 0.08, cy + r * 0.42), (cx + r * 0.42, cy - r * 0.28)):
            p.drawEllipse(QPointF(nx, ny), 1.15, 1.15)

    # Crisp top glass specular crescent
    lens_r = QRectF(cx - r * 0.66, cy - r + 0.9, r * 1.32, r * 0.74)
    p.setBrush(vgrad(lens_r.top(), lens_r.bottom(), (0.0, (255, 255, 255, 220)), (1.0, (255, 255, 255, 0)), x0=cx, x1=cx))
    p.drawEllipse(lens_r)
    p.restore()

    p.setPen(QPen(c("#0d2b6b"), 1.0))
    p.setBrush(Qt.NoBrush)
    p.drawPath(sph)


def aqua_plugin_cube(p, sm=False, accent="blue"):
    """Figure 11-13: 10.2 isometric white/silver 3D plug-in / package cube."""
    floor_shadow(p, 16.0, 28.4, 11.2, 2.3, 72)
    top = poly((16.0, 4.2), (27.4, 9.2), (16.0, 14.2), (4.6, 9.2))
    left = poly((4.6, 9.2), (16.0, 14.2), (16.0, 27.4), (4.6, 22.2))
    right = poly((16.0, 14.2), (27.4, 9.2), (27.4, 22.2), (16.0, 27.4))

    p.setPen(QPen(c("#858b98"), 0.95, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(4.2, 14.2, (0.0, "#ffffff"), (1.0, "#eef1f7")))
    p.drawPath(top)
    p.setBrush(vgrad(9.2, 27.4, (0.0, "#f4f6fa"), (1.0, "#d5dae4")))
    p.drawPath(left)
    p.setBrush(vgrad(9.2, 27.4, (0.0, "#e4e8f0"), (1.0, "#bec5d2")))
    p.drawPath(right)

    # 10.2 Aqua pinwheel rosette on right face (sampled from ch11-209-016.png)
    cx, cy = 21.7, 18.4
    petals = QPainterPath()
    for i in range(8):
        ang = i * 45.0
        pet = ellipse(cx, cy - 3.0, 1.25, 2.8)
        t = QTransform().translate(cx, cy).rotate(ang).translate(-cx, -cy)
        petals = U(petals, t.map(pet))
    paint_gel_shape(p, petals, cy - 5.5, cy + 5.5, accent, shadow=False)
    p.setPen(QPen(c("#1a2230"), 0.7))
    p.setBrush(c("#ffffff"))
    p.drawEllipse(QPointF(cx, cy), 1.3, 1.3)


# ---- Shared Classic 10.2 Objects ----

def paint_magnifier(p, cx=13.0, cy=12.4, r=7.8, scale_f=1.0, ox=0.0, oy=0.0, shadow=True):
    p.save()
    p.translate(ox, oy)
    p.scale(scale_f, scale_f)
    if shadow:
        floor_shadow(p, cx + 4.0, cy + 15.2, 9.0, 2.0, 58)
    p.save()
    p.translate(cx, cy)
    p.rotate(45)
    p.setPen(QPen(c("#585b62"), 0.8))
    p.setBrush(vgrad(-2.0, 2.0, (0.0, "#8e929b"), (0.45, "#ffffff"), (1.0, "#6e727a"), x0=0, x1=0))
    p.drawRoundedRect(QRectF(r - 0.4, -2.0, 3.2, 4.0), 0.7, 0.7)
    h_rect = QRectF(r + 2.2, -2.35, 11.4, 4.7)
    p.setPen(QPen(c("#08080a"), 0.9))
    p.setBrush(vgrad(-2.35, 2.35, (0.0, "#101114"), (0.28, "#7b7f88"), (0.52, "#1c1d22"), (1.0, "#050507"), x0=0, x1=0))
    p.drawRoundedRect(h_rect, 1.8, 1.8)
    p.restore()

    bezel = circ(cx, cy, r + 1.5)
    inner = circ(cx, cy, r - 1.1)
    ring_p = S(bezel, inner)
    p.setPen(Qt.NoPen)
    p.setBrush(rgrad(cx + 1.5, cy + 2.0, r * 1.15, (0.0, (255, 255, 255, 235)), (0.65, (214, 238, 255, 185)), (1.0, (168, 208, 242, 200))))
    p.drawPath(inner)
    lens_arc = QRectF(cx - r * 0.68, cy - r * 0.72, r * 1.25, r * 0.82)
    p.setBrush(vgrad(lens_arc.top(), lens_arc.bottom(), (0.0, (255, 255, 255, 235)), (1.0, (255, 255, 255, 0)), x0=cx, x1=cx))
    p.drawEllipse(lens_arc)
    p.setBrush(vgrad(cy - r - 1.5, cy + r + 1.5, (0.0, "#f8f9fb"), (0.35, "#c4c8d0"), (0.55, "#7c8088"), (0.82, "#e4e7ec"), (1.0, "#9498a0"), x0=cx - r, x1=cx + r))
    p.setPen(QPen(c("#52555c"), 0.95))
    p.drawPath(ring_p)
    p.restore()


def paint_pencil(p, cx=16.5, cy=15.8, length=23.0, width=4.8, angle_deg=32.0, shadow=True, chrome=False):
    if shadow:
        floor_shadow(p, cx - 2.5, cy + 11.2, 8.5, 2.0, 62)
    p.save()
    p.translate(cx, cy)
    p.rotate(angle_deg)
    hw = width / 2.0
    top = -length / 2.0
    eraser_h = 3.2
    ferrule_h = 2.8
    cone_h = 5.0
    shaft_top = top + eraser_h + ferrule_h
    shaft_bot = top + length - cone_h

    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 48))
    p.drawRoundedRect(QRectF(-hw + 1.0, top + 1.2, width, length - cone_h * 0.4), 1.4, 1.4)

    if chrome:
        # 10.2 TextEdit brushed-silver ballpoint pen (ch11-205-005.png)
        p.setPen(QPen(c("#484c56"), 0.85))
        p.setBrush(hgrad(-hw, hw, (0.0, "#8c929e"), (0.38, "#ffffff"), (0.68, "#c2c8d4"), (1.0, "#626874"), y0=0, y1=0))
        p.drawRoundedRect(QRectF(-hw, top, width, length - cone_h), 1.6, 1.6)
        # Pocket clip + dark grip band
        p.setBrush(c("#2a2e36"))
        p.drawRect(QRectF(-hw, shaft_bot - 5.2, width, 4.2))
        p.setPen(QPen(c("#ffffff"), 1.0))
        p.drawLine(QPointF(hw + 0.6, top + 2.5), QPointF(hw + 0.6, top + 10.5))
        cone = poly((-hw, shaft_bot), (hw, shaft_bot), (0.0, shaft_bot + cone_h))
        p.setPen(QPen(c("#484c56"), 0.8))
        p.setBrush(hgrad(-hw, hw, (0.0, "#9aa0ac"), (0.45, "#ffffff"), (1.0, "#686e7a"), y0=0, y1=0))
        p.drawPath(cone)
    else:
        p.setPen(QPen(c("#6e1814"), 0.85))
        p.setBrush(hgrad(-hw, hw, (0.0, "#ff9a94"), (0.45, "#e24d46"), (1.0, "#941d18"), y0=0, y1=0))
        p.drawRoundedRect(QRectF(-hw, top, width, eraser_h + 1.0), 1.4, 1.4)
        p.setPen(QPen(c("#5c6068"), 0.85))
        p.setBrush(hgrad(-hw, hw, (0.0, "#9ca0a8"), (0.35, "#ffffff"), (0.7, "#b8bcc4"), (1.0, "#70747c"), y0=0, y1=0))
        p.drawRect(QRectF(-hw, top + eraser_h, width, ferrule_h))
        p.setPen(Qt.NoPen)
        sh_h = shaft_bot - shaft_top
        p.fillRect(QRectF(-hw, shaft_top, width * 0.34, sh_h), c("#fff0a6"))
        p.fillRect(QRectF(-hw + width * 0.34, shaft_top, width * 0.34, sh_h), c("#f0be56"))
        p.fillRect(QRectF(-hw + width * 0.68, shaft_top, width * 0.32, sh_h), c("#b57e2c"))
        p.setPen(QPen(c("#6e4b18"), 0.85))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(-hw, shaft_top, width, sh_h))
        cone = poly((-hw, shaft_bot), (hw, shaft_bot), (0.0, shaft_bot + cone_h))
        p.setPen(QPen(c("#6e4b18"), 0.85))
        p.setBrush(hgrad(-hw, hw, (0.0, "#f7e2c2"), (0.6, "#dfb686"), (1.0, "#a87e52"), y0=0, y1=0))
        p.drawPath(cone)

    tip = poly((-hw * 0.36, shaft_bot + cone_h * 0.64), (hw * 0.36, shaft_bot + cone_h * 0.64), (0.0, shaft_bot + cone_h))
    p.setPen(Qt.NoPen)
    p.setBrush(c("#201e1c"))
    p.drawPath(tip)
    p.restore()


def paint_heart_path(cx=16.0, cy=15.8, s=11.4):
    hp = QPainterPath()
    hp.moveTo(cx, cy + s * 0.88)
    hp.cubicTo(cx - s * 1.18, cy + s * 0.16, cx - s * 1.15, cy - s * 0.86, cx - s * 0.50, cy - s * 0.86)
    hp.cubicTo(cx - s * 0.16, cy - s * 0.86, cx, cy - s * 0.52, cx, cy - s * 0.36)
    hp.cubicTo(cx, cy - s * 0.52, cx + s * 0.16, cy - s * 0.86, cx + s * 0.50, cy - s * 0.86)
    hp.cubicTo(cx + s * 1.15, cy - s * 0.86, cx + s * 1.18, cy + s * 0.16, cx, cy + s * 0.88)
    hp.closeSubpath()
    return hp


def paint_favorites_heart(p, cx=16.0, cy=16.0, s=11.4, shadow=True):
    if shadow:
        floor_shadow(p, cx, cy + s * 0.92, s * 0.72, 2.2, 68)
    hp = paint_heart_path(cx, cy, s)
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(cy - s * 0.86, cy + s * 0.88, (0.0, "#ff9c94"), (0.32, "#f02c20"), (0.72, "#c41008"), (1.0, "#7d0602"), x0=cx, x1=cx))
    p.drawPath(hp)
    p.setClipPath(hp)
    for lx in (cx - s * 0.46, cx + s * 0.46):
        p.setBrush(rgrad(lx, cy - s * 0.52, s * 0.42, (0.0, (255, 255, 255, 220)), (1.0, (255, 255, 255, 0))))
        p.drawEllipse(QPointF(lx, cy - s * 0.52), s * 0.44, s * 0.32)
    p.restore()
    p.setPen(QPen(c("#680804"), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(hp)


def paint_brass_lock(p, unlocked=False, cx=16.0, cy=16.0, scale_f=1.0, shadow=True):
    p.save()
    p.translate(cx, cy)
    p.scale(scale_f, scale_f)
    p.translate(-16.0, -16.0)
    if shadow:
        floor_shadow(p, 14.5 if unlocked else 16.0, 28.4, 9.6, 2.1, 70)
    bx = 5.6 if unlocked else 7.4
    sh = QPainterPath()
    if not unlocked:
        sh.moveTo(10.8, 14.5)
        sh.lineTo(10.8, 9.5)
        sh.arcTo(QRectF(10.8, 4.2, 10.4, 10.4), 180, -180)
        sh.lineTo(21.2, 14.5)
    else:
        sh.moveTo(19.4, 14.5)
        sh.lineTo(19.4, 9.2)
        sh.arcTo(QRectF(19.4, 4.2, 9.2, 9.6), 180, -180)
        sh.lineTo(28.6, 11.6)
    p.setPen(QPen(c("#4e525c"), 3.4, Qt.SolidLine, Qt.RoundCap))
    p.drawPath(sh)
    p.setPen(QPen(c("#eef2f8"), 1.5, Qt.SolidLine, Qt.RoundCap))
    p.drawPath(sh)

    body = QRectF(bx, 13.5, 17.2, 13.8)
    p.setPen(QPen(c("#6e4b10"), 1.0))
    p.setBrush(hgrad(bx, bx + 17.2, (0.0, "#fce494"), (0.45, "#e6b43c"), (0.8, "#b8821c"), (1.0, "#dfaa34")))
    p.drawRoundedRect(body, 2.2, 2.2)
    kx = bx + 8.6
    kh = U(circ(kx, 19.2, 1.9), poly((kx - 1.0, 19.8), (kx + 1.0, 19.8), (kx + 1.4, 24.2), (kx - 1.4, 24.2)))
    p.setPen(Qt.NoPen)
    p.setBrush(c("#3a2608"))
    p.drawPath(kh)
    p.restore()


def paint_mesh_trash(p, full=False, sm=False):
    """10.2 gleaming chrome-rimmed wire-mesh wastebasket (ch11-202-002.png rightmost)."""
    floor_shadow(p, 16.0, 28.4, 10.2, 2.3, 74)
    basket = QPainterPath()
    basket.moveTo(7.2, 7.6)
    basket.lineTo(24.8, 7.6)
    basket.lineTo(22.2, 26.8)
    basket.quadTo(16.0, 28.2, 9.8, 26.8)
    basket.closeSubpath()

    # Back interior rim
    p.setPen(QPen(c("#585d66"), 0.9))
    p.setBrush(vgrad(5.8, 9.2, (0.0, "#7c828e"), (1.0, "#b8bec8")))
    p.drawEllipse(QRectF(7.2, 5.8, 17.6, 3.6))

    if full:
        # Overflowing crumpled white paper wads peeking above & inside mesh
        for px, py, pr, col in (
            (12.2, 7.2, 3.8, "#ffffff"),
            (17.8, 6.8, 4.1, "#f2f5fb"),
            (20.6, 8.4, 3.2, "#e4e9f2"),
            (14.8, 8.6, 3.6, "#ffffff"),
        ):
            p.setPen(QPen(c("#9aa2b0"), 0.7))
            p.setBrush(c(col))
            p.drawEllipse(QPointF(px, py), pr, pr * 0.82)

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(hgrad(7.2, 24.8, (0.0, "#cfd4de"), (0.35, "#eef1f7"), (0.72, "#a8aebc"), (1.0, "#7c828e")))
    p.setOpacity(0.86)
    p.drawPath(basket)
    p.setOpacity(1.0)
    p.setClipPath(basket)

    if full:
        for px, py, pr in ((13.2, 13.5, 4.5), (18.8, 15.0, 4.3), (15.2, 20.5, 4.8)):
            p.setBrush(c("#ffffff"))
            p.drawEllipse(QPointF(px, py), pr, pr * 0.8)

    if not sm:
        p.setPen(QPen(QColor(42, 46, 54, 135), 0.8))
        for k in range(-12, 26, 3):
            p.drawLine(QPointF(6 + k, 7.2), QPointF(16 + k, 28.2))
            p.drawLine(QPointF(26 - k, 7.2), QPointF(16 - k, 28.2))
    p.restore()

    p.setPen(QPen(c("#4e525b"), 1.0))
    p.setBrush(Qt.NoBrush)
    p.drawPath(basket)

    # Chrome top & bottom bands
    rim_ring = S(ellipse(16.0, 7.5, 9.2, 2.0), ellipse(16.0, 7.5, 7.6, 1.2))
    p.setPen(QPen(c("#484c54"), 0.85))
    p.setBrush(hgrad(6.8, 25.2, (0.0, "#9ca2ae"), (0.4, "#ffffff"), (0.8, "#b8bec8"), (1.0, "#787e8a")))
    p.drawPath(rim_ring)
    bot_band = QPainterPath()
    bot_band.moveTo(9.8, 25.2)
    bot_band.quadTo(16.0, 26.6, 22.2, 25.2)
    bot_band.lineTo(22.0, 26.9)
    bot_band.quadTo(16.0, 28.3, 10.0, 26.9)
    bot_band.closeSubpath()
    p.drawPath(bot_band)


def paint_music_notes(p, cx=16.0, cy=16.0, scale_f=1.0, kind="purple"):
    """Figure 11-4: 10.2 iTunes 3D glossy beamed eighth notes."""
    p.save()
    p.translate(cx, cy)
    p.scale(scale_f, scale_f)
    p.translate(-16.0, -16.0)
    heads = U(
        QTransform().translate(10.2, 21.6).rotate(-22).map(ellipse(0, 0, 3.4, 2.4)),
        QTransform().translate(20.4, 19.6).rotate(-22).map(ellipse(0, 0, 3.4, 2.4)),
    )
    stems = U(
        rr(12.2, 7.8, 2.1, 13.5, 0.6),
        rr(22.4, 5.8, 2.1, 13.5, 0.6),
        poly((12.2, 7.6), (24.5, 5.4), (24.5, 9.0), (12.2, 11.2)),
    )
    paint_gel_shape(p, U(heads, stems), 5.4, 24.0, kind)
    p.restore()
