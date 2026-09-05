---
id: PL-647D
title: Cut the v0.4.0 release: the teachable case
priority: P2
effort: S
status: done
classes: planning, docs
milestone: v0.4.1
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/, docs/items/
added: 2026-09-05
closed: 2026-09-05
pr: 355
not-delegable: proving a release cut means cutting the release. There is no
---

**Problem.** Thirty-six items have closed since v0.3.9 and twelve of v0.4.0's
thirteen Required-scope entries are done, but nothing has stamped them into a
release. Filed under CLAUDE.md's rule that housekeeping a session is about to
do itself is filed before it is done: a release cut carries no id until
somebody starts it, so every in-flight guard the project has reads it as
nobody's work, and two sessions cut v0.3.7 that way (`PL-66FP`).

**Why it matters.** The cut is what makes `docket wave` roll forward to
v0.4.1, what stamps `milestone: 0.4.0` onto the thirty-six items so the next
release's notes do not re-ship them, and what gives `docs/MODEL.md` and the
version table a baseline a reader can cite.

**Where.** `pyproject.toml`, `uv.lock`, `ROADMAP.md` (version-table row,
`current baseline` mark, baseline section, timeline row 3, and the
Required-scope entries recording their own outcomes), `docs/releases/0.4.0.md`.

**The one entry that does not land with it.** `PL-011` (bound the controller's
concentration history) is the thirteenth Required-scope entry and is at
`needs-decision`, in flight on `origin/claude/next-item-75htc6`. It is carried
to v0.4.1 rather than held against this cut: v0.4.0's Definition of done does
not name it, and the retention rule it is waiting on is entangled with whether
`RunHistory` survives at all. Its Required-scope bullet records that outcome
in place, the way the landed entries record theirs.

**Done when.** `pyproject.toml` reads 0.4.0, `uv.lock` agrees, the thirty-six
items carry `milestone: 0.4.0`, `docs/releases/0.4.0.md` exists, `ROADMAP.md`
carries the row, the moved baseline mark and the baseline prose, and
`make check` passes on the result.
