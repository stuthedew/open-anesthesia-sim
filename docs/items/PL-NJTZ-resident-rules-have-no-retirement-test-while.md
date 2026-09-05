---
id: PL-NJTZ
title: Resident rules have no retirement test while checks do, so the resident set can only grow
status: done
priority: P2
effort: S
classes: docs, session-cost
feature: dev-tooling
touches: CLAUDE.md, docs/resident-instructions.md
verify: python3 tools/doc_check.py check && grep -q 'When a resident rule is retired' docs/resident-instructions.md && grep -q 'retired rather than kept' CLAUDE.md
added: 2026-09-05
closed: 2026-09-05
---

**Problem, stated against the asymmetry.** `CLAUDE.md` § "Prefer deterministic
tooling over repeated model work" gives checks a retirement test: "A check earns
its place every run, or it is retired... A check that fires every run without
changing a decision is a defect in the check." Resident rules had no equivalent.
What they had was a protection against removal in § "The queue" - "never delete a
rule for being wordy" - and a refused ceiling. So the resident set could only
grow.

**Measured.** 2026-09-01 to 2026-09-05, resident went 35721 to 44697 characters,
+25% in five days. The one pass that ever removed anything (`PL-JK0M`) took out
770 characters and was overtaken by the next commit, which added 5149
(`PL-WWDT`). `PL-4H01`'s audit found only 563 further characters of defensible
routing, so routing runs an order of magnitude behind growth.

**Why the ceiling refusal does not answer this.**
`docs/resident-instructions.md` refused a numeric ceiling and the refusal is
right: "a limit is met by deleting a rule to reach a number, which is the one
outcome this pass must not produce, and no number the tool could hold would know
which rules a session must see before it reads anything."

That refusal addressed *ceilings*. It did not consider a **qualitative**
retirement test, which is what checks already get and rules did not. The test
written mirrors `CLAUDE.md`'s check-retirement wording rather than imposing a
number: a resident rule is retired when its failure mode is now caught
deterministically - by a check, a hook, or a command that prints the rule at the
moment it fires. Wordiness is still never a reason; obsolescence is.

**Where it lives, and why not either option first proposed.** Two were put to the
project owner and both had a flaw. *Ledger only*, at zero resident cost, leaves
the protection resident and the counterweight not - which recreates precisely the
asymmetry `PL-9J2W` had just fixed for the apparatus, where one side loaded in
every session and the other did not. *Fully resident* costs ~400 characters and
puts a routing-pass procedure into the file the change is trimming.

So: a one-clause pointer resident, immediately after the sentence it qualifies,
and the test itself in the ledger. 184 characters resident, which is the pattern
the rest of `CLAUDE.md` already uses - conclusions resident, arguments in
`docs/resident-instructions.md` where nothing loads them at launch.

**What the test refuses to become**, recorded in the ledger section itself: not a
ceiling (the refusal stands and is quoted there); not a licence to rewrite (a
rule whose evidence went stale while its other triggers have no carrier stays
put, with `PL-4H01`'s `list_sessions` case as the worked example); and not silent
(a retirement is recorded in "What was routed out" with what now enforces it, so
the ledger is an audit trail in both directions).

**Why it matters.** Every resident rule was added because a session got something
wrong once. Nothing ever asked whether that was still true. The cost is paid by
every session forever, and it is an adherence cost rather than a context-rot one:
at roughly 11000 tokens against sessions measured at 304k-436k, resident text is
about 3% of context, but 402 lines against the 200-line figure Anthropic's memory
documentation gives is where adherence degrades - "Bloated CLAUDE.md files cause
Claude to ignore your actual instructions."

**Done when.** A resident rule has a stated condition under which it is removed,
the condition is not a character count, and the protection against deleting a
rule for being wordy still stands.

**Worked.** Clause added after that protection sentence and read back with it to
confirm the two do not contradict: wordiness is still not a reason, obsolescence
now is. The full test is a new section in `docs/resident-instructions.md`, placed
before "Reductions considered and refused" so the ceiling it must not become is
the next thing read. Shipped with `PL-4H01`, which is its first application: net
379 fewer resident characters than `origin/main`.
