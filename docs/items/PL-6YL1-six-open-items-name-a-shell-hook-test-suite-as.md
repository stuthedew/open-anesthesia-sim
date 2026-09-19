---
id: PL-6YL1
title: Six open items name a shell-hook test suite as their verify pytest target while touching subprojects/docket/src, and the rule that catches exactly that class has zero false positives today
priority: P2
effort: M
status: dropped
classes: defect, infra
feature: queue-hygiene
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-16
closed: 2026-09-19
reason: PL-6TP8 retired the prerequisite clause from the field (project owner, 2026-09-19, ratified), so no new command carries a pytest target for this rule to read; the six legacy commands lose theirs as their items are started
---

**Problem.** Six open items name a shell-hook test suite as their verify pytest target while touching subprojects/docket/src, and the rule that catches exactly that class has zero false positives today

**Found 2026-09-16** while triaging `PL-2M4X`, which is one of the six and is
scoped to one of them deliberately.

**The six, measured on the live store.** Items whose `touches` names a file
under `subprojects/docket/src` while their `verify` runs a pytest target outside
`subprojects/docket/tests`:

```
PL-4PC5  P2 M ready   tests/unit/test_docket_digest_hook.py
PL-FT3M  P3 S ready   tests/unit/test_docket_digest_hook.py
PL-J45M  P3 M ready   tests/unit/test_docket_digest_hook.py
PL-MBTZ  P2 M ready   tests/unit/test_docket_branch_guard.py
PL-WNQT  P2 M ready   tests/unit/test_docket_branch_guard.py
PL-Z85N  P2 S ready   tests/unit/test_docket_digest_hook.py
```

Both files are shell-hook suites that import no `docket` module and drive
`bin/docket` as a subprocess against git fixtures, so in each case the pytest
half of the command proves a different suite's health than the one the item
would change. Four of the six are `P2`, which is to say likelier to be delegated
than `PL-J45M`.

**The rule, and it is the point.** "If `touches` names a file under
`subprojects/docket/src`, the `verify` pytest target must be under
`subprojects/docket/tests`" has **six violations and no false positives** on the
store today. The looser rule a reader would reach for first - "the verify target
must be inside `touches`" - is not adoptable: ten open items violate it,
`PL-RWBV` among them, which is the queue's own precedent for this defect class.

**Why it matters.** `CLAUDE.md`'s "find the decidable part and put it in code"
applies exactly: whether a path is under a directory is decidable, the answer is
the same every run, and the alternative is a reader catching it one item at a
time, which is how six accumulated. The harm each one carries is `PL-2M4X`'s -
`bin/docket delegable` offers the item with a command that cannot fail for the
reason the item is about, so a worker's branch is accepted having proved nothing.
`PL-RWBV` settled the shape for the class: "a check decides the difference rather
than a reader".

**Done when.** `docket check` reports an item whose `verify` pytest target sits
outside `subprojects/docket/tests` while its `touches` names
`subprojects/docket/src`, as an advisory rather than an error - the six existing
ones are repaired as their items are started, per the skill's rule against
writing commands away from their work - and the five besides `PL-J45M` are named
in its output. A test in `subprojects/docket/tests/test_checks.py` pins the rule
and its zero false positives.

**Not folded into `PL-2M4X`**, which corrects `PL-J45M` alone and is `S`. This
is the class and the check, and is `PL-RWBV`'s batch-and-mechanize shape rather
than a wider hand correction.

**Re-pointed by `PL-6TP8`, 2026-09-19, and decided by its shape half.** The
rule here is the contract's second obligation made mechanical for one class.
If the field drops prerequisite clauses, no new command carries a pytest target
for this rule to read, the six legacy ones are repaired as their items are
started, and the check is not worth building - this item then drops. If the
field keeps them, build it as briefed. Not started until that is answered.

**Dropped under `PL-6TP8`, 2026-09-19.** The shape half was ratified the same
day: a `verify:` command is the `grep` alone, so no new command carries a
pytest target for this rule to read, and the six that do (`PL-4PC5`,
`PL-FT3M`, `PL-J45M`, `PL-MBTZ`, `PL-WNQT`, `PL-Z85N`) lose it as their items
are started - `PL-2M4X` carries `PL-J45M`'s. A check with a population that
can only shrink to zero and no way to grow fails `CLAUDE.md`'s gate for
building one. The `verify:` this item carried named the check's test and is
removed with it.
