#!/usr/bin/env bash
# =============================================================================
# start.sh — one-command launcher for GitHub Repo Analyzer
#
# What this does, in order:
#   1. Checks Docker is running (macOS: opens Docker Desktop if needed)
#   2. Starts the PostgreSQL container in the background
#   3. Waits until Postgres is actually ready to accept connections
#   4. Creates the Python virtual environment if it doesn't exist yet
#   5. Installs/updates pip packages from requirements.txt
#   6. Runs any pending Alembic database migrations
#   7. Starts the FastAPI server (uvicorn) in the foreground
#   8. On Ctrl+C: cleanly shuts down the server and stops the DB container
#
# Usage:
#   chmod +x start.sh   (only needed the first time — makes it executable)
#   ./start.sh
# =============================================================================

set -e  # exit immediately if any command fails — no silent errors

# -- Colour helpers so output is easy to read ----------------------------------
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()    { echo -e "${GREEN}[✔]${RESET} $1"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $1"; }
error()   { echo -e "${RED}[✘]${RESET} $1"; exit 1; }
section() { echo -e "\n${YELLOW}━━━ $1 ━━━${RESET}"; }

# -- Paths ---------------------------------------------------------------------
# Figure out where this script lives so paths work no matter where you run it from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

# =============================================================================
# STEP 1 — Make sure Docker is running
# =============================================================================
section "Checking Docker"

if ! command -v docker &>/dev/null; then
    error "Docker is not installed. Download it from https://www.docker.com/products/docker-desktop"
fi

# On macOS, Docker Desktop must be open for the daemon to run.
# `docker info` fails with a connection error if the daemon isn't up yet.
if ! docker info &>/dev/null; then
    warn "Docker daemon isn't running — attempting to start Docker Desktop..."
    open -a Docker  # macOS-specific: opens Docker Desktop app

    # Poll until Docker is ready (can take ~20 seconds on first launch)
    echo -n "    Waiting for Docker to start"
    for i in $(seq 1 30); do
        if docker info &>/dev/null; then
            echo ""  # newline after the dots
            break
        fi
        echo -n "."
        sleep 2
        if [ "$i" -eq 30 ]; then
            echo ""
            error "Docker didn't start in time. Please open Docker Desktop manually and re-run."
        fi
    done
fi

info "Docker is running"

# =============================================================================
# STEP 2 — Start the PostgreSQL container
# =============================================================================
section "Starting PostgreSQL (Docker)"

cd "$SCRIPT_DIR"  # docker-compose.yml lives at the project root

# -d = detached (runs in background so this script can keep going)
# --wait = waits until the container is healthy before returning (Docker Compose v2)
docker compose up -d --wait 2>/dev/null || docker compose up -d
# Note: older Docker Compose (v1) doesn't support --wait, so we fall back to plain -d
# and handle the readiness check ourselves in the next step.

info "PostgreSQL container started"

# =============================================================================
# STEP 3 — Wait until Postgres is actually accepting connections
# =============================================================================
section "Waiting for PostgreSQL to be ready"

# The container starting ≠ Postgres being ready to accept queries.
# pg_isready pings Postgres and exits 0 when it's ready.
echo -n "    Waiting"
for i in $(seq 1 20); do
    if docker compose exec -T db pg_isready -U postgres -q 2>/dev/null; then
        echo ""
        break
    fi
    echo -n "."
    sleep 1
    if [ "$i" -eq 20 ]; then
        echo ""
        error "PostgreSQL didn't become ready in time. Check: docker compose logs db"
    fi
done

info "PostgreSQL is ready"

# =============================================================================
# STEP 4 — Set up the Python virtual environment
# =============================================================================
section "Setting up Python environment"

cd "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
    warn "No venv found — creating one at backend/venv ..."
    python3 -m venv "$VENV_DIR"
    info "Virtual environment created"
else
    info "Virtual environment already exists"
fi

# Activate the venv — from here on, `python` and `pip` refer to the venv's versions.
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
info "Virtual environment activated (Python: $(python --version))"

# =============================================================================
# STEP 5 — Install / sync pip packages
# =============================================================================
section "Installing dependencies"

# --quiet suppresses the wall of text, but errors still show.
# We always run this — pip is smart enough to skip already-installed packages.
pip install -q -r requirements.txt
info "Dependencies up to date"

# =============================================================================
# STEP 6 — Run Alembic migrations
# =============================================================================
section "Running database migrations"

# `upgrade head` applies all migrations that haven't been applied yet.
# If the DB is already up to date, Alembic just says "nothing to do" and exits 0.
alembic upgrade head
info "Database schema is up to date"

# =============================================================================
# STEP 7 — Start the FastAPI server
# =============================================================================
section "Starting FastAPI server"

# Trap Ctrl+C (SIGINT) and SIGTERM so we can clean up gracefully.
# Without this, Ctrl+C would just kill the script and leave Docker running.
cleanup() {
    echo ""
    section "Shutting down"
    warn "Stopping FastAPI server..."
    # uvicorn is running in the foreground so killing the script kills it too.
    warn "Stopping PostgreSQL container..."
    cd "$SCRIPT_DIR" && docker compose stop
    info "All done. Goodbye!"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
info "Server starting at http://127.0.0.1:8000"
info "API docs at      http://127.0.0.1:8000/docs"
info "Press Ctrl+C to stop everything cleanly"
echo ""

# --reload = auto-restarts when you save a Python file (great for development)
# --app-dir = where to find the app package
# app.main:app = the FastAPI instance inside backend/app/main.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
