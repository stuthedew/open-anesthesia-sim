---
id: PL-BX1C
title: bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it, though the skill says a dropped item has no command to run
priority: P2
effort: S
status: ready
classes: defect
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
verify: grep -q 'def test_a_dropped_items_verify_command_is_not_run' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it, though the skill says a dropped item has no command to run

**Found 2026-09-19 closing `PL-4Q9B`** (record clone trust and the permitted
ref operations), which dropped `PL-TFWR` as superseded.

`.claude/skills/docket/SKILL.md` says: "A `dropped` item, or one carrying
`not-delegable:`, has no command to run, and the check says which applies
rather than stopping the audit dead (`PL-L4KX`)." That is not what happens when
the dropped item still carries the field. `bin/docket verify --self PL-TFWR`
ran its command and printed:

```
FAIL  `verify:` command passes - python3 tools/doc_check.py check && grep -qF 'git push origin --delete' CLAUDE.md
```

followed by `REJECT`. The command was correct to fail: the item was dropped
*because* that CLAUDE.md line was deliberately not added, so the command names
work nobody did. Deleting the stale field cleared it and the audit went to
`ACCEPT`.

**Why it matters.** Dropping an item is the normal disposition for one
superseded by other work, and an item at `ready` already carries a command by
rule - so the two meet constantly, and the collision produces a `REJECT` on a
correct close-out. That trains a reader to skim the block where a real
protected-path failure is printed, which is the cost `PL-69JZ` and `PL-7XTS`
already paid once for the four self-audit guards.

**Shape of a fix, not chosen.** Either `verify` skips the command whenever the
status is closed-and-dropped, matching what the skill already claims; or
`docket check` refuses the combination at store-validation time, where the
message can say "a dropped item should not carry a `verify:`" instead of
surfacing as a failing command. The second is the louder and earlier of the
two, and it is the one that would have caught this before the audit ran.

**Not the same as re-pointing a closed item's command**, which `docket check`
correctly refuses (`PL-JZ1D`). A `done` item's command is a record of what was
run and passed; a `dropped` item's never ran against anything and records
nothing.

**Done when.** Closing a `dropped` item that still carries a `verify:` reaches
`ACCEPT` without anyone deleting the field - either because `bin/docket verify`
skips the command at that status, or because `bin/docket check` refuses the
combination at store-validation time - and a test drives a dropped item whose
recorded command fails, asserting the audit does not refuse on it.
