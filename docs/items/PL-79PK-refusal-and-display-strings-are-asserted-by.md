---
id: PL-79PK
title: Refusal and display strings are asserted by unanchored substring or not at all, so 174 of the 279 unit-tier mutant survivors change only message text, and format_case_discard_warning's singular rule survives the whole suite because '1 recorded control change' is a substring of '1 recorded control changes'
priority: P2
effort: M
status: ready
classes: test
feature: tests-detect-wrong-values
touches: tests/unit
added: 2026-10-17
payoff: a refusal or warning a learner reads is asserted as a whole string, so a wrong plural or a changed sentence fails a test instead of passing as a substring
verify: grep -q 'def test_the_case_discard_warning_is_pinned_whole' tests/unit/test_formatting.py
---

**Problem.** Refusal and display strings are asserted by unanchored substring or not at all, so 174 of the 279 unit-tier mutant survivors change only message text, and format_case_discard_warning's singular rule survives the whole suite because '1 recorded control change' is a substring of '1 recorded control changes'

**Severity: low for most cases; one reaches a learner.** Audit: survivor
triage of the 279 unit-tier mutation survivors, plus a whole-suite run of the
display-string mutant.

**Evidence.** The triage sorted the 279 survivors into 174 that change only
message text, 38 equivalent, 13 unreachable and 54 real gaps. The
message-only mutants survive because refusals are asserted by unanchored
substring, or not at all. By area:

- Matrix exponential and alveoli: `match="interval_s"` in
  `test_matrix_exponential.py`, `match="gas_volume_l"` in `test_alveolar.py`
  and `match="not a state vector"` in `test_resume_at.py` are unanchored. No
  test asserts `multiply`'s left-operand shape message, `propagate`'s shape
  message or the finiteness message on the propagator output. One anchored
  full-message literal per refusal would kill 9 of these 17 survivors.
- Compartments: `match="volume_l"` (which `re.search` also matches inside
  'XXvolume_lXX'), `match="smallest supported step"`,
  `'"Supported simulation step" in str(...)'`, `match="no simulation_step_s"`,
  and a `^`-anchored regex in `test_patient.py` with no `$`. These account for
  44 of the 52 message-only survivors in that group.
- Circuit and uptake system: many guards are tested with `pytest.raises(Error)`
  and no match (range ends, circuit volume, `set_agent_amount`,
  `advance_fresh_gas`). Others match only a parameter name or a phrase
  ('minimum above its maximum', 'initial_agent_l', 'delivered_agent_l',
  'vaporizer maximum'). The concentration-confusion messages are anchored at
  the start only, so their warning about a hundredfold error is never checked.
- Shared guards: where a guard is called, its `name` argument is never checked
  (21 of 40 survivors), although `core/validation.py`'s docstring says the
  name is the only thing that tells a reader which value was refused
  (`PL-SPN6`). The run-length refusal is checked with
  `f'{86400:g} s' in message`, which the limit clause already satisfies, so
  the time-reached number the test's docstring says it covers is never
  checked. `tests/integration/test_controller.py` compares
  `supported_limit_reason` with `_the_reason_the_refused_step_would_give()`,
  which calls the same `require_supported_run_length`, so it is no check
  either.
- Data and timeline: 27 survivors change only message text (schema window,
  nonnegative validator, short citation, `authority_for`, display-state and
  anchored refusals).
- Presentation: display strings are checked by substring, and axis labels are
  compared after `float()` parsing, which erases the rule under test.
  `mac_axis_ticks`' rule of "no decimal on whole-MAC steps" is therefore
  unchecked.

The display-string case reaches a learner. Mutant
`format_case_discard_warning__mutmut_2` changes `if control_change_count == 1`
to `if (control_change_count == 1) and False`. It survived the whole simulator
suite at `25ef454b` (5734 passed, 575 s). The parametrized test asserts
`expected in warning`, and '1 recorded control change' is a substring of '1
recorded control changes', which is the exact defect the test's docstring says
it guards against. `test_simulation_view.py` and `test_dashboard_frame.py`
compare against `format_case_discard_warning` itself, so they cannot catch it
either. Mutants 4, 10 and 11 of the same function also survive. The new-case
confirmation dialog would read "1 recorded control changes".

Some guard messages have been fixed since the mutation run at `b9b3c812`.
`PL-19Y0` moved the agent-simulation validator's checks into `__setattr__`,
and its test now pins `f'^{total} must be nonnegative and finite$'`. A re-run
should drop those survivors.

**Why it matters.** `.claude/rules/sources-and-docstrings.md` says "A refusal
names what was refused", and banners show refusals word for word. The suite
does not enforce that rule. And because 174 of 279 survivors are message
noise, every future mutation run buries its few real gaps among them.

**Where.** The unit test files named above; `src/anesthesia_sim/app/formatting.py`
(`format_case_discard_warning`) and its test in `tests/unit/test_formatting.py`.

**Recommended fix.** Use anchored full-string assertions (`match="^...$"`, or
`str(raised.value) == "..."`) on at least one refusal per call site, and
whole-string equality for display strings. The first test to write, checked
against the current output:
`assert format_case_discard_warning("Sevoflurane", 60.0, 1) == "The current sevoflurane case — 1m of simulated time, 1 recorded control change — will be discarded along with its chart history. This cannot be undone."`.
It also kills mutants 4, 10 and 11. Before pinning a guard's message, fix the
owner prefix where it is missing (`PL-2TZT`: five guard names are passed
without the object's name). Otherwise pinning today's text would freeze one
bare "volume_l must be positive and finite" shared by three tissue groups and
the venous pool.

**Done when.** `format_case_discard_warning__mutmut_2` fails a test, and every
refusal message a banner can show is asserted by an anchored full string.

**Related.** `PL-2TZT` (ready; owner prefixes on guard names) comes first for
the messages it touches. `PL-Y1PS` records the mutation recipe a re-run would
use.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
