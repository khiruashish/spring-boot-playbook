#!/usr/bin/env bash
# Runs all coding-interview tests and writes one report per test class to outputs/ (shown on the docs pages).
#   ./run-tests.sh          run tests, (re)write outputs/
#   ./run-tests.sh --check  what CI runs: fail if any test fails or a report differs from the committed one
set -euo pipefail
cd "$(dirname "$0")"
mvn -B -q test
python3 report.py "${1:-write}"
