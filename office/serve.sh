#!/usr/bin/env bash
# Open the desk board. Ctrl-C to stop.
cd "$(dirname "$0")" || exit 1
echo "Desk board → http://localhost:8787"
exec python3 -m http.server 8787
