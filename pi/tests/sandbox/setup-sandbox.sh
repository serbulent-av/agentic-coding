#!/usr/bin/env bash
#
# setup-sandbox.sh — build an isolated pi config sandbox for delegation tests.
#
# Mechanism:
#   pi honors the PI_CODING_AGENT_DIR environment variable, which overrides the
#   config directory (default ~/.pi/agent). Sessions, settings, agents, skills,
#   and workflows all resolve under that directory. By pointing it at
#   /tmp/pi-sandbox we get a fully isolated pi environment — no Docker needed —
#   that cannot read from or write to the real ~/.pi/agent (in particular, the
#   sandbox starts with an EMPTY sessions/ directory so real session history is
#   never touched).
#
# What this script builds:
#   /tmp/pi-sandbox/       isolated pi config dir (copied config + symlinked assets)
#   /tmp/team-sandbox-proj scratch git repo the agent team works in during tests
#
# Idempotent: the sandbox is destroyed and rebuilt on every run; the scratch
# project is (re)initialized only if it lacks a .git directory.
#
# SYMLINK WRITE-THROUGH (accepted risk): the sandbox symlinks skills/npm/bin/
# install into the REAL host directories, so in the env-var variant
# (run-test.sh) any write under those paths inside the sandbox hits the real
# ~/.pi/agent. Skills and other symlinked assets are treated as read-only by
# the harness; symlinks were chosen over copies to save space and keep setup
# fast. The Docker variant (run-docker-test.sh) cannot write through because
# the host paths the symlinks point at are unreachable inside the container.
#
# Runtime footprint: /tmp/pi-sandbox and /tmp/team-sandbox-proj only.

set -euo pipefail

REAL_AGENT_DIR="$HOME/.pi/agent"
SANDBOX_DIR="/tmp/pi-sandbox"
PROJECT_DIR="/tmp/team-sandbox-proj"

# --- Pre-check: required config files (hard requirements) -------------------
REQUIRED_CONFIG=(auth.json settings.json models-store.json subagents.json AGENTS.md)
for f in "${REQUIRED_CONFIG[@]}"; do
    if [ ! -f "$REAL_AGENT_DIR/$f" ]; then
        echo "error: required config $REAL_AGENT_DIR/$f missing" >&2
        exit 1
    fi
done
if [ ! -d "$REAL_AGENT_DIR/agents" ]; then
    echo "error: required config $REAL_AGENT_DIR/agents missing" >&2
    exit 1
fi

# --- Rebuild the sandbox from scratch ---------------------------------------
rm -rf "$SANDBOX_DIR"
mkdir -p "$SANDBOX_DIR"

# Config/state files the sandbox needs to authenticate and load agents
# (existence verified above).
for f in "${REQUIRED_CONFIG[@]}"; do
    cp -a "$REAL_AGENT_DIR/$f" "$SANDBOX_DIR/$f"
done

# Agent definitions (.md files) — the team under test.
cp -a "$REAL_AGENT_DIR/agents" "$SANDBOX_DIR/agents"

# Large/static assets are symlinked (not copied) to keep setup fast — see the
# SYMLINK WRITE-THROUGH note in the header. Missing ones are skipped silently
# so the script works on partial installs.
for d in skills npm bin install; do
    if [ -e "$REAL_AGENT_DIR/$d" ]; then
        ln -s "$REAL_AGENT_DIR/$d" "$SANDBOX_DIR/$d"
    fi
done

# Fresh empty sessions/ (never copy real sessions) and workflows/.
mkdir -p "$SANDBOX_DIR/sessions" "$SANDBOX_DIR/workflows"
if [ -d "$REAL_AGENT_DIR/workflows" ]; then
    # Tolerate absence and an empty dir (nullglob -> no match stays empty).
    shopt -s nullglob
    workflow_js=("$REAL_AGENT_DIR"/workflows/*.js)
    if [ ${#workflow_js[@]} -gt 0 ]; then
        cp -a "${workflow_js[@]}" "$SANDBOX_DIR/workflows/"
    fi
    shopt -u nullglob
fi

# --- Scratch git project the team will work in ------------------------------
# Probe for a working repo instead of testing for a .git directory: a missing
# dir makes git -C fail (so we init), a valid repo is skipped, and a worktree
# gitfile (.git FILE pointing elsewhere) also probes as a repo and is skipped
# rather than re-initialized.
if ! git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    mkdir -p "$PROJECT_DIR"
    git init -b master "$PROJECT_DIR"
    cat > "$PROJECT_DIR/README.md" <<'EOF'
# team-sandbox-proj

Scratch repository used by the agentic-coding delegation test harness.
Files created here are throwaway; the repo lives under /tmp.
EOF
    # -c flags set identity for this commit only; no global git config needed.
    git -C "$PROJECT_DIR" -c user.name="Sandbox Harness" \
        -c user.email="sandbox@localhost" \
        add README.md
    git -C "$PROJECT_DIR" -c user.name="Sandbox Harness" \
        -c user.email="sandbox@localhost" \
        commit -m "Initial scratch project for delegation tests"
fi

# --- Summary ----------------------------------------------------------------
# Capture HEAD first: under set -e a failure here aborts instead of being
# swallowed inside the echo's command substitution.
PROJECT_HEAD="$(git -C "$PROJECT_DIR" rev-parse --short HEAD)"

echo "Sandbox built:"
echo "  config dir : $SANDBOX_DIR (PI_CODING_AGENT_DIR target)"
echo "  sessions   : $SANDBOX_DIR/sessions (empty, isolated from real sessions)"
echo "  workflows  : $SANDBOX_DIR/workflows ($(ls "$SANDBOX_DIR/workflows" | wc -l) file(s))"
echo "  project    : $PROJECT_DIR ($PROJECT_HEAD)"
