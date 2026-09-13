---
id: PL-F4JS
title: bin/docket triage omits the **Decision needed.** requirement from the rules it prints, so triaging an item to needs-decision fails check after the edit
priority: P2
effort: S
status: done
classes: defect, infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_cli.py
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_triage_states_the_rules_a_chosen_status_adds' subprojects/docket/tests/test_cli.py
---

**Problem.** `bin/docket triage` closes with "The rules these answers have to
satisfy" and prints six of them, read from `docket.toml` and the checker so that
a triaging session does not have to re-derive what `docket check` will enforce.
One rule is missing: `checks.py:231` errors on an item at `needs-decision` whose
body has no `**Decision needed.**` line. Nothing in the triage output says so.

**Why it matters.** The list is presented as complete - it is the whole reason
the skill says "do not read the store for this, and do not re-derive the rules
from here". A session that trusts it, sets an item to `needs-decision` and runs
`make docket` gets an error after the edit is written, which costs a round trip
and ~40 s of `check` runtime to discover. Observed 2026-09-02 triaging
`PL-B0YN`; the fix was one heading, and finding out it was needed was the
expensive part.

The brief-sections rule *is* printed ("a status past `untriaged` needs the full
brief"), which is what makes the omission misleading rather than merely
incomplete: the output looks like it covers the body requirements.

**Where.** `_triage_rules` in `subprojects/docket/src/docket/render.py`, which
builds the block `render_triage` prints, beside the existing brief-sections
line; `subprojects/docket/tests/test_cli.py` holds the triage output tests.
(The rendering is in `render.py`, not in `cli.py` as this brief first said.)

**Worth checking while there.** Whether any other status-conditional rule in
`checks.py` is absent from the same block; the two found so far are the brief
sections (printed) and this one (not).

**Done when.** `bin/docket triage` names the `**Decision needed.**` requirement
in its rules block, and a test pins that the block covers the status-conditional
rules `checks.py` enforces.

**Worked.** The audit **Worth checking while there.** asked for found three
more, not one: `blocked` requires a `blocked-by` (`checks.py:362`), and
`dropped` requires both a `reason` (`:414`) and a `closed` date (`:419`) -
and a triage pass sets all three statuses, `dropped` explicitly on the
skill's instruction. All four now come from one table,
`checks.STATUS_REQUIREMENTS`, which the checker and `_triage_rules` both
read, so a requirement cannot be enforced without being printed. A
parametrized test pins each entry to an actual refusal from `docket check`,
which is what stops the table's prose drifting from the checker.
