#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Put back the settings that contrib/apply-pinstripe.sh saved before switching to Pinstripe.
set -euo pipefail

state="${XDG_DATA_HOME:-$HOME/.local/share}/pinstripe-style/previous-settings"
if [[ ! -f "$state" ]]; then
    echo "no saved settings at $state; nothing to revert" >&2
    exit 1
fi
declare -A prev
while IFS='=' read -r k v; do prev[$k]="$v"; done < "$state"

wr() { kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; }

[[ -n "${prev[colorscheme]}" ]] && plasma-apply-colorscheme "${prev[colorscheme]}" >/dev/null || true
[[ -n "${prev[desktoptheme]}" ]] && plasma-apply-desktoptheme "${prev[desktoptheme]}" >/dev/null || plasma-apply-desktoptheme default >/dev/null
[[ -n "${prev[icons]}" ]] && { /usr/libexec/plasma-changeicons "${prev[icons]}" >/dev/null 2>&1 || wr kdeglobals Icons Theme "${prev[icons]}"; }
wr kdeglobals KDE widgetStyle "${prev[widgetstyle]:-Breeze}"
for pair in font:font menufont:menuFont toolbarfont:toolBarFont smallfont:smallestReadableFont; do
    k=${pair%%:*}; key=${pair#*:}
    if [[ -n "${prev[$k]}" ]]; then wr kdeglobals General "$key" "${prev[$k]}"; else kwriteconfig6 --file kdeglobals --group General --key "$key" --delete; fi
done
if [[ -n "${prev[wmfont]}" ]]; then wr kdeglobals WM activeFont "${prev[wmfont]}"; else kwriteconfig6 --file kdeglobals --group WM --key activeFont --delete; fi
[[ -n "${prev[deco_library]}" ]] && wr kwinrc org.kde.kdecoration2 library "${prev[deco_library]}"
[[ -n "${prev[deco_theme]}" ]] && wr kwinrc org.kde.kdecoration2 theme "${prev[deco_theme]}"
wr kwinrc org.kde.kdecoration2 ButtonsOnLeft "${prev[buttons_left]}"
wr kwinrc org.kde.kdecoration2 ButtonsOnRight "${prev[buttons_right]}"
[[ -n "${prev[gtktheme]}" ]] && busctl --user call org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig setGtkTheme s "${prev[gtktheme]}" >/dev/null 2>&1 || true

dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:2 int32:0 || true
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:1 int32:0 || true
dbus-send --session --type=method_call --dest=org.kde.KWin /KWin org.kde.KWin.reconfigure || true
mv "$state" "$state.reverted"
echo "restored the settings from before Pinstripe"
