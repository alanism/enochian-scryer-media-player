#!/usr/bin/env bash
set -euo pipefail
src="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo="$(dirname -- "$src")"
cd "$repo"
npm ci --no-audit --no-fund
npm run build -w rqbit-webui
mkdir -p "$src/web" "$src/bin"
cp -r crates/librqbit/webui/dist/. "$src/web/"
# Build the engine from the checked-out source unless already supplied.
if [[ "${1:-}" == --source-engine ]]; then
  cargo build --release -p rqbit
  install -m755 target/release/rqbit "$src/bin/rqbit"
elif [[ ! -x "$src/bin/rqbit" ]]; then
  python3 "$src/fetch-engine.py"
fi
printf 'Bundle ready. Install with %s/install.sh\n' "$src"
