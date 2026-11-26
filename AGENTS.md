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

## Handoff: read this first if you are picking the work up

The user (Franco) works with more than one agent: Claude Code, and Google Antigravity while
Claude's usage limit resets. Whoever picks the work up continues from the two sections below,
and **must update both before stopping**. Keep them short and true: the next agent (possibly
Claude again) relies on them to resume without re-deriving anything.

### How this user works

* Goal: an Aqua look for Plasma 6 that is **as true to Mac OS X 10.2 as possible**, measured
  against Apple's 2002 HIG (`reference/aqua-hig-2002.pdf`, not in git; see
  `reference/README.md`). The user notices small inaccuracies (a seam, a missing pinstripe, a
  cut-off gradient) from screenshots of the live desktop, and calls out work that looks
  "tacky". Don't claim something is fixed until a render, and ideally pixel samples, show it.
* Show results as pictures. Render previews (tools above) and update `docs/preview.html`;
  the user also has a private claude.ai page of it that only Claude can republish, so other
  agents should just keep the local `docs/preview.html` and `docs/screenshots/` current.
* Ask before anything outward-facing or hard to undo: switching their themes, pushing,
  installing system-wide. System installs need their sudo password; give them the command to
  run in their own terminal.
* Fedora 45, KDE Plasma 6.8 on Wayland, NVIDIA, two 1920×1080 screens, zsh, Luxi Sans as the
  UI font (Lucida Grande stand-in). They already run Pinstripe everywhere
  (`contrib/apply-pinstripe.sh`); `contrib/revert-pinstripe.sh` undoes it.

### Current state (update this)

*Last updated: 2026-11-26 by Claude Code (Opus 5.5).*

* Repos: `~/projects/pinstripe-style` (this one) and `~/projects/oxygen-traffic-lights` (window
  decoration). Both have local commits only; nothing is pushed and no remote is set.
* Installed on the user's machine:
  * Widget style plugin: `/usr/lib64/qt6/plugins/styles/pinstripe.so`, **one build behind**:
    the progress-bar gel, flat disclosure triangles, menu shortcut column, KWindowShadow drop
    shadows, matte bevel buttons, group boxes and alerts are built in `build-system/` but not
    installed yet. To install (user runs it, needs sudo):
    `sudo install -Dm755 build-system/bin/styles/pinstripe.so /usr/lib64/qt6/plugins/styles/pinstripe.so`
    then restart apps.
  * Plasma style, GTK theme, icons, colour schemes, kstyle themerc: `~/.local/share/...`
    (current; reinstall with `cmake --install build` after regenerating). After installing the
    Plasma style switch to another style and back; after icons, remove
    `~/.cache/icon-cache.kcache`.
  * Decoration: `/usr/lib64/qt6/plugins/org.kde.kdecoration3/org.kde.oxygentrafficlights.so`
    (current, with the pinstriped title bar).
* Recently matched to the HIG: group boxes (Fig. 8-2..8-4), alerts (6-2), small system and
  label fonts, list rows (7-32), menus (chapter 4) with the 10.2 shortcut column, bevel buttons
  (7-14), sorted header (7-34), disclosure triangles (7-34), 16 px progress bar with measured
  fill rows (7-27), Plasma busy spinner, menu/tooltip drop shadows.
* Known limits (not bugs to fix): QML/Kirigami pages can't show pinstripes; GTK tabs can't be
  centred; Plasma Dock triangle sized for a 44 px panel; libadwaita ignores GTK themes.

### Backlog (update this; highest value first)

1. **Install the latest widget style build** (command above) and check on the live desktop:
   menus should show drop shadows; group boxes, bevel buttons and progress bars as in
   `docs/screenshots/`. Ask the user for a screenshot if you can't take one.
2. **Plasma progress bar / slider groove** (`bar_meter_*` in `tools/make_plasma_theme.py`): use
   the measured progress rows (see `GelKind::Progress` in `style/gel.cpp`) and 16 px height for
   progress; the slider groove shares the SVG, so check sliders after.
3. **GTK parity with this round**: progress fill rows, flat grey disclosure triangles
   (treeview expander), matte bevel buttons (`button.image-button` / toolbar buttons with
   frames), group boxes are `frame` with a label: etched line, title on the border, small
   font; list headings in the small font.
4. **Help tags (tooltips)**: compare with HIG/10.2 artwork (pale yellow, black text, 11 pt);
   check padding and the shadow in the live session.
5. **Toolbars**: HIG chapter 7 "Toolbars" and chapter 11 icon guidance; Finder-style
   icon-above-label toolbars with no frames, small system font labels (labels done in Qt).
6. **Window title bar** (`../oxygen-traffic-lights`): compare height, title font (13 pt) and
   the traffic-light spacing with HIG Figure 5-x window anatomy; inactive title text colour.
7. **Default-button pulse**: compare timing and the paler phase with a 10.2 recording if one
   can be found; currently a 1.7 s cosine between full colour and a paler gel.
8. **Sheets and drawers** (HIG chapter 5): Qt has no direct equivalent; skip unless the user
   asks.
9. Keep `docs/preview.html` and the README screenshots current after each round.

### Session log (append one line per session, newest last)

* 2026-11-25 Claude Code: decoration fork, Qt style, Plasma style, GTK theme, icon theme,
  switch/revert scripts, repo prep; first HIG polish rounds.
* 2026-11-26 Claude Code: HIG rounds 1-3 (group boxes, alerts, fonts, menus, shadows, bevel
  buttons, progress, disclosure triangles, spinner); AGENTS.md handoff. Stopped at ~91 % of
  the 5-hour usage limit.
