#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$root/vlc/install.sh"
"$root/rqbit/enochian/install.sh"
if [[ "${1:-}" == --make-default ]]; then
  xdg-mime default enochian-vlc.desktop video/mp4
  printf 'MP4 default: %s\n' "$(xdg-mime query default video/mp4)"
fi
