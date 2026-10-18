---
id: PL-M3YJ
title: Turn on mypy's warn_unused_configs so a dead [[tool.mypy.overrides]] is reported rather than sitting inert - PL-7SVX's flet_charts and msgpack entries are gone and only pyqtgraph's is live, so the cost of turning it on is zero today
priority: P3
effort: S
status: dropped
classes: infra
touches: pyproject.toml
added: 2026-09-16
closed: 2026-10-18
reason: Measured 2026-10-18 with mypy on this branch: the flag cannot do what the item wants and adds a note to every run. It reports a section whose module pattern matches nothing imported, not an ignore_missing_imports that has become unneeded, so pyqtgraph shipping stubs would still be silent. Its output is a note with exit 0, so it fails nothing. And the bare uv run mypy already notes three live patterns as unused: pyqtgraph.* (no submodule is imported) and xdist and xdist.* (only tests/ imports xdist, and that pass is tools/ignore_check.py). A note that fires on every run and changes no decision is the check CLAUDE.md retires.
verify: uv run mypy && grep -q '^warn_unused_configs = true$' pyproject.toml
---

**Problem.** Turn on mypy's warn_unused_configs so a dead [[tool.mypy.overrides]] is reported rather than sitting inert - PL-7SVX's flet_charts and msgpack entries are gone and only pyqtgraph's is live, so the cost of turning it on is zero today

**Why it matters.** A `[[tool.mypy.overrides]]` block is a *suppression*: it
tells the checker to stop reporting something for a named module. When the
module goes away the suppression does not - it sits in `pyproject.toml`
matching nothing, and mypy says nothing about it, because
`warn_unused_configs` is off by default. That is the false-green shape this
repository has already paid for twice (`PL-20PT`, and `PL-JRS3` for the same
reason in `tools/`): a guard that would pass on a tree it no longer describes.
The specific risk it leaves open is a suppression outliving its reason - the
`pyqtgraph` block exists because that package ships neither stubs nor
`py.typed`, and if it ever does, nothing reports that `strict` is still being
relaxed for it.

**Why the cost is zero today, which is what makes this worth doing now.**
`PL-7SVX`'s port removed the `flet_charts` and `msgpack` entries, so
`pyqtgraph` is the only override left and it is live. Turning the flag on
therefore adds no work and no output - it only starts reporting the *next*
dead entry. Turned on later, after another entry has gone stale, it is a
failing gate plus an archaeology question about why the entry was there.

**Done when.** `warn_unused_configs = true` is set under `[tool.mypy]` in
`pyproject.toml`, `make check` passes with it on, and the comment above the
`pyqtgraph` override says that the flag is what will report it once
`pyqtgraph` ships stubs - so the next reader knows the removal will be
announced rather than having to remember to look.
