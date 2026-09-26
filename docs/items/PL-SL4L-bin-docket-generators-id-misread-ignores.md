---
id: PL-SL4L
title: bin/docket generators <id> --misread ignores --misread without saying so and prints the ordinary cluster view
priority: P3
effort: S
status: done
classes: defect
feature: generator-identification
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-24
closed: 2026-09-26
payoff: bin/docket generators stops accepting a flag it then ignores, so its output means what was asked for
verify: grep -q 'def test_generators_given_an_id_and_misread_does_not_ignore_the_flag' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket generators <id> --misread ignores --misread without saying so and prints the ordinary cluster view

**Premise re-checked at triage, 2026-09-24.** `bin/docket generators PL-B8HZ
--misread` and `bin/docket generators PL-B8HZ` print identical output, and both
exit 0. In `cmd_generators`, `args.misread` is read only on the no-id branch.
The parser adds the optional `head` and `--misread` with nothing relating them.

**Why it matters.** Little is lost, because the id view already prints the
head's `misread:` line. What costs is the silence. A flag accepted and then
ignored teaches a reader that a flag may not do what it says, and this is the
command a grooming pass reads its head comparison from.

**Done when.** `bin/docket generators` given an id and `--misread` either
refuses the pair or prints what the flag asks for. Either way it no longer
prints the cluster view as if the flag were honoured, and a test in
`subprojects/docket/tests/test_cli.py` pins it.

**Generator check.** A one-off: an argument pair that nothing validates. No
head's `misread:` states a fact about command-line flags.

**Worked.** 2026-09-26, on `claude/pl-batch-04-d15tqm`. Of the brief's two
routes, the pair is refused rather than printed as a filtered misread list:
the id view already carries its head's `misread:` line, which the brief itself
notes, so a second rendering of one line would add output without adding an
answer. `cmd_generators` checks the pair before reading the clusters, prints a
refusal naming both commands that answer, and exits 1, the convention this
file's other command-level refusals use, rather than argparse's exit 2. The
test reuses the `_overlapping_heads` fixture and asserts neither the cluster
view nor the head's `misread:` line is printed.
