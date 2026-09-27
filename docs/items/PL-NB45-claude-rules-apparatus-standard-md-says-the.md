---
id: PL-NB45
title: .claude/rules/apparatus-standard.md says 'the fifteen apparatus tests under tests/unit/' where workflow_paths lists 35, and a count in a rule drifts at the rate tools/ grows
priority: P3
effort: S
status: ready
classes: docs
feature: worker-instructions
touches: .claude/rules/apparatus-standard.md
added: 2026-09-27
payoff: the sentence saying how far the apparatus test bar reaches stays true as apparatus tests are added
verify: grep -qF 'applies to the apparatus tests under' .claude/rules/apparatus-standard.md
---

**Problem.** .claude/rules/apparatus-standard.md says 'the fifteen apparatus tests under tests/unit/' where workflow_paths lists 35, and a count in a rule drifts at the rate tools/ grows

**Evidence, 2026-09-27.** `.claude/rules/apparatus-standard.md` § "What a test on this side is for":
"nothing stricter applies to the fifteen apparatus tests under `tests/unit/`".
`docket.toml`'s `workflow_paths` lists 35 such files, and
`tools/workflow_paths_check.py` counts the same 35 on the real tree. The
number was true when written and is wrong in the direction that undersells
the rule's reach.

**Re-confirmed on starting, 2026-09-27: the problem holds as filed.** The sentence
still says fifteen. `workflow_paths` lists 35 files under `tests/unit/`, all of
them test files present on disk, and the check's own rule - a test file is
apparatus when it does not import the product package - finds the same 35
among `tests/unit/test_*.py`. The count arrived with `PL-N6Y0` (#522) on
2026-09-13, when the list held exactly 15 there, so twenty apparatus tests have
been added in the fortnight since and nothing held the sentence to any of them.
The file's other claims about the tree still hold: `FlightReport.unreadable`,
`PullRequestHistory.declined`, `doc_check`'s `Report.declined`, and the rule it
quotes from `tools/workflow_paths_check.py`.

**Why it matters.** The sentence is the one that says how far the apparatus test
bar reaches, and it understates that by more than half. Kept as a number it
cannot stay true: it goes stale with every apparatus test added, and nothing
reports it when it does.

**Recommendation:** drop the number - "the apparatus tests under
`tests/unit/`" - rather than update it, since `workflow_paths` and the check
already say which files those are and a count here is a third copy that
drifts at the rate `tools/` grows. Found by `PL-12P8`'s docs sweep; not fixed
there because the file is outside that item's `touches`. It is also what
`PL-4FBP`'s rule for counts asks: a count no check holds is stated without the
number.

**Done when.** The sentence names the apparatus tests under `tests/unit/`
without a count, and leaves which files they are to `docket.toml`'s
`workflow_paths` and `tools/workflow_paths_check.py`, which the paragraph after
it already cites.

**Generator check.** A one-off, which the close-out docs sweep caught as
designed, the shape `PL-397Q` recorded: `PL-12P8`'s sweep found it. The fact
misread is the link between a document sentence and the tree fact it restates
(`PL-4FBP`, `PL-G424`, both closed 2026-09-19), and neither head's route claims
this kind. `PL-4FBP` leaves apparatus prose under `.claude/` unbound, its rule
for counts advice there, by decision; `PL-G424` leaves prose drift that is not a
citation to judgment and the capture rule. Not `PL-8ZGY`'s: no path sits on the
wrong side of the lane boundary here, and the sentence restates the list's size
rather than placing anything.
