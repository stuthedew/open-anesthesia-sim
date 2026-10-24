---
id: PL-7FPD
title: Since PL-CZXN no check measures whether a branch weakens a test of the apparatus or of app/'s Qt modules, or a simulator test on a branch that changes no function mutmut mutates: verify's mutation check mutates only core/ and four app/ modules, and the assertion check it replaced read every .py file
priority: P1
effort: L
status: ready
classes: safety
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, pyproject.toml, docs/mutation-testing.md
added: 2026-10-24
payoff: a branch that loosens a test of a displayed value, its unit or its label is refused before it merges, instead of passing with a note
verify: grep -q 'def test_a_branch_that_weakens_a_display_test_is_refused' tests/unit/test_diff_mutation.py && grep -qF 'src/anesthesia_sim/app/dashboard_frame.py' pyproject.toml
reenters: PL-CZXN
---

**Problem.** Since PL-CZXN no check measures whether a branch weakens a test of the apparatus or of app/'s Qt modules, or a simulator test on a branch that changes no function mutmut mutates: verify's mutation check mutates only core/ and four app/ modules, and the assertion check it replaced read every .py file

**Found 2026-10-24 while building `PL-CZXN`.** Of the 445 first-parent merges on `main` from 2026-10-01 to 2026-10-24, 40 changed a function in a module mutmut mutates, and 138 changed a test file that mentions `anesthesia_sim` without changing such a function, mostly Qt and layout work under `app/` and its integration tests. On those 138, and on every apparatus branch, the mutation check passes with nothing to run. It names each changed simulator test file in a note, so the gap is said on the page rather than hidden, but nothing refuses a weakened test there. The owner's ratified decision on `PL-CZXN`, on 2026-10-19, chose the mutation check. This cost was first written down when that item was built, in its brief's paragraph "What it does not cover", on 2026-10-24, so the case put to the owner did not carry it.

[superseded 2026-10-24: sized and narrowed to the display modules under "Recommended route, and its cost" below] One route, not yet sized: for a changed simulator unit test file, mutate the functions its base version reaches, and refuse a mutant the base's tests kill and the branch's tests do not. Where the source is unchanged, a mutant has the same name on both sides, so the comparison is exact. The cost is the run time, since one test can reach most of `core/`.

**Why it matters.** `CLAUDE.md`'s safety-critical standard treats presentation correctness as safety: the right number with the wrong unit or label is still a safety failure. A unit test of a displayed value, its unit or its label is what stops such a change from reaching a learner. Since `PL-CZXN`, a branch can loosen one and merge with only a note, unless the same branch also changes a function that mutmut mutates.

**Decision needed.** Should a check come back that catches a change weakening a test of what the interface displays: a value, its unit or its label?

- **Yes.** A branch that loosens such a test is refused before it merges, as a branch that leaves a changed display line untested already is. Branches that change those tests wait longer for `verify`.
- **No.** Those tests stay unmeasured. A loosened test reaches `main` with a note in `verify`'s output and nothing else.

**Recommended: yes.** `CLAUDE.md`'s safety-critical standard treats presentation correctness as safety, and nothing now measures these tests.

**Why it is the owner's call.** It reopens part of the owner's 2026-10-19 ratified decision on `PL-CZXN`, on a cost that case did not carry. `CLAUDE.md` says a ratified decision is reopened on ordinary evidence and put back to the owner.

**Decided 2026-10-24: yes.** Bring back a check that catches a change weakening a test of what the interface displays (project owner, 2026-10-24, ratified, over leaving the `app/` display tests unmeasured, as the 2026-10-19 PL-CZXN decision did). The coordinator relayed the answer to the triage session. The owner ratified the yes, not a mechanism, so the route below stays the recommended one rather than a decided one.

**Recommended route, and its cost.** Two parts, both in `tools/diff_mutation.py` and `pyproject.toml`. Neither needs a change to `verify.py`, because the verdict's `uncaught` list is already what `verify` refuses on.

1. **Mutate the display modules that the unit tests already reach.** Add to `[tool.mutmut] only_mutate` the `app/` modules that import no Qt and that unit tests import: at least `dashboard_frame.py`, `chart_frame.py` and `control_timeline.py`, which build the readouts, the chart labels and the control text. A branch that changes one of their functions then answers for its changed lines, as a branch changing `formatting.py` already does. The Qt widget modules, such as `simulation_view.py` and `run_view.py`, stay out. Their tests are integration tests, which the check does not run.
2. **Compare each changed test with its base version, over the display modules only.** For each simulator unit test file the branch changes, take the mutants of the `app/` modules in `only_mutate` that the base version of its changed test functions reaches. Run them against the base version and against the branch's versions of the changed files. A mutant that the base version kills and the branch's versions do not is a weakened test, and goes into `uncaught`. Where the source is unchanged, a mutant has the same name on both sides, so the comparison is exact. Treat the whole file as changed when a line outside any test function changes, such as a fixture or a helper. Where the base version fails on the branch's source with no mutant applied, report the file as not compared rather than refusing, because the branch changed what the test checks. Only `app/` mutants, because a display test's job is to catch a fault in the display code, and that choice is what keeps the run short. A test that reaches no display mutant costs only mutmut's coverage pass.

**Measured 2026-10-24, on four cores that other sessions shared.** The load average was 14 to 22, so each time is an upper bound. Each run selected only the named tests, and mutmut ran every mutant they reach.

- The whole of `tests/unit/test_formatting.py` reached 1,832 of 2,584 mutants and took 538 s.
- The two test functions that `#1572` changed in `tests/unit/test_dashboard_frame.py`, with `dashboard_frame.py` added to the scope, reached 1,837 of 3,320 mutants and took 968 s. Only 202 of those mutants were in `app/`. The rest were in `core/`, because the tests build a run.
- The same two tests, with mutmut asked for the `app/` mutants only, ran 202 mutants in 113 s.

So the route costs about two minutes for each version of a changed display test, or about four minutes per changed file. Comparing every mutant reached would cost 9 to 16 minutes per version. 138 of the 445 merges since 2026-10-01 changed a simulator test without changing a mutated function, so the comparison would start on about one merge in three. Only those that change a display test pay for its mutants. A weakened core test on such a branch stays unmeasured under this route, and is filed as `PL-H57W` with these numbers.

**Done when.** `docket verify` refuses a branch that changes a simulator unit test so that a mutant of a display module, which the test's base version kills, survives the branch's version. It passes a branch whose changed test still kills every such mutant. `tests/unit/test_diff_mutation.py` has a test of each, and the refusing one is `test_a_branch_that_weakens_a_display_test_is_refused`. `[tool.mutmut] only_mutate` names `dashboard_frame.py`, `chart_frame.py` and `control_timeline.py` beside the four `app/` modules it already names. `docs/mutation-testing.md` says what stays unmeasured: the Qt widget modules and the integration tests, core tests on a branch that changes no core function (`PL-H57W`), and the apparatus tests (`PL-LBNN`). A building session that finds a cheaper route to the same refusal may take it, and says so in the item.

**Generator check.** An instance of `PL-4W2L`'s fact, "whether a branch's diff weakens its tests", reached through `PL-CZXN`, which closed on 2026-10-24. `PL-CZXN`'s replacement check stopped covering three things the removed check covered: tests changed on a branch that changes no mutated function, tests of the `app/` modules mutmut does not mutate, and the apparatus tests. Recorded as `reenters: PL-CZXN`, since that fix should have covered this site. `PL-CZXN` itself re-enters `PL-4W2L`.
