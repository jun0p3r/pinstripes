# AGENTS.md

Notes for coding agents (and people) working on Pinstripe: an Aqua look for KDE Plasma 6
modelled on Mac OS X 10.2 "Jaguar". Read this before changing anything.

## What is here

| Part | Source | Built / generated output |
|---|---|---|
| Qt 6 widget style ("Pinstripe", "Pinstripe Graphite") | `style/` (C++, a `QProxyStyle` over Fusion) | `build/bin/styles/pinstripe.so` |
| Plasma style | `tools/make_plasma_theme.py` | `plasma/pinstripe/` |
| GTK 3 / GTK 4 theme | `tools/make_gtk_theme.py` | `gtk/Pinstripe/` |
| Icon theme "Oxygen Pinstripe" (symbolic icons) | `tools/make_icons.py` | `icons/Oxygen-Pinstripe/` |
| Colour schemes | `colors/*.colors` (hand-written) | installed as-is |
| Switch / revert a session | `contrib/apply-pinstripe.sh`, `contrib/revert-pinstripe.sh` | |
| Offscreen previews | `tools/gallery/` (Qt), `tools/preview_plasma.py`, `tools/gtk_gallery.py`, `tools/preview_icons.py` | `docs/screenshots/` |

The window decoration lives in a sibling repo, `../oxygen-traffic-lights` (a fork of Oxygen's
KDecoration3 plugin with traffic-light buttons and a pinstriped title bar).

**Never hand-edit generated output** (`plasma/pinstripe/`, `gtk/Pinstripe/`,
`icons/Oxygen-Pinstripe/`). Change the generator and rerun it; the output is committed so the
repo installs without Python.

## Where the look comes from

Everything follows Apple's *Aqua Human Interface Guidelines*, June 2002 (`reference/aqua-hig-2002.pdf`, kept out of git; see `reference/README.md`) (chapter 7, Controls;
chapter 8, Layout; chapter 10, Fonts). Measurements and colours were taken from that document:
sizes from its specification text, colours by sampling its artwork pixel by pixel. Keep it
that way:

* **Don't eyeball a value you can measure.** Sample the HIG artwork (`pdfimages` extracts the
  lossless figures) or real 10.2 screenshots, and put the numbers in a comment next to the code.
* Key numbers: push button 20 px with 14 px end caps (OK/Cancel 69 px); check box / radio
  18 × 18 incl. shadow; pop-up 20 px, text 9 px from the left; tab 23 px, 12 px text inset,
  6-row accent bar `#0057ae #a2d7f0 #a8d1ee #51b0ea #79ccff #acefff` plus a 3-row grey shadow;
  text field 22 px with a 3 px inner shadow; slider thumb 15 × 15 (15 × 18 pointed); scroll bar
  15 px; window margins 20 px, controls 12 px apart; group box contents 16 px from the border;
  list rows 19 pt; system font 13 pt, small system font 11 pt (list headings, help tags, alert
  informative text).
* Window pinstripe rows: 255, 238, 230, 238 (4 px period). Menu rows: 255, 249, 238, 249.
* Aqua blue gel column (20 px pop-up cap): pale lens, sharp edge at ~45 %, then brightening to
  cyan. The scroll thumb uses its own measured columns (`GelKind::Thumb` in `style/gel.cpp`).
* Behaviour: only the default button is coloured (and pulses); inactive windows lose colour;
  dialog buttons in Mac order; menus separate groups with space, not lines.
* One deliberate departure: the selection highlight is a glossy striped gel (Jaguar's was flat).
  It has a fixed 11 px lens and 8 px glow with a tiled striped middle, identical in Qt
  (`paintSelection`), Plasma (`selection()` in the Plasma generator) and GTK (`SELECTION`).
  Change all three together.

## Build and check

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_GALLERY=ON -DCMAKE_INSTALL_PREFIX=$HOME/.local && cmake --build build
```

```bash
python3 tools/make_plasma_theme.py && python3 tools/make_gtk_theme.py && python3 tools/make_icons.py
```

Check every visual change with a render, never only by reading the code, and compare against
the HIG artwork at 3× zoom with nearest-neighbour scaling:

```bash
QT_PLUGIN_PATH=$PWD/build/bin ./build/bin/pinstripe-gallery /tmp/g Pinstripe $PWD/colors/Pinstripe.colors
```

GTK renders headless through Broadway (nothing appears on screen):

```bash
broadwayd :7 & GDK_BACKEND=broadway BROADWAY_DISPLAY=:7 python3 tools/gtk_gallery.py 3 /tmp/gtk3.png
```

When a render looks right, check the pixels too (sample a row across the control). Several
bugs here were only visible as numbers: a gradient that should be flat, a seam one pixel wide.

## Things that already went wrong once

* **GTK ignores the centre slice of `border-image`**, even with `fill`. Gels in GTK are three
  background layers (start cap, middle, end cap) built by `three()` in the GTK generator.
* **GTK 3 fades the edges of a stretched 1 px image.** The middle layer is tiled
  (`repeat-x`), never stretched, and starts 1 px under each cap.
* **CSS selector lists:** appending `:checked` to `"a, b"` only applies it to `b`. Use single
  selectors where pseudo-classes get appended.
* **GTK's `margin: auto` doesn't exist**, so GTK notebook tabs can't be centred.
* **QML (Kirigami) apps only read palette colours**, so they can't show the window pinstripe
  brush. Don't try to fix that from the style.
* **Plasma frames can't centre a shape.** The Dock triangle sits in a stretched bottom border
  between wide transparent corners; it is sized for the default 44 px panel.
* **Shell:** with `set -o pipefail`, `cmd | grep -q x` fails when grep exits early; test with
  `[[ -n "$(cmd)" ]]`. Never `pkill -f` a pattern that appears in your own command line.
* **zsh** is the user's shell: `$var` isn't word-split; use arrays or `${=var}`.

## Installing and the user's session

* The Plasma style, GTK theme, icons and colour schemes work from `~/.local/share`.
* Qt doesn't search `~/.local/lib64/plugins`, so the widget style plugin must be installed to
  `/usr/lib64/qt6/plugins/styles/` (needs sudo; ask the user to run it) or found via
  `QT_PLUGIN_PATH`.
* Don't switch the user's themes, fonts or decoration without asking. `contrib/apply-pinstripe.sh`
  saves the previous settings and `contrib/revert-pinstripe.sh` restores them.
* Plasma caches icons and SVGs: after changing installed icons remove
  `~/.cache/icon-cache.kcache`; after changing the Plasma style, switch to another style and back.

## Commits

Commit only files you changed. The repo's author is set locally; end commit messages with the
co-author line the session's instructions give.
