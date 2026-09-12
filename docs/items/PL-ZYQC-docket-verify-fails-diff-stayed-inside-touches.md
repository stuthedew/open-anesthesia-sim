---
id: PL-ZYQC
title: docket verify fails 'diff stayed inside touches' on any close-out that follows the skill's instruction to let docket record ride the commit it is already making
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
milestone: v0.4.14
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-07
closed: 2026-09-12
pr: 496
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_pr_only_addition_to_another_items_file_is_not_outside_touches' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify fails 'diff stayed inside touches' on any close-out that follows the skill's instruction to let docket record ride the commit it is already making.

Two instructions in the apparatus give opposite answers about the same commit.
The `docket` skill's close-out, step 1, says of `bin/docket record`: "Let the
write ride a commit you are already making; do not compose one for it, and do
not open a pull request for it alone." `bin/docket verify <id>` then reads that
same commit against the item's `touches` and reports every `docs/items/*.md`
the record wrote as a path outside the commission.

Observed 2026-09-07 closing `PL-X204` (the accounting guard reading the
validator it is called on). `bin/docket record` wrote `pr:` onto `PL-0ZGK`,
`PL-2B7B` and `PL-BKDP` — the three numbers `docket check`'s own advisory said
the base was owed, and the advisory cleared once they were written. `bin/docket
verify PL-X204` then returned `REJECT` with:

```text
FAIL  diff stayed inside `touches` - 3 path(s) outside
        docs/items/PL-0ZGK-main-s-quality-run-has-failed-on-its-last-three.md
        docs/items/PL-2B7B-triage-the-seven-captures-open-on-the-evening.md
        docs/items/PL-BKDP-a-v0-4-8-tag-exists-on-the-commit-that-closed.md
```

**Why it matters.** It is not a wrong answer that a reader can act on — the
paths are named, and a session that knows what `record` does can see what
happened. The cost is that the failure is unavoidable rather than
informative: any session that follows the close-out as written and then runs
`verify` gets it, so the check fires on correct work and cannot distinguish
correct work from the thing it exists to catch. `CLAUDE.md` calls that a
defect in the check — "a check that fires every run without changing a
decision costs attention forever and trains a session to skim the output
where a real advisory also appears" — and the real advisory here is the
*other* `FAIL` in the same block, the protected-path one, which is the line
a reader of a delegated `core/` change actually needs to see.

**Where.** `bin/docket verify`'s `touches` audit, against the `docket` skill's
close-out step 1 (`.claude/skills/docket/SKILL.md`).

**Decision needed.** Which of the two moves.

**Recommended: exempt a `pr:`-only front-matter addition from the `touches`
audit.** `verify` already reads the diff, so the exemption is decidable from
the diff alone — an out-of-`touches` path under `docs/items/` whose only
change is one added `pr:` line — with nothing to plumb between two commands
that run at different times. It is narrow enough that anything else written
into another item still fails, which is the property the audit exists for. Its
cost is a second reading of what `record` may write, held in `verify`; that is
worth accepting because the shape being matched is one line that `record`
itself refuses to write twice differently.

The two rejected alternatives, and why:

- **Have `record` report which paths it wrote, so `verify` subtracts exactly
  those.** Stronger in principle — no pattern to keep in step — but `record`
  and `verify` run at different times with a commit in between, so it needs
  somewhere to leave that list. Every candidate for that is state the store
  does not currently keep, to remove an ambiguity the diff does not actually
  have.
- **Give `record` its own commit, and teach `verify` to ignore a commit whose
  whole diff is `docs/items/`.** Reverses "do not compose one for it", which
  was written deliberately, and `PL-X3WZ` records what reading a queue-only
  commit as a claim already cost. Not to be taken without checking that
  reasoning first.

**Found.** Closing `PL-X204` and running `bin/docket verify` on the result, as
that item's close-out calls for.

**Done when.** A close-out commit that let `bin/docket record` write `pr:` onto
other items passes `bin/docket verify <id>`'s `touches` audit, while a diff that
changes anything else in another item's file still fails it. A test covers both
halves - the sanctioned `pr:`-only addition and an ordinary edit to a
neighbouring item - since an exemption with no test for what it still refuses is
an exemption that quietly widens.
