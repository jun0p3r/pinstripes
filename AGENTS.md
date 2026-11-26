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

*Last updated: 2026-11-26 by Perplexity Computer (Gemini 4 Carbon).*

* Repos & remotes:
  * Pinstripe suite: GitHub `https://github.com/jun0p3r/pinstripes` (`main`), local path on user's
    machine `~/projects/pinstripe-style`.
  * Window decoration: GitHub `https://github.com/jun0p3r/oxygen-traffic-lights`, local sibling
    `~/projects/oxygen-traffic-lights`.
  * Note: the user asked to push every major and minor step to `origin/main` and keep `AGENTS.md`
    updated for seamless handoff across Claude Code, Google Antigravity and Perplexity Computer.
* **Oxygen-wide 10.2 Aqua icon remake (in progress — Phase 1 complete & pushed)**:
  * Modular icon library created in `tools/icons_lib/` (`materials.py`, `places_devices.py`,
    `apps_categories.py`) and wired into `tools/make_icons.py` (builds all PNG sizes + SVGs in
    ~2.3 s, ~11 MB total in `icons/Oxygen-Pinstripe/`):
    * `places/`: **74/74** Oxygen names covered (49 masters + 28 aliases at 16–128 px): sky-blue
      and 9 colour-tinted pinstriped Aqua folders, 10.2 Save-dialog (`al-107-045.png`) recessed
      folder glyphs (`Documents`, `Downloads`, `Music`, `Pictures`, `Movies`, `Sites`, `Public`
      yellow diamond walking-person road sign), `Home` cottage, Aqua `Desktop`, sapphire `Network`
      globe on drive pedestal, Xserve `network-server` blades, and empty/full chrome wire-mesh
      `Trash` (`ch11-202-002.png`).
    * `devices/`: **89/89** Oxygen names covered (40 masters + 50 aliases at 16–128 px): Studio
      Display `computer`, white clamshell iBook `computer-laptop`, Figure 11-14 brushed-aluminum
      3.5" internal drive (`#d6d5db..#9d9ca1`) and amber-anodized external USB/FireWire drive
      (`#f4961e..#ffc448`), Figure 11-15 iridescent CD/DVD/BD discs and 3.5" floppy, snow-white
      scroll-wheel iPod, cylindrical aluminum iSight webcam, Apple Pro Keyboard/Mouse/Speakers,
      and UFO AirPort Base Station wireless levels.
    * `apps/`: **207/207** Oxygen names covered (+ Plasma 6 `org.kde.*` / freedesktop aliases; 59
      masters + 173 aliases at 16–128 px): sampled two-tone Finder smiley (`#9cbdff..#3052b6` /
      `#dceaff..#95a6de`, open-stroke nose & smile), TextEdit angled ruled pad + chrome pen,
      Preview stacked ocean photos + loupe, Mail scalloped hawk stamp, Safari mariner's compass,
      pinstriped-bezel Terminal (`>_`) and Process Viewer ECG monitors, Console amber LED matrix,
      Stickies, QuickTime player, iTunes CD + eighth notes, Calculator, Key Caps `⌘` keycap,
      Sherlock deerstalker + magnifier, Chess wooden knight, and 12 distinct Figure 11-12 System
      Preferences brushed-silver light-switch wall plates (`#fafafa..#dcdde0` with 4 corner screws)
      covering all 45+ `preferences-*` entries.
    * `categories/`: **40/40** Oxygen names covered (19 masters + 21 aliases at 16–128 px),
      including 10.2 `Applications` ruler-pencil-brush "A" and `Utilities` hammer & wrench.
    * `applets/`: **40/40** Oxygen PNG widget icons covered (16 masters + 24 aliases at 16–48 px).
    * `actions/`: **111** 10.2 masters (+200 aliases at 16–48 px & `32@2x`) already built; ~787
      additional niche Oxygen `actions/` names remain for Phase 3.
    * `symbolic/` & `panel/status/`: 426 menu-extra & symbolic SVGs.
  * Refreshed `docs/screenshots/plasma-desktop.png` (Dock & Go menu now render the 10.2 Finder,
    Terminal, Safari, Mail, System Preferences, Help and Mesh Trash icons),
    `docs/screenshots/icons-places-apps.png`, `docs/screenshots/icons.png`, `docs/preview.html`
    and `README.md`. Removed committed `.pyc` files and added `__pycache__/` + `*.py[cod]` to
    `.gitignore`.
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

1. **Finish remaking the remaining Oxygen icon categories in 10.2 Aqua style** (`tools/make_icons.py`
   already has `try: import` hooks ready at lines 2348–2371 for all three modules — create each
   module, rerun `python3 tools/make_icons.py`, render & visually inspect contact sheets, update
   `AGENTS.md`, and push after each step!):
   * **Phase 2A — `tools/icons_lib/mimetypes_icons.py` (`build_mimetypes_painters()`)**: cover all
     **441** Oxygen `mimetypes/` names (198 upstream real + 243 aliases) using `aqua_sheet()` from
     `materials.py` (Figure 11-11 "Do this": hovered curled white document with integrated central
     10.2 artwork and integrated uppercase bottom label `PDF`, `PNG`, `JPEG`, `SVG`, `MP3`, `MP4`,
     `ZIP`, `TAR`, `HTML`, `CSS`, `JS`, `PY`, `C++`, `RS`, `SH`, `TTF`, etc.; `pref_strip=True` for
     config/desktop/theme files per Figure 11-12; `aqua_plugin_cube()` for `package-x-generic`,
     `.rpm`, `.deb`, `.flatpak`, `.appimage`, `.apk` per Figure 11-13; `.iso`/`.dmg` optical image).
   * **Phase 2B — `tools/icons_lib/status_emblems_emotes.py`
     (`build_status_emblems_emotes_painters() -> (status, emblems, emotes, animations, special)`)**:
     cover all **129** `status/` icons (10.2 amber Caution triangle with `!`, crimson octagon Stop,
     Aqua blue Get Info sphere, brass lock, 28 Sherlock-style 3D golden sun / silver moon / puffy
     glass cloud weather icons, iChat glossy glass presence gems, battery/volume/wireless status),
     all **35** `emblems/` (Finder curved alias arrow `alias_arrow_badge()`, lock, heart, VCS
     check/plus/delta/bolt, GPG trust), all **51** `emotes/` (2002 iChat glossy 3D amber-yellow gel
     spheres with expressive faces + heart/rose/gift/food/drink), **4** `animations/` and **4**
     `special/`.
   * **Phase 3 — `tools/icons_lib/actions_extra.py` (`extend_action_painters(base_actions)`)**:
     extend `actions/` from 311 names to all **1,098** Oxygen `actions/` names (IDE `code-*`,
     `debug-*`, `run-build*`; vector/Calligra `draw-*`, `transform-*`, `align-*`, `distribute-*`,
     `format-*-node`, `object-*`, `layer-*`; `insert-table`/`edit-table-*`, `office-chart-*`,
     `view-calendar*`, `view-pim-*`, `view-financial-*`, `flag-*`, `tag*`, `mixer-*`, `im-*`,
     `irc-*`, `games-*`, `view-certificate*`).
   * Reference inventory check: clone `https://github.com/KDE/oxygen-icons.git` with
     `--filter=blob:none --no-checkout --depth 1` and diff `git ls-tree -r HEAD` against generated
     `icons/Oxygen-Pinstripe/32x32/<cat>/` to verify 0 missing names across all 2,212 Oxygen PNG
     entries.
2. **Live desktop verification**: pull on Fedora, run `cmake --install build && rm -f ~/.cache/icon-cache.kcache`,
   and inspect Dolphin, Konsole, KMail, System Settings, Kickoff and the Plasma Dock.
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
