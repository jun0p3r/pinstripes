# Mac OS X 10.2 "Jaguar" Aqua Icon Set — Design & Material Notes

All 11 icons in `svg/*.svg` are hand-authored `128 × 128` vector artworks built specifically for `librsvg` + `cairo`, modelled directly on the June 2002 *Aqua Human Interface Guidelines* Chapter 11 ("Icons", pp. 199–210) reference plates in `./reference/`.

## Core Principles Applied

1. **Overhead Studio Lighting & Zero Cartoon Outlines**:
   - Every object is lit from **directly above** (with subtle bottom/environment bounce light and Gaussian-blurred ambient + contact shadows underneath).
   - Surfaces meet through **material contrast, machined specular bevels, and recessed shadow seams** rather than dark ink outlines.
2. **Perspective Matched by Icon Genre** (HIG Fig. 11-18..11-22):
   - **Shelf / Straight-on** (`0°` camera): `system-file-manager` (Finder plaque), `utilities-terminal` (Studio Display monitor), `systemsettings` (wall switch plate), `accessories-calculator` (desktop accessory), `user-home` (gabled stucco cottage), `internet-web-browser` (floating sapphire glass globe).
   - **Angled Desk Perspective**: `folder` and `folder-download` (slightly angled 10.2 Aqua acrylic folders), `drive-harddisk` (diminishing 3.5" internal aluminum enclosure), `user-trash` (tapered cylindrical wastebasket viewed slightly from above), `accessories-text-editor` (stacked `-27°` yellow and `-11.5°` white ruled pads crossed by a `+26.5°` chrome ballpoint pen).
3. **KDE Branding in Native 10.2 Materials**:
   - Where Mac OS X 10.2 placed an Apple mark, the official **KDE K + cogwheel** emblem is sculpted in the exact local material: embossed metallic silver on the `utilities-terminal` pinstriped acrylic chin, and 3D carved slate-graphite Aqua glass with an S-curved upper specular reflection on the `systemsettings` brushed-platinum switch plate.
4. **Readable Prose** (HIG p. 206):
   - `accessories-text-editor` uses genuine readable italic serif prose (`Dear Jon, ... Best, Kate Chen`) aligned to sky-blue stationery rules rather than wavy greeked lines.

## Per-Icon HIG Reference Mapping & Sampled Palettes

| Icon (`svg/<name>.svg`) | HIG Reference Plate | Key Sampled Colours & Material Details |
|---|---|---|
| `folder` | `i-021.png`, `hig_key_zooms.png` | Translucent sky-blue rear & front Aqua acrylic (`#f2ffff` → `#87c8fc` → `#3f85de` + `#d4f7ff` radial bottom bounce), fine `2.6 px` tilted pinstripes, crisp white paper sheet tucked inside pocket, overhead glossy lip. |
| `folder-download` | `i-021.png` + 10.2 Save-sheet folders | Identical 10.2 sky-blue Aqua folder with Breeze's download arrow + tray recessed into the front acrylic leaf (`#17468a` → `#2e6fc7` impression + blurred white lower-lip catchlight). |
| `user-home` | `i-020.png`, `hig_key_zooms.png` | Warm cream stucco walls (`#fdfbf5` → `#cbc2ae`), overhanging espresso-slate gabled roof (`#6e665f` → `#141210`) casting a blurred eave shadow, 4-pane mullioned gable window with mahogany louvred shutters, stone chimney, carved honey-oak 4-panel door (`#d8904a` → `#6e3810`) with brass knob. |
| `system-file-manager` | `i-002.png` (left), `hig_key_zooms.png` | Sampled two-tone Finder plaque: royal periwinkle-cobalt left (`#b8d0f8` → `#3a5ac2` → `#8ba3e6`) and icy lavender-blue right (`#dce7ff` → `#90a0d6` → `#ccd9fc`), 4-sided cushion bevels, chiseled butt-capped dark-navy eyes, wide smile, and overhanging S-curve nose divider casting soft 3D shadows onto the plaque. |
| `user-trash` | `i-002.png` (right), `hig_key_zooms.png` | Empty spun-chrome wire-mesh wastebasket: multi-stop cylindrical studio horizon reflection (`#cfd0d8` → `#ffffff` → `#686874` → `#ffffff` → `#4e4e58`), tubular rolled top rim, full interior back-wall mesh visible inside the elliptical mouth, and 36 curved front chrome wire strands over a metallic base pan. |
| `utilities-terminal` | `i-003.png`, `i-010.png`, `hig_key_zooms.png` | Authentic 10.2 Studio Display silhouette (**rounded `r=11` top corners, crisp `r=2` square bottom corners**), `2.1 px` vertical acrylic pinstripes, recessed charcoal CRT glass with 5 subtle vertical tonal bands (`#313237` → `#141518`) + curved upper-left glass reflection, glowing `>_` prompt, and miniature embossed KDE K+cogwheel chin badge. |
| `systemsettings` | `i-015.png` (left) | Horizontal brushed-platinum wall switch plate (`#f9f9fa` → `#dadbdc`), vertical seam at `x=43.5`, 4 slotted chrome corner screws at natural slot angles (`90°`, `0°`, `-42°`, `+42°`), protruding 3D white rocker switch casting a blurred downward shadow, and 3D slate-graphite Aqua glass KDE K+cogwheel emblem (`#8a949c` → `#414c54`). |
| `drive-harddisk` | `i-017.png` (bottom-center) | Diminishing-perspective die-cast satin aluminum 3.5" drive (`#f5f5f9` → `#b7b6bd`), stroke-free embossed platter & spindle relief, recessed black/silver barcode spec label, 5 dark Torx cover screws, gunmetal front bay with left cast scoop, 9 cooling vents, and glowing chartreuse-lime LED (`#ebff54`). |
| `internet-web-browser` | `i-017.png` (bottom-left) + `breeze/internet-web-browser.svg` | Liquid sapphire Aqua glass globe: deep midnight-indigo crown (`#02052b` → `#194cb4`) to incandescent cyan-white bottom caustic (`#bcf0ff` → `#ffffff`), subtle internal Earth continents, 7 glowing geodesic orbital light arcs with blooming star-white intersection nodes, curved top lens highlight, and blue floor caustic. |
| `accessories-text-editor` | `i-005.png` (TextEdit) | Canary-yellow ruled pad (`-27°`) beneath crisp white sky-blue ruled letter sheet (`-11.5°`) with readable italic serif prose, crossed by a `+26.5°` mirror-chrome retractable ballpoint pen with 11 lathe-turned grip rings, tapered pocket clip, clicker plunger, and conical horizon-reflected nose cone. |
| `accessories-calculator` | `i-009.png` (right) | Straight-on desktop calculator with curved bright-white moulded top cap (`y=10..23.4`), horizontal seam, brushed satin-platinum body, recessed cool-grey LCD (`123456.89`), and 4 × 5 crisp bright-white sculpted chicklet keys including the 2-row `=` key. |
