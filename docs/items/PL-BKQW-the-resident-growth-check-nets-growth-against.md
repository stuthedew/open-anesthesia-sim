---
id: PL-BKQW
title: The resident-growth check nets growth against shrinkage, so resident text trimmed to pay for an addition is invisible in the total
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-01
closed: 2026-09-01
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_trim_that_pays_for_an_addition_is_an_advisory_at_net_zero' tests/unit/test_doc_check.py
---

**Problem.** `check_resident_instructions` compares one number against one
number: the resident line total in the working tree against the total at the
tip of the default branch. Growth and shrinkage therefore cancel. A change that
adds nine lines to `CLAUDE.md` and cuts nine from
`.claude/rules/instruction-writing.md` reports `growth == 0`, raises no
advisory at all, and reads as a free diff.

**Why it matters.** That is precisely the outcome the check's own docstring
says must never happen: "a limit would be met by deleting a rule to reach a
number, which is the one outcome the routing pass must not produce." The
docstring uses it to argue against a threshold, correctly - and then the metric
underneath is blind to the same outcome arriving with no threshold in sight. A
session that reads "resident instructions grew 9 lines; every session pays this
before it has read anything" and goes looking for nine lines to give back
produces a clean report, and the rule it deleted is gone without anyone being
asked.

The rules most exposed are the ones written most tightly, because a session
hunting for lines to cut takes them where the prose looks compressible - and
the safety-critical clinical-output standard is resident precisely because a
session that opens no matching file must still see it.

The project owner named this directly on 2026-09-01: additions they explicitly
ask for should land "without causing other, presumably streamlined text to
suffer due to an arbitrary count limit". There is no count limit, and this item
is the reason one is not needed - the harm a limit would cause is reachable
without it, and is what the check now looks for.

**Where.** `tools/doc_check.py`'s `check_resident_instructions`, and
`tests/unit/test_doc_check.py`.

**Approach.** Two changes, both to what the check says rather than to what it
permits; nothing is thresholded and nothing fails.

1. **A second advisory for a change that both grows and shrinks the resident
   set**, whatever the two sum to. It is decidable from the per-file deltas
   already computed, needs no judgment, and does not catch a routing pass:
   moving a rule out to a path-scoped file shrinks alone, with no matching
   growth, and stays silent exactly as it does today.
2. **The growth advisory stops reading as a budget.** It named the cost -
   "every session pays this" - and then listed only routing as the remedy,
   which leaves a session with a number it cannot reduce honestly and an
   implied instruction to reduce it. It now states that there are two answers
   and no third: route it, or keep it and say why. Text the project owner
   asked for is the second answer, already given. And it says plainly never to
   trim other resident text to offset the number.

**Done when.** A change that adds resident text and removes other resident text
raises an advisory even when the two cancel exactly, a pure routing pass still
raises none, and the growth advisory names keeping the text as a legitimate
answer rather than implying the number must come down.

**Closed 2026-09-01, in the session the project owner asked for it,** per the
rule that a behavior change takes effect in the session that asks for it. All
three new assertions were confirmed to fail against `origin/main`'s
`doc_check.py` before the fix and pass after it.
