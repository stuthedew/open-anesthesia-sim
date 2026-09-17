---
id: PL-K82G
title: bin/docket verify's absolute 'no existing assertion removed' check has no passing route for an item whose own work makes a rendered string false, so a correct close-out REJECTs
priority: P2
effort: M
status: ready
classes: defect
feature: delegation
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-17
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'falsifies' subprojects/docket/src/docket/model.py
---

**Problem.** bin/docket verify's absolute 'no existing assertion removed' check has no passing route for an item whose own work makes a rendered string false, so a correct close-out REJECTs

**Found 2026-09-17** closing `PL-C6XD`, which deleted one of two independent
copies of the `RESERVED` release refusal. The copy it deleted was pinned by
`assert 'Not 0.2.8: the roadmap gives that version to "the workflow works"' in
status`. That assertion is not weakened by the item's work; it is *falsified*
by it, because printing the sentence it pins is the defect. No arrangement of
the tests keeps it, and `bin/docket verify --self PL-C6XD` therefore printed

```
  FAIL  no existing assertion removed - 1 line(s)
          assert 'Not 0.2.8: the roadmap gives that version to "the workflow works"' in status
```

on a close-out with every other check green, `make check` passing and a
strictly stronger replacement test in the same file.

**Why the check cannot see it.** `verify._net_line_changes` folds identical
added and removed lines per file, then `dropped = [line for line in removed if
"assert" in line]`. A substring grep over removed lines cannot distinguish
three cases it currently merges: an assertion weakened to let bad work pass,
an assertion moved or reworded with its subject intact, and an assertion whose
subject the item was commissioned to delete. Only the first is the hazard the
check exists for. `PL-VP40` already narrowed it once, folding out cancelling
pairs so a line removed and restored stops reporting; this is the same class of
over-report one step further out, and the one that cannot be folded away
because nothing identical comes back.

**Why it matters.** It is absolute by design and by documentation - the four
integrity checks "stay absolute", per `.claude/skills/docket/SKILL.md` step 5
and `subprojects/docket/README.md` § "Verification is scoped, not just green" -
so a session meeting it has exactly two moves, and both are bad. It can add a
line somewhere purely to make the fold cancel, which is gaming the thing that
measures it; or it can report `REJECT` and push anyway, which is `CLAUDE.md`'s
"an advisory nobody acts on" arriving at the one gate that is supposed to be
unarguable. The second is what `PL-C6XD` did, with the reason stated in its
reply - but the precedent is set either way, and the next session has a worked
example of shipping through a red integrity check.

**Sibling, not duplicate.** `PL-L4KX` is the same shape from a different
cause - `verify` REJECTs every close-out of a dropped or not-delegable item
because it refuses an empty `verify:`. Both are "the close-out the skill
prescribes cannot reach ACCEPT". They want one answer to the question of what a
correct-but-unclearable integrity FAIL should do, and probably the same commit.

**Answered here rather than left open, and the four candidates are not
equal.** Three of them are eliminated by rules this repository already states,
which is the test `.claude/skills/docket/SKILL.md` gives for whose decision this
is - an item answerable by reading the code and applying a stated rule is a
session's.

- **Reported under `--self` only**, as a fifth commission-style `NOTE`.
  Cheapest, and refused by the reason the split already states:
  `subprojects/docket/README.md` keeps the four integrity checks absolute in
  `--self` precisely because that is where the session grading itself is least
  able to see its own weakening.
- **Cancel against an added assertion naming the same subject** - the same test
  function, or the same expected-value expression. Refused by `CLAUDE.md`'s "do
  not script the judgment": whether a replacement covers what the removal gave
  up is the judgment half, and a tool that guesses at it "is worse than no
  tool, because its output looks authoritative and is not".
- **Leave it absolute and document the `REJECT`.** Refused by `CLAUDE.md`'s "a
  check earns its place every run": a gate a correct close-out trips, which the
  session is then expected to talk its way past, is the defect that trains a
  reader to skim the block where a real failure is printed.

**So: declare it in the item.** A front-matter field - `falsifies:` - naming the
exact assertion lines the commissioned work makes untrue, which `verify` folds
out of `dropped` and prints alongside the check rather than silently. The
removal stays visible and becomes a commissioned act rather than an unexplained
one, which is the property the check exists for; what changes is only that the
declaration is written before the review reads it instead of argued afterwards.

The obvious objection - that a worker could simply declare whatever it wanted to
delete - is already answered by a guard in the same command. `verify`'s
`front_matter_check` refuses a branch that edited its own item's front matter at
all, naming re-scoping `touches` and rewriting `verify:` as exactly the moves it
exists to catch (`PL-20PT`). A `falsifies:` line added on the branch is the same
move and is caught the same way; one written into the commission before the work
is the reviewer's own text. So the field costs a schema entry and buys back a
gate that a correct close-out can clear, with no new way to lie that the command
does not already refuse.

**This is a session's recommendation, not a decision the project owner
specified**, so ordinary evidence reopens it - a measurement, a cost this case
did not carry, or a shape of falsified assertion the field cannot express.

**Done when.** An item may declare `falsifies:` in its front matter;
`bin/docket verify` folds those lines out of the `no existing assertion removed`
check and prints what it folded, so `PL-C6XD`'s close-out would have reached
`ACCEPT` with the removal still on the page. `docket check` validates the field
like any other. `subprojects/docket/tests/test_verify.py` pins three shapes: a
declared line folded, an undeclared removal still refused, and a declared line
that the diff does not actually remove reported rather than ignored.
`.claude/skills/docket/SKILL.md` step 5 and `subprojects/docket/README.md`
§ "Verification is scoped, not just green" both say the four integrity checks
stay absolute, so both need the one sentence that says what a declaration is.

**`PL-L4KX` is sequenced with this, not merged into it.** It is the same
"correct close-out cannot reach `ACCEPT`" shape from a different cause - an
empty `verify:` on a dropped or not-delegable item - and it wants the opposite
remedy, an exemption rather than a declaration. Work them together so one
reading of the gate settles both; do not fold them into one item, because
declaring a falsified assertion and exempting an absent command are different
edits to different checks.
