---
id: PL-SPZT
title: The web container's uv is 0.8.17 against pyproject's required-version >= 0.12.5, and both uv self update and the standalone installer are blocked from it, so a session that wants the quality suite has to find the pip route itself
status: untriaged
added: 2026-09-14
---

**Problem.** The web container's uv is 0.8.17 against pyproject's required-version >= 0.12.5, and both uv self update and the standalone installer are blocked from it, so a session that wants the quality suite has to find the pip route itself

**Why it matters.** Every `uv run` and `make check` refuses with "Required uv
version `>=0.12.5` does not match the running version `0.8.17`" until the
session works out an install route, and the two obvious ones fail in this
container: `uv self update` dies on GitHub's unauthenticated API rate limit
and `curl https://astral.sh/uv/install.sh` gets a 403 from the egress proxy.
What worked on 2026-09-14 (`PL-GS3R`'s session): `python3 -m pip install -U
'uv>=0.12.5'`, which lands `/usr/local/bin/uv` *behind* the stale
`/root/.local/bin/uv` on `PATH`, so the old binary has to be moved aside or
the new one linked over it before `make check` sees it. That is paid again by
every session in a fresh container, which is every web session.

**Where.** The session-start hook under `.claude/hooks/`, or `docs/worker.md`;
`PL-VHLZ` (nothing installs `libegl1`) is the same shape of finding for a
different dependency.

**Done when.** A fresh web session can run `make check` without first
repairing `uv`, or `docs/worker.md` states the pip route and the `PATH` fix in
two lines.
