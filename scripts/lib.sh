#!/usr/bin/env bash
#
# lib.sh - Shared functions for resume-website scripts.
#
# Sourced by start-local.sh, stop-local.sh, start-prod.sh, stop-prod.sh.
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
print_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_cmd()   { echo -e "${CYAN}[CMD]${NC}   $1"; }

# ── Port helpers ──────────────────────────────────────────────────────────────

# Return all PIDs listening on a given port (one per line)
pids_on_port() {
    local port=$1
    if command -v lsof &>/dev/null; then
        lsof -ti :"$port" -P -n 2>/dev/null || true
    elif command -v ss &>/dev/null; then
        ss -tlnp "sport = :$port" 2>/dev/null \
            | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' || true
    fi
}

# Return 0 (true) if anything is listening on the port, 1 (false) otherwise
is_port_open() {
    local port=$1
    if command -v lsof &>/dev/null; then
        lsof -i :"$port" -P -n 2>/dev/null | grep -q LISTEN
    elif command -v ss &>/dev/null; then
        ss -tlnp "sport = :$port" 2>/dev/null | grep -q LISTEN
    else
        return 1
    fi
}

# Kill EVERY process on a port — SIGTERM, then SIGKILL if needed.
# Returns 0 if the port is free afterwards, 1 if something still holds it.
kill_port() {
    local port=$1
    local label=$2
    local pids
    pids=$(pids_on_port "$port")

    if [[ -z "$pids" ]]; then
        print_info "Port $port ($label) is already free."
        return 0
    fi

    print_warn "Port $port ($label) is held by PID(s): $(echo "$pids" | tr '\n' ' ')"

    # Send SIGTERM
    for pid in $pids; do
        print_cmd "kill $pid ($label)"
        kill "$pid" 2>/dev/null || true
    done

    # Wait up to 5 s for graceful shutdown, polling every 0.5 s
    local waited=0
    while [[ $waited -lt 10 ]]; do
        pids=$(pids_on_port "$port")
        if [[ -z "$pids" ]]; then
            print_info "Port $port ($label) freed gracefully."
            return 0
        fi
        sleep 0.5
        waited=$((waited + 1))
    done

    # SIGKILL remaining
    print_warn "Force killing remaining processes on port $port..."
    for pid in $pids; do
        print_cmd "kill -9 $pid ($label)"
        kill -9 "$pid" 2>/dev/null || true
    done

    sleep 1

    pids=$(pids_on_port "$port")
    if [[ -n "$pids" ]]; then
        print_error "Port $port ($label) could NOT be freed (stuck PIDs: $(echo "$pids" | tr '\n' ' '))."
        return 1
    fi

    print_info "Port $port ($label) freed after force kill."
    return 0
}

# Block until a port is listening (up to ~15 s). Returns 0 on success.
wait_for_port() {
    local port=$1
    local label=$2
    local i
    for i in $(seq 1 30); do
        if is_port_open "$port"; then
            return 0
        fi
        sleep 0.5
    done
    return 1
}
