---
id: PL-WHG6
title: "Cut v0.4.18: the release where the project checked what it tells the next session"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.19
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 529
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.18"' pyproject.toml && test -f docs/releases/v0.4.18.md
---

**Problem.** Seventeen items finished since v0.4.17 and none had shipped, so
`bin/docket next` and the session-start digest asked every session to offer a
release before taking new work.

**Why it matters.** Filed before the cut rather than after it, per `CLAUDE.md`'s
rule that repository work taking a commit of its own is filed first: every
in-flight guard this project has matches a `PL-` id, and a release cut has none
until somebody starts one. `PL-66FP` is what the unfiled version cost - two
sessions cut v0.3.7 within the hour and the second was discarded at the merge.
The live session list was checked before starting and no other session was
cutting.

**Done when.** `pyproject.toml` is at 0.4.18, `docs/releases/v0.4.18.md` exists,
`ROADMAP.md` carries the version-table row, the moved `current baseline` mark
and the baseline section, and `make check` passes.

**What the release turned out to be about.** Twelve of the seventeen entries are
a statement this repository makes about itself - to a session or to a reader -
that was wrong, missing or unreachable, and none of the twelve was a wrong
calculation. `ROADMAP.md`'s baseline section carries the account.

**The "nothing moved" claim is a measurement here rather than a byte
comparison**, because `PL-9SH6`'s accessor rename reaches `core/` and the
reference suite and so rules byte-identity out. Measured instead, across
`v0.4.17..HEAD`: `src/anesthesia_sim/data/` and `.github/` byte-identical;
`core/` carrying the same 401 numeric literals as a multiset, so the rename
moved no number; and no numeric literal removed from `tests/reference/` (1,405
to 1,445, every addition new), so every pinned published and canonical value
still stands.
