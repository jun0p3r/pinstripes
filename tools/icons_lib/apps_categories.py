# SPDX-License-Identifier: GPL-2.0-or-later
"""Mac OS X 10.2 "Jaguar" Applications (207+), Categories (40+), and Applets (40+) painters."""
import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF, QTransform

from .materials import (
    S,
    U,
    aqua_drive,
    aqua_folder,
    aqua_globe,
    aqua_optical_disc,
    aqua_pinstripe_monitor,
    aqua_plugin_cube,
    aqua_pref_plate,
    aqua_sheet,
    arc_path,
    c,
    circ,
    drop_shadow_path,
    ellipse,
    floor_shadow,
    gear_path,
    glass_disc,
    hgrad,
    line,
    mini_badge_disc,
    paint_brass_lock,
    paint_favorites_heart,
    paint_gel_shape,
    paint_magnifier,
    paint_music_notes,
    paint_pencil,
    plus_path,
    poly,
    polyline,
    rgrad,
    ring,
    rr,
    star_path,
    stroke,
    text_path,
    vgrad,
)
from .places_devices import paint_person_bust, paint_safari_compass


def paint_finder_smiley(p, sm=False):
    """Exact 10.2 Finder two-tone blue smiley square sampled from ch11-202-002.png."""
    rect = QRectF(3.6, 4.2, 24.8, 23.6)
    card = rr(rect.x(), rect.y(), rect.width(), rect.height(), 2.2)
    drop_shadow_path(p, card, 0.0, 1.4, 65)

    p.save()
    p.setClipPath(card)
    # Left cornflower/cobalt half (#9cbdff -> #5272d9 -> #3052b6 -> #4163c5)
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(4.2, 27.8, (0.0, "#9cbdff"), (0.42, "#5272d9"), (0.78, "#3052b6"), (1.0, "#4868cd")))
    p.drawRect(rect)

    # Right periwinkle/sky half bounded by the curved nose-chin dividing line
    div_x = QPainterPath()
    div_x.moveTo(18.6, 3.6)
    div_x.cubicTo(16.2, 8.8, 14.8, 13.4, 14.2, 16.8)
    div_x.lineTo(17.4, 16.8)
    div_x.cubicTo(17.2, 21.0, 18.0, 24.8, 19.2, 28.4)
    div_x.lineTo(30.0, 28.4)
    div_x.lineTo(30.0, 3.6)
    div_x.closeSubpath()
    p.setBrush(vgrad(4.2, 27.8, (0.0, "#dceaff"), (0.45, "#b0bff8"), (0.82, "#95a6de"), (1.0, "#a4b4ec")))
    p.drawPath(div_x)

    # Top glass specular bevel
    p.fillRect(QRectF(3.6, 4.2, 24.8, 1.6), QColor(255, 255, 255, 135))
    p.restore()

    p.setPen(QPen(c("#5c6682"), 1.05))
    p.setBrush(Qt.NoBrush)
    p.drawPath(card)

    # Crisp black Finder face strokes: eyes, nose divider, and wide smile
    p.setPen(Qt.NoPen)
    p.setBrush(c("#10131c"))
    p.drawRoundedRect(QRectF(9.2, 9.6, 2.0, 3.2), 0.5, 0.5)
    p.drawRoundedRect(QRectF(20.6, 9.6, 2.0, 3.2), 0.5, 0.5)

    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(c("#10131c"), 1.65, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    nose = QPainterPath()
    nose.moveTo(18.4, 4.6)
    nose.cubicTo(16.1, 9.2, 14.8, 13.4, 14.2, 16.8)
    nose.lineTo(17.2, 16.8)
    nose.cubicTo(17.1, 21.0, 17.9, 24.5, 19.0, 27.4)
    p.drawPath(nose)

    smile = QPainterPath()
    smile.moveTo(8.0, 19.2)
    smile.cubicTo(11.8, 23.4, 20.2, 23.4, 24.0, 19.2)
    p.drawPath(smile)


def paint_applications_a(p, sm=False):
    """10.2 Finder 'Applications' A-frame built from ruler, yellow pencil & red paintbrush (ch11-212-021.png)."""
    floor_shadow(p, 16.0, 28.2, 12.2, 2.2, 70)
    # Horizontal wooden ruler crossbar
    p.setPen(QPen(c("#6e4b18"), 0.9))
    p.setBrush(vgrad(16.5, 20.5, (0.0, "#f8dca0"), (1.0, "#cf9c52")))
    p.drawRoundedRect(QRectF(4.4, 16.8, 23.2, 3.8), 0.7, 0.7)
    if not sm:
        p.setPen(QPen(c("#6e4b18"), 0.65))
        for rx in range(7, 26, 3):
            p.drawLine(QPointF(rx, 16.9), QPointF(rx, 18.4))
    # Left leg: yellow pencil tilted +24 deg
    paint_pencil(p, 11.8, 16.2, 23.5, 4.0, 24.0, shadow=False, chrome=False)
    # Right leg: crimson artist paintbrush tilted -24 deg
    p.save()
    p.translate(20.2, 16.4)
    p.rotate(-24.0)
    p.setPen(QPen(c("#6e140c"), 0.85))
    p.setBrush(hgrad(-1.9, 1.9, (0.0, "#ff9288"), (0.5, "#d8281c"), (1.0, "#8c1008"), y0=0, y1=0))
    p.drawRoundedRect(QRectF(-1.8, -7.5, 3.6, 18.8), 1.2, 1.2)
    p.setPen(QPen(c("#545862"), 0.8))
    p.setBrush(c("#dfe4ee"))
    p.drawRect(QRectF(-1.9, -10.0, 3.8, 2.8))
    bristle = poly((-1.8, -10.0), (1.8, -10.0), (0.0, -14.4), round_=0.4)
    p.setPen(QPen(c("#4e3418"), 0.75))
    p.setBrush(c("#b87e42"))
    p.drawPath(bristle)
    p.restore()


def paint_blueprint_dev(p, sm=False, hammer=False):
    """Figure 11-3 top-right: angled cyanotype architectural blueprint + steel drafting compass."""
    floor_shadow(p, 16.0, 28.4, 12.2, 2.2, 70)
    p.save()
    p.translate(15.2, 15.8)
    p.rotate(-11)
    bp = QRectF(-10.2, -10.2, 20.4, 20.4)
    p.setPen(QPen(c("#8c94a4"), 0.9))
    p.setBrush(c("#ffffff"))
    p.drawRect(bp.adjusted(-1.2, -1.2, 1.2, 1.2))
    p.setPen(QPen(c("#1b4394"), 0.8))
    p.setBrush(vgrad(-10.2, 10.2, (0.0, "#4676d8"), (1.0, "#244eb0")))
    p.drawRect(bp)
    if not sm:
        p.setPen(QPen(QColor(220, 238, 255, 150), 0.65))
        p.drawRect(QRectF(-7.6, -7.4, 7.2, 6.2))
        p.drawEllipse(QPointF(1.2, 1.8), 5.6, 5.6)
        p.drawLine(QPointF(-8.5, 1.8), QPointF(8.5, 1.8))
        p.drawLine(QPointF(1.2, -8.5), QPointF(1.2, 8.5))
    p.restore()

    if hammer:
        # Xcode/Project Builder hammer over blueprint
        p.save()
        p.translate(19.0, 17.2)
        p.rotate(-38)
        p.setPen(QPen(c("#5c3610"), 0.85))
        p.setBrush(hgrad(-1.8, 1.8, (0.0, "#e8b066"), (0.5, "#be7d32"), (1.0, "#7c4b16"), y0=0, y1=0))
        p.drawRoundedRect(QRectF(-1.8, -5.0, 3.6, 16.5), 1.1, 1.1)
        head = poly((-6.2, -8.4), (5.2, -8.4), (5.2, -4.4), (-3.4, -4.4), (-7.0, -6.0), round_=0.6)
        p.setPen(QPen(c("#484c54"), 0.85))
        p.setBrush(vgrad(-8.4, -4.4, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#7f8692")))
        p.drawPath(head)
        p.restore()
    else:
        # Steel drafting compass (ch11-203-003.png top-right)
        comp = U(
            line(21.6, 8.4, 14.2, 23.6, 2.0),
            line(21.6, 8.4, 25.8, 25.4, 2.0),
            ring(21.6, 7.6, 2.0, 1.4),
            line(16.2, 16.8, 24.4, 17.8, 1.1),
        )
        p.setPen(QPen(c("#444852"), 0.85))
        p.setBrush(vgrad(6.0, 25.5, (0.0, "#ffffff"), (0.5, "#cfd5e0"), (1.0, "#828896")))
        p.drawPath(comp)


def paint_preview_photos(p, sm=False, camera_badge=False):
    """Figure 11-6: stacked angled white-bordered photographs + 10.2 black/silver loupe."""
    floor_shadow(p, 16.5, 28.2, 12.2, 2.2, 70)
    for ang, ox, oy, sky in ((-8, 14.5, 13.5, ("#cf9e64", "#f0d2a8")), (-26, 14.0, 15.6, ("#3c88e6", "#9ad6ff"))):
        p.save()
        p.translate(ox, oy)
        p.rotate(ang)
        card = QRectF(-9.2, -7.8, 18.4, 15.6)
        p.setPen(QPen(c("#848a98"), 0.9))
        p.setBrush(c("#ffffff"))
        p.drawRect(card)
        inner = card.adjusted(1.7, 1.7, -1.7, -2.4)
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(inner.top(), inner.bottom(), (0.0, sky[0]), (1.0, sky[1])))
        p.drawRect(inner)
        # Mountain & sun inside front snapshot
        p.setBrush(c("#2f5d3a" if ang == -26 else "#7c5830"))
        p.drawPolygon(QPolygonF([QPointF(inner.left(), inner.bottom()), QPointF(inner.left() + 5.5, inner.top() + 4.2), QPointF(inner.right(), inner.bottom())]))
        p.restore()

    if camera_badge:
        glass_disc(p, 22.8, 21.0, 5.8, "blue", shadow=False)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(22.8, 21.0), 2.4, 2.4)
    else:
        # 10.2 photographer's black/glass loupe resting on bottom-right corner
        p.setPen(QPen(c("#8c94a4"), 0.85))
        p.setBrush(QColor(225, 240, 255, 165))
        p.drawEllipse(QPointF(22.2, 21.4), 5.6, 5.6)
        p.setPen(QPen(c("#0e1014"), 2.2))
        p.setBrush(rgrad(21.4, 18.6, 5.0, (0.0, (255, 255, 255, 235)), (0.7, (190, 225, 255, 180)), (1.0, (90, 140, 195, 210))))
        p.drawEllipse(QPointF(21.8, 19.2), 4.6, 4.6)


def paint_textedit_pad(p, sm=False):
    """Figure 11-5: 10.2 TextEdit angled ruled notepad on yellow legal pad + chrome pen."""
    floor_shadow(p, 16.0, 28.4, 12.2, 2.2, 70)
    # Canary-yellow backing sheet
    p.save()
    p.translate(13.8, 16.4)
    p.rotate(-22)
    p.setPen(QPen(c("#a88e28"), 0.85))
    p.setBrush(vgrad(-10.0, 10.0, (0.0, "#fff494"), (1.0, "#ebd054")))
    p.drawRect(QRectF(-8.6, -10.2, 17.2, 20.4))
    p.restore()
    # Front white ruled letter sheet
    p.save()
    p.translate(14.8, 15.2)
    p.rotate(-10)
    sh = QRectF(-9.2, -10.8, 18.4, 21.6)
    p.setPen(QPen(c("#848b98"), 0.9))
    p.setBrush(vgrad(-10.8, 10.8, (0.0, "#ffffff"), (1.0, "#eceff6")))
    p.drawRect(sh)
    if not sm:
        p.setPen(Qt.NoPen)
        p.setBrush(c("#4e5666"))
        for i, lw in enumerate((6.0, 13.2, 13.6, 12.8, 13.4, 11.2, 5.4)):
            p.drawRect(QRectF(-7.0, -7.8 + i * 2.2, lw, 0.95))
    p.restore()
    paint_pencil(p, 22.4, 17.4, 21.0, 4.0, 28.0, shadow=False, chrome=True)


def paint_mail_stamp_app(p, sm=False):
    """Figure 11-3 top-third: angled scalloped sky-blue Mail stamp + soaring hawk + postmark."""
    floor_shadow(p, 16.0, 28.4, 12.2, 2.2, 70)
    p.save()
    p.translate(16.2, 15.2)
    p.rotate(-10)
    card = QPainterPath()
    card.addRect(QRectF(-10.8, -10.8, 21.6, 21.6))
    holes = QPainterPath()
    for i in range(7):
        v = -10.8 + i * 3.6
        holes.addEllipse(QPointF(v, -10.8), 1.05, 1.05)
        holes.addEllipse(QPointF(v, 10.8), 1.05, 1.05)
        holes.addEllipse(QPointF(-10.8, v), 1.05, 1.05)
        holes.addEllipse(QPointF(10.8, v), 1.05, 1.05)
    st_p = S(card, holes)
    p.setPen(QPen(c("#8890a0"), 0.85))
    p.setBrush(c("#ffffff"))
    p.drawPath(st_p)
    ins = QRectF(-8.2, -8.2, 16.4, 16.4)
    p.setPen(QPen(c("#4668a6"), 0.8))
    p.setBrush(vgrad(-8.2, 8.2, (0.0, "#9cc2fa"), (1.0, "#5c88e0")))
    p.drawRect(ins)
    # Soaring golden-brown eagle silhouette with swept wings inside stamp (ch11-203-003.png)
    hawk = QPainterPath()
    hawk.moveTo(-1.0, -7.0)
    hawk.cubicTo(1.8, -4.6, 2.8, -2.0, 2.2, 0.2)
    hawk.lineTo(4.2, -0.2)
    hawk.lineTo(2.4, 1.4)
    hawk.cubicTo(4.0, 3.2, 5.4, 5.0, 5.8, 6.4)
    hawk.cubicTo(3.0, 5.2, 1.0, 3.6, -0.2, 1.8)
    hawk.lineTo(-2.2, 3.8)
    hawk.lineTo(-2.8, 1.8)
    hawk.cubicTo(-2.2, -1.2, -2.4, -4.2, -1.0, -7.0)
    hawk.closeSubpath()
    p.setPen(QPen(c("#3a220c"), 0.65))
    p.setBrush(vgrad(-7.0, 6.4, (0.0, "#b87c40"), (0.5, "#78481c"), (1.0, "#3e220a")))
    p.drawPath(hawk)
    p.restore()
    if not sm:
        # Circular postmark cancellation rings at bottom-left
        p.setPen(QPen(QColor(35, 42, 55, 145), 0.8))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(9.8, 21.2), 5.4, 5.4)
        p.drawEllipse(QPointF(9.8, 21.2), 3.6, 3.6)


def paint_painter_palette(p, sm=False):
    """10.2 wooden artist palette with glossy Aqua paint dabs + natural paintbrush."""
    floor_shadow(p, 16.0, 28.4, 12.4, 2.2, 70)
    pal = S(ellipse(15.4, 16.4, 11.8, 9.6), circ(9.6, 18.8, 2.3), circ(6.2, 13.2, 2.6))
    p.setPen(QPen(c("#684218"), 1.0))
    p.setBrush(vgrad(6.8, 26.0, (0.0, "#f5cf96"), (0.55, "#d49a56"), (1.0, "#9e6828")))
    p.drawPath(pal)
    for px, py, kind in ((12.2, 10.8, "red"), (17.8, 10.2, "amber"), (22.0, 13.8, "green"), (21.2, 19.2, "blue")):
        glass_disc(p, px, py, 2.2, kind, shadow=False)
    # Angled artist brush
    p.save()
    p.translate(19.5, 16.0)
    p.rotate(36)
    p.setPen(QPen(c("#4e2c10"), 0.8))
    p.setBrush(c("#8c4e20"))
    p.drawRoundedRect(QRectF(-1.4, -4.5, 2.8, 16.0), 1.0, 1.0)
    p.setBrush(c("#dfe4ee"))
    p.drawRect(QRectF(-1.5, -7.2, 3.0, 2.8))
    p.setBrush(c("#2674e6"))
    p.drawPath(poly((-1.6, -7.2), (1.6, -7.2), (0.0, -11.6), round_=0.4))
    p.restore()


def paint_chess_knight(p, sm=False):
    """Figure 11-8 right: 10.2 Chess carved wooden knight on a 2x2 diamond board."""
    floor_shadow(p, 16.0, 28.4, 12.6, 2.3, 72)
    # 2x2 perspective diamond chessboard
    board = poly((16.0, 17.6), (29.2, 22.8), (16.0, 28.0), (2.8, 22.8))
    p.setPen(QPen(c("#383c46"), 1.0))
    p.setBrush(c("#e8ecf4"))
    p.drawPath(board)
    p.setPen(Qt.NoPen)
    p.setBrush(c("#444a56"))
    p.drawPath(poly((16.0, 17.6), (22.6, 20.2), (16.0, 22.8), (9.4, 20.2)))
    p.drawPath(poly((16.0, 22.8), (22.6, 25.4), (16.0, 28.0), (9.4, 25.4)))
    # Carved honey-oak knight piece
    knight = QPainterPath()
    knight.moveTo(11.4, 22.2)
    knight.cubicTo(11.0, 16.2, 13.8, 12.8, 12.2, 9.8)
    knight.lineTo(9.4, 11.2)
    knight.lineTo(8.8, 9.2)
    knight.lineTo(13.8, 5.2)
    knight.lineTo(15.4, 3.8)
    knight.lineTo(16.8, 5.4)
    knight.cubicTo(20.6, 7.6, 21.8, 13.6, 20.4, 22.2)
    knight.closeSubpath()
    p.setPen(QPen(c("#563410"), 0.95))
    p.setBrush(hgrad(9.0, 21.5, (0.0, "#f8dca0"), (0.45, "#cf9448"), (1.0, "#7c4b16")))
    p.drawPath(knight)
    p.setBrush(vgrad(21.4, 25.0, (0.0, "#f0c87c"), (1.0, "#8c561c")))
    p.drawEllipse(QRectF(10.6, 21.2, 10.8, 3.6))


def paint_ichat_bubbles(p, sm=False, tint="blue"):
    """10.2 iChat translucent glossy Aqua speech bubbles."""
    floor_shadow(p, 16.0, 28.2, 12.0, 2.2, 68)
    back_b = U(ellipse(19.6, 13.2, 8.6, 6.4), poly((23.0, 17.8), (27.2, 21.8), (20.2, 18.8)))
    paint_gel_shape(p, back_b, 6.8, 21.8, "clear")
    front_b = U(ellipse(13.0, 17.6, 9.4, 7.0), poly((8.8, 22.6), (4.6, 26.8), (12.6, 23.8)))
    paint_gel_shape(p, front_b, 10.6, 26.8, tint)


def build_apps_and_categories_painters():
    apps = []
    categories = []
    applets = []

    def ap(name, aliases=""):
        def deco(fn):
            apps.append((name, aliases.split(), fn))
            return fn
        return deco

    def ct(name, aliases=""):
        def deco(fn):
            categories.append((name, aliases.split(), fn))
            return fn
        return deco

    def pl_app(name, aliases=""):
        def deco(fn):
            applets.append((name, aliases.split(), fn))
            return fn
        return deco

    # ---- 1. Core 10.2 User Applications ----

    @ap("system-file-manager", "org.kde.dolphin dolphin knetattach")
    def _(p, sm):
        paint_finder_smiley(p, sm)

    @ap("accessories-text-editor", "kate kwrite org.kde.kate org.kde.kwrite seabass kjournal korg-journal")
    def _(p, sm):
        paint_textedit_pad(p, sm)

    @ap("gwenview", "org.kde.gwenview kuickshow showfoto org.kde.koko")
    def _(p, sm):
        paint_preview_photos(p, sm, camera_badge=False)

    @ap("digikam", "kamoso")
    def _(p, sm):
        paint_preview_photos(p, sm, camera_badge=True)

    @ap("okular", "org.kde.okular acroread graphics-viewer-document")
    def _(p, sm):
        aqua_sheet(p, sm, x=5.5, y=2.5, w=20.0, h=25.5, label="PDF")
        # Stylized crimson Acrobat/PDF ribbon loop + mini glass loupe
        loop = stroke(poly((10.5, 18.8), (15.2, 9.2), (19.8, 17.8), round_=1.2), 1.7)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#cf1e14"))
        p.drawPath(loop)
        paint_magnifier(p, 13.0, 12.4, 7.2, scale_f=0.62, ox=10.8, oy=9.6, shadow=False)

    @ap("kmail", "kmail2 internet-mail org.kde.kmail2 kontact kontact-import-wizard")
    def _(p, sm):
        paint_mail_stamp_app(p, sm)

    @ap("internet-web-browser", "konqueror firefox chromium-browser")
    def _(p, sm):
        paint_safari_compass(p, 16.0, 15.8, 12.0, sm=sm)

    @ap("kaddressbook", "office-address-book org.kde.kaddressbook")
    def _(p, sm):
        # 10.2 Address Book leather-and-Aqua '@' volume with side index tabs
        floor_shadow(p, 16.0, 28.4, 10.8, 2.2, 72)
        for ty, col in ((7.2, "#e85448"), (12.4, "#f0b832"), (17.6, "#4ec042"), (22.4, "#3e86e8")):
            p.setPen(QPen(c("#586070"), 0.75))
            p.setBrush(c(col))
            p.drawRoundedRect(QRectF(23.2, ty, 3.6, 4.2), 0.8, 0.8)
        p.setPen(QPen(c("#4e3218"), 1.0))
        p.setBrush(vgrad(4.2, 27.4, (0.0, "#b8824c"), (0.5, "#8e5c2c"), (1.0, "#643e18")))
        p.drawRoundedRect(QRectF(6.6, 4.2, 18.0, 23.2), 1.8, 1.8)
        p.setBrush(c("#523012"))
        p.drawRect(QRectF(6.6, 4.2, 3.4, 23.2))
        at_p = text_path("@", 17.2, 15.8, px=13.0, bold=True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 248, 235, 235))
        p.drawPath(at_p)

    @ap("office-calendar", "korganizer kalarm korgac korg-todo planner zanshin Charm")
    def _(p, sm):
        # 10.2 iCal angled desk calendar page ('JUL 17')
        floor_shadow(p, 16.0, 28.4, 11.8, 2.2, 72)
        p.save()
        p.translate(16.0, 15.8)
        p.rotate(-8)
        card = rr(-10.4, -11.0, 20.8, 22.0, 2.0)
        p.setPen(QPen(c("#788090"), 1.0))
        p.setBrush(vgrad(-11.0, 11.0, (0.0, "#ffffff"), (1.0, "#e6eaf2")))
        p.drawPath(card)
        p.save()
        p.setClipPath(card)
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(-11.0, -4.2, (0.0, "#f2483c"), (1.0, "#b8180e")))
        p.drawRect(QRectF(-11.0, -11.0, 22.0, 6.8))
        p.restore()
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#ffffff"))
            p.drawPath(text_path("JUL", 0.0, -7.6, px=4.8, bold=True))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#1a1d24"))
        p.drawPath(text_path("17", 0.0, 2.8, px=11.5, bold=True))
        p.restore()

    @ap("knotes", "basket braindump ktip semn")
    def _(p, sm):
        # Figure 11-7: 10.2 Stickies layered pastel yellow notes
        floor_shadow(p, 16.0, 28.2, 11.8, 2.2, 68)
        for ang, ox, oy, col in ((6, 17.5, 17.2, "#f5de62"), (-12, 14.2, 14.4, "#fff288")):
            p.save()
            p.translate(ox, oy)
            p.rotate(ang)
            p.setPen(QPen(c("#a89228"), 0.9))
            p.setBrush(vgrad(-8.5, 8.5, (0.0, "#fff9b2"), (1.0, col)))
            p.drawRect(QRectF(-8.8, -8.4, 17.6, 16.8))
            if not sm and ang < 0:
                p.setPen(QPen(c("#524614"), 1.0, Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(-6.2, -3.6), QPointF(4.8, -3.6))
                p.drawLine(QPointF(-6.2, 0.2), QPointF(6.2, 0.2))
                p.drawLine(QPointF(-6.2, 4.0), QPointF(2.4, 4.0))
            p.restore()

    @ap("amarok", "juk org.kde.elisa kmix multimedia-volume-control esd org.kde.krecorder")
    def _(p, sm):
        # Figure 11-4: 10.2 iTunes iridescent CD + glossy 3D purple/blue eighth notes
        aqua_optical_disc(p, sm, tint="silver")
        paint_music_notes(p, 17.6, 15.8, 0.88, "purple")

    @ap("dragonplayer", "kaffeine kmplayer vlc")
    def _(p, sm):
        # Figure 11-8 left: 10.2 QuickTime brushed-aluminum player + glossy Aqua blue 'Q'
        floor_shadow(p, 16.0, 28.4, 11.8, 2.2, 72)
        win = QRectF(4.4, 4.2, 23.2, 23.6)
        p.setPen(QPen(c("#525762"), 1.0))
        p.setBrush(vgrad(4.2, 27.8, (0.0, "#f5f7fa"), (0.5, "#cfd4de"), (1.0, "#9ea4b2")))
        p.drawRoundedRect(win, 2.0, 2.0)
        scr = QRectF(6.4, 6.4, 19.2, 15.0)
        p.setPen(QPen(c("#12141a"), 0.9))
        p.setBrush(c("#0e121a"))
        p.drawRect(scr)
        q_shape = U(ring(16.0, 13.8, 4.6, 2.2), line(16.4, 14.4, 20.6, 18.4, 2.2))
        paint_gel_shape(p, q_shape, 8.2, 19.2, "blue", shadow=False)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#585e6a"))
            for bx in (12.5, 16.0, 19.5):
                p.drawEllipse(QPointF(bx, 24.6), 1.25, 1.25)

    @ap("k3b", "")
    def _(p, sm):
        # 10.2 Disc Burner amber-and-black trefoil optical disc
        aqua_optical_disc(p, sm, tint="gold")
        cx, cy = 16.0, 15.6
        blades = QPainterPath()
        for a0 in (60, 180, 300):
            sec = QPainterPath()
            sec.moveTo(cx, cy)
            sec.arcTo(QRectF(cx - 9.2, cy - 9.2, 18.4, 18.4), a0 - 26, 52)
            sec.closeSubpath()
            blades = blades.united(sec)
        blades = S(blades, circ(cx, cy, 4.2))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(24, 22, 18, 210))
        p.drawPath(blades)

    @ap("kdevelop", "kommit okteta lokalize amarok_change_language kivio calligrakexy caligrakexy qelectrotech")
    def _(p, sm):
        paint_blueprint_dev(p, sm, hammer=True)

    @ap("krita", "kolourpaint inkscape inkscape-logo scribus kcolorchooser")
    def _(p, sm):
        paint_painter_palette(p, sm)

    @ap("fontforge", "preferences-desktop-font")
    def _(p, sm):
        # 10.2 Font Book sleek dark/silver bound 'Aa' specimen card
        aqua_sheet(p, sm, x=5.5, y=3.0, w=21.0, h=25.5, label="FONTS")
        aa = text_path("Aa", 15.5, 14.8, px=11.5, bold=True, serif=True)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#1b3668"))
        p.drawPath(aa)

    @ap("calligrawords", "application-sxw kthesaurus accessories-dictionary artikulate kverbos")
    def _(p, sm):
        # 10.2 crimson Oxford dictionary / word-processor volume
        floor_shadow(p, 16.0, 28.4, 10.8, 2.2, 72)
        p.setPen(QPen(c("#5e100a"), 1.0))
        p.setBrush(vgrad(4.0, 27.4, (0.0, "#de3628"), (0.6, "#ad180e"), (1.0, "#780c06")))
        p.drawRoundedRect(QRectF(6.4, 4.2, 19.2, 23.2), 1.8, 1.8)
        p.setBrush(c("#5e0c06"))
        p.drawRect(QRectF(6.4, 4.2, 3.6, 23.2))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#fce8b2"))
        p.drawPath(text_path("Aa", 17.6, 15.4, px=10.5, bold=True, serif=True))

    @ap("calligrasheets", "kchart skrooge calligraplan")
    def _(p, sm):
        aqua_sheet(p, sm, x=5.5, y=2.8, w=21.0, h=25.8, lines=False)
        for i, (bh, kind) in enumerate(((7.5, "red"), (12.5, "green"), (10.0, "blue"))):
            bar = rr(9.2 + i * 4.8, 22.8 - bh, 3.6, bh, 0.7)
            paint_gel_shape(p, bar, 22.8 - bh, 22.8, kind, shadow=False)

    @ap("calligrastage", "")
    def _(p, sm):
        # 10.2 Keynote wooden easel + glowing blue presentation chart slide
        floor_shadow(p, 16.0, 28.5, 11.4, 2.2, 70)
        p.setPen(QPen(c("#5e3c14"), 1.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(16.0, 4.4), QPointF(8.6, 27.6))
        p.drawLine(QPointF(16.0, 4.4), QPointF(23.4, 27.6))
        p.drawLine(QPointF(16.0, 4.4), QPointF(16.0, 27.8))
        board = QRectF(4.6, 6.6, 22.8, 15.2)
        p.setPen(QPen(c("#484e5a"), 1.0))
        p.setBrush(vgrad(6.6, 21.8, (0.0, "#1e5ec8"), (1.0, "#6cc4ff")))
        p.drawRoundedRect(board, 1.4, 1.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(12.2, 14.2), 3.6, 3.6)
        p.drawRect(QRectF(17.6, 11.6, 7.2, 1.6))
        p.drawRect(QRectF(17.6, 15.0, 5.6, 1.6))

    @ap("kformula", "kbruch kig step")
    def _(p, sm):
        # Science / Math: Erlenmeyer glass flask filled with glowing cyan Aqua reagent
        floor_shadow(p, 16.0, 28.4, 10.8, 2.2, 70)
        flask = poly((13.2, 5.4), (18.8, 5.4), (18.8, 11.2), (25.8, 25.4), (24.6, 27.2), (7.4, 27.2), (6.2, 25.4), (13.2, 11.2), round_=0.8)
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(5.4, 27.2, (0.0, "#ffffff"), (1.0, "#dce8f8")))
        p.drawPath(flask)
        p.setClipPath(flask)
        liq = QRectF(5.0, 17.6, 22.0, 10.5)
        p.setBrush(vgrad(17.6, 27.2, (0.0, "#6ae6ff"), (0.5, "#1d8ce0"), (1.0, "#0e4ea8")))
        p.drawRect(liq)
        p.setBrush(QColor(255, 255, 255, 180))
        p.drawEllipse(QRectF(9.6, 16.8, 12.8, 2.2))
        p.restore()
        p.setPen(QPen(c("#586882"), 1.05))
        p.setBrush(Qt.NoBrush)
        p.drawPath(flask)
        p.drawRoundedRect(QRectF(12.2, 4.4, 7.6, 2.0), 0.8, 0.8)

    @ap("kopete", "konversation quassel telepathy-kde org.kde.neochat org.kde.tokodon internet-telephony")
    def _(p, sm):
        paint_ichat_bubbles(p, sm, tint="blue")

    @ap("kopete-offline", "")
    def _(p, sm):
        paint_ichat_bubbles(p, sm, tint="graphite")

    @ap("akregator", "knewsticker kblogger")
    def _(p, sm):
        # Folded broadsheet newspaper + glossy amber RSS badge
        floor_shadow(p, 16.0, 28.2, 12.2, 2.2, 70)
        p.save()
        p.translate(15.2, 16.0)
        p.rotate(-7)
        p.setPen(QPen(c("#7c8290"), 0.95))
        p.setBrush(vgrad(-9.5, 9.5, (0.0, "#ffffff"), (1.0, "#dfe4ee")))
        p.drawRoundedRect(QRectF(-10.6, -9.2, 21.2, 18.4), 1.4, 1.4)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#2e3440"))
            p.drawRect(QRectF(-8.4, -6.8, 16.8, 2.4))
            p.setBrush(c("#5c88e0"))
            p.drawRect(QRectF(-8.4, -2.8, 7.4, 6.4))
            p.setBrush(c("#9aa2b2"))
            for yy in (-2.6, 0.0, 2.6, 5.2):
                p.drawRect(QRectF(0.6 if yy < 4 else -8.4, yy, 7.8 if yy < 4 else 16.8, 1.2))
        p.restore()
        mini_badge_disc(p, 23.6, 21.8, 5.6, "amber", U(circ(21.4, 23.8, 1.0), arc_path(21.2, 24.0, 3.2, 0, 90, 1.3), arc_path(21.2, 24.0, 5.4, 0, 90, 1.3)))

    @ap("ark", "utilities-file-archiver")
    def _(p, sm):
        # 10.2 brown parcel archive carton strapped with brass tape & zipper
        floor_shadow(p, 16.0, 28.4, 11.8, 2.2, 72)
        box = QRectF(5.0, 9.8, 22.0, 17.6)
        p.setPen(QPen(c("#68441c"), 1.0))
        p.setBrush(vgrad(9.8, 27.4, (0.0, "#ecc488"), (0.5, "#cf9d58"), (1.0, "#9e6e30")))
        p.drawRoundedRect(box, 1.6, 1.6)
        flaps = poly((3.4, 10.0), (6.6, 5.6), (25.4, 5.6), (28.6, 10.0))
        p.setBrush(vgrad(5.6, 10.0, (0.0, "#f8dfa8"), (1.0, "#d8a864")))
        p.drawPath(flaps)
        # Brass zipper strip down center
        p.setPen(Qt.NoPen)
        p.setBrush(c("#f7e29c"))
        p.drawRect(QRectF(14.2, 5.8, 3.6, 21.4))
        if not sm:
            p.setBrush(c("#785218"))
            for zy in range(7, 26, 2):
                p.drawRect(QRectF(14.6 if (zy // 2) % 2 == 0 else 15.8, zy, 1.6, 1.1))

    @ap("ktorrent", "kget")
    def _(p, sm):
        glass_disc(p, 16.0, 15.6, 12.2, "green")
        arr = U(rr(13.8, 8.8, 4.4, 7.6, 0.9), poly((16.0, 22.6), (22.0, 15.4), (10.0, 15.4), round_=0.5))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawPath(arr)

    @ap("spectacle", "ksnapshot org.kde.spectacle")
    def _(p, sm):
        # 10.2 Grab viewfinder frame + glossy camera lens
        floor_shadow(p, 16.0, 28.2, 11.6, 2.2, 70)
        p.setPen(QPen(c("#4c5260"), 1.8, Qt.DashLine))
        p.setBrush(QColor(225, 240, 255, 110))
        p.drawRoundedRect(QRectF(4.4, 5.0, 23.2, 21.2), 2.0, 2.0)
        glass_disc(p, 16.0, 15.6, 7.6, "blue", shadow=False)
        p.setPen(QPen(c("#ffffff"), 1.2))
        p.setBrush(c("#0e1c38"))
        p.drawEllipse(QPointF(16.0, 15.6), 3.4, 3.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(14.6, 14.2), 1.2, 1.2)

    @ap("ksudoku", "picmi kolf tagua mameexecutor")
    def _(p, sm):
        paint_chess_knight(p, sm)

    # ---- 2. 10.2 Utility Applications (straight-on shelf perspective, HIG p. 207) ----

    @ap("utilities-terminal", "org.kde.konsole konsole yakuake")
    def _(p, sm):
        # Figure 11-3 bottom-second: 10.2 Terminal pinstriped monitor with '>_'
        scr = aqua_pinstripe_monitor(p, sm, screen_bg=("#1c1e22", "#343840"), stand=False)
        prompt = U(
            polyline([(scr.left() + 2.8, scr.top() + 3.2), (scr.left() + 6.4, scr.top() + 5.6), (scr.left() + 2.8, scr.top() + 8.0)], 1.65),
            rr(scr.left() + 7.6, scr.top() + 7.4, 4.2, 1.5, 0.4),
        )
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawPath(prompt)

    @ap("utilities-system-monitor", "system-diagnosis hwinfo ksniffer")
    def _(p, sm):
        # Figure 11-9 left: 10.2 Process Viewer pinstriped monitor + glowing cyan/green ECG waveform
        scr = aqua_pinstripe_monitor(p, sm, screen_bg=("#0d2224", "#16383a"), stand=False)
        if not sm:
            p.setPen(QPen(QColor(60, 150, 140, 70), 0.6))
            for gx in range(int(scr.left()) + 4, int(scr.right()), 4):
                p.drawLine(QPointF(gx, scr.top()), QPointF(gx, scr.bottom()))
        mid_y = scr.center().y() + 1.0
        ecg = polyline(
            [
                (scr.left() + 1.2, mid_y),
                (scr.left() + 6.0, mid_y),
                (scr.left() + 8.2, scr.top() + 2.6),
                (scr.left() + 10.4, scr.bottom() - 2.4),
                (scr.left() + 12.8, mid_y - 2.6),
                (scr.left() + 15.2, mid_y),
                (scr.right() - 1.2, mid_y),
            ],
            1.45,
        )
        p.setPen(Qt.NoPen)
        p.setBrush(c("#58ffd0"))
        p.drawPath(ecg)

    @ap("utilities-log-viewer", "kdebugsettings kbugbuster")
    def _(p, sm):
        # Figure 11-3 bottom-right: 10.2 Console brushed-metal frame with amber LED matrix
        box = rr(3.2, 5.2, 25.6, 21.6, 1.8)
        drop_shadow_path(p, box, 0.0, 1.3, 62)
        p.setPen(QPen(c("#585d68"), 1.0))
        p.setBrush(vgrad(5.2, 26.8, (0.0, "#f4f6fa"), (1.0, "#b8beca")))
        p.drawPath(box)
        scr = QRectF(4.6, 8.2, 22.8, 15.6)
        p.setPen(QPen(c("#141210"), 0.8))
        p.setBrush(c("#1c160c"))
        p.drawRect(scr)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffb828"))
        if not sm:
            p.drawPath(text_path("WARN", 16.0, 12.8, px=5.6, bold=True))
            p.drawPath(text_path("07:36", 16.0, 19.2, px=5.4, bold=True))
        else:
            p.drawRect(QRectF(6.8, 11.4, 18.4, 2.2))
            p.drawRect(QRectF(6.8, 17.6, 14.0, 2.2))

    @ap("partitionmanager", "kdf filelight timevault device-notifier")
    def _(p, sm):
        # 10.2 Disk Utility: 3.5" internal drive + Aqua colour pie chart
        aqua_drive(p, sm, kind="internal")
        cx, cy, r = 16.0, 13.8, 5.6
        for a0, sp, col in ((0, 150, "#2674e6"), (150, 110, "#4ec032"), (260, 100, "#f4aa24")):
            w = QPainterPath()
            w.moveTo(cx, cy)
            w.arcTo(QRectF(cx - r, cy - r * 0.78, 2 * r, 2 * r * 0.78), a0, sp)
            w.closeSubpath()
            p.setPen(QPen(c("#ffffff"), 0.6))
            p.setBrush(c(col))
            p.drawPath(w)

    @ap("kwalletmanager", "kwalletmanager2 kgpg keepsecret")
    def _(p, sm):
        # 10.2 Keychain Access: brass padlock + gleaming silver/gold key on ring
        paint_brass_lock(p, unlocked=False, cx=13.5, cy=16.5, scale_f=0.88)
        key = U(S(circ(23.2, 10.2, 4.2), circ(23.2, 10.2, 1.6)), rr(22.0, 13.8, 2.4, 11.4, 0.8), rr(19.6, 20.6, 2.8, 1.6), rr(19.6, 23.2, 3.2, 1.6))
        p.setPen(QPen(c("#4c505a"), 0.85))
        p.setBrush(hgrad(19.0, 27.4, (0.0, "#ffffff"), (0.5, "#cfd5e0"), (1.0, "#858c9a")))
        p.drawPath(key)

    @ap("accessories-calculator", "kcalc org.kde.kcalc preferences-kcalc-constants")
    def _(p, sm):
        # Figure 11-8 middle: straight-on 10.2 Calculator with LCD & 4x5 Aqua button grid
        calc = rr(6.2, 3.4, 19.6, 25.2, 2.2)
        drop_shadow_path(p, calc, 0.0, 1.3, 62)
        p.setPen(QPen(c("#788090"), 1.0))
        p.setBrush(vgrad(3.4, 28.6, (0.0, "#ffffff"), (0.5, "#eceff5"), (1.0, "#d4d9e4")))
        p.drawPath(calc)
        lcd = QRectF(8.4, 5.8, 15.2, 4.6)
        p.setPen(QPen(c("#6e7888"), 0.8))
        p.setBrush(vgrad(5.8, 10.4, (0.0, "#dce8d8"), (1.0, "#eef6ea")))
        p.drawRoundedRect(lcd, 0.7, 0.7)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#222824"))
            p.drawPath(text_path("123.45", 18.8, 8.1, px=3.8, bold=True))
        for r_i in range(4):
            for c_i in range(4):
                bx = 8.4 + c_i * 3.95
                by = 12.2 + r_i * 3.65
                p.setPen(QPen(c("#8890a0"), 0.65))
                p.setBrush(c("#5294f2" if (c_i == 3 and r_i == 3) else "#ffffff"))
                p.drawRoundedRect(QRectF(bx, by, 3.1, 2.7), 0.6, 0.6)

    @ap("accessories-character-map", "")
    def _(p, sm):
        # Figure 11-3 bottom-left: 10.2 Key Caps sculpted translucent black Command keycap
        floor_shadow(p, 16.0, 27.6, 12.2, 2.2, 72)
        outer = poly((5.2, 7.2), (26.8, 7.2), (28.8, 25.6), (3.2, 25.6), round_=2.0)
        p.setPen(QPen(c("#0e1014"), 1.0))
        p.setBrush(vgrad(7.2, 25.6, (0.0, "#4c505a"), (0.4, "#22252c"), (1.0, "#101216")))
        p.drawPath(outer)
        top_cap = rr(6.8, 8.6, 18.4, 12.8, 2.2)
        p.setPen(QPen(c("#788090"), 0.85))
        p.setBrush(vgrad(8.6, 21.4, (0.0, "#5c626e"), (0.5, "#323640"), (1.0, "#484e5a")))
        p.drawPath(top_cap)
        # Looped Command symbol '⌘'
        cmd = U(
            S(rr(13.6, 12.6, 4.8, 4.8, 0.4), rr(14.7, 13.7, 2.6, 2.6)),
            *[ring(cx, cy, 1.45, 1.05) for cx, cy in ((13.0, 12.0), (19.0, 12.0), (13.0, 18.0), (19.0, 18.0))],
        )
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 230))
        p.drawPath(cmd)

    @ap("clock", "kronometer ktimer preferences-system-time")
    def _(p, sm):
        # 10.2 round brushed-silver & white Aqua analog clock
        floor_shadow(p, 16.0, 28.4, 11.4, 2.2, 72)
        p.setPen(QPen(c("#4b505a"), 1.05))
        p.setBrush(vgrad(3.6, 27.6, (0.0, "#ffffff"), (0.45, "#cfd5e0"), (1.0, "#858c9a")))
        p.drawEllipse(QPointF(16.0, 15.6), 12.0, 12.0)
        p.setPen(QPen(c("#788090"), 0.85))
        p.setBrush(rgrad(16.0, 13.5, 11.0, (0.0, "#ffffff"), (1.0, "#dce6f6")))
        p.drawEllipse(QPointF(16.0, 15.6), 9.8, 9.8)
        if not sm:
            p.setPen(QPen(c("#4e5460"), 0.8))
            for i in range(12):
                a = math.radians(i * 30)
                p.drawLine(QPointF(16 + 7.8 * math.cos(a), 15.6 + 7.8 * math.sin(a)), QPointF(16 + 9.0 * math.cos(a), 15.6 + 9.0 * math.sin(a)))
        p.setPen(QPen(c("#181b22"), 1.6, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(16.0, 15.6), QPointF(16.0, 9.4))
        p.drawLine(QPointF(16.0, 15.6), QPointF(20.8, 17.8))
        p.setPen(QPen(c("#de2618"), 0.9, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(16.0, 17.2), QPointF(12.2, 11.2))

    @ap("kfind", "kmag baloo strigi nepomuk preferences-desktop-baloo preferences-desktop-search")
    def _(p, sm):
        # Figure 11-24 right: 10.2 Sherlock plaid deerstalker cap + silver glass magnifier!
        floor_shadow(p, 16.0, 28.2, 11.8, 2.2, 70)
        cap_brim = ellipse(14.6, 15.2, 11.2, 3.6)
        p.setPen(QPen(c("#2a221c"), 0.95))
        p.setBrush(c("#382e26"))
        p.drawPath(cap_brim)
        dome = QPainterPath()
        dome.moveTo(5.8, 14.8)
        dome.cubicTo(6.4, 5.2, 22.8, 5.2, 23.4, 14.8)
        dome.closeSubpath()
        p.setPen(QPen(c("#3a2c20"), 0.95))
        p.setBrush(vgrad(5.2, 15.0, (0.0, "#a87e58"), (0.6, "#785638"), (1.0, "#4e3622")))
        p.drawPath(dome)
        if not sm:
            p.save()
            p.setClipPath(dome)
            p.setPen(QPen(QColor(220, 190, 150, 95), 0.75))
            for gx in range(7, 23, 3):
                p.drawLine(QPointF(gx, 5), QPointF(gx - 2, 15))
                p.drawLine(QPointF(6, gx - 2), QPointF(24, gx - 2))
            p.restore()
        paint_magnifier(p, 13.0, 12.4, 7.4, scale_f=0.72, ox=8.4, oy=7.8, shadow=False)

    @ap("klipper", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.6, 11.4, 2.2, 72)
        p.setPen(QPen(c("#5e3a14"), 1.0))
        p.setBrush(vgrad(4.6, 27.6, (0.0, "#dfa664"), (0.5, "#be8240"), (1.0, "#8f5920")))
        p.drawRoundedRect(QRectF(5.0, 4.8, 20.0, 22.8), 2.2, 2.2)
        aqua_sheet(p, sm, x=9.8, y=8.4, w=16.6, h=19.4, lines=True, shadow=False)
        clip = U(rr(10.2, 3.6, 9.6, 3.4, 1.1), S(circ(15.0, 3.4, 2.2), circ(15.0, 3.4, 0.9)))
        p.setPen(QPen(c("#4e525a"), 0.85))
        p.setBrush(vgrad(1.2, 7.0, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#858c98")))
        p.drawPath(clip)

    @ap("plasmadiscover", "muondiscover system-software-install system-software-update")
    def _(p, sm):
        # 10.2 Installer / Software Update open parcel box + glowing Aqua blue arrow
        aqua_plugin_cube(p, sm, accent="blue")
        arr = U(rr(13.8, 2.8, 4.4, 8.2, 0.9), poly((16.0, 15.8), (21.6, 9.8), (10.4, 9.8), round_=0.4))
        paint_gel_shape(p, arr, 2.8, 15.8, "blue")

    @ap("help-browser", "")
    def _(p, sm):
        # Classic glossy red-and-white Aqua lifebuoy ring
        floor_shadow(p, 16.0, 28.5, 11.4, 2.2, 74)
        cx, cy = 16.0, 15.6
        ring_p = S(circ(cx, cy, 12.0), circ(cx, cy, 5.2))
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(3.6, 27.6, (0.0, "#ffffff"), (0.6, "#eef2f8"), (1.0, "#c8cfd8")))
        p.drawPath(ring_p)
        p.setClipPath(ring_p)
        for ang in (45, 135, 225, 315):
            p.save()
            p.translate(cx, cy)
            p.rotate(ang)
            p.setBrush(vgrad(-13.0, -4.0, (0.0, "#ff786c"), (0.5, "#de2618"), (1.0, "#9e1008")))
            p.drawRect(QRectF(-3.2, -13.0, 6.4, 9.0))
            p.restore()
        lens = QRectF(cx - 8.4, cy - 11.0, 16.8, 9.2)
        p.setBrush(vgrad(lens.top(), lens.bottom(), (0.0, (255, 255, 255, 190)), (1.0, (255, 255, 255, 0))))
        p.drawEllipse(lens)
        p.restore()
        p.setPen(QPen(c("#686e7c"), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), 12.0, 12.0)
        p.drawEllipse(QPointF(cx, cy), 5.2, 5.2)

    @ap("krdc", "krfb")
    def _(p, sm):
        scr = aqua_pinstripe_monitor(p, sm, screen_bg=("#14489c", "#58b4ff"), stand=True)
        aqua_globe(p, scr.center().x(), scr.center().y(), 5.4, sm=sm, on_stand=False)

    @ap("kdeconnect", "preferences-kde-connect")
    def _(p, sm):
        from .places_devices import build_devices_painters
        floor_shadow(p, 16.0, 28.5, 8.8, 2.1, 70)
        body = QRectF(8.4, 3.2, 15.2, 24.4)
        p.setPen(QPen(c("#383c46"), 1.0))
        p.setBrush(hgrad(8.4, 23.6, (0.0, "#cfd5e0"), (0.5, "#ffffff"), (1.0, "#a8b0be")))
        p.drawRoundedRect(body, 2.6, 2.6)
        scr = QRectF(10.0, 5.8, 12.0, 16.0)
        p.setBrush(vgrad(5.8, 21.8, (0.0, "#1c62c8"), (1.0, "#7cd0ff")))
        p.drawRoundedRect(scr, 1.0, 1.0)
        w = U(circ(16.0, 16.4, 1.2), arc_path(16.0, 16.4, 3.4, 45, 90, 1.3), arc_path(16.0, 16.4, 5.6, 45, 90, 1.3))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawPath(w)

    @ap("java", "")
    def _(p, sm):
        # Porcelain coffee cup + warm steam wisps
        floor_shadow(p, 15.0, 28.2, 10.6, 2.1, 70)
        p.setPen(QPen(c("#6e7684"), 1.8, Qt.SolidLine, Qt.RoundCap))
        p.drawPath(arc_path(22.2, 18.2, 3.6, -90, 180, 1.8))
        cup = QPainterPath()
        cup.moveTo(6.8, 12.4)
        cup.lineTo(23.2, 12.4)
        cup.quadTo(22.4, 26.8, 15.0, 26.8)
        cup.quadTo(7.6, 26.8, 6.8, 12.4)
        p.setPen(QPen(c("#6e7684"), 1.0))
        p.setBrush(hgrad(6.8, 23.2, (0.0, "#ffffff"), (0.6, "#eef2f8"), (1.0, "#bfc6d4")))
        p.drawPath(cup)
        p.setBrush(c("#5e3414"))
        p.drawEllipse(QRectF(7.2, 11.0, 15.6, 3.0))
        steam = U(arc_path(13.0, 7.6, 2.4, 60, 150, 1.3), arc_path(17.4, 6.8, 2.4, -120, 150, 1.3))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#de3824"))
        p.drawPath(steam)

    @ap("wine", "kde-windows")
    def _(p, sm):
        # Crystal wineglass filled with ruby-red wine
        floor_shadow(p, 16.0, 28.4, 8.6, 2.0, 68)
        p.setPen(QPen(c("#6e7684"), 1.2))
        p.drawLine(QPointF(16.0, 17.6), QPointF(16.0, 26.6))
        p.setBrush(c("#dfe6f2"))
        p.drawEllipse(QRectF(10.6, 25.6, 10.8, 2.4))
        bowl = QPainterPath()
        bowl.moveTo(9.4, 5.2)
        bowl.lineTo(22.6, 5.2)
        bowl.quadTo(23.4, 17.8, 16.0, 17.8)
        bowl.quadTo(8.6, 17.8, 9.4, 5.2)
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(235, 245, 255, 170))
        p.drawPath(bowl)
        p.setClipPath(bowl)
        p.setBrush(vgrad(10.2, 17.8, (0.0, "#e62820"), (1.0, "#780804")))
        p.drawRect(QRectF(8.0, 10.2, 16.0, 8.0))
        p.restore()
        p.setPen(QPen(c("#687282"), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(bowl)

    @ap("system-reboot", "")
    def _(p, sm):
        glass_disc(p, 16.0, 15.6, 12.2, "green")
        from .materials import aqua_arrow_path, draw_disc_glyph
        draw_disc_glyph(p, aqua_arrow_path(16.0, 15.6, 7.6, 4.2, 55, -285), dark=False)

    @ap("system-users", "preferences-desktop-user preferences-system-users")
    def _(p, sm):
        paint_person_bust(p, 20.2, 15.2, 0.76, "clear")
        paint_person_bust(p, 12.6, 17.4, 0.84, "blue")

    # ---- 3. 10.2 System Preferences Light-Switch Plate Family (45+ preferences-* & plasma/kde/xorg) ----

    @ap("preferences-system", "systemsettings oxygen kde plasma plasma-studio plasmagik homerun wayland xorg utilities-desktop-extra preferences-other akonadi")
    def _(p, sm):
        # Figure 11-12: brushed-silver light-switch plate + glossy Aqua gear/sphere on right
        aqua_pref_plate(p, sm)
        gp = gear_path(20.0, 16.0, 8, 5.8, 4.2, 1.8)
        paint_gel_shape(p, gp, 10.2, 21.8, "graphite", shadow=False)

    @ap("preferences-desktop-color", "preferences-desktop-display-color preferences-desktop-theme kde-gtk-config preferences-desktop-icons")
    def _(p, sm):
        # 10.2 Appearance / ColorSync plate with luminous 6-wedge Aqua color wheel
        aqua_pref_plate(p, sm)
        cx, cy, r = 19.8, 16.0, 5.8
        for i, col in enumerate(("#f03224", "#f8b81c", "#4ec432", "#28b8e0", "#2664e0", "#a838d8")):
            w = QPainterPath()
            w.moveTo(cx, cy)
            w.arcTo(QRectF(cx - r, cy - r, 2 * r, 2 * r), i * 60, 62)
            w.closeSubpath()
            p.setPen(Qt.NoPen)
            p.setBrush(c(col))
            p.drawPath(w)
        p.setPen(QPen(c("#585e6a"), 0.8))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r, r)

    @ap("preferences-desktop-display", "preferences-desktop-wallpaper preferences-desktop-screensaver preferences-system-windows preferences-system-windows-actions preferences-system-windows-move")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        scr = QRectF(14.2, 10.4, 11.4, 9.2)
        p.setPen(QPen(c("#384862"), 0.85))
        p.setBrush(vgrad(10.4, 19.6, (0.0, "#1c62c8"), (1.0, "#7cd2ff")))
        p.drawRoundedRect(scr, 1.0, 1.0)
        p.setBrush(c("#b8c0ce"))
        p.drawRect(QRectF(18.2, 19.6, 3.4, 2.2))
        p.drawRect(QRectF(16.2, 21.6, 7.4, 1.2))

    @ap("preferences-desktop-sound", "preferences-desktop-text-to-speech")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        spk = U(rr(14.2, 13.8, 2.8, 4.4, 0.5), poly((16.4, 13.8), (20.2, 10.6), (20.2, 21.4), (16.4, 18.2)), arc_path(19.6, 16.0, 3.2, -45, 90, 1.3), arc_path(19.6, 16.0, 5.4, -45, 90, 1.3))
        paint_gel_shape(p, spk, 10.6, 21.4, "blue", shadow=False)

    @ap("preferences-desktop-keyboard", "preferences-desktop- gaming preferences-desktop-gaming preferences-web-browser-shortcuts")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        kb = rr(13.8, 12.2, 12.0, 7.8, 1.0)
        p.setPen(QPen(c("#4e5460"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawPath(kb)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#383e4a"))
        for r_i in range(2):
            for c_i in range(4):
                p.drawRect(QRectF(15.0 + c_i * 2.5, 13.6 + r_i * 2.3, 1.8, 1.5))

    @ap("preferences-desktop-mouse", "preferences-desktop-launch-feedback")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        ms = ellipse(19.8, 16.4, 4.2, 5.8)
        paint_gel_shape(p, ms, 10.6, 22.2, "clear", shadow=False)

    @ap("preferences-system-bluetooth", "preferences-system-bluetooth-inactive hotspot")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        oval = ellipse(19.8, 16.0, 4.6, 6.2)
        paint_gel_shape(p, oval, 9.8, 22.2, "blue", shadow=False)
        rune = polyline([(17.8, 13.8), (21.8, 17.8), (19.8, 19.8), (19.8, 12.2), (21.8, 14.2), (17.8, 18.2)], 1.1)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawPath(rune)

    @ap("network-manager", "preferences-system-network-ethernet preferences-system-network-sharing preferences-desktop-thunderbolt preferences-online-accounts preferences-web-browser-adblock preferences-web-browser-cache preferences-web-browser-cookies preferences-web-browser-identification preferences-web-browser-stylesheets")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        aqua_globe(p, 19.8, 16.0, 5.6, sm=sm, on_stand=False)

    @ap("preferences-desktop-cryptography", "preferences-desktop-user-password preferences-system-login preferences-applications-permissions")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        paint_brass_lock(p, unlocked=False, cx=19.8, cy=16.0, scale_f=0.52, shadow=False)

    @ap("preferences-system-power-management", "preferences-system-performance preferences-system-session-services")
    def _(p, sm):
        # 10.2 Energy Saver glowing glass lightbulb on System Preferences plate
        aqua_pref_plate(p, sm)
        bulb = U(circ(19.8, 14.4, 4.2), rr(17.8, 17.2, 4.0, 2.8, 0.6))
        paint_gel_shape(p, bulb, 10.2, 20.0, "amber", shadow=False)
        p.setPen(QPen(c("#585e6a"), 0.8))
        p.setBrush(c("#bfc6d2"))
        p.drawRoundedRect(QRectF(18.0, 19.8, 3.6, 2.2), 0.5, 0.5)

    @ap("preferences-desktop-accessibility", "preferences-desktop-locale preferences-contact-list preferences-desktop-default-applications preferences-desktop-filetype-association")
    def _(p, sm):
        # 10.2 Universal Access glossy blue circle + white outstretched Vitruvian figure
        aqua_pref_plate(p, sm)
        glass_disc(p, 19.8, 16.0, 5.8, "blue", shadow=False)
        fig = U(circ(19.8, 12.8, 1.1), line(16.6, 14.8, 23.0, 14.8, 1.2), line(19.8, 14.2, 19.8, 17.2, 1.3), line(19.8, 17.0, 18.0, 20.0, 1.2), line(19.8, 17.0, 21.6, 20.0, 1.2))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#ffffff"))
        p.drawPath(fig)

    @ap("preferences-desktop-notification", "preferences-desktop-notification-bell")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        bell = U(circ(19.8, 14.8, 3.4), rr(16.4, 14.8, 6.8, 3.6), rr(15.0, 18.0, 9.6, 1.6, 0.8), circ(19.8, 20.4, 1.2))
        paint_gel_shape(p, bell, 11.4, 21.6, "amber", shadow=False)

    @ap("preferences-desktop-printer", "")
    def _(p, sm):
        aqua_pref_plate(p, sm)
        prn = U(rr(16.6, 11.4, 6.4, 3.0), S(rr(14.6, 14.2, 10.4, 5.2, 1.0), rr(16.6, 17.6, 6.4, 2.2)), rr(16.6, 18.0, 6.4, 3.4))
        paint_gel_shape(p, prn, 11.4, 21.4, "graphite", shadow=False)

    @ap("preferences-plugin", "preferences-plugin-script")
    def _(p, sm):
        aqua_plugin_cube(p, sm, accent="blue")

    # ---- 4. All 40 Oxygen Categories ----

    @ct("applications-all", "applications-accessories applications-other")
    def _(p, sm):
        paint_applications_a(p, sm)

    @ct("applications-utilities", "applications-system")
    def _(p, sm):
        # 10.2 Utilities crossed wooden hammer & chrome wrench (ch11-212-021.png)
        floor_shadow(p, 16.0, 28.2, 11.4, 2.2, 68)
        p.save()
        p.translate(16.0, 16.2)
        p.rotate(-42)
        p.setPen(QPen(c("#5c3610"), 0.9))
        p.setBrush(hgrad(-2.0, 2.0, (0.0, "#e6ad62"), (0.5, "#be7d32"), (1.0, "#7c4b16"), y0=0, y1=0))
        p.drawRoundedRect(QRectF(-1.9, -7.0, 3.8, 19.5), 1.2, 1.2)
        head = poly((-6.8, -10.4), (5.8, -10.4), (5.8, -6.2), (-3.8, -6.2), (-7.6, -7.8), round_=0.7)
        p.setPen(QPen(c("#484c54"), 0.9))
        p.setBrush(vgrad(-10.4, -6.2, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#7f8692")))
        p.drawPath(head)
        p.restore()
        p.save()
        p.translate(16.0, 16.2)
        p.rotate(42)
        wr = U(rr(-2.1, -7.5, 4.2, 19.8, 1.8), S(circ(0.0, -9.2, 4.8), poly((-2.0, -14.5), (2.0, -14.5), (2.0, -8.6), (-2.0, -8.6))))
        p.setPen(QPen(c("#484c54"), 0.95))
        p.setBrush(hgrad(-4.8, 4.8, (0.0, "#ffffff"), (0.45, "#dce1e9"), (1.0, "#8a919e"), y0=0, y1=0))
        p.drawPath(wr)
        p.restore()

    @ct("applications-development", "applications-development-web applications-development-translation applications-engineering")
    def _(p, sm):
        paint_blueprint_dev(p, sm, hammer=False)

    @ct("applications-graphics", "")
    def _(p, sm):
        paint_painter_palette(p, sm)

    @ct("applications-internet", "")
    def _(p, sm):
        aqua_globe(p, 16.0, 15.6, 11.8, sm=sm, on_stand=False)

    @ct("applications-multimedia", "")
    def _(p, sm):
        aqua_optical_disc(p, sm, tint="silver")
        paint_music_notes(p, 17.6, 15.8, 0.88, "purple")

    @ct("applications-office", "")
    def _(p, sm):
        paint_textedit_pad(p, sm)

    @ct("applications-games", "applications-toys")
    def _(p, sm):
        paint_chess_knight(p, sm)

    @ct("applications-science", "applications-education applications-education-science applications-education-mathematics applications-education-school applications-education-university applications-education-language applications-education-miscellaneous applications-education-preschool")
    def _(p, sm):
        apps_map["kformula"](p, sm)

    @ct("preferences-desktop", "preferences-desktop-personal")
    def _(p, sm):
        apps_map["preferences-desktop-color"](p, sm)

    @ct("preferences-desktop-peripherals", "")
    def _(p, sm):
        apps_map["preferences-desktop-keyboard"](p, sm)

    @ct("preferences-desktop-wallpaper", "")
    def _(p, sm):
        apps_map["preferences-desktop-display"](p, sm)

    @ct("preferences-desktop-thunderbolt", "preferences-system-network preferences-system-network-ethernet preferences-online-accounts")
    def _(p, sm):
        apps_map["network-manager"](p, sm)

    @ct("preferences-devices-printer", "")
    def _(p, sm):
        apps_map["preferences-desktop-printer"](p, sm)

    @ct("preferences-kde-connect", "")
    def _(p, sm):
        apps_map["kdeconnect"](p, sm)

    @ct("preferences-applications-permissions", "")
    def _(p, sm):
        apps_map["preferences-desktop-cryptography"](p, sm)

    @ct("preferences-system", "preferences-other")
    def _(p, sm):
        apps_map["preferences-system"](p, sm)

    @ct("preferences-system-users", "system-users")
    def _(p, sm):
        apps_map["system-users"](p, sm)

    @ct("system-help", "")
    def _(p, sm):
        apps_map["help-browser"](p, sm)

    # ---- 5. All 40 Oxygen Plasma Applet PNG Icons (applets/) ----

    @pl_app("org.kde.plasma.analogclock", "org.kde.plasma.digitalclock org.kde.plasma.binaryclock org.kde.plasma.fuzzyclock org.kde.plasma.timer")
    def _(p, sm):
        apps_map["clock"](p, sm)

    @pl_app("org.kde.plasma.calculator", "")
    def _(p, sm):
        apps_map["accessories-calculator"](p, sm)

    @pl_app("org.kde.plasma.calendar", "")
    def _(p, sm):
        apps_map["office-calendar"](p, sm)

    @pl_app("org.kde.plasma.clipboard", "")
    def _(p, sm):
        apps_map["klipper"](p, sm)

    @pl_app("org.kde.plasma.colorpicker", "org.kde.plasma.comic org.kde.plasma.frame")
    def _(p, sm):
        paint_painter_palette(p, sm)

    @pl_app("org.kde.plasma.folder", "")
    def _(p, sm):
        aqua_folder(p, sm, tint="blue")

    @pl_app("org.kde.plasma.notes", "")
    def _(p, sm):
        apps_map["knotes"](p, sm)

    @pl_app("org.kde.plasma.kicker", "org.kde.plasma.kickerdash org.kde.plasma.kickoff org.kde.plasma.quicklaunch applets-template")
    def _(p, sm):
        paint_applications_a(p, sm)

    @pl_app("org.kde.plasma.icontasks", "org.kde.plasma.taskmanager org.kde.plasma.windowlist org.kde.plasma.pager org.kde.plasma.activitybar org.kde.plasma.showActivityManager org.kde.plasma.systemtray")
    def _(p, sm):
        paint_finder_smiley(p, sm)

    @pl_app("org.kde.plasma.mediacontroller", "org.kde.plasma.volume")
    def _(p, sm):
        apps_map["amarok"](p, sm)

    @pl_app("org.kde.plasma.networkmanagement", "")
    def _(p, sm):
        aqua_globe(p, 16.0, 15.6, 11.8, sm=sm, on_stand=False)

    @pl_app("org.kde.plasma.systemloadviewer", "org.kde.plasma.systemmonitor.cpu org.kde.plasma.systemmonitor.memory org.kde.plasma.systemmonitor.net org.kde.plasma.systemmonitor.diskactivity org.kde.plasma.systemmonitor.diskusage")
    def _(p, sm):
        apps_map["utilities-system-monitor"](p, sm)

    @pl_app("org.kde.plasma.battery", "org.kde.plasma.devicenotifier")
    def _(p, sm):
        apps_map["partitionmanager"](p, sm)

    @pl_app("org.kde.plasma.userswitcher", "org.kde.ktpcontactlist")
    def _(p, sm):
        apps_map["system-users"](p, sm)

    @pl_app("org.kde.muonnotifier", "")
    def _(p, sm):
        apps_map["plasmadiscover"](p, sm)

    @pl_app("org.kde.plasma.fifteenpuzzle", "")
    def _(p, sm):
        paint_chess_knight(p, sm)

    apps_map = {n: fn for n, _, fn in apps}
    return apps, categories, applets
