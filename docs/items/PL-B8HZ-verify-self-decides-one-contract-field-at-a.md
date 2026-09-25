---
id: PL-B8HZ
title: verify --self decides one contract field at a time whether to read the base's or the branch's copy of the item, so each field's wrong choice arrives as its own item - six so far, PL-PZ6T and PL-TKFD open
priority: P2
effort: M
status: ready
classes: defect
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
payoff: One stated rule for which copy each contract field is read from, so a new field stops costing an item per wrong direction
verify: grep -q 'def test_a_widened_touches_is_measured_against_the_commission_and_named' subprojects/docket/tests/test_verify.py
root-cause-of: PL-KSV2, PL-PZ6T, PL-TKFD, PL-ZMGR, PL-K4R5, PL-YZJD
generator: live - verify --self chooses the base's or the branch's copy one contract field at a time, and PL-PZ6T (verify:) and PL-TKFD (falsifies:) are still open; every further contract field needs its own choice
misread: Which copy of an item, the base's or the branch's, is authoritative for each contract field
---

**Problem.** verify --self decides one contract field at a time whether to read the base's or the branch's copy of the item, so each field's wrong choice arrives as its own item - six so far, PL-PZ6T and PL-TKFD open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. `PL-5MYR` listed this as
"a bounded tail and not a generator". Three critics each found it a generator
by count (3 of 3). Under `CLAUDE.md`'s rule the count decides the record, and
a bounded tail is an argument about the verdict, not about the record.

**The mechanism.** `verify --self` reads each field of an item's contract from
one of two copies, the base's or the branch's, and the choice is made field by
field as each wrong choice is found. Branch-side reads give false ACCEPTs, and
base-side reads give false REJECTs:

- `PL-KSV2` (done): `not-delegable:` was read from the branch, so a close-out
  could delete its failing `verify:` and ACCEPT. Fixed by `Commission.verify`.
- `PL-PZ6T` (open): `verify --self` runs the branch's `verify:` command
  (`_check_item`'s run of `item.verify`), so a weaker passing command can replace a failing one.
- `PL-ZMGR`, `PL-K4R5` and `PL-YZJD` (done): `falsifies:` is read from the
  base's copy, so the session that knows the string cannot declare it.
  `PL-YZJD` is also listed under `PL-4W2L`, which the critics call a
  misattribution: `PL-4W2L` retired the assertion line matcher and never
  touched this read.
- `PL-TKFD` (open, needs-decision): the base-side residual of `falsifies:`.
  A `ready` item's mid-work discovery, and an item captured and closed on one
  branch, still have no route.

**Why it matters.** Every new contract field will need its own copy decision,
and each wrong one costs an item. `PL-5MYR`'s "the fields are four, three are
decided" leaves out `PL-TKFD`, which is the open end of a field it calls
decided.

**Decision needed.** Should every contract field `verify --self` reads come from one copy, the base's with a named exception for fields whose deciding is the work, or should the per-field choice stay and this head close spent? Recommendation: one rule, stated in `verify.py` beside `Commission`, because `PL-PZ6T` and `PL-TKFD` are the same question asked from opposite directions.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Against this
decision it rules out keeping the per-field choice and closing this head spent:
that is the quick fix that gets done again with the next contract field. The
design round builds the one rule. Reading the direction this way is this
session's call, so ordinary evidence reopens it.

**Done when.** One rule says which copy each contract field is read from, and
why. Either it is stated once where every field reader applies it, or the
owner decides the per-field choice stays and this head is closed spent with
that recorded. The pause in `CLAUDE.md` § "What this project is" applies to
any new check this needs.

## Design round, 2026-09-25

**Recommended: one rule keyed on what kind of statement a field is, stated once
in `Commission`'s docstring in `subprojects/docket/src/docket/verify.py` and
named by every reader in `_check_item`.** Chosen over reading every field from
the base's copy with `needs-decision` as the one exception, which the count
below refutes for `verify:`, and over keeping the per-field choice and closing
this head spent, which the owner's direction of 2026-09-23 rules out.

**The rule.** An item's front matter holds three kinds of statement, and which
copy `verify --self` reads follows from the kind, never from the field:

1. **What the work did** - `status`, `closed`, `reason`, `pr`. The branch's
   copy, because the close-out is what writes them, and they excuse nothing:
   a drop claims no work for a command to prove (`PL-L4KX`, `PL-BX1C`).
2. **What the work was to satisfy, written before it existed** - `verify:`
   and `touches:`. Predictions: a command naming a test not yet written, a
   path list naming files not yet created. The base's copy is the commission
   and is what the branch is measured against. The branch's copy is a
   *correction* of the prediction: it is the evidence the audit runs and
   reads, and it is printed as a correction beside the base's, with the base's
   own result, never substituted silently. A delegated audit refuses the
   correction outright through the front-matter check, as it does today.
3. **What the work may waive** - `falsifies:` and `not-delegable:`. A waiver
   removes a refusal: `falsifies:` folds a removed assertion out of an
   integrity check against the base *tree*, `not-delegable:` excuses the
   command check. A waiver waives only what the base holds, and the base's
   copy is the only word on it. Where the base holds nothing to waive - no
   commissioned command - the check has nothing to refuse and says why, which
   is how a capture closes on `not-delegable:` today (`PL-KSV2`). Where it
   does - a commissioned command, or an assertion in the base tree - a waiver
   the branch writes is printed as the branch's own word and waives nothing.
   The base hands a waiver to the branch by exactly one written statement,
   `status: needs-decision` on the base's copy with the branch closing the
   item (`PL-ZMGR`), because there the answer was the branch's to make and
   what it falsifies follows from the answer.

One sentence carries it: **a correction supplies evidence and is honoured and
printed; a waiver removes a refusal and is the base's; an outcome is the
branch's and excuses nothing.** A new field is placed by one question - does it
say what the work did, what it was to satisfy, or what it may waive - and the
copy follows.

| field | kind | copy read | today | the build changes |
| --- | --- | --- | --- | --- |
| `status`, `closed`, `reason`, `pr` | outcome | branch | branch | nothing |
| `verify:` | prediction | base measured; branch's correction run and printed | branch, silently | run the base's beside it, print the correction (`PL-PZ6T`) |
| `touches:` | prediction | base measured; branch's widening printed | branch, silently | the NOTE names the widening |
| `falsifies:` | waiver | base; hand-off on `needs-decision` | the same | nothing in code; routes recorded (`PL-TKFD`) |
| `not-delegable:` | waiver | waives only a command the base holds | the same (`PL-KSV2`) | nothing |
| `status: needs-decision`, base's copy | the hand-off | base | the same (`PL-ZMGR`) | stated as general to waivers |

**Why a correction and a waiver read from different copies**, since one copy for
every field was the shape this head asked for. Counted first, per
`.claude/rules/expert-review.md`. Of 1,437 close-outs on `main`, 163 (11.3%)
rewrote a `verify:` the base already held, and 582 (40.5%) wrote one the base
never held. Read shape by shape at the closing commit, all 163 are corrections:
92 name no test function (a grep target reworded, a doc line); 34 name a test
that never existed under the commissioned name; 34 keep every test the
commission named and change a clause, 9 of them the `pytest` prerequisite the
allowlist of 2026-09-23 refuses; 3 follow a test that moved file. **None is the
shape `PL-PZ6T` describes** - a commissioned test that exists at close, with the
command swapped away from it. So reading `verify:` from the base and refusing
where the base's fails would have refused 163 correct close-outs and caught
nothing: a check routed around, in `CLAUDE.md`'s words. `PL-4PC5`'s close-out
is among the 163 - the dead command `PL-CWD4` records, corrected at close - and
under this rule its report would have printed the correction, which is the trace
that item wants. The same discipline settles `falsifies:` the other way:
honouring the branch's waiver buys about 2 folds in 502 close-outs (`PL-YZJD`'s
count) at the cost of the property the field exists for. The kinds differ in
what a wrong reading costs. A wrong correction leaves every integrity check
running over the diff; a wrong waiver switches one off. That is why they cannot
share a copy, and why "one copy" was the wrong altitude for the rule.

**What each reader does under the rule** - the build's specification.

- `Commission` holds the base's front matter whole, parsed once, so a new field
  is read from it without a new attribute; `touches` joins `falsifies`,
  `status` and `verify` as the fields the readers take. Its docstring carries
  the rule; each reader in `_check_item` names the kind it applies.
- `verify:` - where the base commissions a command and the branch's differs,
  both run. The branch's decides the check; the base's command and its exit
  are printed under it as a correction, in the shape "commissioned: `A` -
  fails on this tree; this branch runs `B` instead". Where the base commissions
  none, the check's own detail says the command is the branch's own - a suffix
  on the existing line, not a new line, since it is true of 40% of close-outs
  and a line that fires that often is skimmed. This is `PL-PZ6T`, closed by the
  build.
- `touches:` - the scope check compares against the base's `touches` where the
  base holds the item, and the NOTE names which of the paths outside it the
  branch's own widening declares. Advisory in `--self` as today; a delegated
  audit already refuses the edit.
- `falsifies:` and `not-delegable:` - unchanged in code. `PL-TKFD`'s two open
  cases are routes the rule implies, recorded there and in `.claude/skills/docket/modes/close-out.md`.
- Tests: one per row of the table pinning which copy is read, on
  `test_verify.py`'s existing helpers, and the `PL-PZ6T` shape - the base
  commissions a failing test, the branch runs a passing grep - driving the
  printed correction. Docs: `Commission`'s docstring, `subprojects/docket/README.md`
  § "Verification is scoped, not just green", and `.claude/skills/docket/modes/close-out.md`'s "Two of the
  four take an exemption" paragraph, each restated as the three kinds.

**What it does to the members.** `PL-KSV2`, `PL-ZMGR`, `PL-K4R5` and `PL-YZJD`
(done) are each an instance of the rule and stay as they are. `PL-PZ6T` (open,
blocked on this) is the `verify:` row and closes with the build. `PL-TKFD`
(open, `needs-decision`) is disposed of with no code: a waiver is amended where
the commission lives, on the base, by an item-only branch that `CLAUDE.md`'s
capture rule opens a pull request for and arms, after which the work branch
brings `main` in and re-audits; and its captured-and-closed case is the same
route in its natural order, capture first with the declaration and work from
the merged base. Both exist today and neither was written down. Recommended
disposition: record both routes and close it with the build. Its brief asked
to wait for two or three instances; it has two.

**Cost.** M, as filed: `Commission` and three readers in `verify.py`, five or
six tests, three documents. One extra command run per close-out that rewrote
its command, which is 11% of them. Under the pause in `CLAUDE.md` § "What this
project is" nothing new is built: no new check, field or command, and a test
pinning each row is the generator being fixed, which the pause exempts.

**What would change the recommendation.** A close-out in history of the
`PL-PZ6T` shape - none in 163 - or a count showing mid-work `falsifies:`
discoveries are common rather than `PL-YZJD`'s 2 in 502. Either reopens the
row it names, not the rule.

**Decision asked of the project owner:** approve the rule as the build's
specification, or name the row of the table drawn wrongly.

**Decided 2026-09-25: the rule above is the build's specification** (project
owner, 2026-09-25, ratified, over reading every field from the base's copy with
`needs-decision` as the one exception, and over keeping the per-field choice and
closing this head spent). "Agree with recs", so ordinary evidence reopens it,
and the two counts named under "What would change the recommendation" are that
evidence. The build is Stream A's next thread after `PL-KR69`: it moves this
item to `ready` with a `verify:` as it starts, per the `docket` skill's start
mode, and closes `PL-PZ6T` and `PL-TKFD` with it. This design branch changed no
status and yields its claim so the pull request carrying this record can arm.
