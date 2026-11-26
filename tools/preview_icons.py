#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Contact sheet of the Oxygen Pinstripe symbolic icons: 16px and 32px on window pinstripes,
16px white on the glossy selection, and the old Oxygen/Breeze icon for comparison.

    python3 tools/preview_icons.py out.png
"""
import glob
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME = os.path.join(ROOT, "icons", "Oxygen-Pinstripe")
SHOW = sys.argv[2].split(",") if len(sys.argv) > 2 else None


def stripes():
    img = QImage(8, 4, QImage.Format_RGB32)
    for y, v in enumerate((255, 238, 230, 238)):
        for x in range(8):
            img.setPixelColor(x, y, QColor(v, v, v))
    return QBrush(img)


def recolored(path, color):
    data = open(path).read().replace("color:#232629", f"color:{color}")
    return QSvgRenderer(QByteArray(data.encode()))


def old_icon(name):
    for base in ("/usr/share/icons/oxygen", "/usr/share/icons/breeze"):
        r = glob.glob(f"{base}/**/{name}-symbolic.svg", recursive=True)
        if r:
            return r[0]
    return None


def main():
    app = QGuiApplication(sys.argv)
    files = sorted(glob.glob(os.path.join(THEME, "symbolic", "*", "*.svg")))
    seen, picked = set(), []
    for f in files:
        name = os.path.basename(f)[:-len("-symbolic.svg")]
        key = open(f).read()
        if key in seen and not SHOW:
            continue  # one cell per distinct glyph
        seen.add(key)
        if SHOW and name not in SHOW:
            continue
        picked.append((name, f))
    cols = 12
    cw, ch = 96, 92
    rows = (len(picked) + cols - 1) // cols
    img = QImage(cols * cw, rows * ch, QImage.Format_ARGB32)
    p = QPainter(img)
    p.fillRect(img.rect(), stripes())
    font = QFont("Luxi Sans")
    font.setPixelSize(9)
    p.setFont(font)
    for i, (name, f) in enumerate(picked):
        x, y = (i % cols) * cw, (i // cols) * ch
        recolored(f, "#1a1a1a").render(p, QRectF(x + 6, y + 6, 16, 16))
        recolored(f, "#1a1a1a").render(p, QRectF(x + 28, y + 6, 32, 32))
        sel = QRectF(x + 64, y + 6, 26, 22)
        g = QLinearGradient(sel.topLeft(), sel.bottomLeft())
        for pos, c in ((0, "#4a84de"), (0.48, "#2668d6"), (0.52, "#2c74e2"), (1, "#80caff")):
            g.setColorAt(pos, QColor(c))
        p.fillRect(sel, g)
        recolored(f, "#ffffff").render(p, QRectF(x + 69, y + 9, 16, 16))
        old = old_icon(name)
        if old:
            QSvgRenderer(old).render(p, QRectF(x + 70, y + 32, 16, 16))
            p.setPen(QColor(150, 150, 150))
            p.drawText(QRectF(x + 62, y + 48, 32, 10), Qt.AlignCenter, "old")
        p.setPen(QColor(40, 40, 40))
        p.drawText(QRectF(x + 2, y + 60, cw - 4, 30), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere, name)
    p.end()
    img.save(sys.argv[1] if len(sys.argv) > 1 else "icons.png")
    print("wrote", len(picked), "glyphs")


if __name__ == "__main__":
    main()
