---
name: docker
description: Reviews Docker configuration (Dockerfile, docker-compose) for correctness, security, and image efficiency. Activates when explicitly asked to review Docker/container setup, or after hand-editing the generated Dockerfile — not run automatically on every edit.
applies_to: backend
---

This is an on-demand deep review of Docker configuration you've hand-edited after VibeCraft generated the initial Dockerfile — see `.github/instructions/*.instructions.md` for this project's general rules (Docker specifics aren't covered there).

**Dockerfile Best Practices**
- Use official, versioned base images — never `latest` (unpredictable, breaks reproducibility)
- Multi-stage builds: compile/build in a full image, copy artifacts to a minimal runtime image
- `.dockerignore` excludes: `node_modules`, `.git`, `*.log`, local `.env` files, IDE configs
- `COPY` before `RUN` only what is needed for that layer (preserves cache for dependency install)
- `RUN` commands chained with `&&` and cleaned up in the same layer
- `WORKDIR` set explicitly; never rely on the default `/`

**Security**
- Final image runs as a non-root user
- No secrets (`ENV SECRET_KEY=...`) in the Dockerfile — use runtime env or a secrets manager
- Minimal base image: `alpine`, `distroless`, or a `slim` variant
- No `--privileged` flag in production; avoid mounting the Docker socket
- Read-only root filesystem where possible (`--read-only`)

**Docker Compose**
- Service dependencies declared with `depends_on` + `condition: service_healthy`
- Health checks defined for each stateful service (DB, cache, broker)
- Named volumes for persistent data; never anonymous volumes in production compose
- Environment variables from a `.env` file (never hardcoded in `docker-compose.yml`)
- `restart: unless-stopped` for production; `restart: "no"` for dev

**Layer Optimization**
- Dependency installation layer separate from source code layer (cache-friendly):
  - Node.js: `COPY package*.json ./ && RUN pnpm install` → then `COPY . .`
  - Python: `COPY requirements.txt ./ && RUN pip install` → then `COPY . .`
- Final image should contain only runtime artifacts, not build tools

**Image Size**
- Check image size with `docker image inspect`; flag images >500MB for optimization
- Remove build dependencies in multi-stage; avoid installing debug tools in the production image

Produce: a list of Dockerfile issues with a corrected snippet for each, and a Docker Compose review if one exists.
