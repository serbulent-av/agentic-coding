# Delegation sandbox harness

Test harness that verifies the agentic-coding team (patek → philipe, etc.)
actually delegates work, in an isolated environment that cannot touch the real
`~/.pi/agent` config or session history. Two isolation variants are available:
a plain env-var sandbox and a Docker-containerized sandbox.

## Files

- [setup-sandbox.sh](setup-sandbox.sh) — builds `/tmp/pi-sandbox` (isolated pi
  config dir) and `/tmp/team-sandbox-proj` (scratch git repo). Required for
  both variants.
- [Dockerfile](Dockerfile) / [docker-build.sh](docker-build.sh) — image for the
  Docker variant (`pi-team-sandbox:latest`).
- [prompts.sh](prompts.sh) — shared dispatch/workflow prompts, sourced by both
  runners so they can never drift apart.
- [run-test.sh](run-test.sh) — run a delegation test with the env-var variant.
- [run-docker-test.sh](run-docker-test.sh) — run a delegation test inside
  Docker.
- [verify-delegation.py](verify-delegation.py) — checks the recorded session
  files for actual patek→philipe delegation (runs on the **host** for both
  variants).
- [activity-log.md](activity-log.md) — audit log of harness runs.

## Flow

```bash
./setup-sandbox.sh                 # once (re-run to reset the sandbox)
./docker-build.sh                  # Docker variant only; skipped automatically
                                   # by run-docker-test.sh if the image exists

# choose ONE runner — both cost real API calls, so only the dispatcher runs them
./run-test.sh dispatch|workflow
./run-docker-test.sh dispatch|workflow

# verify on the host against /tmp/pi-sandbox/sessions
python3 verify-delegation.py [--strict] [--no-bash] [--sessions-dir DIR]
```

Modes (prompts defined once in [prompts.sh](prompts.sh), sourced by both
runners so they stay byte-identical):

- `dispatch` — ask the agentic team directly; patek should delegate to philipe.
- `workflow` — run the saved `team-pipeline` workflow (requires
  `workflows/team-pipeline.js` to exist; setup-sandbox.sh copies it if present).

Both runners wipe `/tmp/pi-sandbox/sessions` and their previous log before
starting, so `verify-delegation.py` always inspects exactly one run.

Verification exit codes: `0` PASS, `1` FAIL (including no session files),
`2` usage error. `--strict` fails if patek edited files directly; `--no-bash`
fails if patek ran bash directly.

## Isolation mechanisms

**Env-var variant** ([run-test.sh](run-test.sh)): pi honors
`PI_CODING_AGENT_DIR`, which relocates the whole config (settings, agents,
workflows, sessions) to `/tmp/pi-sandbox`. No container — isolation rests on
that one variable plus a fresh, empty `sessions/` directory, so real session
history is never read or written.

**Docker variant** ([run-docker-test.sh](run-docker-test.sh)): same env var,
plus the pi process runs inside a container where the node runtime
(`~/.local/share/pi-node/current` → `/node`) and the pi install
(`~/.pi/agent/install` → `/pi-install`) are bind-mounted **read-only**. The
only writable paths inside the container are `/tmp/pi-sandbox` (mounted at
`/sandbox-agent`) and the scratch project `/tmp/team-sandbox-proj` (mounted at
its identical host path, so the absolute paths in the shared prompts in
[prompts.sh](prompts.sh) work unchanged in-container). The container bypasses
the host launcher and invokes the release
binary directly (`/pi-install/releases/<version>/node_modules/.bin/pi`, version
read from `install/current-version`, falling back to 1.6.0), with
`PI_MANAGED_INSTALL_ROOT=/pi-install` set for managed-install detection.
Sessions land in `/tmp/pi-sandbox/sessions` and are verified on the host.

## Secret hygiene

`setup-sandbox.sh` **copies** `auth.json` (and other config) into
`/tmp/pi-sandbox` — the sandbox needs it to authenticate. The Docker image
contains **no secrets**: only debian:12-slim plus git, python3, and
ca-certificates. Inside the container, host `~/.pi/agent` is entirely
unreachable; `auth.json` enters the container only via the `/tmp/pi-sandbox`
bind mount at runtime, never baked into the image.

## Cost note

`run-test.sh` and `run-docker-test.sh` make **real API calls** (a full pi
delegation run). They are invoked by the dispatcher as part of the delegation
test procedure, not by default in CI or setup.

## Known caveats

**Dangling symlinks in Docker.** `setup-sandbox.sh` symlinks large assets
(`skills`, `npm`, `bin`, `install`) into `/tmp/pi-sandbox` pointing at host
paths. Those symlinks dangle inside the container (host paths are unreachable
there). The core delegation run does not depend on them — the container uses
`/pi-install` directly and config is copied, not symlinked — but if a future
run needs in-container access to a symlinked asset, bind-mount its host target
at the same absolute path with `:ro`.

**Symlink write-through (accepted risk).** Those same symlinks point into the
REAL host directories, so in the env-var variant any write under
`/tmp/pi-sandbox/{skills,npm,bin,install}` hits the real `~/.pi/agent`. This
is an accepted risk: skills and other symlinked assets are treated as
read-only by the harness, and symlinks were chosen over copies to save space
and keep setup fast. The Docker variant cannot write through because the host
paths the symlinks point at are unreachable inside the container.
