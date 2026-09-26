---
id: PL-QKXZ
title: The web container of 2026-09-25 again shipped uv 0.8.17 and no libegl1, so a session there has to repair both before make check will run; only the owner's environment setup script can fix it for every container
status: untriaged
added: 2026-09-26
---

**Problem.** The web container of 2026-09-25 again shipped uv 0.8.17 and no
libegl1, so a session there has to repair both before `make check` will run.
Only the owner's environment setup script can fix it for every container.

**Evidence.** On `claude/pl-batch-01-s8d258`, `uv --version` read 0.8.17
against `pyproject.toml`'s `required-version = ">=0.12.5"`, `uv self update`
failed on GitHub's API rate limit, and `make check` stopped with seven
collection errors, `ImportError: libEGL.so.1`. `PL-K6B2`'s pull request, `#1031`,
records the same `libegl1` install in another container of the same run.
Repaired here with `python3 -m pip install -U 'uv>=0.12.5'` (0.12.19, landing
at `/usr/local/bin/uv`, behind the stale `/root/.local/bin/uv` on `PATH`, so it
was linked over it) and `apt-get update && apt-get install -y libegl1`, after
which `make check` exited 0.

**What this changes.** `PL-SPZT` (the stale `uv`) was left open after it did
not reproduce on 2026-09-15, on the reasoning that one container meeting the
floor proves no pin; it has now reproduced. `PL-VHLZ` (nothing installs
`libegl1`) is done, with its environment half recorded as the owner's since no
file in the tree can prove it; this container did not have it. Whether the
setup script lacks the lines or they did not run is not visible from inside a
session.

**The owner's step.** In the project's environment settings, under Setup
script, two lines would cover both for every new container:

    apt-get update && apt-get install -y libegl1
    python3 -m pip install -U 'uv>=0.12.5' && ln -sf /usr/local/bin/uv /root/.local/bin/uv

**Done when.** A fresh web container runs `make check` with no repair step, or
the owner decides the repair stays each session's and `PL-SPZT`'s `docs/worker.md`
route is the whole answer.
