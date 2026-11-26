#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Install KrystalSVG, the maintained Plasma 6 continuation of Everaldo Coelho's Crystal SVG
# (KDE 3's Aqua-era icon theme), into ~/.local/share/icons/KrystalSVG.
#
# Oxygen Pinstripe inherits it for every full-colour icon it doesn't draw itself. It is
# downloaded rather than bundled because its licence (CC BY-NC-SA, see COPYING inside the theme)
# can't be redistributed in this GPL repository. About 120 MB to download, 430 MB unpacked.
#
#   contrib/install-krystalsvg.sh           install if missing
#   contrib/install-krystalsvg.sh --force   reinstall
set -euo pipefail

RELEASE="2025.08.10-14-20.Plasma5up-krystalSVG-icontheme.tar.gz"
URL="https://invent.kde.org/blackcrack/krystalsvg/-/raw/master/$RELEASE"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons/KrystalSVG"

if [[ -f "$DEST/index.theme" && "${1:-}" != "--force" ]]; then
    echo "KrystalSVG already installed in $DEST"
    exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
echo "downloading KrystalSVG (about 120 MB) from invent.kde.org"
curl -fL --progress-bar -o "$tmp/krystal.tar.gz" "$URL"
mkdir -p "$tmp/x"
tar -xzf "$tmp/krystal.tar.gz" -C "$tmp/x"
src="$(dirname "$(find "$tmp/x" -maxdepth 2 -name index.theme | head -n 1)")"
[[ -f "$src/index.theme" ]] || { echo "unexpected archive layout" >&2; exit 1; }

rm -rf "$DEST"
mkdir -p "$(dirname "$DEST")"
mv "$src" "$DEST"
rm -f "$HOME/.cache/icon-cache.kcache"
echo "installed KrystalSVG in $DEST"
