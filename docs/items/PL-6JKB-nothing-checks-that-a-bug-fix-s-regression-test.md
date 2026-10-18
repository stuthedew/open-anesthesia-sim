---
id: PL-6JKB
title: Nothing checks that a bug fix's regression test fails before the fix: a replay of 58 recent simulator bug-fix commits found every test reproduces its bug, but 16 of them (28%) cannot even be collected against the pre-fix code, so that protection rests on reasoning rather than on a run recorded when the fix merged
priority: P3
effort: S
status: done
classes: docs
feature: test-effectiveness-measurement
milestone: v0.5.26
touches: .claude/rules/test-oracles.md
added: 2026-10-17
closed: 2026-10-17
pr: 1497
payoff: a bug fix's regression test is shown to fail before the fix by a run recorded in its item, not by reasoning
verify: grep -q 'Run a regression test against the code before the fix' .claude/rules/test-oracles.md
---

**Problem.** Nothing checks that a bug fix's regression test fails before the fix: a replay of 58 recent simulator bug-fix commits found every test reproduces its bug, but 16 of them (28%) cannot even be collected against the pre-fix code, so that protection rests on reasoning rather than on a run recorded when the fix merged

**Severity: low today.** The replay found no regression test that fails to
catch its bug. The weakness is that nothing checked this when each fix
merged. Audit: regression-test replay, checked independently by an
adversarial second agent.

**Evidence.** The replay took the 69 commits from `721d2088` (2026-09-17) to
`16769c8d` that added or changed at least one test touching
`src/anesthesia_sim/core`, `data` or `app`. For each commit it put `src/` back
at the parent, deleted any `src/` file the commit added, cleared
`__pycache__`, and ran each added or changed test with
`uv run --frozen pytest -q -p no:cacheprovider -n 0`. Then it restored the fix
and ran the same tests again. 58 of the 69 commits were simulator bug fixes or
mixed commits.

- **40 reproduce directly.** At least one added test fails on the parent with
  an assertion about the defect, and all pass at the fix.
- **16 cannot run on the parent.** Each test file imports, or each test calls,
  an API the fix introduced. One new name in a test module's import block
  makes every test in that file impossible to collect on the parent.
  Variants that drop the new API were built for 7 of these 16, and for 5
  defects inside commits that otherwise reproduce: 12 variants in all. Every
  one fails before the fix with the item's own symptom, and the 9 that could
  run after the fix pass. The verifier then built variants for the 9 verdicts
  that had been judged only by reading, and every one reproduced too.
- 1 reproduces partly (`b684c5c9`, a provenance feature), and 1 has no
  behaviour to reproduce (`c1e73ec8`, `PL-59WB`, a parameter rename).

Several variants reproduce the item's own measurement exactly: `PL-NJPB`'s 126
of 801 dial positions unrecovered; `PL-SM5V`'s 1.9, 3.8, 3.9 and 7.6-7.9 L/min;
`PL-2MD9`'s constant row 0.9999999981; `PL-BBMG`'s 20% sevoflurane accepted
against an 8% maximum; and `PL-HSFV`'s 1000 L/min cardiac output accepted.

Two weaknesses:

- **The fail-before run happens nowhere.** For 16 of 58 bug-fix commits (28%)
  the committed test cannot even be collected against the parent, so its
  protection rests on reasoning, or on this one-off replay.
- **Two regression tests failed at their own fix commit** in the audit's
  container, because they depended on the host's fonts:
  `test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it` (`c128173a`,
  `PL-FPY2`) and
  `test_a_legend_checkbox_draws_its_indicator_in_the_theme[drawn,hidden]`
  (`c05fd0b3`, `PL-7W9N`). Both failures were in preconditions rather than in
  the defect assertion. `db092d80` (`PL-VCF0`, `PL-K9Z5`, 2026-10-11) repaired
  both, and both pass on `main`. Until then, whether these tests failed
  before and passed after depended on which fonts the host had.

**Established practice.** Defects4J admits a bug only with "a triggering test
... that failed before the fix and passes after the fix" (Just, Jalali and
Ernst, ISSTA 2014, doi:10.1145/2610384.2628055). SWE-bench requires at least
one fail-to-pass test per task (Jimenez et al., ICLR 2024, arXiv:2310.06770).
Both are rules for curating benchmarks. The audit found no controlled study of
the practice in day-to-day development.

**Why it matters.** A regression test that was never seen failing may not
test the bug at all. The replay shows that this suite's tests do, but only
because someone ran a one-off audit, and 28% of them cannot show it without a
hand-built variant.

**Proposal.** When a bug fix is made, record its fail-before run in the item:
the command run against the parent and the failing assertion's message. Where
the test needs the fix's new API, record a variant that does not. This can be
prose in the item, needing no new mechanism.

**Decision.** The project owner approved recording the fail-before run
(project owner, 2026-10-17, ratified, over leaving that protection to one-off
replays). It is prose in the item, with no new check or field. The capture
said a check would fall under `CLAUDE.md`'s pause on new workflow mechanisms.
That was wrong, because no workflow-lane head carried `generator: live` that
day (`PL-3KMD`).

**Generator check.** Not a member of any head: it records a practice the
suite lacked, and no other item misreads the same fact.

**Where.** `docs/items/` holds the record. `.claude/rules/test-oracles.md`
states the practice, and loads when a session reads the simulator's tests.

**Done when.** The project owner has decided whether a bug fix's fail-before
run is recorded, and if so where.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above.
