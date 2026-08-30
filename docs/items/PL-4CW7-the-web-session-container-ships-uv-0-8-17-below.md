---
id: PL-4CW7
title: The web session container ships uv 0.8.17, below the project's required-version floor
status: untriaged
added: 2026-08-30
not-delegable: the fix is a setting in the Claude Code environment, outside this repository, so no command run inside a checkout can prove it
---

**Problem.** The Claude Code web environment's container image ships uv 0.8.17
(binary dated 2025-09-10). PL-F5HB added `required-version = ">=0.12.5"` to
`pyproject.toml`, so every `uv` command in a fresh web session now stops with:

    error: Required uv version `>=0.12.5` does not match the running version
    `0.8.17`. Update `uv` by running `uv self update`.

The remedy that message names does not work here either: `uv self update`
reads the GitHub releases API unauthenticated and fails with `GitHub API rate
limit exceeded`. What does work is `pip install --upgrade uv`, since PyPI is
reachable through the session proxy.

The floor is not the underlying problem, only what makes it visible. uv 0.8.17
predates every final 3.14 release, so it cannot fetch the pinned interpreter at
all; without the floor it would fail later and less clearly, with `No download
found for request: cpython-3.14.7-linux-x86_64-gnu`.

**Why it matters.** Every future web session pays a failed `make check`, a
diagnosis and an install before it can run the suite. `README.md` now names
both the error and the working command, which caps the cost, but the fix
belongs in the environment rather than in each session.

**Where.** Outside the repository: the setup script attached to the Claude
Code environment this project uses. `README.md`'s Requirements section is the
in-repo half and is already correct.

**Approach.** Add `pip install --upgrade uv` (or Astral's install script) to
the environment's setup commands so the container starts with a compliant uv,
then confirm a fresh session runs `make check` with no manual step. Nothing in
this repository can do it; the item exists so the finding is not lost.

**Done when.** A fresh web session runs `make check` successfully without
installing anything by hand.
