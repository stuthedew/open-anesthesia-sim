---
id: PL-4W2L
title: design round: pick the altitude for verify's assertion check before the next of its three open items is worked, since six fixes have each uncovered the next and PL-G21K's ratified decision reached only the suppression check beside it
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-20
payoff: settles the assertion check's altitude once instead of paying a seventh special case, which is what the same decision bought for the suppression check beside it
verify: grep -q '^## Decision: the assertion check' docs/items/PL-4W2L-design-round-pick-the-altitude-for-verify-s.md
root-cause-of: PL-5B88, PL-YZJD, PL-2DTK, PL-CNJH, PL-XQGH
generator: live - PL-G21K's fix reached only the suppression check; the assertion half still infers intent from single diff lines, and PL-5B88, PL-4W2L and PL-YZJD arrived after G21K closed (PL-KVDK)
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
text matcher over a raw diff, and `CLAUDE.md` § "do not script the judgment" is
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

## Recommendation: the assertion check (session, 2026-09-22, awaiting the project owner)

**Decision needed.** Which altitude the assertion check works at: (i) statements, compared against the base, with every undeclared change or removal of an existing assertion refused; (ii) statements, refusing only an assertion that left its test and reporting one changed in place; or (iii) today's lines, with the three items patched one at a time.

**Recommendation: (i) - read assertions as statements rather than lines,
compare them against the base, and fold nothing on the shape of an edit.**
Chosen over (ii), refusing only an assertion that left its test and reporting
one changed in place, and over (iii), patching the three items at the line
altitude. Not yet a decision: the `## Decision: the assertion check` heading
this item's `verify:` greps for is written only once the owner answers.

**What the check would be for.** One decidable fact: an assertion that existed
on the base - an `assert` statement (its test, not its message), a call whose
name starts with `assert`, or a `raises`/`warns` context-manager item - is
absent, as Python's own `ast` reads it, after the item's own commits. Existing
assertions are read-only unless the commission says otherwise, so every such
absence refuses unless `falsifies:` (the base's copy, or `PL-ZMGR`'s
self-declaration) matches the assertion's source text. "Existing" means present
in the base's copy of the file; formatting, wrapping and a move within the file
are not changes.

**What it deliberately does not decide.** Whether a changed assertion is
stronger, weaker or merely restated. That is the judgment half, and every shape
rule so far has been a guess at it: the insertion fold (`PL-K1WS`) is how
`approx(2.05)` to `approx(2.05, rel=0.5)` passes (`PL-CNJH`), and the
one-string listing (`PL-K4R5`) prints up to six candidates because it cannot
choose. The report groups each refusal by test function with that function's
assertions before and after, so the reader pairs them and the check chooses
nothing. Unchanged from today and still not decided: whether a new test asserts
the right value (`RESIDUAL`), an assertion moved to another file (two facts,
per file), and anything outside `.py`.

**The count, run 2026-09-22 over the 1,127 non-merge commits of `origin/main`
at `e7120e23`.** Per commit: the per-file fold `_net_line_changes` makes, then
`is_assertion_line`, `replacements` and `literal_swaps` exactly as
`verify_item` wires them (`falsifies:` not replayed); each flagged line then
classified by `ast` on the file before and after that commit.

| what the parser says the flagged removed line was | refused today | folded today |
| --- | --- | --- |
| not an assertion at all (docstring or comment prose) | 3 | 0 |
| an assertion that survives unchanged (reflow, wrap, move) | 25 | 0 |
| an assertion changed in place, its test keeping its count | 679 | 61 |
| an assertion that left a test still present | 41 | 0 |
| an assertion whose test function is gone (deleted, renamed, moved) | 1,099 | 2 |

The parser also finds **43 assertions changed or lost that the matcher never
flagged**: 41 changed on a line it does not read - in every sample, a
continuation line of a wrapped statement, such as an entry of the expected dict
in `test_theme.py` or the exception type inside a wrapped `pytest.raises(` -
and 2 lost with their function.

| rule | commits refused, of 1,127 |
| --- | --- |
| today | 121 |
| (i) | 124 |
| (ii) | 58 |

**The number that would make (i) wrong, then the count.** (i) is wrong if what
it newly refuses is not an assertion change, or if what it stops refusing is.
Of the 6 commits it stops refusing, the parser finds an assertion change in
**0** - each flagged only prose or an unchanged assertion, the trailing-comma
reformat `dfc39bfd` the largest. Of the 9 it starts refusing, **9** changed an
existing assertion: 5 pass today only through the insertion fold (`PL-MN4J`'s
`721d2088` among them), and 4 changed one on a line the matcher cannot see
(`417491fe` changed the expected agent colour mapping). So the whole cost is 9
correct close-outs in 1,127 owing a `falsifies:` line or a sentence of
explanation, against 6 false refusals retired, 41 silent misses closed and the
fold `PL-CNJH` names removed.

**Why not (ii).** It halves the refusals by accepting 66 commits that changed
an existing assertion in place, and in-place modification is the documented
dominant route: on ImpossibleBench's Conflicting-SWEbench, "Claude models and
Qwen3-Coder cheat primarily (>79%) through modifying test cases", and
read-only test access is what the authors found "preventing test modification
attempts" (Zhong, Raghunathan and Carlini, arXiv:2510.20270, 2025,
https://arxiv.org/abs/2510.20270). `--self` is exactly that reader: the session
auditing the test is the session that edited it. The number that would reopen
(ii) is the base rate of weakening among in-place changes, and this history
cannot supply it, because every commit in it merged.

**Why not (iii).** Each of the three can be patched at the line level, and no
patch reaches the 41 continuation-line misses or the 6 false refusals, which
are properties of reading lines rather than defects in any one rule.

**A constraint the implementation owes.** `bin/docket` runs on the bare
`python3` (docket requires `>=3.11`, and this container's is 3.11.15), while
the project requires 3.14. Five source files fail to parse on 3.11 across 62
revisions of this history (3.14's unparenthesized `except`), though no test
file does yet. A file the running interpreter cannot parse must be neither
skipped silently nor refused wholesale: read it with today's line predicate
and name it on the page as read that way, per the floor in
`.claude/rules/apparatus-standard.md`.

**What happens to the three on ratification**, each resolved against the
decision rather than patched:

- `PL-XQGH` dissolves: the parser reads every context-manager item wherever the
  formatter puts it. Dropped, and its parenthesized form becomes a test case.
- `PL-CNJH` dissolves: with no fold, the `approx` loosening refuses as a changed
  assertion, printed before and after. Dropped, and its case becomes a test.
- `PL-2DTK` is not an altitude instance but a reference one, as this brief
  suspected: "existing" has to mean on the base, which the matcher never
  consulted. The decision's own definition settles it, so it rides the same
  change - a form the base's copy does not hold is not charged - and its
  `PL-C4RS`-shaped case becomes a test.
- One implementation item is filed, touching the same three paths as this one.
  It retires `ASSERTION_RE`, `NOT_AN_ASSERTION_RE`, `TOKEN_RE`,
  `tokens_at_depth`, `_inserts_into`, `replacements`, `_one_string_differs` and
  `literal_swaps`, keeping `is_assertion_line` only as the named fallback.
  Nothing outside `verify.py` calls any of them. It rewrites the matcher's
  tests in `test_verify.py` and the README's integrity-check section. It is
  reversible: one module, its tests, one README section.

**If refused**, (ii) or (iii) is recorded under the decision heading instead
and the three are worked against that.
