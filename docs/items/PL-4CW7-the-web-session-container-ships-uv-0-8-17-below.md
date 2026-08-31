---
id: PL-4CW7
title: The web session container ships uv 0.8.17, below the project's required-version floor
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
added: 2026-08-30
touches: docs/items/PL-4CW7-the-web-session-container-ships-uv-0-8-17-below.md
not-delegable: the fix is a setting in the Claude Code environment, outside this repository, so no command run inside a checkout can prove it
pr: 105
closed: 2026-08-31
---

**Problem.** The Claude Code web environment's container image ships uv 0.8.17
(binary dated 2025-09-10). PL-F5HB added `required-version = ">=0.12.5"` to
`pyproject.toml`, so every `uv` command in a fresh web session now stops with:

    error: Required uv version `>=0.12.5` does not match the running version
    `0.8.17`. Update `uv` by running `uv self update`.

The remedy that message names does not work here either: `uv self update`
reads the GitHub releases API unauthenticated and fails with `GitHub API rate
limit exceeded`. What does work is `python3 -m pip install --user --upgrade
uv`, verified in this container: PyPI is reachable through the session proxy,
and `--user` writes the console script to `/root/.local/bin/uv`, which is both
where the stale binary lives and first on `PATH`.

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

**Approach.** Put `python3 -m pip install --user --upgrade uv` in the
environment's Setup script field so the container starts with a compliant uv,
then confirm a fresh session runs `make check` with no manual step. Astral's
install script is the alternative, but it downloads from GitHub releases,
which is what rate-limits `uv self update` here. Nothing in this repository
can make the change; the item exists so the finding is not lost.

**State, 2026-08-30.** The project owner added that line to the environment's
setup script the same day the item was filed, so the fix is applied and only
the confirmation is outstanding. Editing the setup script invalidates the
environment's filesystem snapshot, so the script re-runs on the next session
started in it - which makes the *next fresh session* the test. Nothing needs
scheduling: that session's first `uv` command either reports 0.12.5 or newer
with nothing installed by hand, or it does not. The session that observes it
closes this item.

This item is not part of the v0.2.8 debt gate. It was captured after the gate
list was frozen and describes a problem that did not exist until PL-F5HB
landed the `required-version` floor, so it belongs to the next gate rather
than extending this one.

**Observed 2026-08-31, and the answer is no.** A fresh web session (the one
that did PL-020, the type-check gate) ran `uv --version` before installing
anything and got **0.8.17** - the stale binary at `/root/.local/bin/uv`,
unchanged. `make check` stopped on the `required-version` error at its first
command. `uv self update` still fails on the GitHub rate limit, exactly as
recorded above. That session finished by fetching the wheel from PyPI and
putting its `uv` on `PATH` by hand, so the work landed, but the environment
had not been fixed.

So the setup-script line either was not saved, or the environment the web
sessions actually start in is not the one it was saved to, or the snapshot it
was meant to invalidate did not re-run the script. The item stays open, and
the next fresh session is the next test.

Note `pip download uv` succeeds in this container, so PyPI reachability is
not the failure; only the setup script's effect is.

**Re-saved 2026-08-31** by the project owner, in response to the observation
above. So the test is again the next fresh web session, and again nothing
needs scheduling: its first `uv` command either reports 0.12.5 or newer with
nothing installed by hand, or it does not. A second consecutive 0.8.17 would
mean the environment being edited is not the one these sessions start in,
which is a different problem from the one this item was filed for and should
be recorded as such rather than folded in here.

**Observed 2026-08-31, second reading, and the answer is yes.** A fresh web
session - this one, started after the re-save above - ran `uv --version` as
its first command, before installing anything, and got **uv 0.12.7**
(x86_64-unknown-linux-gnu). The binary at `/root/.local/bin/uv` is dated
2026-08-31 03:06, the minute the container started, where the stale 0.8.17
was dated 2025-09-10: the setup script ran and replaced it. `make check` then
ran through to the end green - ruff, mypy, 690 tests, `docket check` and
`doc_check` - with no manual step and no `required-version` error.

So the re-save took, and the environment being edited is the one these
sessions start in. The failure recorded above was a save that did not stick,
not a wrong environment.

**Done when.** A fresh web session reports uv 0.12.5 or newer from
`uv --version` before anything has been installed by hand, and runs
`make check` through to the end.
