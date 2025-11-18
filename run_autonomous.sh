#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 rick_cli.py --mode autonomous || python3 rick_cli.py
