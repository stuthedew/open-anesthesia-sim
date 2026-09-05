---
id: PL-JZ1D
title: A closed item's verify: command can be silently invalidated by later work, and nothing notices
priority: P2
effort: M
status: done
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-05
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_vcs.py && grep -q 'def test_rewriting_a_closed_item_s_verify_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** `docket check` runs the `verify:` command of every *open* item,
and `verify_required_at_close_from` requires the field to be present at
closure. Nothing checks a *closed* item's command still resolves against the
tree. So the record of what proved an item can rot while the item goes on
reading as proven.

Observed the same day it was written. `PL-MJ7B` closed carrying

```
uv run pytest tests/unit/test_chart_downsampling.py && grep -q 'def test_the_envelope_scan_reads_each_sample_once' tests/unit/test_chart_downsampling.py
```

which was run and watched to fail before the work, exactly as the rule asks.
Hours later `PL-D9WD` restructured `chart_downsampling.py` around an M4
aggregate cache and deleted that test along with the `_CountingValues` helper
it used. The command now exits 1 on `main`. Nothing failed, nothing warned,
and the item still says that command is what proved it.

**Why it matters.** The command *is* the item's proof of work — that is the
whole reason `verify_required_at_close_from` makes a missing one an error
rather than an advisory. A command that no longer resolves is worse than an
absent one, because it looks like provenance and is not, which is the failure
mode `CLAUDE.md` calls out for tooling: output that looks authoritative and
is not.

It is also not rare. Any item whose successor refactors the same file can do
this, and the two most likely successors are the follow-up the first item
filed and the milestone work it cleared the ground for — exactly the pairs
this queue produces on purpose.

**The design question, which is the real content of this item.** A check that
simply ran every closed item's command would be wrong on both counts: it
would cost the whole history's runtime on every `make check`, and it would
fail for the *right* reason constantly, since a superseded test is the normal
outcome of a refactor rather than a defect. `CLAUDE.md`'s "a check earns its
place every run, or it is retired" rules that out.

Candidates, cheapest first:

1. **Decide nothing; record the tree it passed against.** Stamp the closing
   commit's SHA beside the command when an item closes, so a reader knows
   what it was true of. Zero runtime, no false alarms, and it converts a
   claim that goes stale into a claim that stays true. It does not tell
   anyone the command has stopped working.
2. **Check only the items a diff touches.** `tools/doc_check.py candidates`
   already computes documentation lines mentioning anything a diff touches;
   the same shape applied to closed items' `verify:` commands would fire
   only when a change deletes or renames something a closed command names —
   which is exactly when a human should decide whether to re-point it or let
   it go.
3. **Require the superseding item to say so.** A rule rather than a check:
   work that deletes a test named by a closed item's command annotates that
   item. Cheap to state, and it fires only if the session notices, which is
   the half a rule cannot enforce.

**Done when.** The project has decided whether a closed item's proof is meant
to stay runnable or merely to record what was run, and the answer is enforced
or written down rather than assumed. If the answer is the second, `PL-MJ7B`'s
own record is the first thing to correct.

**Decision needed.** Whether a closed item's `verify:` is meant to stay runnable
or only to record what was run. Candidate 1 (stamp the closing commit's SHA
beside the command) makes the claim true forever at zero runtime and tells
nobody when the command stops working; candidate 2 (check only the closed
commands a diff touches, the `doc_check candidates` shape) fires exactly when a
person should decide; candidate 3 is a rule rather than a check and fires only
if the session notices. Running every closed command on every `make check` is
ruled out by `CLAUDE.md`'s "a check earns its place every run".

**Decided (2026-09-05): the record, not a live command — and the answer is
enforced against the *repair* rather than against the rot.**

The measurement settled it. Across this store, 14 of the 179 closed items
carrying a command no longer resolve, and not one of the 14 is a defect: each
is later work correctly consuming the state its predecessor established.
`PL-5WFS`, `PL-9K7K`, `PL-QTN6` and `PL-THVN` are `grep '^blocked-by: PL-…'`
against an item file, which pass exactly while the blocker is unresolved —
commands written in the expectation of stopping. `PL-YLZQ` greps for "Decided,
not yet implemented", removed when the decision was implemented. A field whose
commands are designed to become false cannot be read as a standing claim about
the tree.

That disposes of candidates 2 and 3, and not on principle: a diff-scoped check
would have fired on all 14 and changed no decision on any of them, which is
`CLAUDE.md`'s definition of a check to retire rather than add.

Candidate 1's *reading* is right and its *mechanism* is not needed. Stamping a
SHA re-introduces exactly what retired `commit:` (`PL-T63T`) — a squash-merge
discards the branch commit — and the tree is already recorded by `pr:`, which
outlives the squash and which 246 of the 248 closed items carry. The way back
from a closed command to the tree it last passed on exists today.

What had no guard was the opposite direction. A session meeting a dead command
re-points it at whatever covers the ground now, and the item then names a
command that never ran against the work it claims to prove: a false provenance
where there was a true one, which is worse than an absent one because it looks
authoritative. `records_on_base` reads what the base recorded for each closed
item this checkout changed, and `docket check` errors where a branch changes
it, or adds one to an item closed without a command. An error rather than an
advisory because the rule is exact, and one-sided — the two diffs behind it
return nothing where no merge base resolves, so a truncated checkout
under-reports and no branch is accused of an edit it did not make. Reopening
the item is the way out and needs no flag.

`PL-MJ7B`'s own record needed no correction, which is the decision's first
consequence rather than an omission: the command it carries was run, watched
to fail, and passed on the tree that closed it. It reads as stale only against
the wrong question.
