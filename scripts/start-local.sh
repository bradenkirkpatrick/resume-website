#!/usr/bin/env bash
#
# start-local.sh - Start the local development environment with port safety.
#
# Features:
#   - Kills any leftover processes on ports 8000/5173 before starting
#   - Waits for the port to be confirmed free before launching
#   - Prompts to restart if servers are running (unless -f is passed)
#   - Monitors processes and restarts them if they die unexpectedly
#
# Usage:
#   ./scripts/start-local.sh       # Start or prompt to restart
#   ./scripts/start-local.sh -f    # Force restart without prompting
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/lib.sh"

# Check for force flag in any position (handles npm run start-local -- -f)
FORCE_RESTART=false
for arg in "$@"; do
    if [[ "$arg" == "-f" || "$arg" == "--force" ]]; then
        FORCE_RESTART=true
        break
    fi
done

# ── Dependency check ──────────────────────────────────────────────────────────

if [[ ! -d "$PROJECT_DIR/backend/venv" ]]; then
    print_info "Backend virtual environment not found. Setting up..."
    cd "$PROJECT_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    print_info "Backend dependencies installed."
fi

if [[ ! -d "$PROJECT_DIR/frontend/node_modules" ]]; then
    print_info "Frontend dependencies not found. Installing..."
    cd "$PROJECT_DIR/frontend"
    npm install --silent
    print_info "Frontend dependencies installed."
fi

# ── Port safety: always kill anything on our ports first ──────────────────────

BACKEND_PORT=8000
FRONTEND_PORT=5173

# Check if anything is already running
if is_port_open "$BACKEND_PORT" || is_port_open "$FRONTEND_PORT"; then
    if [[ "$FORCE_RESTART" == "true" ]]; then
        print_warn "Force restart requested — freeing ports..."
        kill_port "$BACKEND_PORT"  "Backend"  || true
        kill_port "$FRONTEND_PORT" "Frontend" || true
    else
        echo ""
        print_warn "Servers are already running on:"
        is_port_open "$BACKEND_PORT"  && echo "  - Backend  (port $BACKEND_PORT)"
        is_port_open "$FRONTEND_PORT" && echo "  - Frontend (port $FRONTEND_PORT)"
        echo ""
        read -r -p "Do you want to restart the servers? (y/N): " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_info "Restarting — freeing ports..."
            kill_port "$BACKEND_PORT"  "Backend"  || true
            kill_port "$FRONTEND_PORT" "Frontend" || true
        else
            print_info "Keeping existing servers running."
            exit 0
        fi
    fi
fi

# Double-check both ports are actually free
if is_port_open "$BACKEND_PORT"; then
    print_error "Port $BACKEND_PORT is still in use. Aborting."
    exit 1
fi
if is_port_open "$FRONTEND_PORT"; then
    print_error "Port $FRONTEND_PORT is still in use. Aborting."
    exit 1
fi

# ── Start backend ─────────────────────────────────────────────────────────────

print_info "Starting backend server on port $BACKEND_PORT..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
print_info "Backend started (PID: $BACKEND_PID)"

print_info "Waiting for backend to be ready..."
if wait_for_port "$BACKEND_PORT" "Backend"; then
    print_info "Backend is ready! → http://localhost:$BACKEND_PORT"
else
    print_error "Backend failed to start within timeout."
    kill_port "$BACKEND_PORT" "Backend" || true
    exit 1
fi

# ── Start frontend ────────────────────────────────────────────────────────────

print_info "Starting frontend server on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/frontend"
npx vite --host 0.0.0.0 --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
print_info "Frontend started (PID: $FRONTEND_PID)"

if wait_for_port "$FRONTEND_PORT" "Frontend"; then
    print_info "Frontend is ready! → http://localhost:$FRONTEND_PORT"
else
    print_error "Frontend failed to start within timeout."
    kill "$FRONTEND_PID" 2>/dev/null || true
    exit 1
fi

echo ""
print_info "=============================================="
print_info "  Local development environment is running!"
print_info "  Frontend: http://localhost:$FRONTEND_PORT"
print_info "  Backend:  http://localhost:$BACKEND_PORT"
print_info "  API Docs: http://localhost:$BACKEND_PORT/docs"
print_info "=============================================="
echo ""

# ── Watchdog: restart processes if they die ───────────────────────────────────
# Runs in the background. If a process dies, it kills the other and starts both.

watchdog_pid=$$
(
    while true; do
        sleep 3
        BACKEND_ALIVE=false
        FRONTEND_ALIVE=false

        if is_port_open "$BACKEND_PORT"; then
            BACKEND_ALIVE=true
        fi
        if is_port_open "$FRONTEND_PORT"; then
            FRONTEND_ALIVE=true
        fi

        if $BACKEND_ALIVE && $FRONTEND_ALIVE; then
            continue
        fi

        # One or both died — restart everything
        print_warn "Process died! Restarting both servers..."
        kill_port "$BACKEND_PORT"  "Backend"  || true
        kill_port "$FRONTEND_PORT" "Frontend" || true

        # Restart backend
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &
        if wait_for_port "$BACKEND_PORT" "Backend"; then
            print_info "Backend restarted."
        else
            print_error "Backend restart failed."
        fi

        # Restart frontend
        cd "$PROJECT_DIR/frontend"
        npx vite --host 0.0.0.0 --port "$FRONTEND_PORT" &
        if wait_for_port "$FRONTEND_PORT" "Frontend"; then
            print_info "Frontend restarted."
        else
            print_error "Frontend restart failed."
        fi
    done
) &

print_info "Watchdog enabled — processes will auto-restart if they crash."
print_info "Use 'npm run stop-local' to stop all servers."
