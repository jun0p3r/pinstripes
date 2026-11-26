#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Contact sheet of the Oxygen Pinstripe icon theme:
1. Full-colour Mac OS X 10.2 Aqua action icons (32px and 16px on window pinstripes, with old
   Oxygen/Breeze icon for comparison).
2. Symbolic & menu-extra glyphs (16px and 32px on pinstripes, 16px white on glossy selection,
   and old symbolic icon for comparison).

    python3 tools/preview_icons.py out.png
"""
import glob
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPixmap
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


def old_symbolic(name):
    for base in ("/usr/share/icons/oxygen", "/usr/share/icons/breeze"):
        r = glob.glob(f"{base}/**/{name}-symbolic.svg", recursive=True)
        if r:
            return r[0]
    return None


def old_action(name):
    for p in (f"/usr/share/icons/oxygen/base/32x32/actions/{name}.png",
              f"/usr/share/icons/oxygen/base/16x16/actions/{name}.png"):
        if os.path.exists(p):
            return p
    return None


def main():
    app = QGuiApplication(sys.argv)

    # 1. Distinct full-colour 10.2 action icons (skip symlinks)
    act_files = sorted(
        f for f in glob.glob(os.path.join(THEME, "32x32", "actions", "*.png"))
        if not os.path.islink(f) and (not SHOW or os.path.basename(f)[:-4] in SHOW)
    )
    actions = [(os.path.basename(f)[:-4], f, f.replace("/32x32/", "/16x16/")) for f in act_files]

    # 2. Distinct symbolic glyphs
    sym_files = sorted(glob.glob(os.path.join(THEME, "symbolic", "*", "*.svg")))
    seen, symbolics = set(), []
    for f in sym_files:
        name = os.path.basename(f)[:-len("-symbolic.svg")]
        key = open(f).read()
        if key in seen and not SHOW:
            continue
        seen.add(key)
        if SHOW and name not in SHOW:
            continue
        symbolics.append((name, f))

    cols = 12
    cw, ch = 96, 92
    hdr_h = 34
    act_rows = (len(actions) + cols - 1) // cols if actions else 0
    sym_rows = (len(symbolics) + cols - 1) // cols if symbolics else 0
    total_h = (hdr_h + act_rows * ch if act_rows else 0) + (hdr_h + sym_rows * ch if sym_rows else 0) + 8

    img = QImage(cols * cw, max(92, total_h), QImage.Format_ARGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    p.fillRect(img.rect(), stripes())

    title_font = QFont()
    title_font.setFamilies(["Lucida Grande", "Luxi Sans", "DejaVu Sans"])
    title_font.setBold(True)
    title_font.setPixelSize(13)
    font = QFont()
    font.setFamilies(["Lucida Grande", "Luxi Sans", "DejaVu Sans"])
    font.setPixelSize(9)

    y_off = 0
    if actions:
        p.setFont(title_font)
        p.setPen(QColor(20, 20, 22))
        p.drawText(QRectF(12, y_off + 8, cols * cw - 24, 20), Qt.AlignVCenter,
                   f"Mac OS X 10.2 Action Icons ({len(actions)} master artworks, 32 px & 16 px vs old Oxygen)")
        p.fillRect(QRectF(12, y_off + 29, cols * cw - 24, 1), QColor(163, 163, 163))
        p.fillRect(QRectF(12, y_off + 30, cols * cw - 24, 1), QColor(255, 255, 255, 190))
        y_off += hdr_h

        p.setFont(font)
        for i, (name, f32, f16) in enumerate(actions):
            x, y = (i % cols) * cw, y_off + (i // cols) * ch
            p.drawPixmap(x + 8, y + 8, 32, 32, QPixmap(f32))
            if os.path.exists(f16):
                p.drawPixmap(x + 46, y + 16, 16, 16, QPixmap(f16))
            old = old_action(name)
            if old:
                p.drawPixmap(x + 70, y + 12, 20, 20, QPixmap(old))
                p.setPen(QColor(135, 135, 135))
                p.drawText(QRectF(x + 64, y + 34, 32, 10), Qt.AlignCenter, "old")
            p.setPen(QColor(35, 35, 35))
            p.drawText(QRectF(x + 2, y + 54, cw - 4, 34), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere, name)
        y_off += act_rows * ch + 6

    if symbolics:
        p.setFont(title_font)
        p.setPen(QColor(20, 20, 22))
        p.drawText(QRectF(12, y_off + 6, cols * cw - 24, 20), Qt.AlignVCenter,
                   f"Menu Extras & Symbolic Glyphs ({len(symbolics)} distinct solid shapes, recolourable)")
        p.fillRect(QRectF(12, y_off + 27, cols * cw - 24, 1), QColor(163, 163, 163))
        p.fillRect(QRectF(12, y_off + 28, cols * cw - 24, 1), QColor(255, 255, 255, 190))
        y_off += hdr_h

        p.setFont(font)
        for i, (name, f) in enumerate(symbolics):
            x, y = (i % cols) * cw, y_off + (i // cols) * ch
            recolored(f, "#1a1a1a").render(p, QRectF(x + 6, y + 6, 16, 16))
            recolored(f, "#1a1a1a").render(p, QRectF(x + 28, y + 6, 32, 32))
            sel = QRectF(x + 64, y + 6, 26, 22)
            g = QLinearGradient(sel.topLeft(), sel.bottomLeft())
            for pos, c in ((0, "#4a84de"), (0.48, "#2668d6"), (0.52, "#2c74e2"), (1, "#80caff")):
                g.setColorAt(pos, QColor(c))
            p.fillRect(sel, g)
            recolored(f, "#ffffff").render(p, QRectF(x + 69, y + 9, 16, 16))
            old = old_symbolic(name)
            if old:
                QSvgRenderer(old).render(p, QRectF(x + 70, y + 32, 16, 16))
                p.setPen(QColor(150, 150, 150))
                p.drawText(QRectF(x + 62, y + 48, 32, 10), Qt.AlignCenter, "old")
            p.setPen(QColor(40, 40, 40))
            p.drawText(QRectF(x + 2, y + 60, cw - 4, 30), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere, name)

    p.end()
    img.save(sys.argv[1] if len(sys.argv) > 1 else "icons.png")
    print(f"wrote {len(actions)} action icons + {len(symbolics)} symbolic glyphs")


if __name__ == "__main__":
    main()
