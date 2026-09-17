---
id: PL-L4KX
title: bin/docket verify REJECTs every close-out of a dropped item and of a not-delegable one, because it refuses an empty verify: with no exemption for either, while docket check accepts both - so the skill's own close-out step cannot reach ACCEPT on work it prescribes
priority: P2
effort: S
status: done
classes: defect
feature: delegation
milestone: v0.4.27
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-16
closed: 2026-09-17
pr: 655
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_dropped_close_out_is_not_a_missing_command' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify REJECTs every close-out of a dropped item and of a not-delegable one, because it refuses an empty verify: with no exemption for either, while docket check accepts both - so the skill's own close-out step cannot reach ACCEPT on work it prescribes

**Observed 2026-09-16** on `PL-0C6W`'s own close-out, the 2026-09-16 triage
pass, which the `docket` skill routes to `bin/docket verify --self` at step 5.
All four ids the closing commit led with came back `REJECT`:

```text
FAIL  has a `verify:` command - none recorded
REJECT
```

**Where.** `subprojects/docket/src/docket/verify.py:667`:

```python
if not item.verify:
    report.checks.append(Check("has a `verify:` command", False, "none recorded"))
    report.stopped_early = True
    return report
```

No exemption, and `stopped_early` means none of the other checks run at all.

**Two distinct shapes reach it, and both are correct states for an item to be
in.**

- **A `dropped` item.** Dropping is a closure - `dropped` sits beside `done` in
  `CLOSED_STATUSES` - and the store's rule for one is a `reason` and a `closed`
  date. It has no command by construction: nothing was built, so nothing proves
  it. Three of the four above were drops.
- **An item carrying `not-delegable`.** `docket check`'s rule is explicit that
  this is the *alternative* to a command: "an item set to `ready` must name a
  `verify:` command, **or** record in `not-delegable` why no command can prove
  it". `PL-0C6W` carried one, on the same argument `PL-2B7B`, `PL-Q2PX` and
  `PL-LYX2` recorded before it.

**The two tools disagree about the same store**, which is the part that makes
this worth an item rather than a shrug. `bin/docket check` reports 0 errors
across all four; `bin/docket verify --self` REJECTs all four. A session
following the skill exactly cannot reconcile them, and the only way to reach
`ACCEPT` is to write a `verify:` onto a closed item - which `docket check`
separately **refuses**, because a closed item's command is a record of what was
run rather than a live specification (`PL-JZ1D`). So the prescribed procedure
has no passing state.

**Why it matters.** This is the same family as `PL-69JZ`, `PL-B5YN` and
`PL-7XTS` - `verify` REJECTing correct work - and it is the residue those three
left. `PL-7XTS` routed every close-out through `--self`, which is what makes
this fire routinely rather than rarely: any close-out that drops an item, and
any close-out of a `not-delegable` item, now ends on a `REJECT` the session must
talk past. That trains a reader to skim the block, which is exactly where a real
protected-path failure is printed - the cost `PL-69JZ` named and this reproduces.

It is `CLAUDE.md`'s second compounding-friction test: a refusal fired so
routinely on correct work that it is routed around rather than read.

**Not the same as `PL-PFK1`**, which is about a session reaching the *bare*
command and never being told `--self` exists. This fires *with* `--self`
already given, and `--self` is documented as relaxing only the four commission
checks - the command guard is one of the four integrity checks it deliberately
holds absolute.

**Approach, and the line to be careful about.** The integrity check is right in
general: a session must not skip the test. What is wrong is treating "no command
recorded" as "the test was skipped" when the store has already decided no
command can exist. So the exemption is narrow and reads the store rather than
the session's word for it: an item at a `CLOSED_STATUSES` value of `dropped`, or
one carrying a non-empty `not-delegable`, has its command check reported as a
`NOTE` naming which of the two applies, and the remaining checks **still run**
rather than stopping early. A `done` item with neither a command nor a
`not-delegable` reason keeps the hard `FAIL`, because that genuinely is a
skipped test and `verify_required_at_close_from` already calls it an error.

**Done when.** `bin/docket verify --self` reaches a verdict other than an
early-stopping `REJECT` on a close-out whose ids are `dropped` or carry
`not-delegable`, with the remaining checks actually run; a `done` item carrying
neither still fails hard; and a test pins all three cases. `docket check` and
`docket verify` then agree about every item in this store.

**Worked 2026-09-17**, with `PL-K82G`, as that item asked - one reading of the
gate settles both, and both exemptions are read off the item as the *base* holds
it rather than off the branch.

Built exactly as the approach above describes: `dropped`, or a non-empty
`not-delegable`, reports the command check as an advisory naming which of the
two applies, and the remaining checks still run instead of stopping early. A
`done` item carrying neither still fails hard and still stops. `docket check`
and `docket verify` now agree about every item in this store.
