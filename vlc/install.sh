#!/usr/bin/env bash
# Install only this bundle and a distinct desktop entry; keep stock VLC untouched.
set -euo pipefail
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
data_dir="${XDG_DATA_HOME:-$HOME/.local/share}"
dest="$data_dir/enochian-vlc"
if ! command -v vlc >/dev/null; then
  printf '%s\n' 'Install the Omarchy dependencies first:' '  sudo pacman -S vlc vlc-gui-skins2 vlc-plugin-ffmpeg vlc-plugin-freetype xorg-xwayland python-gobject gtk3 nodejs' >&2
  exit 1
fi
for required in python3 node; do
  if ! command -v "$required" >/dev/null; then
    printf 'Missing runtime: %s. Install the documented Omarchy dependencies.\n' "$required" >&2
    exit 1
  fi
done
if ! python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk' 2>/dev/null; then
  printf '%s\n' 'Subtitle prompts require python-gobject and gtk3.' >&2; exit 1
fi
if [[ ! -f "$source_dir/subtitle-client/node_modules/opensubs-cli/dist/Run.js" ]]; then
  printf '%s\n' 'Use the complete Linux release ZIP, or run npm ci --prefix vlc/subtitle-client from source.' >&2; exit 1
fi
if [[ "$source_dir" != "$dest" ]]; then
  mkdir -p "$dest/skins"
  install -m755 "$source_dir/enochian-vlc" "$dest/enochian-vlc"
  install -m644 "$source_dir/window_skin.py" "$dest/window_skin.py"
  install -m644 "$source_dir/player_window.py" "$source_dir/subtitles.py" "$dest/"
  cp -r "$source_dir/http" "$dest/"
  cp -r "$source_dir/subtitle-client" "$dest/"
  install -m644 "$source_dir/enochian-vlc.png" "$dest/enochian-vlc.png"
  install -m644 "$source_dir"/skins/*.vlt "$dest/skins/"
fi
mkdir -p "$data_dir/applications"
# Desktop Exec uses its own quoting rules; escape reserved characters without eval.
python - "$dest/enochian-vlc" "$data_dir/applications/enochian-vlc.desktop" <<'PY'
import pathlib,re,sys
exe=sys.argv[1].replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')
# xdg-open's generic desktop parser treats quotes literally. Leave simple paths
# unquoted for Omarchy, while retaining desktop-spec quoting for other paths.
exe=exe if re.fullmatch(r'[a-zA-Z0-9_./+-]+',exe) else '"'+exe+'"'
pathlib.Path(sys.argv[2]).write_text('[Desktop Entry]\nVersion=1.0\nType=Application\nName=Enochian VLC\nComment=VLC with Enochian Elements controls\nExec='+exe+' %U\nIcon='+str(pathlib.Path(sys.argv[1]).with_name('enochian-vlc.png'))+'\nTerminal=false\nCategories=AudioVideo;Player;\nStartupWMClass=Vlc\nMimeType=video/mp4;video/x-matroska;video/webm;audio/mpeg;audio/flac;audio/ogg;\nActions=Ivory;Obsidian;\n\n[Desktop Action Ivory]\nName=Ivory finish\nExec='+exe+' --ivory\n\n[Desktop Action Obsidian]\nName=Obsidian finish\nExec='+exe+' --obsidian\n')
PY
if command -v update-desktop-database >/dev/null; then update-desktop-database "$data_dir/applications"; fi
printf 'Installed Enochian VLC. Find it in the Omarchy launcher.\nLaunch directly: %q\n' "$dest/enochian-vlc"
