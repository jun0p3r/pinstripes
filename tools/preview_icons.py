#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Contact sheet generator for the Oxygen Pinstripe Mac OS X 10.2 Aqua icon theme.

    python3 tools/preview_icons.py out.png [cat1,cat2,...]
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

CAT_TITLES = [
    ("places",     "Places & Folders (10.2 Aqua pinstriped folders, Home cottage, Desktop, Network, Mesh Trash)"),
    ("devices",    "Hardware & Removable Media (Studio Display, iBook, 3.5\" & FireWire/USB drives, iPod, iSight, CD/DVD)"),
    ("apps",       "User Applications & Utilities (Finder, TextEdit, Preview, Mail, Safari, Terminal, System Preferences)"),
    ("categories", "Application Categories & System Preferences Panes"),
    ("mimetypes",  "Document & Package Mimetypes (hovered curled sheets with integrated artwork & labels)"),
    ("status",     "Alerts, Weather, Presence & Status Icons"),
    ("emblems",    "Finder Badges & VCS Emblems"),
    ("emotes",     "iChat Glossy 3D Gel Emotes"),
    ("applets",    "Plasma Desktop Widget Icons"),
    ("actions",    "Toolbar & Menu Action Icons"),
]


def stripes():
    img = QImage(8, 4, QImage.Format_RGB32)
    for y, v in enumerate((255, 238, 230, 238)):
        for x in range(8):
            img.setPixelColor(x, y, QColor(v, v, v))
    return QBrush(img)


def recolored(path, color):
    data = open(path).read().replace("color:#232629", f"color:{color}")
    return QSvgRenderer(QByteArray(data.encode()))


def main():
    app = QGuiApplication(sys.argv)
    out_path = sys.argv[1] if len(sys.argv) > 1 else "icons.png"
    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else None

    cols = 12
    cw, ch = 96, 90
    hdr_h = 34

    sections = []
    for cat, title in CAT_TITLES:
        if only and cat not in only:
            continue
        pref_sz = "48x48" if os.path.isdir(os.path.join(THEME, "48x48", cat)) else "32x32"
        files = sorted(
            f for f in glob.glob(os.path.join(THEME, pref_sz, cat, "*.png"))
            if not os.path.islink(f)
        )
        if not files:
            continue
        all_links = sum(1 for f in glob.glob(os.path.join(THEME, "32x32", cat, "*.png")) if os.path.islink(f))
        entries = []
        for f in files:
            name = os.path.basename(f)[:-4]
            f16 = os.path.join(THEME, "16x16", cat, f"{name}.png")
            entries.append((name, f, f16))
        sections.append((f"{title} — {len(entries)} masters (+{all_links} aliases)", entries))

    sym_files = [] if (only and "symbolic" not in only) else sorted(glob.glob(os.path.join(THEME, "symbolic", "*", "*.svg")))
    seen, symbolics = set(), []
    for f in sym_files:
        name = os.path.basename(f)[:-len("-symbolic.svg")]
        key = open(f).read()
        if key in seen:
            continue
        seen.add(key)
        symbolics.append((name, f))

    total_h = 10
    for _, entries in sections:
        rows = (len(entries) + cols - 1) // cols
        total_h += hdr_h + rows * ch + 6
    if symbolics:
        total_h += hdr_h + ((len(symbolics) + cols - 1) // cols) * ch + 6

    img = QImage(cols * cw, max(96, total_h), QImage.Format_ARGB32)
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

    y_off = 4
    for sec_title, entries in sections:
        p.setFont(title_font)
        p.setPen(QColor(20, 20, 22))
        p.drawText(QRectF(12, y_off + 6, cols * cw - 24, 20), Qt.AlignVCenter, sec_title)
        p.fillRect(QRectF(12, y_off + 28, cols * cw - 24, 1), QColor(163, 163, 163))
        p.fillRect(QRectF(12, y_off + 29, cols * cw - 24, 1), QColor(255, 255, 255, 190))
        y_off += hdr_h

        p.setFont(font)
        for i, (name, f_big, f16) in enumerate(entries):
            x, y = (i % cols) * cw, y_off + (i // cols) * ch
            p.drawPixmap(x + 12, y + 6, 40, 40, QPixmap(f_big))
            if os.path.exists(f16):
                p.drawPixmap(x + 62, y + 22, 16, 16, QPixmap(f16))
            p.setPen(QColor(32, 32, 35))
            p.drawText(QRectF(x + 2, y + 52, cw - 4, 34), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere, name)
        y_off += ((len(entries) + cols - 1) // cols) * ch + 6

    if symbolics:
        p.setFont(title_font)
        p.setPen(QColor(20, 20, 22))
        p.drawText(QRectF(12, y_off + 6, cols * cw - 24, 20), Qt.AlignVCenter,
                   f"Menu Extras & Symbolic Glyphs — {len(symbolics)} distinct solid shapes (recolourable)")
        p.fillRect(QRectF(12, y_off + 28, cols * cw - 24, 1), QColor(163, 163, 163))
        p.fillRect(QRectF(12, y_off + 29, cols * cw - 24, 1), QColor(255, 255, 255, 190))
        y_off += hdr_h

        p.setFont(font)
        for i, (name, f) in enumerate(symbolics):
            x, y = (i % cols) * cw, y_off + (i // cols) * ch
            recolored(f, "#1a1a1a").render(p, QRectF(x + 8, y + 8, 16, 16))
            recolored(f, "#1a1a1a").render(p, QRectF(x + 30, y + 8, 32, 32))
            sel = QRectF(x + 66, y + 8, 24, 22)
            g = QLinearGradient(sel.topLeft(), sel.bottomLeft())
            for pos, col in ((0, "#4a84de"), (0.48, "#2668d6"), (0.52, "#2c74e2"), (1, "#80caff")):
                g.setColorAt(pos, QColor(col))
            p.fillRect(sel, g)
            recolored(f, "#ffffff").render(p, QRectF(x + 70, y + 11, 16, 16))
            p.setPen(QColor(40, 40, 40))
            p.drawText(QRectF(x + 2, y + 54, cw - 4, 32), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere, name)

    p.end()
    img.save(out_path)
    print(f"wrote {out_path} ({img.width()}x{img.height()})")


if __name__ == "__main__":
    main()
