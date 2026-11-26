# SPDX-License-Identifier: GPL-2.0-or-later
"""Mac OS X 10.2 "Jaguar" Places (74+) and Devices (89+) icon painters."""
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
    aqua_sheet,
    arc_path,
    c,
    circ,
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
    paint_heart_path,
    paint_mesh_trash,
    paint_music_notes,
    plus_badge,
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


def paint_home_cottage(p, sm=False):
    """10.2 Finder 'Home' cottage sampled from ch11-211-020.png."""
    floor_shadow(p, 16.0, 28.0, 11.5, 2.2, 72)
    p.setPen(QPen(c("#524d46"), 0.9))
    p.setBrush(vgrad(6.0, 15.0, (0.0, "#f2eee6"), (1.0, "#b8b0a2")))
    p.drawRoundedRect(QRectF(21.2, 6.2, 3.2, 8.5), 0.5, 0.5)

    walls = QRectF(6.8, 14.0, 18.4, 13.2)
    p.setPen(QPen(c("#686258"), 1.0))
    p.setBrush(vgrad(14.0, 27.2, (0.0, "#fcfaf4"), (0.7, "#ede7da"), (1.0, "#d4ccb8")))
    p.drawRect(walls)
    p.drawPath(poly((16.0, 6.2), (25.2, 14.4), (6.8, 14.4)))

    p.setPen(QPen(c("#4f2c0e"), 0.9))
    p.setBrush(vgrad(18.2, 27.2, (0.0, "#c88242"), (1.0, "#7c4618")))
    p.drawRect(QRectF(13.4, 18.4, 5.2, 8.8))
    p.setPen(Qt.NoPen)
    p.setBrush(c("#f0d498"))
    p.drawEllipse(QPointF(17.4, 23.0), 0.65, 0.65)

    p.setPen(QPen(c("#522e12"), 0.85))
    p.setBrush(c("#6e3c16"))
    p.drawRoundedRect(QRectF(13.3, 11.2, 5.4, 4.2), 0.6, 0.6)
    p.setPen(Qt.NoPen)
    p.setBrush(c("#f5f8ff"))
    p.drawEllipse(QPointF(16.0, 13.3), 1.4, 1.4)

    roof = poly((16.0, 4.2), (28.4, 15.4), (26.4, 17.2), (16.0, 7.8), (5.6, 17.2), (3.6, 15.4))
    p.setPen(QPen(c("#141312"), 0.95, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(4.2, 17.2, (0.0, "#5c5955"), (0.5, "#2b2927"), (1.0, "#181716")))
    p.drawPath(roof)


def paint_public_roadsign(p, cx=16.0, cy=18.2, r=6.6):
    """Exact 10.2 'Public' yellow diamond pedestrian road sign (ch11-212-021.png & al-107-045.png)."""
    dm = poly((cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy), round_=0.5)
    p.save()
    p.setPen(QPen(c("#5e4804"), 0.9))
    p.setBrush(vgrad(cy - r, cy + r, (0.0, "#fff068"), (0.55, "#f4c414"), (1.0, "#cf9604"), x0=cx, x1=cx))
    p.drawPath(dm)
    # Walking figure silhouette
    s = r / 6.6
    man = U(
        circ(cx + 0.2 * s, cy - 2.8 * s, 1.05 * s),
        line(cx + 0.1 * s, cy - 1.4 * s, cx - 0.3 * s, cy + 1.0 * s, 1.35 * s),
        line(cx + 0.0 * s, cy - 1.1 * s, cx - 2.0 * s, cy + 0.4 * s, 1.0 * s),
        line(cx + 0.1 * s, cy - 1.1 * s, cx + 1.9 * s, cy + 0.3 * s, 1.0 * s),
        line(cx - 0.3 * s, cy + 0.9 * s, cx - 1.8 * s, cy + 3.4 * s, 1.1 * s),
        line(cx - 0.2 * s, cy + 0.9 * s, cx + 1.6 * s, cy + 3.3 * s, 1.1 * s),
    )
    p.setPen(Qt.NoPen)
    p.setBrush(c("#161512"))
    p.drawPath(man)
    p.restore()


def paint_safari_compass(p, cx=16.0, cy=15.8, r=12.0, sm=False):
    """10.2/10.2.3 Safari brushed-silver mariner's compass over glowing Aqua ocean map."""
    floor_shadow(p, cx, cy + r + 1.0, r * 0.92, 2.2, 74)
    # Brushed silver outer bezel + top suspension ring
    if not sm:
        p.setPen(QPen(c("#545862"), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy - r - 1.1), 2.1, 1.5)
    bezel = circ(cx, cy, r)
    p.setPen(QPen(c("#4b4f58"), 1.05))
    p.setBrush(vgrad(cy - r, cy + r, (0.0, "#ffffff"), (0.4, "#d2d7e0"), (0.7, "#8e94a0"), (1.0, "#dfe3ec"), x0=cx - r, x1=cx + r))
    p.drawPath(bezel)

    face_r = r - 1.9
    face = circ(cx, cy, face_r)
    p.save()
    p.setPen(QPen(c("#103b7a"), 0.85))
    p.setBrush(rgrad(cx, cy - face_r * 0.25, face_r * 1.25, (0.0, "#70d0ff"), (0.55, "#1f74d8"), (1.0, "#0b3a86")))
    p.drawPath(face)
    p.setClipPath(face)

    if not sm:
        p.setPen(QPen(QColor(255, 255, 255, 130), 0.7))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), face_r * 0.68, face_r * 0.68)
        for i in range(16):
            ang = math.radians(i * 22.5)
            r0 = face_r * (0.76 if i % 4 == 0 else 0.84)
            p.drawLine(
                QPointF(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)),
                QPointF(cx + face_r * 0.96 * math.cos(ang), cy + face_r * 0.96 * math.sin(ang)),
            )

    # Classic red-and-silver compass needle at +42 degrees (pointing NE)
    p.save()
    p.translate(cx, cy)
    p.rotate(42)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 15, 40, 85))
    p.drawPath(poly((0, -face_r * 0.88), (2.1, 0), (0, face_r * 0.88), (-2.1, 0)).translated(0.6, 0.9))
    # North red half
    p.setBrush(hgrad(-2.0, 2.0, (0.0, "#ff7668"), (0.5, "#e22618"), (1.0, "#9c0e06")))
    p.drawPath(poly((0, -face_r * 0.88), (2.0, 0), (-2.0, 0)))
    # South silver-white half
    p.setBrush(hgrad(-2.0, 2.0, (0.0, "#ffffff"), (0.5, "#eef2f8"), (1.0, "#aeb6c4")))
    p.drawPath(poly((2.0, 0), (0, face_r * 0.88), (-2.0, 0)))
    p.setPen(QPen(c("#484c56"), 0.6))
    p.setBrush(c("#ffffff"))
    p.drawEllipse(QPointF(0, 0), 1.35, 1.35)
    p.restore()

    # Specular glass sheen
    lens_r = QRectF(cx - face_r * 0.68, cy - face_r + 0.7, face_r * 1.36, face_r * 0.75)
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(lens_r.top(), lens_r.bottom(), (0.0, (255, 255, 255, 190)), (1.0, (255, 255, 255, 0)), x0=cx, x1=cx))
    p.drawEllipse(lens_r)
    p.restore()


def paint_person_bust(p, cx=16.0, cy=16.5, s=1.0, kind="blue"):
    """Glossy 10.2 iChat/Accounts Aqua silhouette bust."""
    floor_shadow(p, cx, cy + 11.2 * s, 9.5 * s, 2.0 * s, 65)
    shoulders = QPainterPath()
    shoulders.moveTo(cx - 9.2 * s, cy + 9.8 * s)
    shoulders.cubicTo(cx - 9.0 * s, cy + 1.8 * s, cx + 9.0 * s, cy + 1.8 * s, cx + 9.2 * s, cy + 9.8 * s)
    shoulders.quadTo(cx, cy + 11.2 * s, cx - 9.2 * s, cy + 9.8 * s)
    shoulders.closeSubpath()
    paint_gel_shape(p, shoulders, cy + 2.0 * s, cy + 10.8 * s, kind)

    # Warm porcelain/silver-pearl spherical head above Aqua shoulders
    hr = 4.6 * s
    hy = cy - 3.6 * s
    p.setPen(QPen(c("#6c5848"), 0.9))
    p.setBrush(rgrad(cx - hr * 0.3, hy - hr * 0.3, hr * 1.4, (0.0, "#fff8f0"), (0.6, "#f0d4b8"), (1.0, "#be9674")))
    p.drawEllipse(QPointF(cx, hy), hr, hr)


def build_places_painters():
    places = []

    def pl(name, aliases=""):
        def deco(fn):
            places.append((name, aliases.split(), fn))
            return fn
        return deco

    # 1. Core & Color-tinted 10.2 Aqua pinstriped folders
    @pl("folder", "inode-directory stock_folder folder-blue")
    def _(p, sm):
        aqua_folder(p, sm, tint="blue")

    @pl("folder-open", "")
    def _(p, sm):
        aqua_folder(p, sm, tint="blue", open_flap=True)

    @pl("folder-add", "")
    def _(p, sm):
        aqua_folder(p, sm, tint="blue")
        plus_badge(p, 24.4, 8.4, 5.0, 2.1)

    for cname in ("cyan", "green", "red", "orange", "yellow", "violet", "brown", "grey", "black"):
        def _make_col(col=cname):
            def _fn(p, sm):
                aqua_folder(p, sm, tint=col)
            return _fn
        places.append((f"folder-{cname}", [], _make_col()))

    # 2. Special 10.2 Finder Folders (al-107-045.png & ch11-212-021.png)
    @pl("folder-documents", "folder-text folder-txt")
    def _(p, sm):
        doc_g = S(
            poly((12.2, 12.8), (18.0, 12.8), (20.2, 15.0), (20.2, 23.4), (12.2, 23.4)),
            rr(13.8, 16.4, 4.8, 1.0),
            rr(13.8, 18.6, 4.8, 1.0),
            rr(13.8, 20.8, 3.4, 1.0),
        )
        aqua_folder(p, sm, glyph=doc_g)

    @pl("folder-download", "folder-downloads")
    def _(p, sm):
        arr = U(rr(14.3, 12.6, 3.4, 6.2, 0.7), poly((16.0, 23.6), (20.8, 18.0), (11.2, 18.0), round_=0.4))
        aqua_folder(p, sm, glyph=arr)

    @pl("folder-music", "folder-sound library-music")
    def _(p, sm):
        notes = U(
            ellipse(13.2, 22.0, 2.1, 1.5),
            ellipse(19.0, 20.8, 2.1, 1.5),
            rr(14.4, 13.8, 1.4, 8.0),
            rr(20.2, 12.6, 1.4, 8.0),
            poly((14.4, 13.6), (21.6, 12.4), (21.6, 14.6), (14.4, 15.8)),
        )
        aqua_folder(p, sm, glyph=notes)

    @pl("folder-pictures", "folder-picture folder-image folder-images")
    def _(p, sm):
        pic = U(
            S(rr(11.0, 13.4, 10.4, 9.2, 0.8), rr(12.2, 14.6, 8.0, 6.8)),
            circ(14.2, 16.6, 1.1),
            poly((12.4, 21.2), (15.4, 17.8), (17.4, 19.8), (18.8, 18.4), (20.0, 21.2)),
        )
        aqua_folder(p, sm, glyph=pic)

    @pl("folder-image-people", "")
    def _(p, sm):
        ppl = U(circ(16.0, 15.6, 2.2), poly((12.0, 23.2), (13.4, 18.6), (18.6, 18.6), (20.0, 23.2), round_=1.0))
        aqua_folder(p, sm, glyph=ppl)

    @pl("folder-videos", "folder-video")
    def _(p, sm):
        film = S(
            rr(10.8, 13.2, 10.8, 9.6, 0.7),
            rr(13.4, 14.4, 5.6, 3.3),
            rr(13.4, 18.5, 5.6, 3.3),
            *[rr(x, y, 1.2, 1.3) for x in (11.5, 19.7) for y in (14.2, 17.2, 20.2)],
        )
        aqua_folder(p, sm, glyph=film)

    @pl("folder-public", "folder-publicshare")
    def _(p, sm):
        aqua_folder(p, sm)
        paint_public_roadsign(p, 16.4, 18.2, 5.8)

    @pl("folder-html", "folder_html")
    def _(p, sm):
        web = U(
            ring(16.2, 18.2, 4.8, 1.2),
            ellipse(16.2, 18.2, 2.3, 4.8).subtracted(ellipse(16.2, 18.2, 1.3, 3.8)),
            rr(11.4, 17.6, 9.6, 1.1),
        )
        aqua_folder(p, sm, glyph=web)

    @pl("folder-network", "folder-remote")
    def _(p, sm):
        aqua_folder(p, sm)
        aqua_globe(p, 21.8, 19.6, 6.4, sm=sm, on_stand=False)

    @pl("folder-cloud", "folder-dropbox folder-gdrive folder-onedrive folder-owncloud")
    def _(p, sm):
        cld = U(circ(13.6, 19.4, 2.6), circ(16.2, 17.2, 3.3), circ(19.2, 19.2, 2.5), rr(13.4, 18.8, 6.0, 3.2))
        aqua_folder(p, sm, glyph=cld)

    @pl("folder-development", "folder-script")
    def _(p, sm):
        dev = U(
            polyline([(14.2, 15.0), (11.2, 18.2), (14.2, 21.4)], 1.6),
            polyline([(18.2, 15.0), (21.2, 18.2), (18.2, 21.4)], 1.6),
            line(16.9, 14.4, 15.5, 22.0, 1.4),
        )
        aqua_folder(p, sm, glyph=dev)

    @pl("folder-favorites", "folder-bookmark")
    def _(p, sm):
        aqua_folder(p, sm, glyph=paint_heart_path(16.2, 18.2, 4.6))

    @pl("folder-locked", "")
    def _(p, sm):
        lk = U(
            S(rr(12.6, 17.4, 7.2, 5.6, 1.0), circ(16.2, 20.0, 1.0)),
            arc_path(16.2, 17.0, 2.2, 0, 180, 1.4),
        )
        aqua_folder(p, sm, glyph=lk)

    @pl("folder-important", "")
    def _(p, sm):
        aqua_folder(p, sm)
        mini_badge_disc(p, 23.2, 21.4, 5.6, "red", U(rr(22.1, 17.8, 2.2, 4.4, 0.9), circ(23.2, 24.0, 1.1)))

    @pl("folder-mail", "")
    def _(p, sm):
        env = S(rr(11.0, 14.4, 10.4, 7.6, 0.9), polyline([(11.6, 15.0), (16.2, 18.8), (20.8, 15.0)], 1.1))
        aqua_folder(p, sm, glyph=env)

    @pl("folder-print", "")
    def _(p, sm):
        prn = U(rr(13.0, 13.4, 6.4, 2.6), S(rr(11.2, 16.0, 10.0, 4.8, 1.0), rr(13.2, 19.0, 6.0, 2.2)), rr(13.2, 19.6, 6.0, 3.2))
        aqua_folder(p, sm, glyph=prn)

    @pl("folder-tar", "")
    def _(p, sm):
        zp = U(*[rr(14.8 if i % 2 == 0 else 16.2, 10.4 + i * 2.2, 2.0, 1.5, 0.3) for i in range(6)], rr(14.6, 23.0, 3.2, 2.4, 0.6))
        aqua_folder(p, sm, glyph=zp)

    @pl("folder-temp", "")
    def _(p, sm):
        clk = U(ring(16.2, 18.2, 4.6, 1.3), line(16.2, 18.2, 16.2, 15.4, 1.3), line(16.2, 18.2, 18.4, 19.4, 1.3))
        aqua_folder(p, sm, glyph=clk)

    @pl("folder-games", "")
    def _(p, sm):
        pad = S(
            U(rr(10.8, 15.6, 10.8, 5.8, 2.6), circ(12.6, 20.2, 2.2), circ(19.8, 20.2, 2.2)),
            plus_path(13.4, 18.2, 1.6, 1.1),
            circ(18.8, 17.6, 0.75),
            circ(20.2, 18.8, 0.75),
        )
        aqua_folder(p, sm, glyph=pad)

    @pl("folder-activities", "")
    def _(p, sm):
        dots = U(circ(13.0, 16.4, 1.9), circ(19.2, 16.4, 1.9), circ(16.1, 21.2, 1.9))
        aqua_folder(p, sm, glyph=dots)

    # 3. Mail In/Out/Sent trays (10.2 Mail wooden/aluminum letter trays)
    def mail_tray(p, arrow_dir=None):
        floor_shadow(p, 16.0, 28.4, 12.2, 2.2, 72)
        back = poly((6.4, 10.0), (25.6, 10.0), (28.4, 24.4), (3.6, 24.4))
        p.setPen(QPen(c("#5e6470"), 1.0))
        p.setBrush(vgrad(10.0, 24.4, (0.0, "#eef1f7"), (1.0, "#b8c0ce")))
        p.drawPath(back)
        # Letter inside tray
        p.setPen(QPen(c("#8890a0"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(8.2, 12.2, 15.6, 9.6), 0.9, 0.9)
        # Front lip with U-cutout
        lip = S(rr(3.6, 21.0, 24.8, 6.2, 1.4), circ(16.0, 21.0, 4.4))
        p.setPen(QPen(c("#545a66"), 1.0))
        p.setBrush(vgrad(21.0, 27.2, (0.0, "#ffffff"), (0.4, "#dce1ec"), (1.0, "#9ba3b2")))
        p.drawPath(lip)
        if arrow_dir == "in":
            arr = U(rr(14.0, 4.2, 4.0, 8.6, 0.9), poly((16.0, 17.6), (21.4, 11.4), (10.6, 11.4), round_=0.4))
            paint_gel_shape(p, arr, 4.2, 17.6, "blue")
        elif arrow_dir == "out":
            arr = U(rr(14.0, 9.4, 4.0, 8.6, 0.9), poly((16.0, 3.8), (21.4, 10.0), (10.6, 10.0), round_=0.4))
            paint_gel_shape(p, arr, 3.8, 18.0, "green")
        elif arrow_dir == "sent":
            plane = poly((6.8, 13.8), (25.8, 6.2), (18.6, 20.6), (15.0, 15.2), round_=0.4)
            paint_gel_shape(p, plane, 6.2, 20.6, "blue")

    @pl("mail-folder-inbox", "")
    def _(p, sm):
        mail_tray(p, "in")

    @pl("mail-folder-outbox", "")
    def _(p, sm):
        mail_tray(p, "out")

    @pl("mail-folder-sent", "")
    def _(p, sm):
        mail_tray(p, "sent")

    @pl("mail-message", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.6, 12.2, 2.2, 68)
        env = QRectF(3.5, 8.2, 25.0, 17.4)
        p.setPen(QPen(c("#78808e"), 1.0))
        p.setBrush(vgrad(8.2, 25.6, (0.0, "#ffffff"), (1.0, "#e4e8f2")))
        p.drawRoundedRect(env, 1.4, 1.4)
        p.setPen(QPen(c("#9aa2b2"), 0.95))
        p.drawLine(QPointF(4.2, 9.0), QPointF(16.0, 18.2))
        p.drawLine(QPointF(27.8, 9.0), QPointF(16.0, 18.2))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#5c88e0"))
        p.drawRect(QRectF(22.8, 10.6, 3.4, 4.0))

    # 4. Home, Desktop, Trash, Network, Server, Favorites, Start-Here
    @pl("user-home", "")
    def _(p, sm):
        paint_home_cottage(p, sm)

    @pl("user-desktop", "desktop")
    def _(p, sm):
        # 10.2 Save-dialog 'Desktop' place icon (al-107-045.png): Aqua blue screen + menu bar + mini windows
        floor_shadow(p, 16.0, 28.0, 12.4, 2.2, 70)
        fr = QRectF(3.0, 5.2, 26.0, 21.0)
        p.setPen(QPen(c("#2a4878"), 1.05))
        p.setBrush(rgrad(16.0, 9.0, 18.0, (0.0, "#68c4ff"), (0.55, "#2472d4"), (1.0, "#0e3c8a")))
        p.drawRoundedRect(fr, 1.8, 1.8)
        # White 10.2 menu bar at top
        p.setPen(Qt.NoPen)
        p.setBrush(c("#f4f6fa"))
        p.drawRect(QRectF(3.6, 5.8, 24.8, 3.0))
        # Mini Finder window + desktop drive icon + bottom glass Dock
        p.setBrush(c("#ffffff", 230))
        p.drawRoundedRect(QRectF(5.8, 11.0, 13.4, 9.6), 1.0, 1.0)
        p.setBrush(c("#cfd6e2"))
        p.drawRect(QRectF(5.8, 11.0, 13.4, 2.2))
        if not sm:
            p.setBrush(c("#ffffff", 210))
            p.drawRect(QRectF(23.2, 10.8, 3.2, 2.8))
            p.drawRect(QRectF(23.2, 15.4, 3.2, 2.8))
        p.setBrush(QColor(255, 255, 255, 165))
        p.drawRect(QRectF(9.0, 23.2, 14.0, 2.4))

    @pl("user-trash", "")
    def _(p, sm):
        paint_mesh_trash(p, full=False, sm=sm)

    @pl("user-trash-full", "")
    def _(p, sm):
        paint_mesh_trash(p, full=True, sm=sm)

    @pl("network-workgroup", "")
    def _(p, sm):
        aqua_globe(p, sm=sm, on_stand=True)

    def paint_xserve_blades(p, sm):
        floor_shadow(p, 16.0, 28.4, 12.6, 2.2, 74)
        for i, y in enumerate((5.6, 13.0, 20.4)):
            blade = QRectF(3.4, y, 25.2, 6.2)
            p.setPen(QPen(c("#4e525c"), 0.95))
            p.setBrush(vgrad(y, y + 6.2, (0.0, "#f8fafc"), (0.45, "#d4d8e2"), (1.0, "#989ea8")))
            p.drawRoundedRect(blade, 1.2, 1.2)
            p.setPen(Qt.NoPen)
            p.setBrush(c("#2a2e36"))
            p.drawRect(QRectF(5.4, y + 2.0, 9.5, 2.2))
            for lx in (21.6, 24.2):
                p.setBrush(c("#3898ff" if lx == 21.6 else "#58d838"))
                p.drawEllipse(QPointF(lx, y + 3.1), 0.95, 0.95)

    @pl("network-server", "")
    def _(p, sm):
        paint_xserve_blades(p, sm)

    @pl("server-database", "network-server-database repository")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.4, 10.6, 2.2, 74)
        for y in (18.2, 12.2, 6.2):
            body = QPainterPath()
            body.moveTo(6.4, y)
            body.lineTo(6.4, y + 6.0)
            body.arcTo(QRectF(6.4, y + 3.6, 19.2, 4.8), 180, 180)
            body.lineTo(25.6, y)
            body.closeSubpath()
            p.setPen(QPen(c("#525762"), 0.95))
            p.setBrush(hgrad(6.4, 25.6, (0.0, "#9aa0ae"), (0.32, "#ffffff"), (0.7, "#cfd5e0"), (1.0, "#7c8390")))
            p.drawPath(body)
            p.setBrush(vgrad(y - 2.4, y + 2.4, (0.0, "#ffffff"), (1.0, "#cfd5e0")))
            p.drawEllipse(QRectF(6.4, y - 2.4, 19.2, 4.8))

    @pl("certificate-server", "")
    def _(p, sm):
        paint_xserve_blades(p, sm)
        mini_badge_disc(p, 23.6, 21.6, 5.8, "amber", star_path(23.6, 21.6, 3.4, 1.5, 6), dark=False)

    @pl("favorites", "bookmarks")
    def _(p, sm):
        paint_favorites_heart(p, 16.0, 16.0, 11.4)

    @pl("compass", "")
    def _(p, sm):
        paint_safari_compass(p, 16.0, 15.8, 12.0, sm=sm)

    @pl("user-identity", "")
    def _(p, sm):
        paint_person_bust(p, 16.0, 16.5, 1.0, "blue")

    @pl("document-multiple", "")
    def _(p, sm):
        aqua_sheet(p, sm, x=4.2, y=2.6, w=17.4, h=22.4, lines=True, shadow=False)
        aqua_sheet(p, sm, x=9.8, y=5.8, w=17.4, h=22.4, lines=True, shadow=True)

    @pl("start-here", "start-here-kde distributor-logo kde-symbolic")
    def _(p, sm):
        # 10.2 Aqua crystal blue sphere with glossy white 'X' Jaguar/Pinstripe emblem
        glass_disc(p, 16.0, 15.6, 12.4, "blue")
        xp = U(
            poly((10.4, 9.8), (13.2, 9.8), (21.6, 21.4), (18.8, 21.4), round_=0.4),
            poly((19.0, 9.8), (21.6, 9.8), (13.0, 21.4), (10.4, 21.4), round_=0.4),
        )
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 20, 60, 100))
        p.drawPath(xp.translated(0, 0.9))
        p.setBrush(c("#ffffff"))
        p.drawPath(xp)

    return places


def build_devices_painters():
    devices = []

    def dv(name, aliases=""):
        def deco(fn):
            devices.append((name, aliases.split(), fn))
            return fn
        return deco

    # 1. Computers, Laptops & Displays
    @dv("computer", "video-display")
    def _(p, sm):
        scr = aqua_pinstripe_monitor(p, sm, screen_bg=("#0f3f8c", "#4eb2f8"), stand=True)
        # Mini Aqua wallpaper swoop inside display
        sw = QPainterPath()
        sw.moveTo(scr.left(), scr.bottom() - 4.0)
        sw.cubicTo(scr.left() + 6.0, scr.top() + 2.0, scr.right() - 6.0, scr.bottom(), scr.right(), scr.top() + 3.0)
        sw.lineTo(scr.right(), scr.bottom())
        sw.lineTo(scr.left(), scr.bottom())
        sw.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 65))
        p.drawPath(sw)

    @dv("computer-laptop", "")
    def _(p, sm):
        # 10.2 snow-white polycarbonate iBook G3 / Titanium PowerBook open clamshell
        floor_shadow(p, 16.0, 28.4, 13.4, 2.3, 74)
        lid = QRectF(5.2, 4.8, 21.6, 15.6)
        p.setPen(QPen(c("#6e7482"), 1.0))
        p.setBrush(vgrad(4.8, 20.4, (0.0, "#ffffff"), (1.0, "#dfe4ee")))
        p.drawRoundedRect(lid, 1.8, 1.8)
        scr = lid.adjusted(2.1, 2.0, -2.1, -2.2)
        p.setPen(QPen(c("#162848"), 0.85))
        p.setBrush(vgrad(scr.top(), scr.bottom(), (0.0, "#1c62c8"), (1.0, "#78ccff")))
        p.drawRect(scr)
        # Perspective keyboard base + front latch slot
        base = poly((5.2, 20.4), (26.8, 20.4), (29.6, 25.8), (2.4, 25.8))
        p.setPen(QPen(c("#686e7c"), 1.0))
        p.setBrush(vgrad(20.4, 25.8, (0.0, "#eef1f7"), (1.0, "#cfd5e2")))
        p.drawPath(base)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#9aa2b2"))
            p.drawPolygon(QPolygonF([QPointF(6.8, 21.3), QPointF(25.2, 21.3), QPointF(26.8, 23.8), QPointF(5.2, 23.8)]))
        p.setPen(QPen(c("#686e7c"), 0.95))
        p.setBrush(vgrad(25.4, 27.4, (0.0, "#ffffff"), (1.0, "#adb4c2")))
        p.drawRoundedRect(QRectF(2.4, 25.2, 27.2, 2.2), 0.9, 0.9)

    @dv("video-television", "tv")
    def _(p, sm):
        scr = aqua_pinstripe_monitor(p, sm, screen_bg=("#1c2230", "#354058"), stand=False)
        if not sm:
            # Color test bars / cinema screen
            cols = ("#f0e848", "#48d8e8", "#58d848", "#e848c8", "#e83828", "#2858e8")
            bw = scr.width() / len(cols)
            p.setPen(Qt.NoPen)
            for i, col in enumerate(cols):
                p.fillRect(QRectF(scr.left() + i * bw, scr.top() + 0.5, bw + 0.2, scr.height() - 1.0), c(col, 195))

    @dv("video-projector", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 26.8, 12.8, 2.3, 72)
        p.setPen(QPen(c("#525762"), 1.0))
        p.setBrush(vgrad(11.0, 24.5, (0.0, "#f8fafc"), (0.5, "#cfd5e0"), (1.0, "#969ca8")))
        p.drawRoundedRect(QRectF(3.2, 11.4, 25.6, 12.6), 2.4, 2.4)
        # Glowing glass projection lens on right
        glass_disc(p, 21.0, 17.6, 5.2, "blue", shadow=False)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#4c505a"))
            for vx in range(6, 14, 2):
                p.drawRect(QRectF(vx, 14.2, 1.1, 7.0))

    # 2. Hard Drives, Removable Drives, Optical, Flash & Floppy (Figures 11-14, 11-15)
    @dv("drive-harddisk", "internal drive-harddisk-solidstate")
    def _(p, sm):
        aqua_drive(p, sm, kind="internal")

    @dv("drive-removable-media", "drive-removable-media-usb")
    def _(p, sm):
        # Figure 11-14 orange external drive with white USB trident
        usb = U(
            circ(16.0, 17.6, 1.6),
            line(16.0, 17.4, 16.0, 8.6, 1.4),
            poly((16.0, 7.2), (17.8, 9.6), (14.2, 9.6)),
            polyline([(16.0, 14.8), (12.4, 12.4), (12.4, 10.6)], 1.2),
            circ(12.4, 10.4, 1.1),
            polyline([(16.0, 13.6), (19.6, 11.4), (19.6, 9.8)], 1.2),
            rr(18.5, 8.8, 2.2, 2.2),
        )
        aqua_drive(p, sm, kind="orange", glyph=usb)

    @dv("drive-removable-media-usb-pendrive", "")
    def _(p, sm):
        # Glossy white polycarbonate USB thumb drive + brushed steel USB-A plug
        floor_shadow(p, 16.0, 28.4, 7.8, 2.0, 68)
        p.setPen(QPen(c("#585d68"), 0.95))
        p.setBrush(hgrad(11.4, 20.6, (0.0, "#b8beca"), (0.45, "#ffffff"), (1.0, "#8c929e")))
        p.drawRoundedRect(QRectF(11.4, 3.8, 9.2, 7.4), 0.8, 0.8)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#2a2e36"))
        p.drawRect(QRectF(13.0, 5.6, 2.0, 2.4))
        p.drawRect(QRectF(17.0, 5.6, 2.0, 2.4))
        body = QRectF(9.6, 10.4, 12.8, 17.2)
        p.setPen(QPen(c("#767c8a"), 1.0))
        p.setBrush(hgrad(9.6, 22.4, (0.0, "#ffffff"), (0.5, "#eef2f8"), (1.0, "#cfd6e4")))
        p.drawRoundedRect(body, 2.8, 2.8)
        glass_disc(p, 16.0, 19.0, 2.6, "blue", shadow=False)

    @dv("drive-optical", "")
    def _(p, sm):
        aqua_drive(p, sm, kind="internal")
        p.save()
        p.translate(16.0, 13.6)
        p.scale(0.58, 0.42)
        p.translate(-16.0, -15.6)
        aqua_optical_disc(p, sm=True)
        p.restore()

    @dv("media-optical", "media-optical-data media-optical-mixed-cd")
    def _(p, sm):
        aqua_optical_disc(p, sm, label="CD", tint="silver")

    @dv("media-optical-audio", "")
    def _(p, sm):
        aqua_optical_disc(p, sm, tint="silver")
        paint_music_notes(p, 18.0, 17.2, 0.68, "purple")

    @dv("media-optical-dvd", "media-optical-dvd-data")
    def _(p, sm):
        aqua_optical_disc(p, sm, label="DVD", tint="dvd")

    @dv("media-optical-dvd-video", "media-optical-video")
    def _(p, sm):
        aqua_optical_disc(p, sm, label="VIDEO", tint="dvd")

    @dv("media-optical-blu-ray", "")
    def _(p, sm):
        aqua_optical_disc(p, sm, label="BD", tint="bluray")

    @dv("media-optical-recordable", "")
    def _(p, sm):
        aqua_optical_disc(p, sm, label="CD-R", tint="gold")

    @dv("media-floppy", "")
    def _(p, sm):
        # Figure 11-15: 3.5" floppy disk
        floor_shadow(p, 16.0, 28.4, 11.6, 2.2, 72)
        disk = poly((5.0, 4.0), (24.4, 4.0), (27.0, 6.6), (27.0, 27.2), (5.0, 27.2), round_=0.8)
        p.setPen(QPen(c("#1b1d22"), 1.05))
        p.setBrush(vgrad(4.0, 27.2, (0.0, "#565b66"), (0.5, "#363a42"), (1.0, "#24272d")))
        p.drawPath(disk)
        p.setPen(QPen(c("#52565e"), 0.9))
        p.setBrush(vgrad(4.0, 12.8, (0.0, "#f8fafc"), (0.5, "#cfd4dc"), (1.0, "#9ea4b0")))
        p.drawRoundedRect(QRectF(9.2, 4.2, 11.8, 8.6), 0.8, 0.8)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#22252a"))
        p.drawRect(QRectF(15.6, 5.4, 3.2, 6.2))
        p.setPen(QPen(c("#8c929e"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(8.0, 15.2, 16.0, 11.8), 0.9, 0.9)

    @dv("media-flash", "media-flash-sd-mmc media-flash-memory-stick media-flash-smart-media secure-card")
    def _(p, sm):
        # Royal-blue anodized SD / Flash memory card with gold contact pins
        floor_shadow(p, 16.0, 28.4, 10.2, 2.1, 70)
        card = poly((6.6, 3.8), (21.6, 3.8), (25.4, 7.6), (25.4, 27.4), (6.6, 27.4), round_=0.8)
        p.setPen(QPen(c("#163872"), 1.0))
        p.setBrush(vgrad(3.8, 27.4, (0.0, "#4c8be8"), (0.5, "#2b64be"), (1.0, "#1c4690")))
        p.drawPath(card)
        p.setPen(QPen(c("#8090a8"), 0.8))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(9.2, 12.6, 13.6, 12.2), 1.0, 1.0)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#e8b838"))
            for gx in range(9, 21, 3):
                p.drawRect(QRectF(gx, 5.4, 1.8, 4.2))

    @dv("media-tape", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.4, 12.4, 2.1, 70)
        p.setPen(QPen(c("#2b2e36"), 1.0))
        p.setBrush(vgrad(7.5, 25.5, (0.0, "#686e7c"), (0.5, "#3e424c"), (1.0, "#262930")))
        p.drawRoundedRect(QRectF(3.2, 7.6, 25.6, 17.6), 2.0, 2.0)
        p.setBrush(c("#f4ecd8"))
        p.drawRoundedRect(QRectF(5.6, 10.0, 20.8, 9.6), 1.0, 1.0)
        p.setBrush(c("#262930"))
        p.drawEllipse(QPointF(11.2, 14.8), 2.4, 2.4)
        p.drawEllipse(QPointF(20.8, 14.8), 2.4, 2.4)

    # 3. Classic White iPod, Audio, Cameras, Input & Peripherals
    @dv("multimedia-player", "multimedia-player-apple-ipod portable")
    def _(p, sm):
        # Iconic 2001/2002 snow-white polycarbonate iPod with cool-blue LCD & mechanical scroll wheel
        floor_shadow(p, 16.0, 28.5, 9.6, 2.2, 72)
        body = QRectF(7.2, 3.2, 17.6, 24.4)
        p.setPen(QPen(c("#7c8290"), 1.0))
        p.setBrush(vgrad(3.2, 27.6, (0.0, "#ffffff"), (0.6, "#f2f5fa"), (1.0, "#d8dee8")))
        p.drawRoundedRect(body, 2.6, 2.6)
        # Ice-blue backlit LCD screen
        p.setPen(QPen(c("#586880"), 0.85))
        p.setBrush(vgrad(5.2, 12.8, (0.0, "#dceeff"), (1.0, "#aad2f8")))
        p.drawRoundedRect(QRectF(9.6, 5.2, 12.8, 7.6), 0.9, 0.9)
        # Scroll wheel + center select button
        p.setPen(QPen(c("#9aa2b0"), 0.85))
        p.setBrush(c("#e4e8f0"))
        p.drawEllipse(QPointF(16.0, 20.2), 5.2, 5.2)
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(16.0, 20.2), 2.1, 2.1)

    @dv("audio-headphones", "headphone audio-headset headset hands-free")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.2, 10.6, 2.1, 68)
        band = arc_path(16.0, 15.6, 9.6, 0, 180, 2.8)
        p.setPen(QPen(c("#484c56"), 0.9))
        p.setBrush(vgrad(4.5, 16.0, (0.0, "#ffffff"), (0.5, "#cfd5e0"), (1.0, "#7c8290")))
        p.drawPath(band)
        for cx in (6.8, 25.2):
            p.setPen(QPen(c("#22252c"), 0.95))
            p.setBrush(hgrad(cx - 3.0, cx + 3.0, (0.0, "#686e7c"), (0.4, "#2c303a"), (1.0, "#16181e")))
            p.drawRoundedRect(QRectF(cx - 2.8, 14.4, 5.6, 10.6), 2.4, 2.4)

    @dv("audio-input-microphone", "microphone audio-input-line")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.4, 8.6, 2.0, 68)
        # Studio silver capsule microphone on chrome stand
        p.setPen(QPen(c("#4c505a"), 0.95))
        p.setBrush(hgrad(11.5, 20.5, (0.0, "#9aa0ac"), (0.42, "#ffffff"), (1.0, "#6e7482")))
        p.drawRoundedRect(QRectF(11.6, 4.0, 8.8, 14.4), 4.4, 4.4)
        if not sm:
            p.setPen(QPen(QColor(60, 65, 75, 120), 0.7))
            for yy in range(7, 15, 2):
                p.drawLine(QPointF(12.4, yy), QPointF(19.6, yy))
        cradle = U(arc_path(16.0, 14.0, 6.8, 180, 180, 1.8), rr(14.9, 20.6, 2.2, 5.4), rr(10.4, 25.4, 11.2, 2.2, 1.0))
        p.setPen(QPen(c("#4c505a"), 0.85))
        p.setBrush(c("#cfd5e0"))
        p.drawPath(cradle)

    @dv("speaker", "hifi")
    def _(p, sm):
        # 10.2 Apple Pro Speaker clear-acrylic sphere with black acoustic cone
        glass_disc(p, 16.0, 15.8, 12.0, "clear")
        p.setPen(QPen(c("#20232a"), 0.9))
        p.setBrush(rgrad(16.0, 15.8, 7.6, (0.0, "#565b68"), (0.6, "#262932"), (1.0, "#12141a")))
        p.drawEllipse(QPointF(16.0, 15.8), 7.4, 7.4)
        p.setBrush(vgrad(12.8, 18.8, (0.0, "#ffffff"), (1.0, "#9aa2b0")))
        p.drawEllipse(QPointF(16.0, 15.8), 2.8, 2.8)

    @dv("audio-card", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.8, 12.2, 2.1, 68)
        p.setPen(QPen(c("#1d5428"), 1.0))
        p.setBrush(vgrad(7.5, 24.5, (0.0, "#3ea854"), (1.0, "#1f7432")))
        p.drawRoundedRect(QRectF(4.4, 8.2, 22.8, 16.2), 1.4, 1.4)
        p.setPen(QPen(c("#585d68"), 1.2))
        p.drawLine(QPointF(4.4, 6.0), QPointF(4.4, 26.8))
        paint_music_notes(p, 16.4, 16.2, 0.7, "amber")

    @dv("input-keyboard", "")
    def _(p, sm):
        # 10.2 translucent acrylic Apple Pro Keyboard
        floor_shadow(p, 16.0, 26.6, 13.4, 2.2, 68)
        kb = poly((3.6, 10.2), (28.4, 10.2), (30.0, 24.4), (2.0, 24.4), round_=1.4)
        p.setPen(QPen(c("#686e7c"), 1.0))
        p.setBrush(vgrad(10.2, 24.4, (0.0, "#ffffff"), (0.5, "#e6eaf2"), (1.0, "#c4cbd8")))
        p.drawPath(kb)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#2c3038"))
            for row, yy in enumerate((12.4, 15.6, 18.8)):
                for col in range(7):
                    p.drawRoundedRect(QRectF(4.8 + col * 3.2 + row * 0.2, yy, 2.4, 2.2), 0.4, 0.4)
            p.drawRoundedRect(QRectF(9.2, 21.6, 13.6, 1.8), 0.4, 0.4)

    @dv("input-mouse", "")
    def _(p, sm):
        # 10.2 elliptical glossy Apple Pro Mouse (pearl/graphite optical shell)
        floor_shadow(p, 16.0, 28.6, 8.4, 2.2, 72)
        p.setPen(QPen(c("#8c92a0"), 1.2, Qt.SolidLine, Qt.RoundCap))
        p.drawPath(arc_path(18.2, 4.2, 2.8, 90, 120, 1.1))
        body = ellipse(16.0, 17.0, 7.8, 10.8)
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(6.2, 27.8, (0.0, "#ffffff"), (0.45, "#e8ecf4"), (0.85, "#bfc6d4"), (1.0, "#eef2f8")))
        p.drawPath(body)
        p.setClipPath(body)
        lens = QRectF(10.6, 7.2, 10.8, 9.2)
        p.setBrush(vgrad(7.2, 16.4, (0.0, (255, 255, 255, 240)), (1.0, (255, 255, 255, 0))))
        p.drawEllipse(lens)
        p.restore()
        p.setPen(QPen(c("#686e7c"), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(body)
        # Translucent scroll pill
        p.setBrush(c("#8492a8"))
        p.drawRoundedRect(QRectF(15.0, 9.2, 2.0, 4.4), 1.0, 1.0)

    @dv("input-gaming", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.6, 12.2, 2.2, 68)
        pad = U(rr(4.8, 9.6, 22.4, 11.2, 5.2), circ(7.8, 20.0, 4.4), circ(24.2, 20.0, 4.4))
        paint_gel_shape(p, pad, 9.6, 24.4, "clear")
        p.setPen(Qt.NoPen)
        p.setBrush(c("#22252c"))
        p.drawPath(plus_path(10.2, 15.2, 2.8, 1.8))
        glass_disc(p, 20.6, 14.0, 1.7, "red", shadow=False)
        glass_disc(p, 23.2, 16.4, 1.7, "blue", shadow=False)

    @dv("input-tablet", "tablet")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.8, 12.8, 2.1, 68)
        p.setPen(QPen(c("#585e6a"), 1.0))
        p.setBrush(vgrad(7.2, 26.2, (0.0, "#f4f6fa"), (1.0, "#bfc6d4")))
        p.drawRoundedRect(QRectF(3.2, 7.6, 25.6, 18.4), 2.0, 2.0)
        p.setPen(QPen(c("#8890a0"), 0.85))
        p.setBrush(c("#dfe6f2"))
        p.drawRect(QRectF(6.2, 10.2, 19.6, 13.2))
        from .materials import paint_pencil
        paint_pencil(p, 20.5, 13.8, 18.5, 3.6, 36.0, shadow=False, chrome=True)

    @dv("camera-photo", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.8, 12.4, 2.2, 72)
        p.setPen(QPen(c("#4e525c"), 0.9))
        p.setBrush(c("#cfd5e0"))
        p.drawRoundedRect(QRectF(7.2, 6.8, 5.6, 3.0), 0.8, 0.8)
        body = QRectF(3.6, 9.0, 24.8, 17.4)
        p.setBrush(vgrad(9.0, 26.4, (0.0, "#ffffff"), (0.45, "#d8dee8"), (1.0, "#969ca8")))
        p.drawRoundedRect(body, 2.4, 2.4)
        # Glass camera lens barrel
        p.setBrush(c("#2c3038"))
        p.drawEllipse(QPointF(17.2, 17.8), 6.4, 6.4)
        glass_disc(p, 17.2, 17.8, 4.6, "blue", shadow=False)
        if not sm:
            p.setPen(QPen(c("#788090"), 0.7))
            p.setBrush(c("#fffbe0"))
            p.drawRoundedRect(QRectF(6.0, 11.2, 4.6, 2.6), 0.5, 0.5)

    @dv("camera-video", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.8, 12.2, 2.2, 70)
        p.setPen(QPen(c("#484c56"), 1.0))
        p.setBrush(vgrad(9.2, 25.8, (0.0, "#f4f6fa"), (0.5, "#c8cfd8"), (1.0, "#858c98")))
        p.drawRoundedRect(QRectF(3.4, 9.6, 18.4, 15.6), 2.4, 2.4)
        lens_cone = poly((21.4, 13.2), (28.6, 10.4), (28.6, 24.4), (21.4, 21.6), round_=0.8)
        p.setBrush(vgrad(10.4, 24.4, (0.0, "#686e7c"), (1.0, "#262932")))
        p.drawPath(lens_cone)
        glass_disc(p, 8.2, 14.0, 2.0, "red", shadow=False)

    @dv("camera-web", "webcam")
    def _(p, sm):
        # Iconic 2003 Apple iSight cylindrical perforated-aluminum FireWire webcam!
        floor_shadow(p, 16.0, 28.5, 9.2, 2.1, 72)
        p.setPen(QPen(c("#585e6a"), 0.95))
        p.setBrush(hgrad(12.5, 19.5, (0.0, "#b4bac6"), (0.45, "#ffffff"), (1.0, "#868c9a")))
        p.drawRect(QRectF(14.2, 21.0, 3.6, 5.2))
        p.drawEllipse(QRectF(9.6, 24.8, 12.8, 3.2))
        cyl = QRectF(9.4, 4.0, 13.2, 18.0)
        p.setBrush(hgrad(9.4, 22.6, (0.0, "#9ca2ae"), (0.38, "#ffffff"), (0.72, "#cfd5e0"), (1.0, "#7c8290")))
        p.drawRoundedRect(cyl, 3.4, 3.4)
        p.setBrush(c("#1e2026"))
        p.drawEllipse(QPointF(16.0, 12.2), 4.8, 4.8)
        glass_disc(p, 16.0, 12.2, 3.3, "blue", shadow=False)

    @dv("scanner", "")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.2, 12.6, 2.2, 72)
        base = poly((4.2, 16.4), (27.8, 16.4), (29.2, 26.4), (2.8, 26.4), round_=1.0)
        p.setPen(QPen(c("#545a66"), 1.0))
        p.setBrush(vgrad(16.4, 26.4, (0.0, "#f4f6fa"), (1.0, "#aeb6c4")))
        p.drawPath(base)
        glass_bed = poly((6.4, 17.2), (25.6, 17.2), (26.6, 23.6), (5.4, 23.6))
        p.setBrush(vgrad(17.2, 23.6, (0.0, "#9ce8ff"), (0.5, "#e8fbff"), (1.0, "#72c4f8")))
        p.drawPath(glass_bed)
        # Raised scanner lid at angle
        lid = poly((5.6, 5.2), (26.4, 5.2), (27.6, 16.4), (4.4, 16.4), round_=0.8)
        p.setBrush(vgrad(5.2, 16.4, (0.0, "#ffffff"), (1.0, "#cfd5e0")))
        p.drawPath(lid)

    @dv("printer", "printer-laser")
    def _(p, sm):
        # 10.2 front-on silver/white desktop printer (ch11-203-003.png)
        floor_shadow(p, 16.0, 28.6, 12.2, 2.3, 74)
        p.setPen(QPen(c("#4e525a"), 0.9))
        p.setBrush(c("#686d78"))
        p.drawRoundedRect(QRectF(8.2, 5.2, 15.6, 7.5), 1.0, 1.0)
        p.setPen(QPen(c("#8c929e"), 0.9))
        p.setBrush(vgrad(3.0, 13.0, (0.0, "#ffffff"), (1.0, "#e2e6ee")))
        p.drawRect(QRectF(9.6, 3.2, 12.8, 9.5))
        body = QRectF(3.6, 11.4, 24.8, 12.4)
        p.setPen(QPen(c("#5d626c"), 1.0))
        p.setBrush(vgrad(11.4, 23.8, (0.0, "#f9fafd"), (0.45, "#e6e9f0"), (0.8, "#b8bec8"), (1.0, "#8f95a0")))
        p.drawRoundedRect(body, 2.8, 2.8)
        hood = QRectF(7.6, 11.6, 16.8, 6.2)
        p.setPen(QPen(c("#2d3036"), 0.9))
        p.setBrush(vgrad(11.6, 17.8, (0.0, "#4c5058"), (0.36, "#cfd4de"), (0.55, "#2f3238"), (1.0, "#585d66")))
        p.drawRoundedRect(hood, 1.4, 1.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#48b828"))
        p.drawEllipse(QPointF(25.8, 16.5), 0.9, 0.9)
        p.setBrush(c("#26282e"))
        p.drawRect(QRectF(7.4, 20.6, 17.2, 2.4))
        out_sheet = poly((8.8, 21.4), (23.2, 21.4), (24.6, 28.4), (7.4, 28.4))
        p.setPen(QPen(c("#858b98"), 0.9))
        p.setBrush(vgrad(21.4, 28.4, (0.0, "#dfe3ec"), (0.3, "#ffffff"), (1.0, "#f5f7fa")))
        p.drawPath(out_sheet)

    @dv("phone", "smartphone pda handset phone-openmoko-freerunner")
    def _(p, sm):
        floor_shadow(p, 16.0, 28.5, 8.4, 2.1, 72)
        body = QRectF(8.2, 3.0, 15.6, 24.8)
        p.setPen(QPen(c("#383c46"), 1.0))
        p.setBrush(hgrad(8.2, 23.8, (0.0, "#cfd5e0"), (0.5, "#ffffff"), (1.0, "#a8b0be")))
        p.drawRoundedRect(body, 2.6, 2.6)
        scr = QRectF(9.8, 5.6, 12.4, 16.4)
        p.setPen(QPen(c("#162844"), 0.85))
        p.setBrush(vgrad(5.6, 22.0, (0.0, "#1c62c8"), (1.0, "#7cd0ff")))
        p.drawRoundedRect(scr, 1.0, 1.0)
        p.setPen(QPen(c("#788090"), 0.8))
        p.setBrush(c("#e8ecf4"))
        p.drawEllipse(QPointF(16.0, 24.8), 1.6, 1.6)

    @dv("cpu", "")
    def _(p, sm):
        # PowerPC G4 ceramic/silver die microprocessor chip with gold edge pins
        floor_shadow(p, 16.0, 28.2, 11.4, 2.2, 70)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#e2b232"))
            for k in range(7, 26, 3):
                p.drawRect(QRectF(k - 0.6, 3.4, 1.3, 25.2))
                p.drawRect(QRectF(3.4, k - 0.6, 25.2, 1.3))
        p.setPen(QPen(c("#1b4d2e"), 1.0))
        p.setBrush(vgrad(5.2, 26.8, (0.0, "#358852"), (1.0, "#1c5832")))
        p.drawRoundedRect(QRectF(5.2, 5.2, 21.6, 21.6), 1.8, 1.8)
        p.setPen(QPen(c("#585e6a"), 0.95))
        p.setBrush(vgrad(9.2, 22.8, (0.0, "#ffffff"), (0.5, "#cfd5e0"), (1.0, "#8e94a2")))
        p.drawRoundedRect(QRectF(9.2, 9.2, 13.6, 13.6), 1.4, 1.4)

    @dv("battery", "")
    def _(p, sm):
        # Glossy 3D silver-and-Aqua cylindrical battery cell
        floor_shadow(p, 16.0, 28.5, 8.8, 2.2, 72)
        p.setPen(QPen(c("#545a66"), 0.9))
        p.setBrush(hgrad(13.2, 18.8, (0.0, "#9ca2ae"), (0.45, "#ffffff"), (1.0, "#7c8290")))
        p.drawRoundedRect(QRectF(13.2, 3.4, 5.6, 3.0), 0.8, 0.8)
        shell = QRectF(8.8, 5.8, 14.4, 21.8)
        p.setPen(QPen(c("#1b4e14"), 1.0))
        p.setBrush(hgrad(8.8, 23.2, (0.0, "#389c28"), (0.38, "#9cff78"), (0.72, "#46be32"), (1.0, "#247618")))
        p.drawRoundedRect(shell, 2.2, 2.2)
        p.setPen(QPen(c("#545a66"), 0.9))
        p.setBrush(hgrad(8.8, 23.2, (0.0, "#9ca2ae"), (0.42, "#ffffff"), (1.0, "#787e8c")))
        p.drawRoundedRect(QRectF(8.8, 5.8, 14.4, 5.4), 1.8, 1.8)

    @dv("modem", "network-wired")
    def _(p, sm):
        # Brushed-silver RJ-45 Ethernet / Modem jack + glowing Aqua blue connector
        floor_shadow(p, 16.0, 28.0, 11.4, 2.1, 70)
        p.setPen(QPen(c("#545a66"), 1.0))
        p.setBrush(vgrad(5.0, 26.0, (0.0, "#fafafa"), (1.0, "#cfd5e0")))
        p.drawRoundedRect(QRectF(4.6, 5.2, 22.8, 21.2), 2.2, 2.2)
        jack = U(rr(9.2, 11.6, 13.6, 9.6, 0.8), rr(12.2, 9.2, 7.6, 3.4, 0.5))
        p.setPen(QPen(c("#1e222a"), 0.9))
        p.setBrush(c("#2a2e38"))
        p.drawPath(jack)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#f0c238"))
            for px in range(11, 22, 2):
                p.drawRect(QRectF(px, 17.8, 1.0, 2.8))

    @dv("network-wired-disconnected", "network-offline")
    def _(p, sm):
        devices_map["modem"](p, sm)
        mini_badge_disc(p, 23.6, 21.8, 5.6, "red", U(line(21.4, 19.6, 25.8, 24.0, 2.0), line(25.8, 19.6, 21.4, 24.0, 2.0)))

    def paint_airport_saucer(p, bars=3):
        """Classic 2002 snow-white UFO-shaped Apple AirPort Base Station + glowing blue signal arcs."""
        floor_shadow(p, 16.0, 28.2, 12.2, 2.2, 72)
        saucer = ellipse(16.0, 22.4, 12.2, 4.6)
        dome = ellipse(16.0, 20.6, 9.2, 4.2)
        p.setPen(QPen(c("#788090"), 1.0))
        p.setBrush(vgrad(17.8, 27.0, (0.0, "#ffffff"), (0.6, "#dfe4ee"), (1.0, "#aeb6c4")))
        p.drawPath(saucer)
        p.setBrush(vgrad(16.4, 24.8, (0.0, "#ffffff"), (1.0, "#e6eaf2")))
        p.drawPath(dome)
        # Status LEDs on saucer rim
        for lx, col in ((12.6, "#58d838"), (16.0, "#3898ff" if bars > 0 else "#9aa2b0"), (19.4, "#58d838" if bars > 1 else "#9aa2b0")):
            p.setPen(Qt.NoPen)
            p.setBrush(c(col))
            p.drawEllipse(QPointF(lx, 23.6), 0.85, 0.85)
        # Aqua blue radio wave arcs above dome
        for idx, rad in enumerate((4.6, 8.0, 11.4)):
            arc_w = arc_path(16.0, 16.8, rad, 48, 84, 2.1)
            if idx < bars:
                paint_gel_shape(p, arc_w, 4.2, 16.8, "blue", shadow=False)
            else:
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(130, 142, 160, 85))
                p.drawPath(arc_w)

    @dv("network-wireless", "network-wireless-100 network-wireless-connected-100 network-wireless-signal-excellent network-wireless-80 network-wireless-connected-80 network-wireless-connected-75")
    def _(p, sm):
        paint_airport_saucer(p, 3)

    @dv("network-wireless-60", "network-wireless-connected-60 network-wireless-signal-good network-wireless-connected-50 network-wireless-40 network-wireless-connected-40 network-wireless-signal-ok")
    def _(p, sm):
        paint_airport_saucer(p, 2)

    @dv("network-wireless-20", "network-wireless-connected-25 network-wireless-connected-20 network-wireless-signal-weak network-wireless-acquiring")
    def _(p, sm):
        paint_airport_saucer(p, 1)

    @dv("network-wireless-00", "network-wireless-connected-00 network-wireless-disconnected network-wireless-signal-none")
    def _(p, sm):
        paint_airport_saucer(p, 0)

    devices_map = {n: fn for n, _, fn in devices}
    return devices
