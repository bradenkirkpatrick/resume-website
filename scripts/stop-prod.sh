#!/usr/bin/env bash
#
# stop-prod.sh - Stop the production environment.
#
# Closes ALL processes on ports 8000 (backend) and 3000 (frontend static).
# Uses SIGTERM first, then SIGKILL if needed. Verifies ports are free.
#
# Usage:
#   ./scripts/stop-prod.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

EXIT_CODE=0

echo ""
print_info "Stopping production environment..."
echo ""

kill_port 8000 "Backend"  || EXIT_CODE=1
kill_port 3000 "Frontend" || EXIT_CODE=1

echo ""
if [[ "$EXIT_CODE" -eq 0 ]]; then
    print_info "All servers stopped — ports 8000 and 3000 are free."
else
    print_error "Failed to free one or more ports."
fi
exit "$EXIT_CODE"
