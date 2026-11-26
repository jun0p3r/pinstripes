#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Switch a Plasma 6 session to Pinstripe: colour scheme, Plasma style, icon theme, widget
# style, GTK theme, Luxi Sans and (if installed) the Oxygen Traffic Lights decoration.
# The previous values are saved first; contrib/revert-pinstripe.sh puts them back.
#
#   contrib/apply-pinstripe.sh [--graphite] [--no-font] [--mac-buttons]
set -euo pipefail

variant=Pinstripe
font=1
mac_buttons=0
for arg in "$@"; do
    case "$arg" in
        --graphite) variant=PinstripeGraphite ;;
        --no-font) font=0 ;;
        --mac-buttons) mac_buttons=1 ;;
        -h|--help) sed -n '3,9p' "$0"; exit 0 ;;
        *) echo "unknown option: $arg" >&2; exit 2 ;;
    esac
done

state_dir="${XDG_DATA_HOME:-$HOME/.local/share}/pinstripe-style"
state="$state_dir/previous-settings"
mkdir -p "$state_dir"

rd() { kreadconfig6 --file "$1" --group "$2" --key "$3"; }
wr() { kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; }

if [[ ! -f "$state" ]]; then
    {
        echo "colorscheme=$(rd kdeglobals General ColorScheme)"
        echo "desktoptheme=$(rd plasmarc Theme name)"
        echo "icons=$(rd kdeglobals Icons Theme)"
        echo "widgetstyle=$(rd kdeglobals KDE widgetStyle)"
        echo "buttonicons=$(rd kdeglobals KDE ShowIconsOnPushButtons)"
        echo "font=$(rd kdeglobals General font)"
        echo "menufont=$(rd kdeglobals General menuFont)"
        echo "toolbarfont=$(rd kdeglobals General toolBarFont)"
        echo "smallfont=$(rd kdeglobals General smallestReadableFont)"
        echo "wmfont=$(rd kdeglobals WM activeFont)"
        echo "deco_library=$(rd kwinrc org.kde.kdecoration2 library)"
        echo "deco_theme=$(rd kwinrc org.kde.kdecoration2 theme)"
        echo "buttons_left=$(rd kwinrc org.kde.kdecoration2 ButtonsOnLeft)"
        echo "buttons_right=$(rd kwinrc org.kde.kdecoration2 ButtonsOnRight)"
        echo "gtktheme=$(busctl --user call org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig gtkTheme 2>/dev/null | sed -E 's/^s "(.*)"$/\1/')"
    } > "$state"
    echo "saved previous settings to $state"
else
    echo "keeping earlier saved settings in $state"
fi

echo "colour scheme: $variant"
plasma-apply-colorscheme "$variant" >/dev/null

echo "Plasma style: pinstripe"
plasma-apply-desktoptheme pinstripe >/dev/null

if [[ ! -f "${XDG_DATA_HOME:-$HOME/.local/share}/icons/KrystalSVG/index.theme" ]]; then
    echo "icons: KrystalSVG (Crystal) missing; Oxygen Pinstripe falls back to Oxygen until you run" >&2
    echo "       contrib/install-krystalsvg.sh" >&2
fi
echo "icons: Oxygen-Pinstripe"
/usr/libexec/plasma-changeicons Oxygen-Pinstripe >/dev/null 2>&1 || wr kdeglobals Icons Theme Oxygen-Pinstripe

style="Pinstripe"
[[ "$variant" == PinstripeGraphite ]] && style="Pinstripe Graphite"
if python3 -c 'import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
a = QApplication(["x", "-platform", "offscreen"])
sys.exit(0 if "Pinstripe" in QStyleFactory.keys() else 1)' 2>/dev/null; then
    echo "widget style: $style"
    wr kdeglobals KDE widgetStyle "$style"
    # Aqua push buttons carry text only, never icons
    wr kdeglobals KDE ShowIconsOnPushButtons false
else
    echo "widget style: Pinstripe plugin not found by Qt; install it system-wide (see README), then rerun" >&2
fi

echo "GTK theme: Pinstripe"
busctl --user call org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig setGtkTheme s Pinstripe >/dev/null 2>&1 || true
gsettings set org.gnome.desktop.interface gtk-theme Pinstripe 2>/dev/null || true
gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:" 2>/dev/null || true
# libadwaita apps ignore GTK themes but still load the user stylesheet; import Pinstripe there
# (after KDE's colours, which kde-gtk-config keeps at the top of the file)
gtk4css="${XDG_CONFIG_HOME:-$HOME/.config}/gtk-4.0/gtk.css"
pinstripe_gtk4="${XDG_DATA_HOME:-$HOME/.local/share}/themes/Pinstripe/gtk-4.0/gtk.css"
if [[ -f "$pinstripe_gtk4" ]] && ! grep -q 'Pinstripe/gtk-4.0/gtk.css' "$gtk4css" 2>/dev/null; then
    mkdir -p "$(dirname "$gtk4css")"
    [[ -s "$gtk4css" && -n "$(tail -c1 "$gtk4css")" ]] && echo >> "$gtk4css"
    printf "@import url('file://%s'); /* pinstripe: libadwaita */\n" "$pinstripe_gtk4" >> "$gtk4css"
    echo "libadwaita: Pinstripe imported in $gtk4css"
fi

if [[ $font == 1 ]]; then
    if [[ -n "$(fc-list "Luxi Sans")" ]]; then
        echo "font: Luxi Sans"
        wr kdeglobals General font "Luxi Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        wr kdeglobals General menuFont "Luxi Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        wr kdeglobals General toolBarFont "Luxi Sans,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        wr kdeglobals General smallestReadableFont "Luxi Sans,8,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        wr kdeglobals WM activeFont "Luxi Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
        gsettings set org.gnome.desktop.interface font-name "Luxi Sans 10" 2>/dev/null || true
    else
        echo "font: Luxi Sans not installed, skipped (see README)" >&2
    fi
fi

if kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key library | grep -q oxygentrafficlights \
   || ls /usr/lib64/qt6/plugins/org.kde.kdecoration3/org.kde.oxygentrafficlights.so >/dev/null 2>&1; then
    echo "window decoration: Oxygen Traffic Lights"
    wr kwinrc org.kde.kdecoration2 library org.kde.oxygentrafficlights
    wr kwinrc org.kde.kdecoration2 theme "Oxygen Traffic Lights"
    if [[ $mac_buttons == 1 ]]; then
        wr kwinrc org.kde.kdecoration2 ButtonsOnLeft XIA
        wr kwinrc org.kde.kdecoration2 ButtonsOnRight ""
    fi
fi

# tell running apps and KWin
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:2 int32:0 || true  # style
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:1 int32:0 || true  # fonts
dbus-send --session --type=method_call --dest=org.kde.KWin /KWin org.kde.KWin.reconfigure || true
echo "done. Some apps pick up the widget style and font only after a restart."
