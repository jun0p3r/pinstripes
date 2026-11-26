#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Offscreen preview of the Pinstripe Plasma style.

Draws the theme's frames the way Plasma's FrameSvg does (fixed corners, tiled borders unless
hint-stretch-borders, stretched centre unless hint-tile-center) into a mock desktop, so the
SVGs can be checked without switching the running desktop's theme.

    python3 tools/preview_plasma.py out.png [wallpaper.jpg]
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPen, QPixmap, QRadialGradient
from PySide6.QtSvg import QSvgRenderer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME = os.path.join(ROOT, "plasma", "pinstripe")
PINSTRIPE_ICONS = os.path.join(ROOT, "icons", "Oxygen-Pinstripe")
ICONS = "/usr/share/icons/oxygen/base"


class FrameSvg:
    def __init__(self, path):
        self.r = QSvgRenderer(path)
        assert self.r.isValid(), path

    def has(self, eid):
        return self.r.elementExists(eid)

    def size(self, eid):
        return self.r.boundsOnElement(eid).size()

    def margins(self, prefix):
        pre = prefix + "-" if prefix else ""
        def m(side, horizontal):
            hint = f"{pre}hint-{side}-margin"
            if self.has(hint):
                s = self.size(hint)
                return s.width() if horizontal else s.height()
            el = {"top": "top", "bottom": "bottom", "left": "left", "right": "right"}[side]
            s = self.size(pre + el)
            return s.width() if horizontal else s.height()
        return m("left", True), m("top", False), m("right", True), m("bottom", False)

    def element(self, p, eid, rect, tile=False):
        if not self.has(eid) or rect.width() <= 0 or rect.height() <= 0:
            return
        if not tile:
            self.r.render(p, eid, rect)
            return
        s = self.size(eid)
        img = QImage(int(s.width() * 2), int(s.height() * 2), QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        ip = QPainter(img)
        self.r.render(ip, eid, QRectF(0, 0, img.width(), img.height()))
        ip.end()
        img.setDevicePixelRatio(2)
        p.save()
        p.setClipRect(rect)
        p.drawTiledPixmap(rect, QPixmap.fromImage(img), QPointF(0, 0))
        p.restore()

    def paint(self, p, rect, prefix="", edges="tlrb"):
        pre = prefix + "-" if prefix and self.has(prefix + "-center") else ""
        tl = self.size(pre + "topleft")
        br = self.size(pre + "bottomright")
        l = tl.width() if "l" in edges else 0
        t = tl.height() if "t" in edges else 0
        r = br.width() if "r" in edges else 0
        b = br.height() if "b" in edges else 0
        stretch = self.has(pre + "hint-stretch-borders")
        tile_center = self.has(pre + "hint-tile-center")
        x0, y0, x1, y1 = rect.left(), rect.top(), rect.right(), rect.bottom()
        cw, ch = rect.width() - l - r, rect.height() - t - b
        if t and l:
            self.element(p, pre + "topleft", QRectF(x0, y0, l, t))
        if t and r:
            self.element(p, pre + "topright", QRectF(x1 - r, y0, r, t))
        if b and l:
            self.element(p, pre + "bottomleft", QRectF(x0, y1 - b, l, b))
        if b and r:
            self.element(p, pre + "bottomright", QRectF(x1 - r, y1 - b, r, b))
        if t:
            self.element(p, pre + "top", QRectF(x0 + l, y0, cw, t), tile=not stretch)
        if b:
            self.element(p, pre + "bottom", QRectF(x0 + l, y1 - b, cw, b), tile=not stretch)
        if l:
            self.element(p, pre + "left", QRectF(x0, y0 + t, l, ch), tile=not stretch)
        if r:
            self.element(p, pre + "right", QRectF(x1 - r, y0 + t, r, ch), tile=not stretch)
        self.element(p, pre + "center", QRectF(x0 + l, y0 + t, cw, ch), tile=tile_center)


def icon(name, size=48):
    for base in (PINSTRIPE_ICONS, ICONS):
        for cat in ("apps", "places", "categories", "actions", "status", "devices", "mimetypes"):
            f = os.path.join(base, f"{size}x{size}", cat, name + ".png")
            if os.path.exists(f):
                return QPixmap(f)
    return QPixmap()


def main():
    app = QGuiApplication(sys.argv)
    out = sys.argv[1] if len(sys.argv) > 1 else "plasma-preview.png"
    wall = sys.argv[2] if len(sys.argv) > 2 else ""
    W, H = 960, 600
    img = QImage(W, H, QImage.Format_ARGB32_Premultiplied)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    if wall and os.path.exists(wall):
        pm = QPixmap(wall).scaled(W, H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        p.drawPixmap(0, 0, pm)
    else:
        bg = QRadialGradient(QPointF(W * 0.52, H * 0.14), W * 0.72)
        bg.setColorAt(0.0, QColor(24, 188, 242))
        bg.setColorAt(0.48, QColor(18, 132, 204))
        bg.setColorAt(1.0, QColor(12, 82, 152))
        p.fillRect(0, 0, W, H, bg)

    font = QFont()
    font.setFamilies(["Lucida Grande", "Luxi Sans", "DejaVu Sans"])  # 10.2 used Lucida Grande 13pt
    font.setPixelSize(13)
    bold = QFont(font)
    bold.setBold(True)
    small = QFont(font)
    small.setPixelSize(11)

    panel = FrameSvg(os.path.join(THEME, "widgets", "panel-background.svg"))
    dialog = FrameSvg(os.path.join(THEME, "dialogs", "background.svg"))
    widget = FrameSvg(os.path.join(THEME, "widgets", "background.svg"))
    tip = FrameSvg(os.path.join(THEME, "widgets", "tooltip.svg"))
    button = FrameSvg(os.path.join(THEME, "widgets", "button.svg"))
    lineedit = FrameSvg(os.path.join(THEME, "widgets", "lineedit.svg"))
    viewitem = FrameSvg(os.path.join(THEME, "widgets", "viewitem.svg"))
    tasks = FrameSvg(os.path.join(THEME, "widgets", "tasks.svg"))
    menubaritem = FrameSvg(os.path.join(THEME, "widgets", "menubaritem.svg"))

    # top panel: the menu bar
    mb = QRectF(0, 0, W, 24)
    panel.paint(p, QRectF(0, 24, W, 8), "north-shadow", edges="b") if panel.has("north-shadow-bottom") else None
    panel.paint(p, mb, "north", edges="b")
    x = 14
    p.setPen(Qt.black)
    p.setFont(bold)
    p.drawText(QRectF(x, 0, 80, 23), Qt.AlignVCenter, "Dolphin")
    x += 78
    p.setFont(font)
    items = ["File", "Edit", "View", "Go", "Window", "Help"]
    go_x = 0
    for it in items:
        w = p.fontMetrics().horizontalAdvance(it) + 20
        if it == "Go":
            go_x = x
            menubaritem.paint(p, QRectF(x, 0, w, 23), "pressed")
            p.setPen(Qt.white)
        p.drawText(QRectF(x, 0, w, 23), Qt.AlignCenter, it)
        p.setPen(Qt.black)
        x += w
    p.drawText(QRectF(W - 150, 0, 140, 23), Qt.AlignVCenter | Qt.AlignRight, "Fri 7:17 PM")
    # menu extras from the Oxygen Pinstripe icon theme
    tray = os.path.join(ROOT, "icons", "Oxygen-Pinstripe", "panel", "status")
    for i, n in enumerate(("notifications", "bluetooth-active", "battery-080-charging", "audio-volume-high", "network-wireless-signal-good")):
        f = os.path.join(tray, n + ".svg")
        if os.path.exists(f):
            data = open(f).read().replace("#232629", "#111111")
            QSvgRenderer(QByteArray(data.encode())).render(p, QRectF(W - 128 - i * 26, 3, 17, 17))

    # an application window drawn by the Pinstripe widget style (optional third argument)
    if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
        win = QPixmap(sys.argv[3])
        wx, wy = 300, 96
        tb = 22
        frame = QRectF(wx, wy, win.width(), win.height() + tb)
        dialog.paint(p, frame.adjusted(-12, -10, 12, 16), "shadow")
        # title bar: 10.2 pinstripes darkening towards the bottom, gel traffic lights
        for yy in range(tb):
            v = (255, 238, 230, 238)[yy % 4] - int(26 * yy / tb)
            p.fillRect(QRectF(wx, wy + yy, win.width(), 1), QColor(v, v, v))
        p.fillRect(QRectF(wx, wy + tb - 1, win.width(), 1), QColor(127, 127, 127))
        for i, (deep, mid, light) in enumerate((((176, 18, 10), (242, 70, 56), (255, 184, 168)),
                                                 ((194, 128, 0), (247, 193, 36), (255, 242, 176)),
                                                 ((44, 134, 18), (108, 203, 58), (216, 248, 168)))):
            cx, cy, rad = wx + 14 + i * 21, wy + 11, 6.5
            g = QRadialGradient(QPointF(cx, cy + 3), rad * 1.4)
            g.setColorAt(0, QColor(*light))
            g.setColorAt(0.5, QColor(*mid))
            g.setColorAt(1, QColor(*deep))
            p.setPen(QPen(QColor(deep[0] // 2, deep[1] // 2, deep[2] // 2), 1))
            p.setBrush(g)
            p.drawEllipse(QPointF(cx, cy), rad, rad)
            lens = QLinearGradient(QPointF(cx, cy - rad), QPointF(cx, cy))
            lens.setColorAt(0, QColor(255, 255, 255, 235))
            lens.setColorAt(1, QColor(255, 255, 255, 40))
            p.setPen(Qt.NoPen)
            p.setBrush(lens)
            p.drawEllipse(QRectF(cx - rad * 0.6, cy - rad + 1, rad * 1.2, rad * 0.85))
        p.setPen(Qt.black)
        p.setFont(font)
        p.drawText(QRectF(wx, wy, win.width(), tb), Qt.AlignCenter, "Home")
        p.drawPixmap(int(wx), int(wy + tb), win)
        p.setPen(QColor(0, 0, 0, 90))
        p.setBrush(Qt.NoBrush)
        p.drawRect(frame.adjusted(-0.5, -0.5, 0.5, 0.5))

    # a popup under "Go", laid out like an Aqua menu
    rows = [("go-home", "Home", "Ctrl+Shift+H"), ("computer", "Computer", "Ctrl+Shift+C"), ("network-workgroup", "Network", "Ctrl+Shift+K"),
            None, ("folder-documents", "Documents", ""), ("folder-download", "Downloads", ""), ("user-trash", "Trash", ""),
            None, ("go-jump", "Go to Folder…", "Ctrl+Shift+G")]
    rh = 22
    pop_h = sum(10 if r is None else rh for r in rows)
    ml, mt, mr, mbm = dialog.margins("")
    pop = QRectF(go_x, 23, 270, pop_h + mt + mbm)
    dialog.paint(p, pop.adjusted(-12, -10, 12, 16), "shadow")
    dialog.paint(p, pop)
    y = pop.top() + mt
    for i, row in enumerate(rows):
        if row is None:
            y += 10
            continue
        ic, label, sc = row
        r = QRectF(pop.left() + ml, y, pop.width() - ml - mr, rh)
        if i == 1:
            viewitem.paint(p, r, "selected")
            p.setPen(Qt.white)
        else:
            p.setPen(Qt.black)
        pm = icon(ic, 16)
        if not pm.isNull():
            p.drawPixmap(int(r.left() + 20), int(r.top() + 3), 16, 16, pm)
        p.setFont(font)
        p.drawText(r.adjusted(44, 0, -12, 0), Qt.AlignVCenter, label)
        if sc:
            p.drawText(r.adjusted(44, 0, -12, 0), Qt.AlignVCenter | Qt.AlignRight, sc)
        y += rh

    # a tray popup (volume) exercising tabs, slider, progress bar, radio buttons and a scroll bar
    scroll = FrameSvg(os.path.join(THEME, "widgets", "scrollbar.svg"))
    slider = FrameSvg(os.path.join(THEME, "widgets", "slider.svg"))
    meter = FrameSvg(os.path.join(THEME, "widgets", "bar_meter_horizontal.svg"))
    tabbar = FrameSvg(os.path.join(THEME, "widgets", "tabbar.svg"))
    radio = FrameSvg(os.path.join(THEME, "widgets", "radiobutton.svg"))
    tp = QRectF(W - 300, 23, 280, 214)
    dialog.paint(p, tp.adjusted(-12, -10, 12, 16), "shadow")
    dialog.paint(p, tp)
    x0, y0 = tp.left() + 14, tp.top() + 12
    # tabs centred over the 6-row blue accent strip; the active tab overlaps row 0 (#0057ae) so it morphs into the strip
    p.setFont(font)
    tab_ws = [p.fontMetrics().horizontalAdvance(lbl) + 24 for lbl in ("Devices", "Applications")]
    tx = tp.left() + (tp.width() - (sum(tab_ws) - 1)) / 2
    tabbar.paint(p, QRectF(tp.left() + 8, y0 + 23, tp.width() - 16, 9), "north-tab-bar")
    sel_r = None
    for i, (label, tw) in enumerate(zip(("Devices", "Applications"), tab_ws)):
        if i == 0:
            sel_r = QRectF(tx, y0, tw, 24)
        else:
            r = QRectF(tx, y0, tw, 23)
            tabbar.paint(p, r, "north-tab")
            p.setPen(Qt.black)
            p.drawText(r, Qt.AlignCenter, label)
        tx += tw - 1
    tabbar.paint(p, sel_r, "north-active-tab")
    p.setPen(Qt.black)
    p.drawText(QRectF(sel_r.left(), sel_r.top(), sel_r.width(), 23), Qt.AlignCenter, "Devices")
    y = y0 + 38
    p.drawText(QRectF(x0, y, 200, 18), Qt.AlignVCenter, "Speakers")
    y += 22
    groove = QRectF(x0, y + 7, 200, 6)
    slider.paint(p, groove, "groove")
    slider.paint(p, QRectF(groove.left(), groove.top(), 140, 6), "groove-highlight")
    slider.element(p, "horizontal-slider-shadow", QRectF(groove.left() + 140 - 10, groove.center().y() - 10, 21, 21))
    slider.element(p, "horizontal-slider-handle", QRectF(groove.left() + 140 - 8, groove.center().y() - 8.5, 17, 17))
    p.drawText(QRectF(groove.right() + 10, y, 50, 20), Qt.AlignVCenter, "70%")
    y += 30
    p.drawText(QRectF(x0, y, 200, 18), Qt.AlignVCenter, "Battery")
    y += 20
    meter.paint(p, QRectF(x0, y, 200, 16), "bar-inactive")
    meter.paint(p, QRectF(x0, y, 92, 16), "bar-active")
    y += 26
    for i, label in enumerate(("Analog stereo", "HDMI output")):
        radio.element(p, "shadow", QRectF(x0 - 2, y - 2, 22, 22))
        radio.element(p, "checked" if i == 0 else "normal", QRectF(x0, y, 18, 18))
        if i == 0:
            radio.element(p, "symbol", QRectF(x0 + 6, y + 5.5, 6, 6))
        p.setPen(Qt.black)
        p.drawText(QRectF(x0 + 26, y, 200, 18), Qt.AlignVCenter, label)
        y += 24
    sb = QRectF(tp.right() - 22, tp.top() + 46, 15, tp.height() - 58)
    scroll.paint(p, sb, "background-vertical")
    scroll.paint(p, QRectF(sb.left(), sb.top() + 6, 15, 60), "slider")

    # the Dock: flush with the bottom edge, as on 10.2
    names = ["system-file-manager", "utilities-terminal", "internet-web-browser", "kmail", "preferences-system", "help-browser", None, "user-trash-full"]
    iw, gap = 48, 10
    dock_w = sum(2 if n is None else iw for n in names) + gap * (len(names) - 1) + 28
    dock = QRectF((W - dock_w) / 2, H - 62, dock_w, 62)
    panel.paint(p, dock, "", edges="tlr")
    x = dock.left() + 14
    for i, n in enumerate(names):
        if n is None:
            p.fillRect(QRectF(x, dock.top() + 10, 1, 46), QColor(0, 0, 0, 80))
            p.fillRect(QRectF(x + 1, dock.top() + 10, 1, 46), QColor(255, 255, 255, 140))
            x += 2 + gap
            continue
        pm = icon(n, 48)
        if not pm.isNull():
            p.drawPixmap(int(x), int(dock.top() + 3), iw, iw, pm)
        if i in (0, 1, 4):
            # running apps: the theme's tasks frame draws the triangle (as Plasma would)
            tasks.paint(p, QRectF(x - 4, dock.top() + 2, iw + 8, dock.height() - 3), "focus" if i == 1 else "normal")
        if i == 1:
            t = QRectF(x + iw / 2 - 36, dock.top() - 30, 72, 20)
            tip.paint(p, t.adjusted(-6, -5, 6, 8), "shadow")
            tip.paint(p, t)
            p.setPen(Qt.black)
            p.setFont(small)
            p.drawText(t, Qt.AlignCenter, "Konsole")
        x += iw + gap
    p.end()
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
