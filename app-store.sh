#!/bin/bash
# pi-app-store: 1
set -eu
cd -- "$(dirname -- "$0")"
case "${1:-}" in
  install) python3 -m py_compile tallyturnstone.py ;;
  run) exec python3 tallyturnstone.py ;;
  *) echo "Use: bash app-store.sh install OR bash app-store.sh run"; exit 1 ;;
esac
