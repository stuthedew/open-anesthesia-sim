---
id: PL-Y0W6
title: Cut the v0.4.3 release: the CI-cost and public-readiness batch
priority: P2
effort: S
status: done
classes: planning, docs
feature: planning-cadence
milestone: v0.4.4
added: 2026-09-06
closed: 2026-09-06
pr: 374
not-delegable: proving a release cut means cutting the release. No command can run beforehand - `make release` refuses while the previous version is untagged, and the version-table row, baseline mark and release prose it stops short of are judged by a reader rather than by a check
---

**Problem.** Cut the v0.4.3 release: the CI-cost and public-readiness batch

**Why it matters.**

**Where.**

**Done when.**

**Cut 2026-09-06.** `make release VERSION=0.4.3` bumped `pyproject.toml`
0.4.2 → 0.4.3, wrote `docs/releases/v0.4.3.md`, stamped `milestone: v0.4.3`
onto twelve items and relocked `uv.lock`. The three `ROADMAP.md` edits it named
were made by hand: the version-table row, the `current baseline` mark moved off
v0.4.2, and the baseline section rewritten. A release-narrative section was
added too, which the command does not ask for and the convention expects
(`PL-K2YF` records the one release that missed it).

**The claim that no shipped code moved was checked rather than asserted.**
`git diff v0.4.2..HEAD -- src/` is empty. `docs/MODEL.md` is *not* byte-identical
this time - one cross-reference changed, because its wash-in caveats said they
belonged "including in `README.md`" and that file no longer exists - so the
baseline section says so rather than repeating the usual sentence. Every moved
file under `tests/` is an apparatus suite.

**What the release is.** Twelve items on two threads. The measured one:
`bin/docket check --verify` was 87 s of the `checks` job's 152 s, and scoping
it to what a branch changed took the job to 59 s. The published one: the
repository went public to stop Actions billing, which makes the minute
arithmetic three of those items were built on moot and leaves the wall clock as
what they bought.

**One thing to know before the next cut.** The version-table row must be
inserted with no blank line between it and the row above, or markdown ends the
table and `doc_check`'s current-baseline check reports "0 rows are marked
current baseline". That happened here and was caught by `make check` before the
commit, which is the check doing its job - but the failure names the marker
rather than the blank line, so it reads as a missing mark rather than an
orphaned row.
