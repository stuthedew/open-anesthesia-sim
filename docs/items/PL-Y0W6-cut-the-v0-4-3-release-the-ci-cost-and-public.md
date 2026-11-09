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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.3 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> `src/` is byte-identical to v0.4.2 and `docs/MODEL.md`'s only change is one cross-reference following the deleted README, so no equation, parameter, numerical method, unit or displayed value moved; the sixth such release and the third in a row. **The measured half.** The `checks` job ran 152 s, of which `bin/docket check --verify` was **87 s** — more than the whole 1 820-test suite — because the replay runs every open item's own `verify:` command and 79 of the 111 that carry one start a fresh `uv run pytest`. That bill grew with the size of the queue rather than with the size of the change, and was paid on every push to every open pull request. `--verify-base` now scopes it to the items a branch actually changed, read from the diff, with the whole-store sweep kept on `push` to the default branch where its answer is a fact about that branch — 102 commands in 74.6 s becomes one in 5.5 s, and the job **152 s → 59 s** on run 34000293113. It is `PL-P3B6`'s argument one step on: if a pre-commit gate cannot have changed whether some other item's work merged, neither can a pull request. A scoped run says what it was scoped to on `docket check`'s own cost line, including when the scope held nothing to run, because a narrowed run reporting no findings is otherwise indistinguishable from a store that holds none. Three smaller gate repairs sit around it: `drift.yml` had resolved a newer `pytest-xdist` every month and never run it — a declared dependency upgraded and untested, which is the hole that workflow exists to close — and now runs `-n auto --dist worksteal` on both suites; `tools/contrast_check.py` had been parsing 3.14 `app/` source under the 3.11 floor, green only because the two files it reads happen to carry no 3.12+ syntax, which since v0.4.2 folded that job into `checks` would have reddened the whole job before uv was installed; and the pull-request title check, the one gate no session could run before pushing, now discovers the title from the branch's own open pull request and skips silently on every way that lookup can fail, so `make check` stays green offline. **The published half** is smaller in the diff and larger in consequence. The repository is public — *to stop the Actions billing, not as a publication decision* — which makes the minute arithmetic three of these items were built on moot: standard runners are free and unlimited on public repositories, and what the work still buys is wall clock and the runner slots that throttle parallel sessions. `README.md` was deleted rather than corrected and stays deleted under a check; the human-facing pass `PL-XYRN` gated is deliberately unrun; and both are recorded where a later session would otherwise read a public repository with no front door as a gap rather than a decision. Which leaves the quietest thread: the concurrency comment claimed the repository was public and runners free while it was private, was corrected to private-and-billed, and was wrong again within hours — so its argument now rests on the runner slot, which holds under either answer, with the billing position dated and stated once rather than woven through the reasoning. Twelve items, one of which is the v0.4.2 cut itself.
