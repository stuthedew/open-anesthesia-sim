---
paths:
  - "/tests/unit/**"
  - "/tests/integration/**"
  - "/tests/reference/**"
---

# Where a simulator test's expected value comes from

A test catches a wrong clinical value only when its expected value was worked
out some other way than by running the code under test. Coverage does not show
whether that is so, and neither does a mutation score. An audit of this suite
on 2026-10-17 found four safety gaps that the whole suite passed over. In each
one, no test compared the value with an independently found expected value, or
the test case was too small to tell correct code from wrong code. The project
owner adopted the practice below on that audit's recommendation (project owner,
2026-10-17, ratified, over leaving it as advice in one reply, `PL-3KMD`). The
gaps themselves are the items of the `tests-detect-wrong-values` feature.

It applies when you write or change a test of a value that a learner could
see: a concentration, a MAC fraction, a band, a time, a label or a message. A
test that imports `anesthesia_sim` is the simulator's, which is the rule
`tools/workflow_paths_check.py` applies. A tooling test is held to
`.claude/rules/apparatus-standard.md` instead.

1. **Take the expected value from a source independent of the code under
   test.** Any of these will do: a literal transcribed from a paper, with its
   table or page in a comment; a closed-form solution; a calculation the test
   does itself; or a fresh run built directly with the settings the test is
   about. Never read the expected value from the snapshot, state or object
   that the test exercises. Both MAC-awake band tests took their expected
   band from the snapshot under test, so a band left at the previous agent's
   values after a switch passes them (`PL-JPS2`).
2. **Check a control that changes a run's state against a fresh run.** An
   agent switch, a reset or a branch is meant to produce a particular state.
   Build that state directly, without the control, and compare the two. A
   switch to desflurane that kept sevoflurane's compartments passed every
   test, while showing an alveolar fraction of 2.95% at 5 minutes instead of
   3.59% (`PL-QJXS`).
3. **Check a stored clinical value against its source, not only against
   itself.** A literal pin copied from the data file catches a later change to
   the value. It does not catch a value that was wrong when it was stored. So
   each stored clinical value also needs one test whose expected literal was
   transcribed from the adopted source, with the source's table or page beside
   it. A 10% error in sevoflurane's MAC-awake fraction passes all 1,654
   data-dependent unit and integration tests (`PL-H1JH`).
4. **Say how large an error a published-data comparison can detect.** Where a
   test claims to validate the model against published data, its docstring
   states the size of error it would catch. The Yasuda comparison passes with
   the fat tissue:gas coefficient doubled or halved, so passing it does not
   show that the fat compartment is right (`PL-9YHR`).
5. **Test a rule about a collection with at least three entries.** With two
   entries, many wrong slices give the same list as the right one:
   `segments[:-1]` and `segments[:1]` are equal. Every test of
   `RunDefinition.record_change`'s dial-moved-back branch used two stretches,
   so a mutant that deletes every later stretch passes all 5,734 simulator
   tests (`PL-ZH1F`).
6. **Run a regression test against the code before the fix.** It must fail
   there. Record the command and the failing assertion's message in the
   item. Where the test needs an interface that the fix added, record a
   variant that does not need it. A replay on 2026-10-17 found that 16 of 58
   recent regression tests could not even be collected against the code
   before their fix (`PL-6JKB`).

A high mutation score does not replace any of this. mutmut never changes the
data files or module-level constants, and a mutant cannot show whether an
expected value is right. `PL-Y1PS` holds the mutation recipe and its baseline.
