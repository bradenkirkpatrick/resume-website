#!/usr/bin/env bash
#
# stop-local.sh - Stop the local development environment.
#
# Closes ALL processes on ports 8000 (backend) and 5173 (frontend).
# Uses SIGTERM first, then SIGKILL if needed. Verifies ports are free.
#
# Usage:
#   ./scripts/stop-local.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

EXIT_CODE=0

echo ""
print_info "Stopping local development environment..."
echo ""

kill_port 8000 "Backend"  || EXIT_CODE=1
kill_port 5173 "Frontend" || EXIT_CODE=1

echo ""
if [[ "$EXIT_CODE" -eq 0 ]]; then
    print_info "All servers stopped — ports 8000 and 5173 are free."
else
    print_error "Failed to free one or more ports."
fi
exit "$EXIT_CODE"
