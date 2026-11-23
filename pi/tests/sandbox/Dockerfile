# Dockerfile — base image for the Docker-isolated delegation sandbox.
#
# This image is intentionally minimal: it provides only the OS-level tools pi
# and the agent team need at runtime (git, python3, TLS roots). The node
# runtime and the pi install are NOT baked in — they are bind-mounted
# read-only at container start (see run-docker-test.sh):
#
#   ~/.local/share/pi-node/current  ->  /node        (node/npm/npx/corepack)
#   ~/.pi/agent/install             ->  /pi-install  (pi releases)
#
# SECRET HYGIENE: this image contains NO secrets and no pi config. auth.json
# and the rest of the sandbox config enter the container only at runtime via
# the /tmp/pi-sandbox bind mount; nothing is COPYed or ADDed here.

FROM debian:12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        python3 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Node is mounted at /node at runtime; put it on PATH so `node`, `npm`, etc.
# resolve without absolute paths.
ENV PATH="/node/bin:${PATH}"

# Use CMD (not ENTRYPOINT) so ad-hoc smoke-test commands exec directly:
#   docker run --rm pi-team-sandbox:latest node --version   # runs node
# With no arguments the container drops into a bash shell; add -it for actual
# interactive use (without -t there is no TTY, without -i stdin is closed).
CMD ["/bin/bash"]
