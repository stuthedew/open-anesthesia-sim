---
id: PL-K4R5
title: An item whose deliverable is a changed output string always REJECTs docket verify --self, because falsifies: can only be declared on the base's copy before the work
priority: P3
effort: S
status: done
classes: defect, infra
feature: verify-assertion-check
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket
added: 2026-09-20
closed: 2026-09-20
payoff: stops a correct close-out spending the owner's attention on an explained-away REJECT, every time an item changes what a command prints
verify: grep -q 'def test_a_changed_string_names_its_candidates_and_still_counts' subprojects/docket/tests/test_verify.py
---

**Problem.** An item whose deliverable is a changed output string always REJECTs docket verify --self, because falsifies: can only be declared on the base's copy before the work

**Why it matters.** `bin/docket verify --self` keeps four integrity checks
absolute, and "no existing assertion removed" is one of them - correctly, since
a session may re-scope its own commission but may not weaken what measures it.
The exemption is `falsifies:`, read from the base's copy of the item so that a
reviewer wrote it first, which is the whole worth of the field.

But a whole class of item cannot satisfy that. Where the deliverable *is* a
changed output string - `PL-FCM3` on 2026-09-20 is the worked example - the
test pinning the old string must change, and there is no arrangement of the
tests that keeps it. So:

- `bin/docket new` writes no `falsifies:`, and nothing in the capture rule
  suggests one.
- Triage could write it, but only by opening the test file and copying the
  exact assertion line, which is work done away from the work - the practice
  the `verify:` rules already identify as how every wrong command here came to
  exist.
- The session doing the work knows the string precisely, and is the one party
  forbidden to declare it.

The result is a `REJECT` on correct work, which the skill handles by telling
the session to report it. That is the right fallback and it is not free: it
spends the project owner's attention at every such item, and a `REJECT` that
is routinely explained away is the shape `CLAUDE.md` names as an advisory
being routed around.

**What is not being proposed.** Not relaxing the check, and not letting a
session declare its own exemption. Both are the thing the field exists to
prevent.

**Done when.** Either the gap is closed - something writes `falsifies:` at the
moment the class of item is recognised, before the work, or the check learns to
tell a *replaced* assertion from a deleted one - or the case is recorded as
accepted friction with its reasoning, so the next session meeting it stops
re-deriving this.

**Decision needed.** Whether this is worth closing at all. One count would
settle it: how many closed items removed or reworded an existing assertion, and
how many of those carried a `falsifies:`. It has not been run.

**`PL-K82G` already refused the fallback this leaves in place.** It is the item
that built `falsifies:`, closed in `v0.4.27`, and it weighed "leave it absolute
and document the `REJECT`" as one of four candidates and rejected it by name,
on `CLAUDE.md`'s "a check earns its place every run": *"a gate a correct
close-out trips, which the session is then expected to talk its way past, is
the defect that trains a reader to skim the block where a real failure is
printed."*

That is exactly what happened closing `PL-FCM3` on 2026-09-20, three releases
later. The field existed and was unusable: nothing on the capture or triage
path writes it, and the one party who knows the assertion string verbatim - the
session doing the work - is the party `front_matter_check` correctly forbids
from declaring it. So the close-out fell back to reporting the `REJECT` in a
reply, which is the disposition `PL-K82G` ruled out.

This is therefore not a re-opening of `PL-K82G`'s decision. Its reasoning is
accepted whole; what is reported is that the mechanism it built does not reach
the case it was built for unless somebody writes the field before the work, and
nothing yet does.

**Measured, 2026-09-20 - the count this item said would settle it.** It asked
for two numbers: how many closed items removed or reworded an existing
assertion, and how many of those carried a `falsifies:`. Replayed with
`verify.py`'s own `is_assertion_line` and `replacements` over the 502 single-id
squash close-outs on `origin/main` - single-id because `item_commits` selects
per id, and a multi-id squash no longer records which commit was whose:

| | |
| --- | --- |
| close-outs replayed | 502 |
| removing at least one assertion line | 61 |
| would `REJECT` `no existing assertion removed` | 57 (11.4%) |
| ...of those, the changed-string shape this item names | 20 |
| items in the whole store carrying a `falsifies:` | **0 of 1,324** |

The second number is the finding. The field shipped in `v0.4.27` (`#655`) and
has never been written onto an item, open or closed, so the exemption
`PL-K82G` built has a passing route nobody has ever taken.

**Three ways to close the gap, all refuted by measurement.**

- **Teach the check to tell a replaced assertion from a deleted one** - the
  second branch of "Done when" above. It cannot: the original string is gone,
  so the diff holds nothing that separates a commissioned rewrite from an
  expectation dropped. **15 of the 20 have more than one candidate**, and
  `PL-FCM3` - this item's own worked example - has **six** for one removal.
  Its real rewrite is neither first nor last, so a pairing would have recorded
  `assert "what they wait on: PL-ZZZZ" in printed` as the replacement for a
  gate summary line and printed the guess as fact. Folding this shape at all
  would also have folded `PL-6580`, whose seven disclaimer assertions genuinely
  left the suite when the prose they read was deleted - the hazard the check
  exists for.
- **Anchor the fold on the commission's own `verify:` string**, which a
  reviewer writes at triage, before the work, and which therefore carries the
  same property `falsifies:` buys. It explains **1 of the 20**.
- **Have triage copy the old string out of the brief it is already reading**,
  which would refute this item's second bullet. The string is in the item for
  **3 of the 20** - `PL-026`, `PL-6580` and `PL-1J0P`. `PL-FCM3` was one of the
  three, which is what made the route look general. The bullet stands.

**Done, as the first branch of "Done when" cannot be reached and the third is
what the evidence supports.** The check keeps refusing - the removal is real -
and now reports what it could not decide, which is the apparatus floor in
`.claude/rules/apparatus-standard.md`: an answer must be true or must say what
it could not read. `literal_swaps` names every same-file line differing from the
removal by exactly one string, prints the true count with the first three, and
folds none. `PL-FCM3`'s own `REJECT` now reads:

```
  FAIL  no existing assertion removed - 1 line(s), 1 differing by one string
          one string differs, still counted: assert "1 this gate can clear, ...
                candidate 1 of 6: assert "what they wait on: PL-ZZZZ" in printed
                candidate 2 of 6: assert "1 this gate can clear, 2 waiting on ...
                candidate 3 of 6: assert "blocked outside the gate: PL-001, ...
          which candidate replaced it is not decidable from the diff, so none is
          folded; `falsifies:` on the base's copy is what declares this shape
```

Strings only, deliberately narrow: a changed *number* keeps its subject and
changes what is expected of it, which `PL-K1WS` already identified as a
weakened assertion. Widening to numbers is one alternative away should an item
ever be filed whose deliverable is a changed numeric output.

The `docket` skill's close-out records the case so the next session reporting
this `REJECT` spends a line rather than re-deriving the three refutations, and
names the one case where triage can still declare the field: where the item's
own brief already quotes the old string.

**`PL-K82G`'s decision is untouched.** It rejected "leave it absolute and
document the `REJECT`" as a substitute for building a passing route, and built
one. What is reported here is that the route it built is unreachable in
practice, which is evidence it did not have - and the answer is not to relax
the check but to make its refusal readable.
