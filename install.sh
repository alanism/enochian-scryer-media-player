#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$root/vlc/install.sh"
"$root/rqbit/enochian/install.sh"
if [[ "${1:-}" == --make-default ]]; then
  mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}"
  xdg-mime default enochian-vlc.desktop video/mp4
  if [[ "$(xdg-mime query default video/mp4)" != enochian-vlc.desktop ]]; then
    printf '%s\n' 'The MP4 association could not be verified. Choose Enochian VLC in your file manager.' >&2
    exit 1
  fi
  printf 'MP4 default: %s\n' "$(xdg-mime query default video/mp4)"
fi
