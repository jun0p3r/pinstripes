#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Install the Pinstripe Firefox chrome (firefox/chrome/userChrome.css) into a Firefox profile.
#
#   contrib/install-firefox.sh                 the default profile
#   contrib/install-firefox.sh /path/profile   a specific profile
#   contrib/install-firefox.sh --remove        put the previous userChrome.css back
#
# It turns on toolkit.legacyUserProfileCustomizations.stylesheets (through user.js), copies the
# stylesheet into <profile>/chrome/ and its images into <profile>/chrome/pinstripe/. An existing
# userChrome.css that isn't ours is kept as userChrome.css.pre-pinstripe. Restart Firefox after.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"

default_profile() {
    local base
    for base in "${XDG_CONFIG_HOME:-$HOME/.config}/mozilla/firefox" "$HOME/.mozilla/firefox"; do
        [[ -f "$base/installs.ini" ]] || continue
        local rel
        rel="$(sed -n 's/^Default=//p' "$base/installs.ini" | head -n 1)"
        [[ -n "$rel" && -d "$base/$rel" ]] && { echo "$base/$rel"; return; }
    done
    return 1
}

remove=false
if [[ "${1:-}" == "--remove" ]]; then remove=true; shift; fi
profile="${1:-$(default_profile)}" || { echo "no Firefox profile found; pass its path" >&2; exit 1; }
chrome="$profile/chrome"

if $remove; then
    if [[ -f "$chrome/userChrome.css.pre-pinstripe" ]]; then
        mv -f "$chrome/userChrome.css.pre-pinstripe" "$chrome/userChrome.css"
    elif grep -q "Pinstripe for Firefox" "$chrome/userChrome.css" 2>/dev/null; then
        rm -f "$chrome/userChrome.css"
    fi
    rm -rf "$chrome/pinstripe"
    echo "removed the Pinstripe Firefox chrome from $profile (restart Firefox)"
    exit 0
fi

mkdir -p "$chrome/pinstripe"
if [[ -f "$chrome/userChrome.css" ]] && ! grep -q "Pinstripe for Firefox" "$chrome/userChrome.css"; then
    cp -n "$chrome/userChrome.css" "$chrome/userChrome.css.pre-pinstripe"
fi
cp "$here/firefox/chrome/userChrome.css" "$chrome/userChrome.css"

assets="$here/gtk/Pinstripe/gtk-3.0/assets"
for a in tab tab-active tab-active-backdrop; do
    for part in s m e; do
        cp "$assets/$a-$part.png" "$chrome/pinstripe/"
    done
done
icons="$here/icons/Oxygen-Pinstripe"
for i in go-previous go-next view-refresh process-stop go-home; do
    cp -L "$icons/24x24/actions/$i.png" "$chrome/pinstripe/$i.png"
    cp -L "$icons/48x48/actions/$i.png" "$chrome/pinstripe/$i@2.png"
done

pref='user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
grep -qF "$pref" "$profile/user.js" 2>/dev/null || echo "$pref" >> "$profile/user.js"
echo "installed the Pinstripe Firefox chrome in $profile (restart Firefox)"
