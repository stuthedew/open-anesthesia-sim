---
id: PL-S2L4
title: bin/docket delegable offers items that docs/worker.md forbids a worker to touch
status: untriaged
added: 2026-08-30
---

**Problem.** Two lists say what a delegated worker may not edit, and they
disagree. `docket.toml`'s `protected_paths` names the scientific paths -
`src/anesthesia_sim/core`, `src/anesthesia_sim/data`, `docs/MODEL.md` - and is
what `Item.delegability` reads. `docs/worker.md` adds a second, wider rule the
worker is told to obey: "**Never edit the checks themselves**: `Makefile`,
`pyproject.toml`, `.github/workflows/`, `.claude/`, `docket.toml`."

Nothing reads the second list. So `bin/docket delegable` offered PL-F5HB (the
Python 3.14 release-candidate fix) as work for a cheaper model while that
item's `touches` named `pyproject.toml`, which `docs/worker.md` forbids the
same worker to open. The worker would have had to break its own instructions
or return the item unfinished.

**Why it matters.** `delegable` exists so a session can hand work off without
reading the queue. A list that includes work the worker is forbidden to do
makes the command untrustworthy in exactly the case it was built for, and the
contradiction surfaces only after a worker has been spawned and has read its
brief.

**Where.** `docket.toml` (`protected_paths`), `docs/worker.md` (the "Never
edit the checks themselves" bullet), and
`subprojects/docket/src/docket/model.py` (`Item.delegability`,
`_is_protected`).

**Approach.** One list has to become the other's source. The cheap version is
to add the check paths to `protected_paths`, which lets `delegability` decide
the whole rule and lets `docs/worker.md` cite the config rather than restate
it. Worth deciding as part of that: whether the wider list should block
delegation outright or only warn, since "may not edit the Makefile" is a
different kind of prohibition from "may not edit the physiology".

**Done when.** An item whose `touches` names a path `docs/worker.md` forbids
is not listed by `bin/docket delegable`, and the prohibition is stated in one
place rather than two.
