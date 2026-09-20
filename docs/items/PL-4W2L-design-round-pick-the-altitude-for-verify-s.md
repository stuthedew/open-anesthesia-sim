---
id: PL-4W2L
title: design round: pick the altitude for verify's assertion check before the next of its three open items is worked, since six fixes have each uncovered the next and PL-G21K's ratified decision reached only the suppression check beside it
priority: P2
effort: M
status: ready
classes: defect, infra
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-20
payoff: settles the assertion check's altitude once instead of paying a seventh special case, which is what the same decision bought for the suppression check beside it
verify: grep -q '^## Decision: the assertion check' docs/items/PL-4W2L-design-round-pick-the-altitude-for-verify-s.md
---

**Problem.** design round: pick the altitude for verify's assertion check before the next of its three open items is worked, since six fixes have each uncovered the next and PL-G21K's ratified decision reached only the suppression check beside it

**Why it matters.** `no existing assertion removed` is one of the four
integrity checks `--self` may never relax, so every false positive blocks a
correct close-out until a reader talks past it - and a reader who has learned
to explain away this block is the reader who skims a real weakening. That is
`CLAUDE.md`'s second compounding-friction test, and the inflow is the other
half: each fix so far has uncovered the next, so the three open items are not
three defects but three symptoms of an altitude that was never chosen.

**Decision (project owner, 2026-09-20, ratified, over letting the three items
below be worked one at a time).** A design round comes first. `PL-G21K` put the
same argument for the *suppression* check and it held: one decision retired a
marker, narrowed the matcher and closed four items, where the four would each
have been a special case. The assertion check beside it has the same history
and no such decision.

**The accretion, which is the evidence.** Six fixes so far, each uncovering the
next: `PL-7TYC` (shape and file suffix), `PL-K1WS` (pair a removal with its
replacement), `PL-K82G` (the `falsifies:` escape hatch), `PL-QJQL`
(`with pytest.raises(...)`), `PL-XMNC` (replay scope), `PL-K4R5` (name the
candidates it cannot decide). Three remain open:

| item | what it names |
| --- | --- |
| `PL-XQGH` | the parenthesized multi-manager `with (` form leaves `pytest.raises` on a line matching nothing |
| `PL-CNJH` | the replacement pairing folds an assertion whose inserted argument *loosens* it - `approx(2.05)` to `approx(2.05, rel=0.5)`; 4 of 56 folds across 905 commits change what the line asserts |
| `PL-2DTK` | `--self` cancels an added line against its removal only within the commits it selects per id, so an item is charged with a removal a sibling commit had added |

**What the round has to settle, stated so it is not re-derived.** The check
answers an *intent* question - did this branch weaken what measures it - with a
text matcher over a raw diff, and `CLAUDE.md`'s "do not script the judgment" is
the rule it keeps crossing. `PL-G21K`'s resolution was not "a better matcher":
it was to remove the one marker whose question belonged to another tool and to
stop reading non-code. The analogous question here is which of the three items
above are *instances* of one altitude decision and which are genuine separate
defects - `PL-2DTK` in particular reads as a scoping bug rather than an
altitude one, and may not belong in the round at all.

**Name the number first.** Per `.claude/rules/expert-review.md`: before
proposing to narrow, fold or retire anything here, state what the suppressed
side would have to be worth for the proposal to be wrong, then count it over
`main`. `PL-G21K` did this by importing `verify.py` from both sides and
replaying every added line; the same replay over *removed* lines is the
measurement this round needs, and `is_assertion_line` is already the predicate
to run it with.

**Do not close this by patching one of the three.** The round's output is a
recorded decision - ratified or refused - after which the three are closed,
dropped, or re-scoped against it. That is the shape `PL-G21K` used.

**Done when** a decision is recorded here naming what the assertion check is
for and what it deliberately does not decide, and `PL-XQGH`, `PL-CNJH` and
`PL-2DTK` are each resolved against it rather than individually patched.

The `verify:` command greps this file for a `## Decision: the assertion check`
heading, so the round's outcome is written here under that exact heading.
A design round's deliverable is prose, and prose is the only thing a command
can discriminate on: `true` would pass on a branch that held no round at all.
