#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Breeze icon names drawn as truthfully as possible to the Mac OS X 10.2 icons in Apple's
June 2002 HIG chapter 11 figures: soft photographic shading with no hard outlines (edges come
from light and shade), light from directly above, platinum and white plastics with fine vertical
pinstripes, glossy plastics, chrome, crisp paper, soft shadows. The KDE logo stands in where
Apple used its own. Writes artwork/aqua-icons/<name>.svg on a 128 px canvas; tools/make_icons.py renders
them into the Oxygen Pinstripe theme. Run with plain python3 (it needs librsvg only to preview)."""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "artwork", "aqua-icons")
os.makedirs(OUT, exist_ok=True)

BASE = """
<filter id="drop" x="-30%" y="-30%" width="160%" height="170%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="1.8"/><feOffset dy="2.2"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="0.9"/><feOffset dy="1"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.3"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="b05"><feGaussianBlur stdDeviation="0.5"/></filter>
<filter id="b1" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1"/></filter>
<filter id="b2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="brush" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.003 0.7" numOctaves="3" seed="7" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.9 -0.4" result="w"/>
  <feComposite in="w" in2="SourceGraphic" operator="in" result="wi"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -0.6 0.3" result="d"/>
  <feComposite in="d" in2="SourceGraphic" operator="in" result="di"/>
  <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="wi"/><feMergeNode in="di"/></feMerge>
</filter>
<pattern id="pin" width="2" height="2" patternUnits="userSpaceOnUse">
  <rect width="1" height="2" fill="#9aa2aa" fill-opacity="0.2"/>
</pattern>
<pattern id="pinH" width="2" height="2" patternUnits="userSpaceOnUse">
  <rect width="2" height="1" fill="#9aa2aa" fill-opacity="0.18"/>
</pattern>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.3" stop-color="#d6dade"/>
  <stop offset="0.48" stop-color="#8e959c"/><stop offset="0.52" stop-color="#5c636a"/>
  <stop offset="0.6" stop-color="#b9bfc5"/><stop offset="1" stop-color="#f2f4f6"/>
</linearGradient>
<linearGradient id="chromeX" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6b737b"/><stop offset="0.2" stop-color="#e9ecef"/>
  <stop offset="0.35" stop-color="#ffffff"/><stop offset="0.55" stop-color="#9ba2a9"/>
  <stop offset="0.75" stop-color="#dfe3e7"/><stop offset="1" stop-color="#6b737b"/>
</linearGradient>
<radialGradient id="floor" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#000" stop-opacity="0.45"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>
"""


def svg(name, defs, body):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
                f'<defs>{BASE}{defs}</defs>{body}</svg>\n')


def floor(cx, cy, rx, ry, op=1.0):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#floor)" opacity="{op}"/>'


def kde_cog(cx, cy, r):
    teeth = 11
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4) - math.pi / 2
        rr = r if (i % 4) in (0, 1) else r * 0.84
        pts.append(f"{cx + rr * math.cos(a):.2f} {cy + rr * math.sin(a):.2f}")
    hole = (f"M{cx + r * 0.64:.2f} {cy}a{r * 0.64:.2f} {r * 0.64:.2f} 0 1 0 {-r * 1.28:.2f} 0"
            f"a{r * 0.64:.2f} {r * 0.64:.2f} 0 1 0 {r * 1.28:.2f} 0z")
    k = r * 0.38
    kp = (f"M{cx - k * 0.75:.2f} {cy - k:.2f}h{k * 0.42:.2f}v{k * 0.8:.2f}l{k * 0.75:.2f} {-k * 0.8:.2f}"
          f"h{k * 0.55:.2f}l{-k * 0.92:.2f} {k * 0.95:.2f}l{k * 0.98:.2f} {k * 1.05:.2f}h{-k * 0.56:.2f}"
          f"l{-k * 0.8:.2f} {-k * 0.86:.2f}v{k * 0.86:.2f}h{-k * 0.42:.2f}z")
    return "M" + "L".join(pts) + "z" + hole + kp


# ============================================================================ folders
# Jaguar's folder: soft sky-blue card, tab on the left, lit top lips, a pale glow towards the
# bottom of the front, no outline; edges are a slightly deeper blue.
FOLDER = """
<linearGradient id="fBack" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#8cc3f3"/><stop offset="1" stop-color="#3f86d6"/>
</linearGradient>
<linearGradient id="fIn" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#2d69b7"/><stop offset="1" stop-color="#4e93dd"/>
</linearGradient>
<linearGradient id="fFront" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#d8edff"/><stop offset="0.05" stop-color="#a9d4fb"/>
  <stop offset="0.55" stop-color="#6eb2f0"/><stop offset="1" stop-color="#4c98e6"/>
</linearGradient>
<linearGradient id="fEdge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#1f5fb0" stop-opacity="0.35"/><stop offset="0.06" stop-color="#1f5fb0" stop-opacity="0"/>
  <stop offset="0.94" stop-color="#1f5fb0" stop-opacity="0"/><stop offset="1" stop-color="#1f5fb0" stop-opacity="0.35"/>
</linearGradient>
<radialGradient id="fGlow" cx="0.5" cy="1" r="0.7">
  <stop offset="0" stop-color="#c9efff" stop-opacity="0.8"/><stop offset="1" stop-color="#c9efff" stop-opacity="0"/>
</radialGradient>
<linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#eceff3"/>
</linearGradient>
"""


def folder(glyph="", inside="", ft=44, lean=0):
    fr = (f"M{9 - lean} {ft + 3}a3 3 0 0 1 3-3h{104 + 2 * lean}a3 3 0 0 1 3 3"
          f"L119 112a4 4 0 0 1-4 4H13a4 4 0 0 1-4-4z")
    return f"""
{floor(64, 118, 60, 5, 0.7)}
<g filter="url(#drop)">
  <path d="M9 24a4 4 0 0 1 4-4h29a4 4 0 0 1 3.3 1.8l4.6 6.4a2.5 2.5 0 0 0 2 1H115a4 4 0 0 1 4 4V112H9z" fill="url(#fBack)"/>
  <path d="M9 24a4 4 0 0 1 4-4h29a4 4 0 0 1 3.3 1.8l4.6 6.4a2.5 2.5 0 0 0 2 1H115a4 4 0 0 1 4 4V112H9z" fill="none" stroke="#2a64b4" stroke-opacity="0.45"/>
  <path d="M13 21h29M52 30h63" stroke="#fff" stroke-opacity="0.8"/>
  <rect x="11" y="34" width="106" height="{ft - 28}" rx="2" fill="url(#fIn)"/>
  {inside}
  <path d="{fr}" fill="url(#fFront)"/>
  <path d="{fr}" fill="url(#fGlow)"/>
  <path d="{fr}" fill="url(#fEdge)"/>
  <path d="M{10 - lean} {ft + 2}h{108 + 2 * lean}l-0.6 {(116 - ft) * 0.42:.1f}c-34 3-72 3-{106 + 2 * lean} 0z" fill="url(#gloss)" opacity="0.38"/>
  <path d="{fr}" fill="none" stroke="#2a64b4" stroke-opacity="0.45"/>
  <path d="M{11 - lean} {ft + 0.8}h{106 + 2 * lean}" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M12 115.4h104" stroke="#2a6fc4" stroke-opacity="0.5"/>
</g>
{glyph}"""


def press(d):
    """Stamped into the card: deep navy, a white catch-light on the lower edge, a shadow inside the top."""
    return (f'<path d="{d}" fill="#ffffff" fill-opacity="0.85" transform="translate(0 1.3)"/>'
            f'<path d="{d}" fill="#2c5aa6"/>'
            f'<clipPath id="pc"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="none" stroke="#0d2c63" stroke-opacity="0.8" stroke-width="2.4" '
            f'transform="translate(0 1)" clip-path="url(#pc)" filter="url(#b05)"/>')


HOUSE = "M64 60l-24 20h7v21h12V89h10v12h12V80h7z"
ARROW = "M57 58h14v18h10L64 94 47 76h10zM43 98h42v5H43z"
svg("folder", FOLDER, folder())
svg("user-home", FOLDER, folder(press(HOUSE)))
svg("folder-download", FOLDER, folder(press(ARROW)))

LINES = ["Pinstripe notes for the", "Aqua remix of Breeze.", "Light from above, real", "paper, metal and glass.",
         "Soft shadows beneath.", "Shine on chrome."]


def sheet(x, y, w, h, rot, lines, size=4.2):
    cid = f"c{x}{y}"
    t = "".join(f'<text x="{x + 6}" y="{y + 10 + i * (size + 1.9):.1f}" font-family="Luxi Serif, DejaVu Serif, serif" '
                f'font-size="{size}" fill="#333a42">{s}</text>' for i, s in enumerate(lines))
    return (f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})" filter="url(#soft)">'
            f'<clipPath id="{cid}"><rect x="{x + 3}" y="{y}" width="{w - 6}" height="{h}"/></clipPath>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#paper)" stroke="#c4c8cd" stroke-width="0.8"/>'
            f'<g clip-path="url(#{cid})">{t}</g></g>')


svg("system-file-manager", FOLDER, folder(
    inside=sheet(20, 20, 74, 56, -6, LINES[3:]) + sheet(30, 24, 78, 56, 4, LINES), ft=58, lean=3))

# ============================================================================ trash
# Breeze's ribbed bin in brushed steel, soft and photographic: shading defines the edges.
TRASH = """
<linearGradient id="tBody" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#7d858d"/><stop offset="0.15" stop-color="#c3c9cf"/>
  <stop offset="0.35" stop-color="#f6f7f9"/><stop offset="0.55" stop-color="#d0d5da"/>
  <stop offset="0.85" stop-color="#9ba3ab"/><stop offset="1" stop-color="#737b83"/>
</linearGradient>
<linearGradient id="tTop" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d4d9de"/>
</linearGradient>
<linearGradient id="tShade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#000" stop-opacity="0.22"/><stop offset="0.25" stop-color="#000" stop-opacity="0"/>
  <stop offset="0.85" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.12"/>
</linearGradient>
<clipPath id="tClip"><path d="M26 36L35 111a29 6 0 0 0 58 0L102 36z"/></clipPath>
"""
ribs = ""
for i in range(11):
    u = (i + 0.5) / 11
    a = math.cos(math.pi * u)
    xt, xb = 64 - a * 36, 64 - a * 28
    w = 2.6 * math.sin(math.pi * u) + 0.5
    ribs += (f'<path d="M{xt:.1f} 40L{xb:.1f} 116" stroke="#4d555d" stroke-opacity="0.28" stroke-width="{w + 1.4:.1f}" filter="url(#b05)"/>'
             f'<path d="M{xt - 0.9:.1f} 40L{xb - 0.7:.1f} 116" stroke="#fff" stroke-opacity="0.75" stroke-width="{w * 0.5:.1f}"/>')
svg("user-trash", TRASH, f"""
{floor(64, 117, 34, 4)}
<g filter="url(#soft)">
  <path d="M26 36L35 111a29 6 0 0 0 58 0L102 36z" fill="url(#tBody)"/>
  <g clip-path="url(#tClip)">
    <rect x="20" y="30" width="88" height="90" fill="url(#tBody)" filter="url(#brush)" opacity="0.6"/>
    {ribs}
    <rect x="20" y="30" width="88" height="90" fill="url(#tShade)"/>
    <rect x="20" y="34" width="88" height="10" fill="#000" fill-opacity="0.28" filter="url(#b2)"/>
    <path d="M44 38L49 118" stroke="#fff" stroke-width="7" stroke-opacity="0.7" filter="url(#b1)"/>
  </g>
  <path d="M22 30v6a42 9 0 0 0 84 0v-6z" fill="url(#tBody)"/>
  <ellipse cx="64" cy="30" rx="42" ry="9" fill="url(#tTop)"/>
  <ellipse cx="64" cy="30" rx="42" ry="9" fill="none" stroke="#7d858d" stroke-opacity="0.45"/>
  <ellipse cx="64" cy="29.3" rx="36" ry="6.4" fill="none" stroke="#fff" stroke-width="1.2"/>
  <ellipse cx="64" cy="31.5" rx="18" ry="3.6" fill="#000" fill-opacity="0.22" filter="url(#b2)"/>
  <path d="M49 30c0-9 5-11 15-11s15 2 15 11" fill="none" stroke="#6f777f" stroke-width="6" stroke-linecap="round"/>
  <path d="M49 30c0-9 5-11 15-11s15 2 15 11" fill="none" stroke="url(#chrome)" stroke-width="4.2" stroke-linecap="round"/>
</g>""")

# ============================================================================ terminal (utility)
# Figures 11-3 and 11-9: a platinum display with fine vertical pinstripes and soft rounded
# corners, the screen set deep in the bezel, white ">_" in the top-left, the maker's mark below.
TERM = """
<linearGradient id="plat" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#e4e4e6"/><stop offset="0.12" stop-color="#cbcbcd"/><stop offset="0.85" stop-color="#c6c6c8"/><stop offset="1" stop-color="#d8d8da"/>
</linearGradient>
<linearGradient id="recess" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#8b9299"/><stop offset="0.6" stop-color="#c9ced3"/><stop offset="1" stop-color="#f7f8f9"/>
</linearGradient>
<linearGradient id="scr" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#4c5458"/><stop offset="0.7" stop-color="#44474d"/><stop offset="1" stop-color="#2a2c30"/>
</linearGradient>
<linearGradient id="scrGloss" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<clipPath id="glass"><rect x="22" y="20" width="84" height="68" rx="3"/></clipPath>
"""
svg("utilities-terminal", TERM, f"""
<g filter="url(#drop)">
  <rect x="8" y="9" width="112" height="106" rx="11" fill="url(#plat)"/>
  <rect x="8" y="9" width="112" height="106" rx="11" fill="url(#pin)"/>
  <rect x="8.5" y="9.5" width="111" height="105" rx="10.5" fill="none" stroke="#fff" stroke-width="1.2"/>
  <rect x="8.5" y="9.5" width="111" height="105" rx="10.5" fill="none" stroke="#8d949b" stroke-opacity="0.35"/>
  <rect x="17" y="15" width="94" height="78" rx="6" fill="url(#recess)"/>
  <rect x="20" y="18" width="88" height="72" rx="4" fill="#31363b" filter="url(#b1)"/>
  <rect x="22" y="20" width="84" height="68" rx="3" fill="url(#scr)"/>
  <g clip-path="url(#glass)">
    <text x="27" y="34" font-family="Luxi Mono, DejaVu Sans Mono, monospace" font-size="13" font-weight="bold" fill="#f4f5f6">&gt;_</text>
    <rect x="22" y="20" width="84" height="34" fill="url(#scrGloss)"/>
    <path d="M60 20h30L60 88H30z" fill="#fff" opacity="0.07"/>
    <rect x="22" y="20" width="84" height="68" fill="none" stroke="#000" stroke-opacity="0.4" stroke-width="3" filter="url(#b2)"/>
  </g>
  <path d="{kde_cog(64, 103, 5)}" fill="#ffffff" fill-rule="evenodd" transform="translate(0 0.8)"/>
  <path d="{kde_cog(64, 103, 5)}" fill="#a3a9af" fill-rule="evenodd"/>
</g>""")

# ============================================================================ settings (preferences)
# Figure 11-12: preferences are a brushed light-switch plate: a narrow left panel with the switch,
# a wide right panel with the maker's mark in glossy graphite, a screw in each corner.
SET = """
<linearGradient id="plate" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fbfcfd"/><stop offset="1" stop-color="#dfe3e7"/>
</linearGradient>
<linearGradient id="slot" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#5d646b"/><stop offset="1" stop-color="#c7ccd1"/>
</linearGradient>
<linearGradient id="lever" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#a6adb4"/><stop offset="0.35" stop-color="#ffffff"/><stop offset="1" stop-color="#b9c0c6"/>
</linearGradient>
<linearGradient id="leverTop" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#cfd5da"/>
</linearGradient>
<linearGradient id="mark" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#9aa0a5"/><stop offset="0.35" stop-color="#6b757c"/><stop offset="1" stop-color="#4c5a61"/>
</linearGradient>
<radialGradient id="dome" cx="0.45" cy="0.3" r="0.8">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#d0d5da"/><stop offset="1" stop-color="#8d949b"/>
</radialGradient>
<clipPath id="markClip"><path id="markPath"/></clipPath>
"""


def screw(cx, cy, ang):
    t = f'transform="rotate({ang} {cx} {cy})"'
    return (f'<circle cx="{cx}" cy="{cy + 0.8}" r="3.2" fill="#000" fill-opacity="0.25" filter="url(#b05)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="3" fill="url(#dome)"/>'
            f'<path d="M{cx - 2.2} {cy}h4.4" stroke="#5c636a" stroke-width="1.1" {t}/>'
            f'<path d="M{cx - 2} {cy + 0.8}h4" stroke="#fff" stroke-width="0.5" {t}/>')


cog = kde_cog(80, 62, 28)
svg("systemsettings", SET, f"""
<g filter="url(#drop)">
  <rect x="8" y="10" width="112" height="104" rx="4" fill="url(#plate)"/>
  <rect x="8" y="10" width="112" height="104" rx="4" fill="url(#plate)" filter="url(#brush)" opacity="0.8"/>
  <rect x="8.5" y="10.5" width="111" height="103" rx="3.5" fill="none" stroke="#fff" stroke-width="1.2"/>
  <rect x="8.5" y="10.5" width="111" height="103" rx="3.5" fill="none" stroke="#8d949b" stroke-opacity="0.4"/>
  <path d="M42 11v102" stroke="#a7adb3"/><path d="M43 11v102" stroke="#fff"/>
  <rect x="20" y="44" width="12" height="36" rx="2" fill="url(#slot)"/>
  <rect x="21" y="45" width="10" height="34" rx="1.5" fill="#3d4349" filter="url(#b05)"/>
  <path d="M21.5 64h9l2 10h-13z" fill="#000" fill-opacity="0.45" filter="url(#b1)"/>
  <path d="M21 46.5h10l1 17h-12z" fill="url(#lever)"/>
  <path d="M20.6 44.5h10.8l-0.4 3h-10z" fill="url(#leverTop)"/>
  <path d="M21.5 47.6h9" stroke="#fff" stroke-width="0.8"/>
  {screw(25, 18, 30)}{screw(25, 106, 70)}{screw(112, 18, -40)}{screw(112, 106, 10)}
  <path d="{cog}" fill="#ffffff" fill-rule="evenodd" transform="translate(0 1.4)"/>
  <path d="{cog}" fill="url(#mark)" fill-rule="evenodd"/>
  <path d="{cog}" fill="none" stroke="#2a2f33" stroke-opacity="0.35" stroke-width="0.6"/>
  <clipPath id="cogc"><path d="{cog}" fill-rule="evenodd"/></clipPath>
  <ellipse cx="80" cy="46" rx="27" ry="15" fill="url(#gloss)" opacity="0.75" clip-path="url(#cogc)"/>
</g>""")

# ============================================================================ hard disk (hardware)
# Figure 11-14 internal disk: a tall aluminium drive seen from above, its top a long trapezoid
# with the platter's circle and arm cut-out stamped in, a black label at the top, a short front
# face with vents and a small LED.
HD = """
<linearGradient id="hTop" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#d6d5da"/><stop offset="0.2" stop-color="#c4c3c8"/><stop offset="0.8" stop-color="#aaa9af"/><stop offset="1" stop-color="#cfced3"/>
</linearGradient>
<linearGradient id="hFront" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#8a8a93"/><stop offset="0.3" stop-color="#51505a"/><stop offset="1" stop-color="#3c3b44"/>
</linearGradient>
<linearGradient id="hStamp" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#9aa1a8"/><stop offset="1" stop-color="#ffffff"/>
</linearGradient>
<radialGradient id="led" cx="0.4" cy="0.35" r="0.7">
  <stop offset="0" stop-color="#fffbe0"/><stop offset="0.5" stop-color="#e6d23a"/><stop offset="1" stop-color="#8a7a10"/>
</radialGradient>
<clipPath id="hClip"><path d="M30 8h68l14 92H16z"/></clipPath>
"""
svg("drive-harddisk", HD, f"""
{floor(64, 116, 56, 7)}
<g filter="url(#soft)">
  <path d="M16 100h96v10a3 3 0 0 1-3 3H19a3 3 0 0 1-3-3z" fill="url(#hFront)"/>
  <path d="M16.5 100.6h95" stroke="#fff" stroke-opacity="0.9"/>
  {''.join(f'<rect x="{50 + i * 2.6:.1f}" y="104" width="1.4" height="6" fill="#1f2226"/>' for i in range(11))}
  <circle cx="98" cy="107" r="2" fill="url(#led)"/>
  <path d="M30 8h68l14 92H16z" fill="url(#hTop)"/>
  <g clip-path="url(#hClip)"><rect x="0" y="0" width="128" height="104" fill="url(#hTop)" filter="url(#brush)" opacity="0.35"/></g>
  <path d="M30.5 8.6h67" stroke="#fff"/>
  <path d="M16.8 99.4h94.4" stroke="#fff" stroke-opacity="0.9"/>
  <rect x="41" y="13" width="46" height="9" rx="1" fill="#1d2125"/>
  <text x="64" y="19.4" font-family="Luxi Sans, DejaVu Sans" font-size="3.6" text-anchor="middle" fill="#e8eaec">120 GB Internal Hard Disk</text>
  <path d="M58 30a27 22 0 1 0 22 2" fill="none" stroke="url(#hStamp)" stroke-width="2.4" transform="translate(0 0.8)"/>
  <path d="M58 30a27 22 0 1 0 22 2" fill="none" stroke="#4f565d" stroke-width="1.6"/>
  <path d="M80 32l14-8" stroke="#4f565d" stroke-width="1.4"/><path d="M80 33l14-8" stroke="#fff" stroke-width="1"/>
  <path d="M36 52a27 22 0 0 0 54 0" fill="none" stroke="#fff" stroke-width="1.2" stroke-opacity="0.9" transform="translate(0 10)"/>
  <ellipse cx="62" cy="54" rx="9" ry="7" fill="#b9b8be" stroke="#4f565d" stroke-width="1.6"/>
  <ellipse cx="62" cy="55" rx="9" ry="7" fill="none" stroke="#fff" stroke-width="0.9"/>
  {''.join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#a3aab0"/><circle cx="{x}" cy="{y - 0.4}" r="0.8" fill="#fff"/>' for x, y in ((34, 12), (94, 12), (21, 94), (107, 94)))}
</g>""")

# ============================================================================ web browser
# Figure 11-14's globe: deep blue glass, white meridians and parallels with bright nodes, a big
# soft specular cap and a pale glow welling up from the bottom.
GL = """
<linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#28338a"/><stop offset="0.3" stop-color="#2a5fc0"/>
  <stop offset="0.6" stop-color="#4a8fd8"/><stop offset="0.85" stop-color="#9fcaf3"/><stop offset="1" stop-color="#bfe0fa"/>
</linearGradient>
<radialGradient id="gRim" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0.8" stop-color="#0a1a5a" stop-opacity="0"/><stop offset="1" stop-color="#0a1a5a" stop-opacity="0.55"/>
</radialGradient>
<radialGradient id="gWell" cx="0.5" cy="1" r="0.6">
  <stop offset="0" stop-color="#c8f2ff" stop-opacity="0.9"/><stop offset="1" stop-color="#8fdcff" stop-opacity="0"/>
</radialGradient>
<radialGradient id="node" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#bfe6ff" stop-opacity="0"/>
</radialGradient>
<clipPath id="ball"><circle cx="64" cy="58" r="48"/></clipPath>
"""
lines = ""
for d in (-32, -16, 0, 16, 32):
    rx = (48 * 48 - d * d) ** 0.5
    lines += f'<ellipse cx="64" cy="{58 + d:.1f}" rx="{rx:.1f}" ry="{rx * 0.28:.1f}" fill="none" stroke="#fff" stroke-opacity="0.55" stroke-width="1.3"/>'
for w in (14, 32, 46):
    lines += f'<ellipse cx="64" cy="58" rx="{w}" ry="48" fill="none" stroke="#fff" stroke-opacity="0.55" stroke-width="1.3" transform="rotate(-14 64 58)"/>'
nodes = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="url(#node)"/>' for x, y in
                ((44, 40), (78, 32), (96, 62), (58, 74), (34, 66), (72, 92), (90, 44)))
svg("internet-web-browser", GL, f"""
{floor(64, 114, 42, 6)}
<g filter="url(#soft)">
  <circle cx="64" cy="58" r="48" fill="url(#gBlue)"/>
  <g clip-path="url(#ball)">
    {lines}
    {nodes}
    <circle cx="64" cy="58" r="48" fill="url(#gWell)"/>
    <circle cx="64" cy="58" r="48" fill="url(#gRim)"/>
  </g>
  <ellipse cx="64" cy="32" rx="34" ry="20" fill="url(#gloss)" opacity="0.85"/>
</g>""")

# ============================================================================ text editor
# Figure 11-5: lined paper with real text, a yellow sheet peeking out behind, a chrome pen.
ED = """
<linearGradient id="yel" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f6e27a"/><stop offset="1" stop-color="#e5c23a"/>
</linearGradient>
<linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f1f3f6"/>
</linearGradient>
<pattern id="rules" width="128" height="6" patternUnits="userSpaceOnUse" y="1">
  <rect y="5.4" width="128" height="0.6" fill="#7ab0e6" fill-opacity="0.7"/>
</pattern>
<linearGradient id="barrel" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#5d646b"/><stop offset="0.25" stop-color="#ffffff"/><stop offset="0.45" stop-color="#c9ced3"/>
  <stop offset="0.6" stop-color="#6e767e"/><stop offset="0.8" stop-color="#d8dce0"/><stop offset="1" stop-color="#7c848c"/>
</linearGradient>
<linearGradient id="grip" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#3a3f44"/><stop offset="0.3" stop-color="#9ba2a9"/><stop offset="0.6" stop-color="#1e2226"/>
  <stop offset="1" stop-color="#4d545a"/>
</linearGradient>
"""
TXT = ["Dear Jay,", "", "Maybe you already know I might", "have this story to tell you. It is",
       "about the light that comes from", "above and the paper on the desk,", "and how the pen rests across it",
       "while the words dry slowly.", "", "Best,", "Pinstripe"]
rows = "".join(f'<text x="30" y="{25 + i * 6}" font-family="Luxi Sans, DejaVu Sans" font-size="4.1" fill="#2a3037">{t}</text>'
               for i, t in enumerate(TXT) if t)
svg("accessories-text-editor", ED, f"""
{floor(62, 116, 50, 5, 0.8)}
<g filter="url(#drop)">
  <g transform="rotate(-8 56 64)"><rect x="18" y="16" width="70" height="92" fill="url(#yel)"/></g>
  <g transform="rotate(3 62 62)">
    <rect x="24" y="12" width="76" height="98" fill="url(#pg)" stroke="#c2c6cb" stroke-width="0.8"/>
    <rect x="24" y="20" width="76" height="90" fill="url(#rules)"/>
    <path d="M24 12.5h76" stroke="#fff"/>
    {rows}
  </g>
</g>
<g filter="url(#drop)" transform="rotate(-58 82 76)">
  <path d="M40 72h54a4 4 0 0 1 4 4v0a4 4 0 0 1-4 4H40z" fill="url(#barrel)"/>
  <path d="M28 72h12v8H28z" fill="url(#grip)"/>
  <path d="M28 72L16 76l12 4z" fill="url(#barrel)"/>
  <path d="M16 76l5-1.6v3.2z" fill="#3a3f44"/>
  <path d="M60 70.8h26a1.5 1.5 0 0 1 0 3H60z" fill="url(#barrel)"/>
</g>""")

# ============================================================================ calculator (accessory)
# Figure 11-8: an idealised white calculator, straight on: pinstriped top band, a pale LCD
# window, a grid of soft white keys, a tall equals key.
CALC = """
<linearGradient id="cBody" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e6e9ec"/>
</linearGradient>
<linearGradient id="cHead" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f7f8f9"/><stop offset="1" stop-color="#d9dde1"/>
</linearGradient>
<linearGradient id="lcd" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#c9cdd1"/><stop offset="1" stop-color="#eef0f2"/>
</linearGradient>
<linearGradient id="key" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.7" stop-color="#f1f3f5"/><stop offset="1" stop-color="#d0d5da"/>
</linearGradient>
"""
labels = [["C", "%", "/", "*"], ["7", "8", "9", "-"], ["4", "5", "6", "+"], ["1", "2", "3", ""], ["0", ".", "±", ""]]
keys = ""
kw, kh, gx, gy = 19, 12.4, 4, 3.2
for r, row in enumerate(labels):
    for c, lab in enumerate(row):
        x, y = 20 + c * (kw + gx), 44 + r * (kh + gy)
        h = kh
        if c == 3 and r == 3:
            h = kh * 2 + gy
            lab = "="
        elif c == 3 and r == 4:
            continue
        keys += (f'<rect x="{x}" y="{y + 1.2}" width="{kw}" height="{h}" rx="2.5" fill="#000" fill-opacity="0.22" filter="url(#b05)"/>'
                 f'<rect x="{x}" y="{y}" width="{kw}" height="{h}" rx="2.5" fill="url(#key)"/>'
                 f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{kw - 1}" height="{h - 1}" rx="2" fill="none" stroke="#9aa1a8" stroke-opacity="0.45"/>'
                 f'<path d="M{x + 2} {y + h - 0.4}h{kw - 4}" stroke="#a8adb2"/><path d="M{x + 2} {y + 0.9}h{kw - 4}" stroke="#fff"/>'
                 f'<text x="{x + kw / 2}" y="{y + h / 2 + 2.2:.1f}" font-family="Luxi Sans, DejaVu Sans" font-size="6" '
                 f'text-anchor="middle" fill="#3a4047">{lab}</text>')
svg("accessories-calculator", CALC, f"""
<g filter="url(#drop)">
  <rect x="12" y="8" width="104" height="114" rx="5" fill="url(#cBody)"/>
  <rect x="12" y="8" width="104" height="14" rx="5" fill="url(#cHead)"/>
  <rect x="12" y="8" width="104" height="14" rx="5" fill="url(#pinH)"/>
  <path d="M12 22h104" stroke="#a9afb5" stroke-opacity="0.6"/><path d="M12 23h104" stroke="#fff"/>
  <rect x="12.5" y="8.5" width="103" height="113" rx="4.5" fill="none" stroke="#959ca3" stroke-opacity="0.5"/>
  <rect x="19" y="26" width="90" height="14" rx="2.5" fill="#9aa0a6"/>
  <rect x="20" y="27" width="88" height="12" rx="2" fill="url(#lcd)"/>
  <rect x="20" y="27" width="88" height="3" rx="1.5" fill="#000" fill-opacity="0.18" filter="url(#b05)"/>
  <rect x="20.5" y="27.5" width="87" height="11" rx="1.6" fill="none" stroke="#7d848b" stroke-opacity="0.6"/>
  <text x="104" y="36" font-family="Luxi Sans, DejaVu Sans" font-size="8" text-anchor="end" fill="#22272c">123456.89</text>
  {keys}
</g>""")

print("wrote", len(os.listdir(OUT)), "icons to", OUT)
