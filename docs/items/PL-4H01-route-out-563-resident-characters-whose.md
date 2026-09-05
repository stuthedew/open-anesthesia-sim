---
id: PL-4H01
title: Route out 563 resident characters whose carriers already exist: the lane sentence, the finish-a-feature bullet, and the duplicated quality-suite line
priority: P2
effort: S
status: done
classes: docs, session-cost
feature: dev-tooling
milestone: v0.4.2
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-05
closed: 2026-09-05
pr: 362
verify: python3 tools/doc_check.py check && ! grep -q 'A prompt naming a lane' CLAUDE.md && ! grep -q 'Prefer finishing a feature' CLAUDE.md
---

**Problem.** Three resident rules state something a deterministic carrier now
states better, at the moment it fires. `CLAUDE.md` § "Prefer deterministic
tooling over repeated model work" calls deleting prose that something
deterministic enforces "the strongest outcome here", and these are the cases
that qualify.

**Measured, 2026-09-05.** The resident set was 44697 characters over 637 lines.
A block-by-block pass against all six tools in `tools/`, all four hooks, and
`.claude/skills/docket/SKILL.md` found five routing candidates totalling ~1980
characters, of which three are defensible at **563 characters**. Every carrier
already existed; nothing was built. Byte counts were measured on `origin/main`
rather than estimated: 334 + 159 + 70.

**What moved, and to what.** The three rows are recorded in
`docs/resident-instructions.md` § "What was routed out" with the carrier named
for each. In summary: the lane sentence to `cli.py`'s lane line, which prints
which lane its own answer is in and the other lane's pick with the literal
command; the finish-a-feature bullet to `plan.py`'s `rank()`, which prints the
rule verbatim beside every ranked item; and the quality-suite line to nothing at
all, because it was a strict duplicate of a more precise statement twenty-seven
lines below it that names `mypy` and adds when to run it.

**Each carrier was observed firing before its rule was removed**, not assumed
from reading the code. `bin/docket next` was run against this store and printed
both lines.

**Alternative considered and refused.** The `list_sessions` bullet in
`.claude/rules/instruction-writing.md` is 1287 characters, the largest single
candidate anywhere, and its cited evidence (`PL-66FP`, two sessions cutting
v0.3.7) is now hard-refused in `release.py` and suppressed in the digest by
`render.py`. Left resident anyway: three of its four named triggers - a tag, a
merge, a branch deletion - meet no check and are not a `docket` mode, so a reply
recommending one would load nothing. Cutting only the dead clause is *rewriting*,
which the routing policy forbids.

**One earlier judgment is superseded, and the dates are why.** `PL-H7XN`
judgment 6 reached the finish-a-feature bullet already and stopped short of
removing it: "describes what `docket next` already ranks, so the prose is
enforced and one line survives." That judgment closed 2026-08-31. The carrier it
was weighing was the *ranking*. `plan.py` did not begin printing the rule
verbatim beside every ranked item until `PL-B0YN` landed on 2026-09-01, one day
later. A rule the tool merely obeys is a weaker case for removal than one the
tool states in the reader's own words at the moment of the decision, so this is a
new argument rather than a reversal of a settled one - and it is recorded here
because the difference is a single day and would otherwise read as ignoring
`PL-H7XN`.

**Not reopened.** The four entries in `docs/resident-instructions.md`
§ "Reductions considered and refused" were re-read and none has a new argument.
In particular `import_boundary_check.py` enforces two of the seven architecture
invariants but cites `CLAUDE.md` as their source, so deleting the prose would
strand the citation - which is the refusal's own reasoning.

**Why the number is small, and why that is the finding.** `PL-JK0M` predicted
it: "The honest expectation is that a large share of the 548 lines is
required-resident under the project's own test." It was right. The resident set
is not bloated with routable material, so growth cannot be answered by routing
alone - which is what `PL-NJTZ` is for, and why the two shipped together.

**Done when.** The three rules are gone from `CLAUDE.md`, each is recorded in
`docs/resident-instructions.md` § "What was routed out" with its carrier, and
`make check` reports the resident total down against `origin/main`.

**Worked.** All three removed. Combined with `PL-NJTZ`'s +184-character pointer
clause, the resident set went 44545 to 44166 characters and 637 to 631 lines -
**379 fewer characters than `origin/main`**, the first net reduction recorded
since `PL-JK0M`'s -770. `doc_check` caught a real defect in the first draft of
the ledger row, which cited `tests/test_cli.py` instead of
`subprojects/docket/tests/test_cli.py`; the citation check is the reason that
did not reach `main`.
