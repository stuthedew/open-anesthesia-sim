---
id: PL-T5J5
title: Eight tests hold the 24 h supported run length as literal text instead of reading MAXIMUM_ELAPSED_SIMULATION_TIME_S, so a deliberate change to the limit fails them where the application is right
priority: P2
effort: S
status: ready
classes: test
feature: numerical-domain
touches: tests/unit/test_supported_ranges.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py
added: 2026-10-03
payoff: a deliberate change to the supported run length fails only the one test written to pin it, so a real regression in the limit's text is not edited away with eight spurious failures
verify: ! grep -qE 'VALUE == "23h59m59|widest == "23h59m59|"24 h" in|"86400 s" in|length of 24 hours|== 864_000|\) == "24 ?h(ours)?"' tests/unit/test_supported_ranges.py tests/unit/test_dashboard_frame.py tests/unit/test_formatting.py && grep -q 'MAXIMUM_ELAPSED_SIMULATION_TIME_S == 86_400.0' tests/unit/test_supported_ranges.py
---

**Problem.** Eight tests hold the 24 h supported run length as literal text instead of reading MAXIMUM_ELAPSED_SIMULATION_TIME_S, so a deliberate change to the limit fails them where the application is right

**Asked for by the project owner, 2026-10-03,** in the thread that merged #1292
(`PL-73ZN`, `PL-BMY5`): "shouldn't they ensure the text matches the actual set
limit? Not a hard coded 24hr? What's the point of having a variable when it
expects a hard coded value in the tests?"

**Measured the same day.** With `MAXIMUM_ELAPSED_SIMULATION_TIME_S` set to
172 800.0 (48 h) and the whole suite run, 9 of 3 670 tests fail. Every failure
is a test expecting the 24-hour text where the application printed the 48-hour
value; the application itself reads the constant everywhere. Eight are copies
of the value:

- `test_supported_ranges.py`: `test_the_shipped_step_reaches_the_boundary_exactly`
  (`== 864_000`) and `test_the_run_length_refusal_says_what_was_reached_and_why`
  (`"86400 s"`, `"24 h"`).
- `test_dashboard_frame.py`: `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`
  and `test_the_supported_run_length_notice_does_not_describe_a_failure` (the
  banner's "24 hours"), and `test_the_widest_readout_strings_are_the_formatters_own_extremes`
  (`"23h59m59.9s"`).
- `test_formatting.py`: `test_the_supported_run_length_is_stated_from_the_model_s_own_constant`,
  `test_the_clock_reads_the_supported_limit_the_way_the_limit_is_stated` and
  `test_the_widest_reachable_clock_string_is_what_the_reserved_width_assumes`.

The ninth, `test_the_supported_run_length_is_twenty_four_hours`, is a pin by
design: its docstring says it exists so a silent edit to the constant fails
rather than ships, and it fails on a deliberate edit for the same reason.

**Why it matters.** A deliberate change to the limit should fail exactly the
tests that state the limit as a fact, so the person making it reads each one.
Eight spurious failures teach the opposite: update every expectation that
mentions 24 h until the suite goes green, which is the moment a real
regression in the banner or the refusal text gets edited away with them.

**Not copies, and staying as they are.** Fixtures that pass a sample reason
string such as "this run has reached 86400 s of simulated time" through the
controller and the dashboard (nothing reads the number in them); formatter
cases with a literal input, such as `format_elapsed(86_399.9)`, which hold for
any limit; and the reference tests whose comparison window is the published
mean curves' first 24 hours, a scientific window rather than a copy of the
limit.

**Candidate fix.** Derive each of the eight expectations from the constant, or
from `format_supported_run_length()` where the test checks a sentence that
embeds it. The two width tests cannot simply derive their literal, because
`WIDEST_READOUT_VALUE` is itself computed from the constant, so the derived
assertion would restate the code: replace the pinned string with the premise
it stood for, that no reachable instant formats wider than the last tenth
before the limit. Keep the ninth test pinned, and say in its docstring that it
is the one test a deliberate change edits, alongside `docs/MODEL.md` §
"Supported run length".

**Done when.** The eight tests read the limit from the constant and still fail
against a banner, refusal or clock that states a limit other than the
constant's; with the constant set to 48 h the whole suite fails only
`test_the_supported_run_length_is_twenty_four_hours`, and at 24 h it passes.
