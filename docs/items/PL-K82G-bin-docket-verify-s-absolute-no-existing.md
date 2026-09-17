---
id: PL-K82G
title: bin/docket verify's absolute 'no existing assertion removed' check has no passing route for an item whose own work makes a rendered string false, so a correct close-out REJECTs
status: untriaged
feature: delegation
added: 2026-09-17
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

**Candidate answers, none obviously right.** The judgment half must not be
scripted, per `CLAUDE.md`, so each of these keeps the removal *visible* and
only changes who signs it off:

- **Declared in the item.** A front-matter field naming the exact assertion
  lines the work falsifies, which `verify` cancels against and prints. The
  removal stays auditable and becomes a commissioned act rather than a silent
  one; the cost is a new field and a new way to lie in front matter.
- **Reported under `--self` only**, as a fifth commission-style `NOTE`. Cheapest,
  and wrong in the direction that matters: `--self` is where the session grading
  itself is least able to see its own weakening, which is why these four were
  kept absolute there.
- **Cancel against an added assertion naming the same subject** - the same test
  function, or the same expected-value expression. Deterministic, but it is the
  guess at the judgment half that `CLAUDE.md` says a tool must not make.
- **Leave it absolute and say so.** Document that a falsified assertion is a
  legitimate `REJECT` a session reports rather than clears, which is what
  happens today undocumented. Honest, and it keeps a red gate that a correct
  close-out trips, which is the thing `CLAUDE.md` calls a defect in the check.

**Done when.** A close-out whose work falsifies an existing assertion has one
prescribed route, written down, and either reaches `ACCEPT` by it or is
documented as a `REJECT` the session is expected to explain. `PL-L4KX` is
answered by the same decision or explicitly excluded from it. A test in
`subprojects/docket/tests/test_verify.py` pins whichever route is chosen.
