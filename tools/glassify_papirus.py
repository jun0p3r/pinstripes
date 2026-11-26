#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Mac OS X 10.2 "Jaguar" Aqua Auto-Glassifier for the entire Papirus icon set.

Transforms flat Material Papirus SVGs into 3D 10.2 Aqua liquid-gel SVGs & PNGs:
1. Strips Papirus's flat 1 px drop-shadow (opacity ~0.1-0.2 black) and 1 px white top rim overlays.
2. Upgrades every flat fill colour into a 4-stop 10.2 Aqua gel vertical gradient (lifted crown ->
   rich deep core at 42% -> vibrant mid at 78% -> luminous bounce at 100%).
3. Adds soft 3D inner bevel & cast shadow to foreground glyphs/details.
4. Wraps the icon silhouette in the signature 10.2 Aqua optical stack (modelled on claude-desktop.svg):
   - Tinted soft Gaussian silhouette drop shadow
   - Pooled bottom radial internal caustic glow
   - Curved top specular meniscus lens inset inside an eroded 3D pillow rim
   - Hairline darkened brand-hue outer surface-tension rim.
5. Supports two modes per icon:
   - "badge" (default): Full multi-layer 10.2 Aqua gel across the entire icon.
   - "symbol": Pops a foreground brand glyph out of a flat circle/square Material plate, colours it
     in the plate's brand colour, scales it up to fill the canvas, and glassifies the free-standing
     brand silhouette directly (exact claude-desktop / discord look).
"""
import colorsys
import copy
import glob
import io
import json
import os
import re
import xml.etree.ElementTree as ET

import cairo
import gi
gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPIRUS_DIR = os.path.join(ROOT, ".cache", "papirus-icon-theme", "Papirus")
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

NAMED_COLORS = {
    "white": "#ffffff", "black": "#000000", "red": "#ff0000", "green": "#008000",
    "blue": "#0000ff", "yellow": "#ffff00", "cyan": "#00ffff", "magenta": "#ff00ff",
    "gray": "#808080", "grey": "#808080", "orange": "#ffa500", "purple": "#800080",
}


def parse_style(elem):
    """Return merged dict of presentation attributes + inline style."""
    st = {}
    for k in ("fill", "opacity", "fill-opacity", "stroke", "stroke-width", "stroke-opacity", "display", "visibility"):
        if k in elem.attrib:
            st[k] = elem.attrib[k].strip()
    raw = elem.attrib.get("style", "")
    for part in raw.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            st[k.strip()] = v.strip()
    return st


def set_style(elem, st):
    for k in ("fill", "opacity", "fill-opacity", "stroke", "stroke-width", "stroke-opacity"):
        elem.attrib.pop(k, None)
    elem.attrib["style"] = ";".join(f"{k}:{v}" for k, v in st.items() if v is not None)


def hex_to_rgb(col):
    if not col:
        return None
    c = col.strip().lower()
    if c in ("none", "transparent") or c.startswith("url("):
        return None
    c = NAMED_COLORS.get(c, c)
    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) >= 6:
            try:
                return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)
            except ValueError:
                return None
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", c)
    if m:
        return tuple(min(255, int(x)) / 255.0 for x in m.groups())
    return None


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(round(v * 255)))) for v in rgb))


def make_aqua_stops(rgb, is_foreground=False):
    """Build 4-stop 10.2 Aqua gel curve (c0, c1, c2, c3) + glow + dark tint from base RGB."""
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if is_foreground and l > 0.88 and s < 0.15:
        # Crisp pearl/ivory bevel for white inner symbols
        return ("#ffffff", "#f0f3f9", "#e2e7f2", "#ffffff", "#ffffff", "#dce4f2", "#1e2636", "#5a6478")

    if s < 0.08:
        # Neutral charcoal / graphite / silver -> 10.2 Graphite or Platinum Aqua glass
        if l < 0.38:
            # Obsidian / Slate Graphite Aqua Glass
            return ("#6d7788", "#262b36", "#353c4a", "#707d94", "#d6e4ff", "#7f95b8", "#0b0e14", "#171b24")
        elif l < 0.72:
            # Brushed Mid-Silver / Titanium Aqua Glass
            return ("#d5dae4", "#6e7585", "#858d9e", "#dfe4ef", "#ffffff", "#cbd3e3", "#1e222b", "#454b57")
        else:
            # Frosted Pearl / White Acrylic Aqua Glass
            return ("#ffffff", "#d0d6e3", "#dfe4ef", "#f8f9fc", "#ffffff", "#e4e9f5", "#2b3140", "#7c8496")

    # Chromatic colour: enrich Material pastels/flats into lush 10.2 Aqua jewel tones
    s_core = min(1.0, s * 1.18 + 0.06)
    s_top = max(0.25, s * 0.82)
    s_bot = max(0.30, s * 0.86)

    l_core = max(0.20, min(0.54, l * 0.82))
    l_mid = max(0.28, min(0.66, l * 0.96 + 0.04))
    l_top = max(l_core + 0.18, min(0.84, l * 1.18 + 0.14))
    l_bot = max(l_mid + 0.16, min(0.88, l * 1.22 + 0.16))

    c0 = rgb_to_hex(colorsys.hls_to_rgb(h, l_top, s_top))
    c1 = rgb_to_hex(colorsys.hls_to_rgb(h, l_core, s_core))
    c2 = rgb_to_hex(colorsys.hls_to_rgb(h, l_mid, s_core))
    c3 = rgb_to_hex(colorsys.hls_to_rgb(h, l_bot, s_bot))
    glow0 = rgb_to_hex(colorsys.hls_to_rgb(h, min(0.95, l_bot + 0.18), max(0.20, s * 0.65)))
    glow1 = rgb_to_hex(colorsys.hls_to_rgb(h, min(0.84, l_bot + 0.05), max(0.35, s * 0.85)))
    shad = rgb_to_hex(colorsys.hls_to_rgb(h, max(0.08, l_core * 0.34), min(1.0, s_core)))
    edge = rgb_to_hex(colorsys.hls_to_rgb(h, max(0.14, l_core * 0.52), min(1.0, s_core)))
    return (c0, c1, c2, c3, glow0, glow1, shad, edge)


def _local_tag(elem):
    t = elem.tag
    return t.split("}", 1)[1] if "}" in t else t


SHAPE_TAGS = {"path", "rect", "circle", "ellipse", "polygon", "polyline"}


def is_papirus_shadow_or_rim(elem):
    """Detect Papirus's flat 1px shadow (opacity<=0.25 dark) or 1px top highlight (opacity<=0.25 white)."""
    st = parse_style(elem)
    if st.get("display") == "none" or st.get("visibility") == "hidden":
        return True
    op = 1.0
    for k in ("opacity", "fill-opacity"):
        if k in st:
            try:
                op *= float(st[k])
            except ValueError:
                pass
    if op <= 0.26:
        fill = st.get("fill", "#000000")
        rgb = hex_to_rgb(fill)
        if rgb is None:
            return False
        # Dark shadow or pure-white rim overlay
        if max(rgb) <= 0.22 or min(rgb) >= 0.92:
            return True
    return False


def strip_overlays(parent):
    for ch in list(parent):
        tag = _local_tag(ch)
        if tag in ("defs", "namedview", "metadata", "title", "desc"):
            continue
        if is_papirus_shadow_or_rim(ch):
            parent.remove(ch)
        elif tag in ("g", "svg"):
            strip_overlays(ch)
            if len(ch) == 0 and tag == "g":
                parent.remove(ch)


def is_simple_plate(elem, vw, vh):
    """Check if first top-level shape is a generic circle / square / rounded-rect badge plate."""
    tag = _local_tag(elem)
    if tag == "circle":
        r = float(elem.attrib.get("r", 0))
        return r >= min(vw, vh) * 0.36
    if tag == "ellipse":
        rx = float(elem.attrib.get("rx", 0))
        ry = float(elem.attrib.get("ry", 0))
        return min(rx, ry) >= min(vw, vh) * 0.36
    if tag == "rect":
        w = float(elem.attrib.get("width", 0))
        h = float(elem.attrib.get("height", 0))
        return w >= vw * 0.68 and h >= vh * 0.68
    if tag == "path":
        d = elem.attrib.get("d", "")
        # Common Papirus circle/squircle path ("M 62,32 A 30,30 ..." or single closed outer contour without subpaths)
        subpaths = len(re.findall(r"[Mm]", d))
        if subpaths == 1 and re.search(r"[Aa]\s*2[6-9]|30", d):
            return True
        if subpaths == 1 and len(d) < 260 and ("56" in d or "58" in d or "60" in d):
            return True
    return False


def _measure_alpha_bbox(svg_bytes, size=128):
    """Render SVG via librsvg to measure exact non-zero alpha bounding box (x0, y0, x1, y1) in [0..size]."""
    h = Rsvg.Handle.new_from_data(svg_bytes)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    cr = cairo.Context(surf)
    vp = Rsvg.Rectangle()
    vp.x, vp.y, vp.width, vp.height = 0, 0, size, size
    h.render_document(cr, vp)
    surf.flush()
    buf = surf.get_data()
    stride = surf.get_stride()
    # Check alpha byte (offset 3 in BGRA on little-endian x86_64)
    min_x, min_y, max_x, max_y = size, size, -1, -1
    mv = memoryview(buf)
    for y in range(size):
        row = mv[y * stride:(y + 1) * stride]
        # Fast scan of alpha bytes
        alphas = row[3::4]
        if any(a > 8 for a in alphas):
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
            for x, a in enumerate(alphas):
                if a > 8:
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
    if max_x < min_x:
        return (size * 0.12, size * 0.12, size * 0.88, size * 0.88)
    return (min_x, min_y, max_x + 1, max_y + 1)


def can_extract_symbol(svg_path, category="apps"):
    """Return True if an apps SVG is strictly [1 simple circle/square plate] + [1 inner brand glyph]."""
    if category != "apps":
        return False
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        strip_overlays(root)
        elems = [ch for ch in root if _local_tag(ch) not in ("defs", "style", "metadata", "title", "namedview")]
        if len(elems) != 2:
            return False
        vw, vh = _get_viewbox(root)[2:]
        tag0 = _local_tag(elems[0])
        if tag0 == "circle":
            if float(elems[0].attrib.get("r", 0)) < min(vw, vh) * 0.38:
                return False
        elif tag0 == "rect":
            w = float(elems[0].attrib.get("width", 0))
            h = float(elems[0].attrib.get("height", 0))
            if w < vw * 0.72 or h < vh * 0.72 or abs(w - h) > vw * 0.12:
                return False
        else:
            return False
        st0 = parse_style(elems[0])
        rgb0 = hex_to_rgb(st0.get("fill", ""))
        if rgb0 is None:
            return False
        fg_rgbs = _collect_rgbs(elems[1])
        return len(fg_rgbs) == 1
    except Exception:
        return False


def _get_viewbox(root):
    vb = root.attrib.get("viewBox")
    if vb:
        parts = [float(x) for x in re.split(r"[\s,]+", vb.strip()) if x]
        if len(parts) == 4:
            return tuple(parts)
    w = float(re.sub(r"[^0-9.]", "", root.attrib.get("width", "64")) or 64)
    h = float(re.sub(r"[^0-9.]", "", root.attrib.get("height", "64")) or 64)
    return (0.0, 0.0, w, h)


def _collect_rgbs(elem):
    out = []
    st = parse_style(elem)
    rgb = hex_to_rgb(st.get("fill", ""))
    if rgb is not None:
        out.append(rgb)
    for ch in elem:
        out.extend(_collect_rgbs(ch))
    return out


def _recolor_tree(elem, target_hex):
    tag = _local_tag(elem)
    if tag in SHAPE_TAGS or tag == "g":
        st = parse_style(elem)
        if "fill" in st and st["fill"] not in ("none", "transparent"):
            st["fill"] = target_hex
            set_style(elem, st)
        elif tag in SHAPE_TAGS and "fill" not in st and tag != "g":
            st["fill"] = target_hex
            set_style(elem, st)
    for ch in elem:
        _recolor_tree(ch, target_hex)


def glassify_svg_to_bytes(svg_path, mode="badge"):
    """Transform a Papirus SVG into a 128x128 Mac OS X 10.2 Aqua Gel SVG (returned as UTF-8 bytes)."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    vx, vy, vw, vh = _get_viewbox(root)
    strip_overlays(root)

    orig_defs = []
    content_elems = []
    for ch in list(root):
        tag = _local_tag(ch)
        if tag in ("defs", "style"):
            orig_defs.append(copy.deepcopy(ch))
        elif tag not in ("metadata", "title", "desc", "namedview"):
            content_elems.append(copy.deepcopy(ch))

    if not content_elems:
        with open(svg_path, "rb") as f:
            return f.read()

    # Determine dominant/base colour for shadow, glow, and symbol mode
    plate_rgb = None
    st0 = parse_style(content_elems[0])
    plate_rgb = hex_to_rgb(st0.get("fill", ""))
    all_rgbs = []
    for el in content_elems:
        all_rgbs.extend(_collect_rgbs(el))
    if plate_rgb is None:
        # Pick most saturated or first RGB
        plate_rgb = max(all_rgbs, key=lambda c: colorsys.rgb_to_hls(*c)[2], default=(0.20, 0.50, 0.90))

    # Optional Symbol Mode: pop foreground brand symbol out of flat Material badge plate!
    used_symbol_mode = False
    if mode == "symbol" and len(content_elems) >= 2 and is_simple_plate(content_elems[0], vw, vh):
        # If plate is neutral grey/white and symbol is coloured, keep symbol's own colour;
        # otherwise paint symbol in the plate's vibrant brand colour!
        fg_rgbs = []
        for el in content_elems[1:]:
            fg_rgbs.extend(_collect_rgbs(el))
        plate_s = colorsys.rgb_to_hls(*plate_rgb)[2]
        fg_max_s = max((colorsys.rgb_to_hls(*c)[2] for c in fg_rgbs), default=0.0)
        if plate_s >= 0.12 or fg_max_s < 0.12:
            brand_rgb = plate_rgb if plate_s >= 0.08 else (0.22, 0.48, 0.88)
            brand_hex = rgb_to_hex(brand_rgb)
            content_elems = content_elems[1:]
            for el in content_elems:
                _recolor_tree(el, brand_hex)
            plate_rgb = brand_rgb
        else:
            content_elems = content_elems[1:]
            plate_rgb = max(fg_rgbs, key=lambda c: colorsys.rgb_to_hls(*c)[2])
        used_symbol_mode = True

    # Measure exact visual bounding box of the clean shapes so our Aqua lens & glow fit Tightly!
    probe_svg = ET.Element(f"{{{SVG_NS}}}svg", {"viewBox": f"{vx} {vy} {vw} {vh}", "width": "128", "height": "128"})
    for d_el in orig_defs:
        probe_svg.append(copy.deepcopy(d_el))
    for el in content_elems:
        probe_svg.append(copy.deepcopy(el))
    probe_bytes = ET.tostring(probe_svg, encoding="utf-8")
    bx0, by0, bx1, by1 = _measure_alpha_bbox(probe_bytes, 128)

    # Convert measured 128-space bbox back to viewBox coordinates
    ux0 = vx + (bx0 / 128.0) * vw
    uy0 = vy + (by0 / 128.0) * vh
    ux1 = vx + (bx1 / 128.0) * vw
    uy1 = vy + (by1 / 128.0) * vh
    uw = max(vw * 0.1, ux1 - ux0)
    uh = max(vh * 0.1, uy1 - uy0)

    # If symbol mode was used (or icon is tiny), scale cleanly to fill ~82% of the canvas (leaving room for drop shadow)
    sym_transform = ""
    if used_symbol_mode:
        target_span = min(vw, vh) * 0.80
        scale_f = min(2.4, max(1.0, target_span / max(uw, uh)))
        scx = (ux0 + ux1) / 2.0
        scy = (uy0 + uy1) / 2.0
        tcx = vx + vw / 2.0
        tcy = vy + vh * 0.485
        sym_transform = f"translate({tcx:.3f},{tcy:.3f}) scale({scale_f:.3f}) translate({-scx:.3f},{-scy:.3f})"
        ux0 = tcx - (uw * scale_f) / 2.0
        ux1 = tcx + (uw * scale_f) / 2.0
        uy0 = tcy - (uh * scale_f) / 2.0
        uy1 = tcy + (uh * scale_f) / 2.0
        uw *= scale_f
        uh *= scale_f

    # Upgrade every solid fill in content_elems to a 4-stop 10.2 Aqua linearGradient
    grad_defs = []
    grad_cache = {}

    def upgrade_elem(elem, depth_idx=0):
        is_fg = (depth_idx > 0) and not used_symbol_mode
        st = parse_style(elem)
        fill_val = st.get("fill")
        rgb = hex_to_rgb(fill_val) if fill_val else None
        if rgb is not None:
            key = (rgb_to_hex(rgb), is_fg)
            if key not in grad_cache:
                gid = f"agGrad{len(grad_cache)}"
                c0, c1, c2, c3, *_ = make_aqua_stops(rgb, is_foreground=is_fg)
                grad_cache[key] = gid
                grad_defs.append(
                    f'<linearGradient id="{gid}" x1="{(ux0+ux1)/2:.2f}" y1="{uy0:.2f}" '
                    f'x2="{(ux0+ux1)/2:.2f}" y2="{uy1:.2f}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0.00" stop-color="{c0}"/>'
                    f'<stop offset="0.42" stop-color="{c1}"/>'
                    f'<stop offset="0.78" stop-color="{c2}"/>'
                    f'<stop offset="1.00" stop-color="{c3}"/>'
                    f'</linearGradient>'
                )
            st["fill"] = f"url(#{grad_cache[key]})"
            set_style(elem, st)
        for ch in elem:
            upgrade_elem(ch, depth_idx)

    upgraded_xml_parts = []
    unit = vw / 64.0
    for idx, el in enumerate(content_elems):
        el_copy = copy.deepcopy(el)
        upgrade_elem(el_copy, idx)
        raw_el_xml = ET.tostring(el_copy, encoding="unicode")
        if idx > 0 and not used_symbol_mode:
            # Add subtle 3D inner cast shadow behind foreground glyphs/details so they pop in 3D!
            shadow_clone = copy.deepcopy(el)
            _recolor_tree(shadow_clone, "#080d18")
            sh_xml = ET.tostring(shadow_clone, encoding="unicode")
            upgraded_xml_parts.append(
                f'<g transform="translate(0, {0.95*unit:.3f})" opacity="0.34" filter="url(#agInnerBlur)">{sh_xml}</g>'
            )
        upgraded_xml_parts.append(raw_el_xml)

    inner_group = "\n      ".join(upgraded_xml_parts)
    if sym_transform:
        inner_group = f'<g transform="{sym_transform}">\n      {inner_group}\n    </g>'

    # Optical stack parameters in viewBox units
    plate_l = colorsys.rgb_to_hls(*plate_rgb)[1]
    _, _, _, _, glow0, glow1, shad_hex, edge_hex = make_aqua_stops(plate_rgb, is_foreground=False)
    sr, sg, sb = hex_to_rgb(shad_hex)
    cx = (ux0 + ux1) / 2.0
    shine_y = uy0 + uh * 0.41
    shine_dip = uy0 + uh * 0.53
    drop_dx = 0.35 * unit
    drop_dy = 2.25 * unit
    drop_blur = 1.65 * unit
    glow_blur = 1.15 * unit
    inner_blur = 0.65 * unit
    rim_erode = 0.95 * unit
    edge_erode = 0.42 * unit

    # Keep white/paper plates crisp without washing out inner text/lines
    shine_op0 = 0.62 if plate_l > 0.76 else 0.86
    shine_op1 = 0.30 if plate_l > 0.76 else 0.48
    glow_op0 = 0.48 if plate_l > 0.76 else 0.85
    glow_op1 = 0.24 if plate_l > 0.76 else 0.46

    # Pad viewBox generously so full-bleed 60x60 Papirus shapes never clip their Aqua drop shadow!
    pvx = vx - vw * 0.055
    pvy = vy - vh * 0.045
    pvw = vw * 1.11
    pvh = vh * 1.135

    orig_defs_xml = "\n    ".join(ET.tostring(d, encoding="unicode") for d in orig_defs)
    grad_defs_xml = "\n    ".join(grad_defs)

    out_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="128" height="128" viewBox="{pvx:.2f} {pvy:.2f} {pvw:.2f} {pvh:.2f}">
  <defs>
    {orig_defs_xml}
    {grad_defs_xml}
    <g id="agCleanIcon">
      {inner_group}
    </g>
    <filter id="agDropShadow" x="-30%" y="-30%" width="160%" height="170%">
      <feColorMatrix type="matrix" values="0 0 0 0 {sr:.3f}  0 0 0 0 {sg:.3f}  0 0 0 0 {sb:.3f}  0 0 0 0.42 0"/>
      <feGaussianBlur stdDeviation="{drop_blur:.3f}"/>
    </filter>
    <filter id="agInnerBlur" x="-25%" y="-25%" width="150%" height="155%">
      <feGaussianBlur stdDeviation="{inner_blur:.3f}"/>
    </filter>
    <filter id="agGlowBlur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="{glow_blur:.3f}"/>
    </filter>
    <filter id="agAlphaWhite" x="-10%" y="-10%" width="120%" height="120%">
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/>
    </filter>
    <filter id="agInsetWhite" x="-15%" y="-15%" width="130%" height="130%">
      <feMorphology in="SourceAlpha" operator="erode" radius="{rim_erode:.3f}" result="eroded"/>
      <feGaussianBlur in="eroded" stdDeviation="{0.35*unit:.3f}" result="softEroded"/>
      <feColorMatrix in="softEroded" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/>
    </filter>
    <filter id="agEdgeRing" x="-10%" y="-10%" width="120%" height="120%">
      <feMorphology in="SourceAlpha" operator="erode" radius="{edge_erode:.3f}" result="inner"/>
      <feComposite in="SourceAlpha" in2="inner" operator="out" result="ring"/>
      <feColorMatrix in="ring" type="matrix" values="0 0 0 0 {hex_to_rgb(edge_hex)[0]:.3f}  0 0 0 0 {hex_to_rgb(edge_hex)[1]:.3f}  0 0 0 0 {hex_to_rgb(edge_hex)[2]:.3f}  0 0 0 0.72 0"/>
    </filter>
    <mask id="agSilhouetteMask">
      <use href="#agCleanIcon" filter="url(#agAlphaWhite)"/>
    </mask>
    <mask id="agInsetRimMask">
      <use href="#agCleanIcon" filter="url(#agInsetWhite)"/>
    </mask>
    <radialGradient id="agBottomGlow" cx="{cx:.2f}" cy="{uy1 + uh*0.04:.2f}" r="{max(uw, uh)*0.56:.2f}" gradientUnits="userSpaceOnUse">
      <stop offset="0.00" stop-color="{glow0}" stop-opacity="{glow_op0:.2f}"/>
      <stop offset="0.48" stop-color="{glow1}" stop-opacity="{glow_op1:.2f}"/>
      <stop offset="1.00" stop-color="{glow1}" stop-opacity="0.00"/>
    </radialGradient>
    <linearGradient id="agTopShine" x1="{cx:.2f}" y1="{uy0 - uh*0.04:.2f}" x2="{cx:.2f}" y2="{shine_dip:.2f}" gradientUnits="userSpaceOnUse">
      <stop offset="0.00" stop-color="#ffffff" stop-opacity="{shine_op0:.2f}"/>
      <stop offset="0.50" stop-color="#ffffff" stop-opacity="{shine_op1:.2f}"/>
      <stop offset="1.00" stop-color="#ffffff" stop-opacity="0.08"/>
    </linearGradient>
  </defs>

  <!-- 1. Soft tinted Aqua drop shadow -->
  <g transform="translate({drop_dx:.3f}, {drop_dy:.3f})">
    <use href="#agCleanIcon" filter="url(#agDropShadow)"/>
  </g>

  <!-- 2. 4-stop Aqua gel body + inner bevelled details -->
  <use href="#agCleanIcon"/>

  <!-- 3. Pooled bottom internal caustic glow + inset top curved specular lens -->
  <g mask="url(#agSilhouetteMask)">
    <ellipse cx="{cx:.2f}" cy="{uy1:.2f}" rx="{uw*0.58:.2f}" ry="{uh*0.36:.2f}" fill="url(#agBottomGlow)" filter="url(#agGlowBlur)"/>
  </g>
  <g mask="url(#agInsetRimMask)">
    <path d="M {vx-10} {vy-10} H {vx+vw+10} V {shine_y:.2f} Q {cx:.2f} {shine_dip:.2f} {vx-10} {shine_y:.2f} Z" fill="url(#agTopShine)"/>
  </g>

  <!-- 4. Hairline darkened brand-hue outer surface-tension rim -->
  <use href="#agCleanIcon" filter="url(#agEdgeRing)"/>
</svg>
"""
    return out_svg.encode("utf-8")


def render_svg_bytes_to_png_bytes(svg_bytes, px):
    h = Rsvg.Handle.new_from_data(svg_bytes)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, px, px)
    cr = cairo.Context(surf)
    vp = Rsvg.Rectangle()
    vp.x, vp.y, vp.width, vp.height = 0, 0, px, px
    h.render_document(cr, vp)
    buf = io.BytesIO()
    surf.write_to_png(buf)
    return buf.getvalue()


def _collect_installed_desktop_icons():
    """Return set of icon names referenced by installed .desktop apps & KCMs on this machine."""
    import configparser
    names = set()
    for pat in (
        "/usr/share/applications/*.desktop",
        os.path.expanduser("~/.local/share/applications/*.desktop"),
        "/var/lib/flatpak/exports/share/applications/*.desktop",
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications/*.desktop"),
    ):
        for p in glob.glob(pat):
            cp = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                cp.read(p, encoding="utf-8")
                ic = cp["Desktop Entry"].get("Icon", "").strip()
                if ic:
                    names.add(os.path.splitext(os.path.basename(ic))[0])
            except Exception:
                pass
    return names


def scan_entire_papirus(papirus_dir=PAPIRUS_DIR):
    """Scan 100% of unique full-colour Papirus master icons + all symlinks/aliases across all sizes.
    Returns ordered list of dicts: {id, category, name, size_dir, svg_path, aliases, installed}.
    """
    if not os.path.isdir(papirus_dir):
        import subprocess
        clone_dst = os.path.dirname(papirus_dir)
        os.makedirs(os.path.dirname(clone_dst), exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/PapirusDevelopmentTeam/papirus-icon-theme.git", clone_dst],
            check=True,
        )
    seen = {}
    aliases = {}
    for sz in ("64x64", "48x48", "32x32", "24x24", "22x22", "16x16"):
        sz_dir = os.path.join(papirus_dir, sz)
        if not os.path.isdir(sz_dir) or os.path.islink(sz_dir):
            continue
        for cat in sorted(os.listdir(sz_dir)):
            cat_dir = os.path.join(sz_dir, cat)
            if not os.path.isdir(cat_dir) or os.path.islink(cat_dir):
                continue
            if cat in ("symbolic", "symbolic-up-to-20", "panel"):
                continue
            # Only include 48x48/32x32 actions (full-colour), skip 16-24 monochrome actions
            if cat == "actions" and sz in ("16x16", "22x22", "24x24"):
                continue
            for fn in sorted(os.listdir(cat_dir)):
                if not fn.endswith(".svg"):
                    continue
                full = os.path.join(cat_dir, fn)
                stem = fn[:-4]
                if os.path.islink(full):
                    tgt = os.path.basename(os.readlink(full))
                    if tgt.endswith(".svg"):
                        t_stem = tgt[:-4]
                        aliases.setdefault((cat, t_stem), set()).add(stem)
                else:
                    if (cat, stem) not in seen:
                        seen[(cat, stem)] = (sz, full)

    installed = _collect_installed_desktop_icons()

    # Priority ordering so the user's installed apps & core icons come first, followed by all 6,676 icons
    cat_rank = {
        "apps": 0, "mimetypes": 1, "places": 2, "devices": 3,
        "status": 4, "emblems": 5, "emotes": 6, "actions": 7, "animations": 8,
    }
    FOLDER_THEMES = (
        "folder-adwaita", "folder-breeze", "folder-brown", "folder-Carmine", "folder-catppuccin",
        "folder-cyan", "folder-darkcyan", "folder-deeporange", "folder-dracula", "folder-grey",
        "folder-indigo", "folder-magenta", "folder-manjaro", "folder-mint", "folder-nordic",
        "folder-orange", "folder-palebrown", "folder-paleorange", "folder-pink", "folder-red",
        "folder-teal", "folder-ubuntu", "folder-violet", "folder-white", "folder-yaru", "folder-yellow",
    )

    items = []
    for (cat, stem), (sz, full) in seen.items():
        al_list = sorted(aliases.get((cat, stem), set()) - {stem})
        all_names = {stem} | set(al_list)
        is_inst = bool(all_names & installed)
        is_theme_folder = (cat == "places" and stem.startswith(FOLDER_THEMES))
        items.append({
            "id": f"{cat}/{stem}",
            "category": cat,
            "name": stem,
            "size_dir": sz,
            "svg_path": full,
            "aliases": al_list,
            "installed": is_inst,
            "_sort": (
                0 if is_inst else (2 if is_theme_folder else 1),
                cat_rank.get(cat, 9),
                stem.lower(),
            ),
        })

    items.sort(key=lambda d: d["_sort"])
    for d in items:
        d.pop("_sort", None)
    return items


if __name__ == "__main__":
    items = scan_entire_papirus()
    print(f"Indexed {len(items)} unique Papirus masters ({sum(1 for x in items if x['installed'])} installed on this PC).")
