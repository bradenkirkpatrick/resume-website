#!/usr/bin/env bash
#
# start-prod.sh - Start the production environment with port safety.
#
# Features:
#   - Kills any leftover processes on ports 8000/3000 before starting
#   - Waits for the port to be confirmed free before launching
#   - Prompts to restart if servers are running (unless -f is passed)
#   - Monitors processes and restarts them if they die unexpectedly
#
# Usage:
#   ./scripts/start-prod.sh       # Start or prompt to restart
#   ./scripts/start-prod.sh -f    # Force restart without prompting
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/lib.sh"

# Check for force flag in any position (handles npm run start-prod -- -f)
FORCE_RESTART=false
for arg in "$@"; do
    if [[ "$arg" == "-f" || "$arg" == "--force" ]]; then
        FORCE_RESTART=true
        break
    fi
done

BACKEND_PORT=8000
FRONTEND_PORT=3000

# ── Environment ────────────────────────────────────────────────────────────────

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    print_warn "No .env file found. Creating from example..."
    if [[ -f "$PROJECT_DIR/.env.example" ]]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        print_info "Created .env from .env.example. Please update the values."
    fi
fi

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Ensure frontend is built
if [[ ! -d "$PROJECT_DIR/frontend/dist" ]]; then
    print_info "Building frontend for production..."
    cd "$PROJECT_DIR/frontend"
    npm install --silent
    npx vite build
    print_info "Frontend built successfully."
fi

# ── Port safety ────────────────────────────────────────────────────────────────

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

if is_port_open "$BACKEND_PORT"; then
    print_error "Port $BACKEND_PORT is still in use. Aborting."
    exit 1
fi
if is_port_open "$FRONTEND_PORT"; then
    print_error "Port $FRONTEND_PORT is still in use. Aborting."
    exit 1
fi

# ── Start backend (production mode) ────────────────────────────────────────────

print_info "Starting backend server (production mode) on port $BACKEND_PORT..."
cd "$PROJECT_DIR/backend"
if [[ ! -d venv ]]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --workers 4 &
BACKEND_PID=$!
print_info "Backend started (PID: $BACKEND_PID)"

if wait_for_port "$BACKEND_PORT" "Backend"; then
    print_info "Backend is ready! → http://localhost:$BACKEND_PORT"
else
    print_error "Backend failed to start within timeout."
    kill_port "$BACKEND_PORT" "Backend" || true
    exit 1
fi

# ── Start frontend static server ───────────────────────────────────────────────

print_info "Starting frontend static server on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/frontend"
npx serve dist -l "$FRONTEND_PORT" --no-clipboard &
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
print_info "  Production environment is running!"
print_info "  Frontend: http://localhost:$FRONTEND_PORT"
print_info "  Backend:  http://localhost:$BACKEND_PORT"
print_info "  API Docs: http://localhost:$BACKEND_PORT/docs"
print_info "=============================================="
echo ""

# ── Watchdog ───────────────────────────────────────────────────────────────────

(
    while true; do
        sleep 5
        BACKEND_ALIVE=true
        FRONTEND_ALIVE=true

        is_port_open "$BACKEND_PORT"  || BACKEND_ALIVE=false
        is_port_open "$FRONTEND_PORT" || FRONTEND_ALIVE=false

        if $BACKEND_ALIVE && $FRONTEND_ALIVE; then
            continue
        fi

        print_warn "Process died! Restarting both servers..."
        kill_port "$BACKEND_PORT"  "Backend"  || true
        kill_port "$FRONTEND_PORT" "Frontend" || true

        # Restart backend
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate 2>/dev/null || true
        uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --workers 4 &
        wait_for_port "$BACKEND_PORT" "Backend" && print_info "Backend restarted." || print_error "Backend restart failed."

        # Restart frontend
        cd "$PROJECT_DIR/frontend"
        npx serve dist -l "$FRONTEND_PORT" --no-clipboard &
        wait_for_port "$FRONTEND_PORT" "Frontend" && print_info "Frontend restarted." || print_error "Frontend restart failed."
    done
) &

print_info "Watchdog enabled — processes will auto-restart if they crash."
print_info "Use 'npm run stop-prod' to stop all servers."
