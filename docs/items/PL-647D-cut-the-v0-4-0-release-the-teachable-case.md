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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.0 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> A case runs at 1, 5, 20, 60 or 300x in steps that never change size, on a time base spanning fifteen minutes to twelve hours that defaults to fitting the run, against a vertical axis fixed at 0-3 x MAC for every agent rather than at one agent's vaporizer dial maximum - so the three obstacles this milestone was scoped on are answered together: the reservoirs that cause context-sensitive emergence (muscle at 135 min, fat at 42 h for sevoflurane) become reachable in minutes of wall clock, a 1 MAC run fills the plot instead of its bottom quarter, and three agents whose MACs differ threefold are finally comparable. Changing agent is now an explicit new case that names what will be lost before discarding it. Underneath, the recorded run is keyed by substance and quantity rather than by six flat compartment floats, so nitrous oxide will add a substance rather than reshape the record v0.5.0's forking proof is written against. Interface work on an untouched model: `src/anesthesia_sim/core/` and `src/anesthesia_sim/data/` are byte-identical to v0.3.9 and every changed source file is under `app/`, so no equation, parameter, numerical method or solver step moved, and the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference tests are unchanged and passing. Twelve of the milestone's thirteen Required-scope entries have landed; `PL-011`'s retention rule is the thirteenth and was dropped on 2026-09-05, superseded by the score architecture rather than deferred, with the outcome recorded in place in that section. The remaining twenty-one items of the thirty-six are apparatus: the release script's own in-flight guard after two sessions cut v0.3.7 independently, the resident-instruction budget, and eleven live defects in the queue's ranking and its checks.
