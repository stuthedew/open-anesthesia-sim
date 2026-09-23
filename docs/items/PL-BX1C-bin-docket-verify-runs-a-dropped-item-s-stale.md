---
id: PL-BX1C
title: bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it, though the skill says a dropped item has no command to run
priority: P2
effort: S
status: done
classes: defect
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, .claude/skills/docket/modes/close-out.md
added: 2026-09-19
closed: 2026-09-23
verify: grep -q 'def test_a_dropped_items_verify_command_is_not_run' subprojects/docket/tests/test_verify.py
recurrences: 2026-09-22 PL-23C7, 2026-09-23 PL-KSV2 withdrawn 2026-09-23 PL-KSV2
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

**Second occurrence, and the count, 2026-09-21.** It fired again closing
`PL-CHF2` (the capture that `PL-TH7P` duplicated shipped work), whose commit
drops `PL-TH7P`. `bin/docket verify --self PL-CHF2 PL-TH7P` returned `ACCEPT`
for `PL-CHF2` and `REJECT` for `PL-TH7P`, on:

```
FAIL  `verify:` command passes - uv run pytest subprojects/docket/tests/test_cli.py -q && grep -rq 'def test_new_prints_candidate_duplicates' subprojects/docket/tests
```

Every other guard passed, `make check` was green, and the command was correct
to fail: it pins a test name that the shipped work never used. The field was
left in place this time rather than deleted, so the `REJECT` stands in the
record as an instance of this item.

**How often it can fire: 31 of the 164 `dropped` items in the store carry a
`verify:`** (counted 2026-09-21). So it is not a rare collision, and the number
carries a constraint this brief's **Shape of a fix** does not: the second
option - having `bin/docket check` refuse the `dropped` + `verify:` combination
at store-validation time - would fail `make check` on all 31 of them the moment
it landed. It needs a dated cutover keyed on `closed`, in the shape
`docket.toml` already uses for `verify_required_at_close_from` and
`payoff_required_from`, or it is not shippable. The first option - `verify`
skipping the command at that status - carries no such cost, which is a point
for it that the "louder and earlier" reading alone does not weigh.

**Done when.** Closing a `dropped` item that still carries a `verify:` reaches
`ACCEPT` without anyone deleting the field - either because `bin/docket verify`
skips the command at that status, or because `bin/docket check` refuses the
combination at store-validation time - and a test drives a dropped item whose
recorded command fails, asserting the audit does not refuse on it.

**Counted over the whole store, 2026-09-21 (`PL-PT7M`'s close-out).** The
collision is not rare and the workaround is not being applied consistently: of
**170 `dropped` items, 34 still carried a `verify:` command** before that
close-out ran - 20%. Every one of those 34 would `REJECT` its own audit today
if anybody re-ran it, on a command describing work the drop says will not be
done.

`PL-PT7M` met five of them at once. It dropped six items under
`.claude/rules/citation-drift.md`, five of which carried a command, and
`bin/docket verify --self` printed `FAIL ... REJECT` for each while
`make check` was green and every other guard passed - the sixth, `PL-Z5FG`,
carried no command and went straight to `ACCEPT`, which is the controlled
comparison this item's case wants. Three of the five commands asserted the
*opposite* of the decision recorded beside them: `PL-8T3Z`'s asked that
`PL-K2C8`'s `touches` name the hook, which is exactly what the closed-brief
clause says not to do.

The five were deleted, on this brief's own precedent from `PL-TFWR`, leaving 29
of 170. That is a workaround applied by hand at each close-out, which is what
this item exists to remove: the tool should read `status: dropped` and say so,
rather than every session learning the same thing from a `REJECT`.


**Recurred 2026-09-22 (`#922`, captured as `PL-23C7` and dropped into this
item at triage 2026-09-23).** Dropping `PL-XQGH`, `PL-CNJH` and `PL-2DTK`
REJECTed each on its own test-name `grep`, with every integrity check and
`make check` green. Since `#929` added those three test names, the same audit
would ACCEPT them, so a dropped item's command flips with unrelated work and
proves nothing either way. 38 of 191 dropped items carried a `verify:` on
2026-09-23, up from 29 of 170 on 2026-09-21.

**Worked 2026-09-23.** Took the first shape. `verify` reads `status: dropped`
and does not run the command. It prints it as a `NOTE`: `not run: a dropped
item built nothing, so no command can prove it`, the same words the no-command
half of `PL-L4KX`'s exemption already used. The second shape, `docket check`
refusing the combination, was not built. It is a new check, which the generator
pause refuses while `PL-1P5V` is live, and it would have needed a dated cutover
for the 38 dropped items already carrying a command.

The drop is read off the branch's copy, like the rest of that exemption, and it
has to be: the drop is what the close-out writes. That grants nothing. A drop
claims no work for a command to prove, the integrity checks still run over the
diff, and a delegated audit refuses a worker who drops its own item, through
`front_matter_check`.

Writing that down found the docs claiming the opposite. `verify_item`'s
docstring, `subprojects/docket/README.md` and the close-out skill all said both
exemptions are read from the base, which is true of `falsifies:` alone. For the
`not-delegable:` half it is a real self-grant under `--self`, reproduced and
filed as `PL-KSV2`. The three documents now say what is read where and point
there.

Three tests. `test_a_dropped_items_verify_command_is_not_run` uses a command
that leaves a file if it runs, so "not run" is observed rather than inferred.
`test_the_same_command_on_a_done_item_still_runs_and_refuses` pins that the skip
is keyed on the drop. `test_a_worker_dropping_its_own_item_is_still_refused_in_a_delegated_audit`
pins the guard the reasoning above rests on. The first and third fail with the
fix reverted; the second passes either way, by design. The 38 dropped items
still carrying a command are left as they are.
