---
id: PL-TPXR
title: app/control_timeline.py's module docstring says its one unit conversion is from a fraction to the percent the delivered dial is displayed in, but since PL-NJPB format_control_value also converts the recorded percent to a fraction before format_percent, so the docstring misstates where the delivered value's units change (found closing PL-KSLX)
priority: P2
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: src/anesthesia_sim/app/control_timeline.py
added: 2026-11-01
payoff: a reader of control_timeline.py learns that the module itself turns the dial's percent into a fraction, so nobody passes it a fraction and displays a hundredth of the setting
verify: ! grep -qF 'The one unit conversion is from a' src/anesthesia_sim/app/control_timeline.py
---

**Problem.** app/control_timeline.py's module docstring says its one unit conversion is from a fraction to the percent the delivered dial is displayed in, but since PL-NJPB format_control_value also converts the recorded percent to a fraction before format_percent, so the docstring misstates where the delivered value's units change (found closing PL-KSLX)

**Reproduced 2026-11-01.** The module docstring says: "The one unit conversion
is from a fraction to the percent that the delivered dial is displayed in, and
`formatting.py` performs it rather than this module spelling it out again." For
the delivered dial, `format_control_value` returns
`format_percent(fraction_from_percent(Percent(value)))`. So the module converts
the recorded percent to a fraction itself, and `format_percent` converts it
back.

**Why it matters.** The module docstring is the first thing a reader of
`control_timeline.py` reads about units. It says the module does no unit
conversion of its own. A reader who trusts it could pass a fraction to
`format_control_value`, and the delivered dial would then display a hundredth
of its value. The function's own docstring is correct, so the displayed value
is right today.

**Done when.** The module docstring says where the delivered value's units
change: the recorded value is a percent, `format_control_value` converts it to
a fraction, and `format_percent` in `formatting.py` converts that fraction to
the displayed percent.

**Generator check.** One-off in the `stale-source-claims` sweep. The docstring
restates where the code converts units, and it went stale when `PL-NJPB` changed
the recorded unit to percent. That is `PL-4FBP`'s fact at family altitude, but
in a code docstring, which `PL-FM15` placed outside the documents that
`PL-4FBP`'s convention binds. So it is not recorded as a re-entry.
