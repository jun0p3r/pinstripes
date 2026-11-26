# AGENTS.md

Notes for coding agents (and people) working on Pinstripe: an Aqua look for KDE Plasma 6
modelled on Mac OS X 10.2 "Jaguar". Read this before changing anything.

## What is here

| Part | Source | Built / generated output |
|---|---|---|
| Qt 6 widget style ("Pinstripe", "Pinstripe Graphite") | `style/` (C++, a `QProxyStyle` over Fusion) | `build/bin/styles/pinstripe.so` |
| Plasma style | `tools/make_plasma_theme.py` | `plasma/pinstripe/` |
| GTK 3 / GTK 4 theme | `tools/make_gtk_theme.py` | `gtk/Pinstripe/` |
| Icon theme "Oxygen Pinstripe" (10.2 full-colour + symbolic icons) | `tools/make_icons.py` + `tools/icons_lib/` | `icons/Oxygen-Pinstripe/` |
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

* Repos & remotes:
  * Pinstripe suite: GitHub `https://github.com/jun0p3r/pinstripes` (`main`), local path on user's
    machine `~/projects/pinstripe-style`.
  * Window decoration: GitHub `https://github.com/jun0p3r/oxygen-traffic-lights`, local sibling
    `~/projects/oxygen-traffic-lights`.
  * Note: the user asked to push every major and minor step to `origin/main` and keep `AGENTS.md`
    updated for seamless handoff across Claude Code, Google Antigravity and Perplexity Computer.
* **Icon direction (decided by the user, 2026-11-26)**: the procedural `tools/icons_lib/`
  places/devices/apps/categories/applets read as flat clip-art, so they are **no longer emitted**
  (the modules stay in the repo, unused). `Oxygen Pinstripe` now has three layers:
  * **Hand-drawn icons** (`artwork/aqua-icons/*.svg`, written by `tools/draw_aqua_icons.py`,
    rendered to PNG by `make_icons.py` via librsvg with KDE aliases in `ARTWORK_ICONS`): folder,
    user-home, folder-download, user-trash, system-file-manager, utilities-terminal,
    systemsettings, drive-harddisk, internet-web-browser, accessories-text-editor,
    accessories-calculator. They follow the HIG chapter 11 figures as closely as possible (the
    user wants them truthful to 10.2 and skeuomorphic, not a loose remix): no hard outlines, light
    from directly above, colours measured from the figures (monitor bezel #c6c7c8, screen
    #484b50; globe navy #28338a at the top to #bfe0fa at the bottom; disk top #c4c3c8..#aaa9af,
    front #4a4a54; logo #9aa0a5..#4c5a61). The KDE logo replaces Apple's. Side-by-side with
    Apple's figures: `docs/mockups/aqua-remix/hig-side-by-side.png`.
  * **Glass toolbar action icons** (111 + 200 aliases) and the 426 menu-extra symbolics. The
    user found the action icons too heavy: `render_action_png` now paints through `SoftPainter`,
    which lifts dark outline pens toward a mid tone, draws them 30 % thinner and turns near-black
    glyph fills into Jaguar's dark grey #3b3e43 (matching the Finder's light-rimmed Back/Forward
    buttons in real 10.2 screenshots). Symbolic glyphs are eroded by `thin()` (0.18 units, 0.27 on
    the panel); more than that breaks the Bluetooth rune and clipboard lines apart.
  * **Panel = 10.2 menu extras** (user's choice: outlined, like the real Jaguar menu bar). Tray
    names (`TRAY` prefixes) are rebuilt with `STROKE_SCALE = MENU_EXTRA_STROKE` (0.6) plus line
    versions from `menu_extra_overrides()` (bell, Bluetooth rune, sun, update ring, clipboard,
    phone, moon/night light, Caps Lock, weather set, power profiles, eject). They replace the
    `-symbolic` glyph for those names, because Plasma's tray asks for `-symbolic` names at 16 px;
    every other symbolic glyph keeps the solid style. **Plasma caches tray icons in memory:**
    after installing, `systemctl --user restart plasma-plasmashell.service` (toggling the icon
    theme isn't enough). Crystal sits before Breeze in the fallback chain, so any tray name we
    don't draw shows Crystal's colour art; add it to the overrides. One unidentified solid up
    arrow remains in the user's tray.
  * **Crystal for everything else**: `index.theme` inherits `KrystalSVG,oxygen,breeze,hicolor`.
    KrystalSVG (https://invent.kde.org/blackcrack/krystalsvg) continues Everaldo's KDE 3 Crystal
    SVG. Its licence is **CC BY-NC-SA**, so it must never be committed here; users install it
    with `contrib/install-krystalsvg.sh` (120 MB download, into `~/.local/share/icons/KrystalSVG`),
    and `apply-pinstripe.sh` warns when it's missing. Nuvola (LGPL) and Bluecurve (GPL) were
    compared and rejected (`docs/mockups/aqua-remix/classic-sets-compare.png`).
* To install on the user's Fedora machine after pulling `main`:
  * User-local themes, icons & colours:
    `git pull && cmake -S . -B build -G Ninja -DCMAKE_INSTALL_PREFIX=$HOME/.local && cmake --install build && rm -f ~/.cache/icon-cache.kcache`
    (then switch Plasma style or icon theme away and back in System Settings to flush caches).
  * System-wide Qt style + KWin decoration (needs sudo, if not yet installed from last round):
    `sudo install -Dm755 build-system/bin/styles/pinstripe.so /usr/lib64/qt6/plugins/styles/pinstripe.so && sudo install -Dm755 ../oxygen-traffic-lights/build-system/bin/org.kde.oxygentrafficlights.so /usr/lib64/qt6/plugins/org.kde.kdecoration3/org.kde.oxygentrafficlights.so && dbus-send --session --type=method_call --dest=org.kde.KWin /KWin org.kde.KWin.reconfigure`
* Regenerating icons on another machine gives **pixel-identical PNGs with different bytes**
  (each Qt version compresses PNGs differently). Before committing a regeneration, check that
  pixels actually changed (e.g. PIL `ImageChops.difference(...).getbbox()`), and
  `git checkout -- icons` if they didn't, to avoid thousands of no-op file changes. Run the
  generators with plain `python3`, not `python3 -I`: isolated mode drops the script folder from
  `sys.path`, so `tools/icons_lib` isn't found and the generator stops after clearing its output.
* Known limits (not bugs to fix): QML/Kirigami pages can't show pinstripes; GTK tabs can't be
  centred; Plasma Dock triangle sized for a 44 px panel; libadwaita ignores GTK themes.

### Backlog (update this; highest value first)

1. **Extend the hand-drawn set** where Crystal and the hand-drawn icons clash. Next: the folder
   family (`folder-documents`, `-music`, `-pictures`, `-videos`, `-desktop`, `-public`,
   `-templates`, coloured folders) as the Jaguar folder with a stamped glyph, and
   `user-trash-full`. Add each to `tools/draw_aqua_icons.py` + `ARTWORK_ICONS`, compare against
   the HIG figures, and render the resolver sheet (QIcon.fromTheme with explicit
   `setThemeSearchPaths`, since PySide's bundled Qt only searches `:/icons`). Don't recreate the
   cancelled procedural phases (mimetypes, status, emblems, actions_extra): Crystal covers them,
   and those `try: import` hooks in `make_icons.py` would shadow it.
2. **Live desktop check of the new icons** in Konsole, KMail, System Settings, Kickoff and the Dock
   (Dolphin checked 2026-11-26).
3. **Default-button pulse & small control variants** (HIG chapter 8, p. 160).

### Session log (append one line per session, newest last)

* 2026-11-25 Claude Code: decoration fork, Qt style, Plasma style, GTK theme, icon theme,
  switch/revert scripts, repo prep; first HIG polish rounds.
* 2026-11-26 Claude Code: HIG rounds 1-3 (group boxes, alerts, fonts, menus, shadows, bevel
  buttons, progress, disclosure triangles, spinner); AGENTS.md handoff. Stopped at ~91 % of
  the 5-hour usage limit.
* 2026-11-26 Antigravity (Gemini 4): glassy bevel buttons and seamless selected-tab-to-strip
  join across Qt, Plasma and GTK; Plasma 16 px progress + 6 px dark slider groove; GTK 3/4 HIG
  parity (progress rows, expanders, group boxes, sorted small-font headers); Finder toolbars,
  help-tag padding, 22 px title bar + 13 px traffic lights in `oxygen-traffic-lights`; refreshed
  all previews.
* 2026-11-26 Antigravity (Gemini 4): added 111 full-colour Mac OS X 10.2 Aqua action icons
  (+200 aliases, 16–48 px & `32@2x`) to `Oxygen Pinstripe` sampled from HIG Chapter 11 (Finder,
  Mail, Preview, Print Dialog, Formatting Palette), switched Qt/Plasma/GTK previews to
  `Oxygen-Pinstripe`, and refreshed all screenshots and docs.
* 2026-11-26 Perplexity Computer (Gemini 4 Carbon): fixed README `oxygen-traffic-lights` GitHub
  link, cleaned `.pyc` files / `.gitignore`, created modular `tools/icons_lib/` and remade 100 %
  of Oxygen's `places/` (74), `devices/` (89), `apps/` (207), `categories/` (40) and PNG
  `applets/` (40) in sampled 10.2 Aqua style (16–128 px), refreshed `plasma-desktop.png` + icon
  contact sheets, wired Phase 2/3 hooks (`mimetypes`, `status/emblems/emotes`, `actions_extra`)
  and updated `AGENTS.md` for handoff.
* 2026-11-26 Claude Code (Opus 5.5, on the user's machine): pulled all agents' work, built both
  repos, confirmed the icon generator reproduces the committed icons pixel for pixel, installed
  the user-local parts (themes, icons, GTK, colours) and reloaded Plasma's caches; the live
  panel shows the new Dock and tray icons. The system-wide widget style + decoration install was
  started in the user's terminal and is waiting for their sudo password.
* 2026-11-26 Claude Code (Opus 5.5): system-wide install done; menu bar fix (whole bar on window
  stripes); `gh` signed in so pushes work; set up `~/projects/AGENT-CHAT.md` as a mailbox with
  Antigravity. Icons: hand-drawn HIG-matched set (`artwork/aqua-icons/`), procedural colour
  categories dropped, theme now inherits Crystal via KrystalSVG (`contrib/install-krystalsvg.sh`).
* 2026-11-26 Claude Code (Opus 5.5): thinner symbolics (`thin()`), lighter toolbar action icons
  (`SoftPainter`), checked against Jaguar screenshots from guidebookgallery.org (menu bar volume
  extra, Finder and Mail toolbars).
