# Oxygen Pinstripe — Mac OS X 10.2 "Jaguar" Hand-Crafted Icon Style Guide

This guide documents the exact palettes, lighting/shadow filters, SVG material stacks, camera/perspective rules, canvas metrics, and QA workflow used to craft the base `128 × 128` icons in `artwork/aqua-icons/*.svg`. Follow these recipes closely so icons authored by different agents sit side-by-side as one cohesive June 2002 Aqua studio set.

---

## 1. Sampled 10.2 Palettes

Every palette below was sampled directly from the lossless figures in Apple's June 2002 *Aqua Human Interface Guidelines* Chapter 11 (`~/projects/agy-aqua-icons/reference/i-000.png`..`i-027.png`). Use `gradientUnits="userSpaceOnUse"` on a `0 0 128 128` canvas unless building a tiny reusable `<g>` widget.

### A. Sky-Blue Aqua Folder Acrylic (`folder.svg`, `folder-download.svg`)
| Part | Stops (`0.00 → 1.00`) | Notes |
|---|---|---|
| Rear leaf (`#backLeaf`) | `#f2faff` (0.00) → `#cce8ff` (0.16) → `#8ac2f4` (0.52) → `#5d9be0` (0.86) → `#4c88cf` (1.00) | Translucent sky-blue acrylic, slightly cooler/deeper than front flap; `0.9 px` stroke `#7ca6d4 → #3c6ca4`. |
| Front leaf (`#frontAqua`) | `#f2ffff` (0.00) → `#ccf2ff` (0.13) → `#87c8fc` (0.38) → `#4e98f0` (0.68) → `#3f85de` (0.88) → `#84ccff` (1.00) | Note the brighter `#84ccff` upturned stop at `1.00` (internal bottom bounce!). Outer stroke `0.85 px #3168ab` (`0.75` opacity). |
| Radial bottom glow (`#aquaGlow`) | `#d4f7ff` (`0.78`) → `#7ecaff` (`0.28` at `0.55`) → `#428ce2` (`0.00` at `1.00`) | Centered near bottom hinge `(62, 105)`, `r="46"`. |
| Recessed folder glyph (`#recessedCobalt`) | `#17468a` (`0.84`) → `#235db0` (`0.78` at `0.55`) → `#2e6fc7` (`0.74` at `1.00`) | Stamped into front acrylic; paired with `+1.8 px` blurred `#ffffff` (`0.72`) bottom lip catchlight and `-0.8 px #0b2c5e` (`0.45`) top inner rim. |

### B. Liquid Aqua Glass (`internet-web-browser.svg` & Coloured Variants)
| Variant | Top Crown (`0.00–0.16`) | Mid Body (`0.34–0.74`) | Bottom Internal Caustic (`0.90–1.00`) | Outer Tension Stroke (`0.8 px`) |
|---|---|---|---|---|
| **Sapphire (Classic Aqua)** | `#02052b` → `#091d6e` | `#194cb4` → `#327ce0` → `#6cbaf8` | `#bcf0ff` → `#f2feff` + radial `#ffffff` (`0.96`) | `#18479e` (`0.58` opacity) |
| **Indigo / Blurple** | `#0d1354` → `#222e9e` | `#4756eb` → `#6478ff` | `#9ec6ff` → `#e8f7ff` + radial `#ffffff` (`0.92`) | `#1d288a` (`0.62` opacity) |
| **Amethyst / Plum** | `#120229` → `#310b68` | `#6422b0` → `#9b4be6` | `#dfa6ff` → `#f9ebff` + radial `#ffffff` (`0.90`) | `#2c095e` (`0.68` opacity) |
| **Ruby / Crimson** | `#38040c` → `#7a0c18` | `#c81e2b` → `#ef4852` | `#ff9ea4` → `#fff0f2` + radial `#ffffff` (`0.90`) | `#6e1018` (`0.62` opacity) |
| **Emerald / Mint** | `#032b1a` → `#0b663e` | `#15a868` → `#42d692` | `#9ef5cc` → `#eefff7` + radial `#ffffff` (`0.90`) | `#0d5c38` (`0.60` opacity) |
| **Amber / Tangerine** | `#4a1802` → `#963808` | `#dc6814` → `#ff9e2c` | `#ffe078` → `#fffbe6` + radial `#ffffff` (`0.90`) | `#8c360a` (`0.62` opacity) |

### C. 3D Slate-Graphite Aqua Glass Emblem (`systemsettings.svg`, HIG `i-015.png`)
* Body vertical gradient (`#graphiteGlass`): `#8a949c` (`0.00`) → `#68747d` (`0.32`) → `#4b5760` (`0.72`) → `#414c54` (`0.90`) → `#6b7882` (`1.00`).
* Bottom radial bounce (`#graphiteBounce`): `#9cb0be` (`0.52`) → `#60707c` (`0.15` at `0.65`) → `#404c54` (`0.00`).
* Carved silver-plate seat: `+0.9, +1.3 px` `#ffffff` (`0.92`) bottom-right bevel + `-0.7, -0.8 px` `#2a3136` (`0.82`) top-left recess.

### D. Brushed Platinum, Moulded White Plastic & Studio Display Acrylic
* **Switch plate satin platinum** (`systemsettings.svg`): `#f9f9fa` (`0.00`) → `#f1f1f3` (`0.22`) → `#e5e6e8` (`0.65`) → `#dadbdc` (`0.94`) → `#c6c8cc` (`1.00`), outer `0.85 px` stroke `#7d8086`, inner top/left `1.5 px #ffffff`, inner bottom/right `1.3 px #96999f`.
* **Moulded white plastic cap / chicklet keys** (`accessories-calculator.svg`): `#ffffff` (`0.00`) → `#f8f8f9` (`0.42`) → `#eaeaec` (`0.88`) → `#dcdce0` (`1.00`), `0.7 px` border `#9a9aa0`, inner `0.95 px #ffffff` top/left lip.
* **Studio Display vertical pinstriped bezel** (`utilities-terminal.svg`): base `#ffffff → #eaecf0 → #c6cad1` overlaid with `<pattern width="2.1" height="8">` (`1.15 px #fcfdfe` at `0.92` + `0.95 px #cfd3da` at `0.68`).
* **Charcoal CRT glass** (`utilities-terminal.svg`): 5 stepped vertical sheen bands `#313237`, `#292a2f`, `#222327`, `#1b1c20`, `#141518` left-to-right + curved upper-left `#ffffff` (`0.16 → 0.02`) reflection.

### E. Die-Cast Aluminum, Spun Chrome, Paper & Warm Woods
* **Die-cast satin aluminum** (`drive-harddisk.svg`): `#f5f5f9` (`0.00`) → `#dedee5` (`0.06`) → `#cbcbd2` (`0.45`) → `#b7b6bd` (`0.86`) → `#aeacb4` (`0.96`) → `#f2f2f7` (`1.00` front bevel!). Gunmetal front bay: `#1e1f25 → #585963 → #2c2d34`. Lime LED: `#ffffff → #ebff54 → #9ad418 → #456b08`.
* **Cylindrical mirror chrome** (`accessories-text-editor.svg` pen): `#2c3038` (`0.00`) → `#b4bac4` (`0.14`) → `#ffffff` (`0.32`) → `#ffffff` (`0.49`) → `#5e646e` (`0.62`) → `#1e2229` (`0.76`) → `#d4dae4` (`0.90`) → `#2d323a` (`1.00`).
* **Ring / collar spun chrome** (`user-trash.svg`): `#cfd0d8` (`0.00`) → `#ffffff` (`0.11`) → `#686874` (`0.24`) → `#8b8b96` (`0.38`) → `#f5f5fc` (`0.56`) → `#ffffff` (`0.68`) → `#4e4e58` (`0.82`) → `#b8b8c2` (`0.93`) → `#dedee6` (`1.00`).
* **Crisp white stationery & canary pad** (`accessories-text-editor.svg`): white sheet `#ffffff → #f9fafc → #edf0f5 → #dfe4ec` (`0.7 px #aeb6c2` edge, `0.65 px #bfd0e6` rules); yellow pad `#fff484 → #f3da5c → #dec03e` (`0.7 px #b59a28` edge).
* **Cream stucco, honey-oak & slate roof** (`user-home.svg`): stucco `#fdfbf5 → #f2ede1 → #dfd8c7 → #cbc2ae`; honey-oak `#d8904a → #b46c2c → #8c4c1a → #6e3810`; espresso-slate roof `#6e665f → #423b36 → #24201d → #141210`.

---

## 2. Lighting & Shadow Recipe

1. **Key Light Direction**: Strictly **from directly above (`90°`)**, never `45°` top-left. Top horizontal rims receive crisp `1.2–1.7 px #ffffff` specular bevels; bottom interiors receive soft upward bounce light from the white/pinstriped floor.
2. **Generous Filter Bounds (Critical for `librsvg`)**: SVG's default filter region (`-10%` to `120%`) clips Gaussian tails on narrow ellipses into ugly flat-edged rectangles visible on pinstripes. Always declare explicit generous bounds:
   ```xml
   <filter id="floorBlur" x="-30%" y="-45%" width="160%" height="200%">
     <feGaussianBlur stdDeviation="4.6"/>
   </filter>
   <filter id="contactBlur" x="-20%" y="-30%" width="140%" height="170%">
     <feGaussianBlur stdDeviation="1.8"/>
   </filter>
   ```
3. **Two-Layer Grounded Floor Shadow (+ Caustic for Glass)**:
   * **Layer 1 — Ambient diffuse shadow**: `<ellipse cx="64" cy="111.5" rx="46" ry="6.5" fill="#000000" fill-opacity="0.28..0.34" filter="url(#floorBlur)"/>` (use `#000a1c` cool midnight tint under blue/glass icons).
   * **Layer 2 — Tight contact shadow**: `<rect x=".." y="108.5" height="4.2" rx="2" fill="#000000" fill-opacity="0.44..0.52" filter="url(#contactBlur)"/>` right along the resting base so the object feels planted, never floating.
   * **Layer 3 — Coloured caustic (translucent glass only)**: `<ellipse cx="64" cy="112.5" rx="20" ry="3.2" fill="#3a98ff" fill-opacity="0.26" filter="url(#causticBlur)"/>` (`stdDeviation="2.2"`).
4. **Straight-On Wall Plaques & Accessories** (`systemsettings`, `utilities-terminal`, `accessories-calculator`):
   * Duplicate the body silhouette shifted `dx = +1.0..+1.5` (or `0`), `dy = +3.0..+3.8`, `fill="#000000" fill-opacity="0.28..0.30"`, `stdDeviation="2.8..3.2"`.
5. **Inter-Object Cast Shadows** (protruding toggle switch, pen across paper, roof eave over stucco):
   * Offset `(+1.2..+3.4, +2.4..+4.2)`, `stdDeviation="2.2..2.8"`, `fill-opacity="0.26..0.46"`.

---

## 3. How to Build Each Material

### A. Translucent Aqua Glass (Orbs, Lenses, Glossy Badges)
Never draw glass as a flat fill + white crescent. Build all 6 layers inside `<clipPath>`:
1. **Base vertical `linearGradient`**: very dark midnight pole at `0.00` (`#02052b`) → saturated mid-tone (`#327ce0`) → pale incandescent cyan/tint at `1.00` (`#f2feff`). That dark top crown is what makes the white top specular pop!
2. **Internal bottom caustic `radialGradient`**: centered near the bottom edge (`cy ≈ bottom - 9`), `r ≈ 0.85 × radius`, `#ffffff` (`0.92`) fading to `0.0`.
3. **Atmospheric rim `radialGradient`**: transparent up to `offset="0.60"`, darkening toward `1.00` (`0.35–0.65` opacity) for spherical curvature.
4. **Internal suspended details** (geodesic arcs, glyphs): draw a `feGaussianBlur` (`stdDeviation="2.0"`) glow pass underneath a crisp `#ffffff` core pass.
5. **Top lens specular highlight**: curved `<ellipse>` or S-curved `<path>` covering the upper `~32%` height, filled with `#ffffff` (`0.72` at top → `0.34` at `0.35` → `0.00` at bottom).
6. **Surface tension edge**: `0.8 px` dark tinted stroke (`0.58` opacity) + optional `1.4 px` inner blurred pale rim (`#aee8ff` `0.42`).

### B. Mirror & Spun Chrome (Pens, Bezels, Screws, Wire Mesh)
* **Why grey gradients fail**: A smooth `#eeeeee → #888888` gradient reads as matte grey plastic. Real 10.2 chrome reflects a **sharp dark studio horizon** right next to a **pure `#ffffff` sky plateau** (`dark #2c3038 → silver #b4bac4 → pure #ffffff plateau → sharp horizon #5e646e / #1e2229 → secondary bounce #d4dae4 → dark edge`).
* **Conical chrome** (pen nose cones): divide into crisp triangular wedges sharing the apex — one jet-dark horizon wedge (`#101318`), one razor-sharp `#ffffff` wedge, and a silver mid-tone (`#b4bac4`).
* **Slotted chrome screws** (`systemsettings.svg`): `r="3.8..4.3"`, `+0.6 px #ffffff` bottom plate lip, `-0.3 px #60646b` top socket, `#ffffff → #c2c5cb → #757980 → #4e5258` dome, `1.25 px #2d3035` slot + `0.65 px #ffffff` slot lip. Vary screw slot angles (`90°`, `0°`, `-42°`, `+42°`) so hardware looks hand-assembled, never cloned!
* **Woven wire mesh** (`user-trash.svg`): draw a dark wire core pass (`1.45 px #1e1e24`) + `-0.5 px` upward-shifted specular wire pass (`0.92 px url(#frontWire)`).

### C. Brushed Platinum & System Preferences Panes (`systemsettings.svg` & `preferences-*`)
For `preferences-*` icons, HIG Chapter 11 (`i-015.png`) defines **two** official switch-plate layouts:
1. **Main System Settings (`systemsettings.svg`, `i-015.png` left)**: horizontal `110 × 88` brushed-platinum plate (`x=9..119, y=20..108, rx=2.0`), vertical seam at `x=43.5` (`1 px #9699a0` left + `1.1 px #ffffff` right), 4 corner screws, protruding 3D white rocker switch (`x=22.8..30.2, y=50.5..78.0`) in left compartment, 3D emblem in right compartment.
2. **Individual Preference Pane Icons (`i-015.png` right — ideal for System Settings KCMs!)**: vertical `86 × 106` sheet/plate (`x=21..107, y=11..117, rx=1.5`) with:
   * Left narrow brushed-platinum switch strip (`x=21..49`) holding the exact same 3D white rocker toggle (`x=31..38.4, y=48..75.5`, no corner screws on `i-015.png` right) + vertical divider seam at `x=49`.
   * Right satin-white/platinum compartment (`x=49..107`) featuring a **3D curled top-right corner** (`(84, 11) → (107, 34)`, casting a soft blurred shadow underneath the curl onto the right compartment) and a **full-colour 10.2 Aqua skeuomorphic object** (speaker, monitor, padlock, bell, globe, colour wheel, keyboard, etc.) centered in `x=52..103, y=42..104`! (Alternatively, concrete standalone 10.2 hardware/objects per KCM work great too — whichever reads clearest in System Settings' 32 px sidebar.)
* **Brushed grain overlay**: `<pattern width="16" height="3">` with `1 px #ffffff` (`0.18`) and `0.8 px #6e7278` (`0.05`) horizontal lines over `#switchPlate`.

### D. Translucent Acrylic Folders & Stamped Folder Family (`folder-*.svg`)
Keep the exact `folder.svg` geometry untouched across the entire `folder-*` family so Dolphin views align to the pixel. Stamp category glyphs onto `#frontShape` (inside `clip-path="url(#clipFront)"`, **underneath** `#frontGlass` and the top white lip!) using the front flap's perspective shear:
```xml
<g id="folderGlyph" transform="matrix(1.0, -0.072, -0.055, 1.0, 4.2, 4.8)">
  <!-- Centered around (64, 72), ~34-40 px wide/tall -->
</g>
<use href="#folderGlyph" transform="translate(0, 1.8)" fill="#ffffff" fill-opacity="0.72" filter="url(#emblemBevel)"/>
<use href="#folderGlyph" fill="url(#recessedCobalt)"/>
<use href="#folderGlyph" transform="translate(0, -0.8)" fill="none" stroke="#0b2c5e" stroke-width="0.9" stroke-opacity="0.45"/>
```
For coloured folders (`folder-red`, `folder-green`, etc.), hue-shift `#backLeaf`, `#frontAqua`, `#aquaGlow`, and `#recessedCobalt` together while preserving luminance stops and `#frontGlass`.

### E. Crisp Paper, Ruled Stationery & Readable Text (`accessories-text-editor.svg`)
* Fill `#ffffff → #dfe4ec` diagonally; add a `1.0 px #ffffff` inner top/left highlight inside the sheet's `<clipPath>`, and a `0.7 px #aeb6c2` outer cut-paper stroke.
* **HIG p. 206 rule**: Never draw wavy "greeked" lines for document text. Use real `<text>` in `Georgia, Liberation Serif, serif` (italic prose) or `Luxi Sans, DejaVu Sans, sans-serif` at `4.3–5.2 px` in dark ink `#171a20` aligned onto `0.65 px #bfd0e6` rules.

### F. 3D Carved Slate-Graphite Emblem (`systemsettings.svg`)
1. `<use href="#emblem" transform="translate(0.9, 1.3)" fill="#ffffff" opacity="0.92"/>` (bottom-right plate bevel)
2. `<use href="#emblem" transform="translate(-0.7, -0.8)" fill="#2a3136" opacity="0.82"/>` (top-left recess)
3. `<use href="#emblem" fill="url(#graphiteGlass)"/>`
4. Inside `<g clip-path="url(#clipEmblem)">`: `#graphiteBounce` rect + `<use href="#emblem" fill="none" stroke="#1e252a" stroke-width="2.6" opacity="0.62" filter="url(#kdeInner)"/>` (`stdDeviation="1.2"`) + S-curved upper glass sheen (`#ffffff` `0.66 → 0.10`).

---

## 4. Perspective & Camera by HIG Genre

Apple's June 2002 HIG (pp. 200–205, Figs. 11-18..11-22) assigns distinct cameras to each icon genre:

1. **Utilities, System Preferences & Floating Orbs — Straight-On Shelf (`0°` orthographic)**:
   * `utilities-terminal`, `systemsettings`, `accessories-calculator`, `user-home`, `internet-web-browser`.
   * Verticals are strictly vertical; horizontals are strictly horizontal. Depth comes from recessed bezels, protruding controls, and overhead shadows.
2. **Hardware Enclosures & Containers — Desk Perspective (`~18°–25°` downward look)**:
   * `drive-harddisk`: top face narrows toward the back (`x=25..103` at `y=20`, width `78`) and widens toward the front (`x=14..114` at `y=93.5`, width `100`), revealing a `17.5 px` tall 3D front chassis (`y=93.5..111`).
   * `user-trash`: tapered cylinder viewed slightly from above so the top rim opens into an ellipse (`rx=42.5, ry=10.2`, ratio `0.24`), revealing the curved back interior wall inside the mouth.
3. **Folders — Angled 10.2 Pocket Perspective**:
   * Rear leaf stands nearly upright (`y=16..112`) while the front acrylic flap tilts forward-right (`-4.2°` top lip from `(19.5, 43)` up to `(113.1, 36.6)`).
4. **Expressive User Applications — Angled Desk Canvas + Action Tool**:
   * `accessories-text-editor` (`i-005.png`): tilted canvas (`-11.5°` white sheet over `-27°` yellow pad) crossed diagonally by a `+26.5°` realistic chrome tool casting a blurred shadow across both sheets.
   * **Never put Mac OS X 10.2 app icons on iOS / macOS Big Sur rounded-square "squircles"!** Use real objects, tilted documents/blueprints + tools, floating Aqua glass sculptures, or spun-chrome medallions.

---

## 5. Canvas Margins, Optical Weight & Where the Floor Is

All SVGs use `viewBox="0 0 128 128" width="128" height="128"`.

* **The Floor Line (`y = 108..112.5`)**:
  * Resting bases of grounded objects land at **`y = 108.5..112.2`**.
  * Why not lower? An ambient shadow at `cy = 111.5..113.5` with `ry = 6.0` and `stdDeviation = 4.8` needs `~14 px` below its center (`y = 112..126`) to decay smoothly to zero alpha before `y = 128`. Anything resting below `y = 115` clips its shadow against the bottom canvas edge!
* **Top & Side Margins (Optical Weight Balancing)**:
  * **Standard square-ish objects** (`folder`, `utilities-terminal`, `user-home`, `drive-harddisk`): `x ≈ 13..115`, `y ≈ 15..112` (`~100 × 96 px`).
  * **Spheres & circular medallions** (`internet-web-browser`): `cx = 64, cy = 60.5, r = 47.5..49.0` (`y = 11.5..109.5`), centered `3.5 px` above canvas midpoint so room remains for the floor shadow at `cy = 113`.
  * **Wide horizontal plates** (`systemsettings`): `x = 9..119, y = 20..108` (`110 × 88 px`).
  * **Tall portrait objects** (`accessories-calculator`): `x = 22..106, y = 10..118` (`84 × 108 px`). Narrower width compensates for taller height so every icon occupies roughly `8,500–9,600 px²` of visual mass.

---

## 6. What to Check at 16, 22, 32 & 48 px

`make_icons.py` rasterizes `artwork/aqua-icons/*.svg` via `librsvg` (`Rsvg.Handle.render_document`) across `RICHER_SIZES` (`16`, `22`, `32`, `48`, `64`, `128`, plus `@2x`). Always render and inspect downscaled sizes before committing:

* **48 px (`DesktopDefault`)**:
  * Check fine patterns (`vertPinstripe`, `aquaStripes`, `backMeshPat`) for moiré aliasing. A pattern period of **`2.1–2.6 px`** in 128-space (`~0.8–1.0 px` at 48 px) blends smoothly into realistic satin texture without zebra banding.
* **32 px (`ToolbarDefault` / System Settings KCM sidebar)**:
  * Verify primary internal parts remain distinct: keypad grid gaps (`>= 3.3 px` in 128-space = `~0.85 px` at 32 px), toggle rocker + cast shadow, KDE `K` vs cogwheel teeth, pen silhouette against white paper.
* **22 px (`PanelDefault`) & 16 px (`SmallDefault` / Dolphin list view)**:
  * `1 px` details in 128-space shrink to `0.125 px` at 16 px and disappear. Recognition at `16–22 px` depends 100% on **silhouette + broad high-contrast tonal gradients** (e.g. `#02052b` dark crown vs `#ffffff` bottom caustic on spheres; bright `#ffffff` paper vs `#fff484` yellow corner + dark chrome pen; `#f9f9fa` silver plate vs dark `#414c54` emblem).
  * Keep outer strokes `<= 0.9 px` (`0.5–0.75` opacity). A `2.5 px` dark border in 128-space becomes a muddy grey halo at 16 px.

---

## 7. Workflow: References, Rendering & Comparing

1. **Measure Reference First**: Open the closest June 2002 HIG figure in `~/projects/agy-aqua-icons/reference/` (or Jaguar screenshots), sample RGB stops across top/mid/bottom/rim, and note key proportions (corner radii — e.g. Terminal's `r=11` top corners vs `r=2` square bottom corners!).
2. **Author Clean SVG**: Hand-write `<svg viewBox="0 0 128 128">` with named `<defs>`, `userSpaceOnUse` gradients, `<clipPath>` interior shading, and zero hard outlines.
3. **Render via `librsvg` onto Jaguar Pinstripes**:
   Test-render using `Rsvg.Handle` + `cairo.ImageSurface` (identical to `render_artwork_png` in `tools/make_icons.py`) composited onto Jaguar's 4-row pinstripe background `(255, 238, 230, 238)`. **Never audit on solid white or solid dark grey alone** — pinstripes immediately expose clipped `<filter>` boxes, unclosed interior paths, and weak highlights.
4. **Build a Side-by-Side Multi-Size Audit Card**:
   Composite `[2002 HIG figure] | [128×128 SVG] | [48 / 32 / 16 px]` on one sheet, inspect the PNG visually, fix at least the 2–3 subtlest material/alignment flaws in a second pass, and re-verify `QIcon.fromTheme` resolution after running `python3 tools/make_icons.py`.

---

## 8. Mistakes to Avoid

* **Hard cartoon outlines** (`stroke="#000000" stroke-width="2"`): destroys the photographic 10.2 look immediately. Separate surfaces with value contrast, `1.2–1.7 px #ffffff` sunlit bevels, and `0.7–0.9 px` mid-tone material edges.
* **Procedural `QPainterPath` polygon art**: lacks Gaussian inner cushion bevels, clipped radial bounce lights, and soft cast shadows; always author rich `librsvg` SVGs for full-colour icons.
* **Modern iOS / Big Sur rounded-square app tiles**: never wrap icons in uniform rounded squares.
* **Default SVG `<filter>` bounds**: forgetting `x="-30%" y="-45%" width="160%" height="200%"` clips drop shadows into visible grey boxes against pinstripes.
* **`objectBoundingBox` linear gradients on horizontal/vertical `<line>`s**: per the SVG spec, a horizontal or vertical line has zero bounding-box height or width, so `librsvg` skips `url(#grad)` strokes on `<line>` unless `gradientUnits="userSpaceOnUse"` is set!
* **Flat 2-stop grey "metal"**: chrome needs sharp dark horizon reflections (`#1e2229`) adjacent to `#ffffff`; die-cast aluminum needs a bright `#f2f2f7` front-lip bevel + stroke-free embossed light/shadow relief.
* **Open back rims on containers**: on cylindrical mouths (`user-trash`), clip the back wall to the **upper** ellipse arc (`A rx,ry 0 0 1`) and the front wall to the **lower** ellipse arc (`A rx,ry 0 0 0`) so pinstripes don't peek through the back half of the opening.
* **Wavy "greeked" text lines**: always use real readable `<text>` (HIG p. 206).
* **Generic prefix aliases in `ARTWORK_ICONS`**: never alias `preferences-desktop` or `preferences-system` — KDE's icon loader falls back from `preferences-desktop-*` to `preferences-desktop` before consulting `Inherits=KrystalSVG`, hiding every specific KCM icon.
* **Apple trademarks**: never ship the Apple logo or Apple's Finder smiley face; sculpt the official KDE `K` + cogwheel in native 10.2 materials instead.
