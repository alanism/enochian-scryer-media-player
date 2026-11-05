#!/usr/bin/env bash
set -euo pipefail
src="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
data_dir="${XDG_DATA_HOME:-$HOME/.local/share}"
dest="$data_dir/enochian-rqbit"
[[ -x "$src/bin/rqbit" && -f "$src/web/index.html" ]] || { echo 'Build the Enochian bundle first.' >&2; exit 1; }
mkdir -p "$dest/bin" "$dest/web" "$data_dir/applications"
install -m755 "$src/companion.py" "$dest/companion.py"
install -m755 "$src/bin/rqbit" "$dest/bin/rqbit"
cp -r "$src/web/." "$dest/web/"
install -m644 "$src/icon.png" "$dest/icon.png"
install -m644 "$src/ENGINE-LICENSE.txt" "$dest/ENGINE-LICENSE.txt"
python - "$dest" "$data_dir/applications/enochian-rqbit.desktop" <<'PY'
from pathlib import Path
import sys,re
root=Path(sys.argv[1]);exe=str(root/'companion.py').replace('%','%%')
if not re.fullmatch(r'[a-zA-Z0-9_./+-]+',exe):exe='"'+exe.replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('`','\\`')+'"'
Path(sys.argv[2]).write_text(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Enochian Rqbit
Comment=Torrent transfers with playback in Enochian VLC
Exec=/usr/bin/python3 {exe}
Icon={root}/icon.png
Terminal=false
Categories=Network;FileTransfer;P2P;
StartupWMClass=EnochianRqbit
Actions=Stop;

[Desktop Action Stop]
Name=Stop transfers and service
Exec=/usr/bin/python3 {exe} --stop
''')
PY
update-desktop-database "$data_dir/applications"
echo 'Installed Enochian Rqbit. Find it in the Omarchy launcher.'
