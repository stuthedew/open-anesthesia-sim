---
id: PL-32Z9
title: main is red: PL-D1RT's verify: command already passes on a tree carrying none of its work, and only the push-to-main --verify sweep can see it, so no pull request will go red and every merge re-reds main
priority: P2
effort: S
status: done
classes: defect
feature: queue-hygiene
milestone: v0.4.26
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 646
verify: bin/docket check && grep -q '^status: done' docs/items/PL-D1RT-docs-working-notes-md-s-ui-structure-thread-and.md
---

**Problem.** main is red: PL-D1RT's verify: command already passes on a tree carrying none of its work, and only the push-to-main --verify sweep can see it, so no pull request will go red and every merge re-reds main

**The failure, verbatim** from run 2106 on `d7a3b05b` (2026-09-16 17:49:57Z),
the only error in an otherwise green job:

> `PL-D1RT` is open but its `verify:` command already passes (1 of 164
> checked). Either the work landed and the item was never closed - close it -
> or the command does not discriminate and proves nothing, in which case
> `docket verify` would ACCEPT a branch that did none of the work

**No pull request can show it, and that is by design rather than a gap.**
`.github/workflows/quality.yml` gives the whole-store `--verify` sweep to the
push-to-`main` event only; a pull request gets `--verify-base`, which replays
just the items its own diff edits. `PL-SDHR` measured the sweep at 87 s of a
152 s job and `PL-P3B6` argued the scope, so both halves are deliberate. The
consequence is the one this item is about: a store error of this kind is
invisible until it is already on `main`, and stays red through every
subsequent merge that does not touch the item.

**Which of the two dispositions is a judgment, not a lookup.** The evidence
points at the second, but does not settle the first:

- `PL-D1RT`'s command is `python3 tools/doc_check.py check && ! grep -qF
  '`v0.5.x — the interface pass` row of "The timeline"' ROADMAP.md`, and its
  own brief - written the same day - records that the row **no longer
  exists**. So the negated `grep` was already true when the command was
  recorded, which is the "written away from the work and never run" shape
  `.claude/skills/docket/SKILL.md` warns about.
- Whether `PL-D1RT`'s *work* is done is the separate question, and it has
  moved since: `PL-PHKP` (#634, merged 2026-09-16) re-pointed the interface
  pass to `v0.7.x`, so "item 34's timing paragraph and `PL-037Y` read
  correctly against a port that precedes v0.5.0" has to be re-read against a
  third ordering rather than the one the item was written under.

**The structural fix is already filed and is not this item.** `PL-879R`
(`needs-decision`) is that `docket check` advises on a `verify:` command's
*outcome* but never its *shape*, so a command that cannot discriminate is
reported only once it has started passing. `PL-Y1W6` is the same class one
instance earlier - `main` red on `PL-S5YM`'s bare `-k` selector - and was
dropped. This item is the live instance blocking `main` now; `PL-879R` is what
stops the next one.

**Done when** `main`'s quality run is green: `PL-D1RT` is either closed with a
command that was run and seen to fail first, or re-pointed at something only
its work creates, with the choice between those two recorded in its brief.

**The open half, settled 2026-09-16 by re-reading both targets** (found from
the other direction, by `PL-7SVX`'s session reading `main` red after #638
merged). The bullet above is right that `PL-D1RT`'s "Done when" has to be
re-read against a third ordering. Re-read against it, **its work is done** -
both named targets now carry the current ordering, and neither places the
interface pass after v0.5.0:

- **Item 34's timing paragraph.** `ROADMAP.md` now reads "*Placement (project
  owner, 2026-09-08, and moved 2026-09-16). After v0.7.0, as the `v0.7.x — the
  interface pass` row of "The timeline"*". Correct, dated, and it names the
  move.
- **The UI-structure thread.** `docs/WORKING_NOTES.md` now narrates the change
  rather than asserting either ordering: the row is "*written `v0.5.x` and
  sitting between v0.5.0 and v0.6.0 then, and `v0.7.x` sitting after item 34's
  two releases since 2026-09-16 (`PL-PHKP`)*".
- **`PL-037Y`.** Its brief turns on a wrong gloss of `PL-NGF7` and describes
  that item as "deferred to the Qt port with an expected disposition of
  `dropped`" - port-relative rather than v0.5.0-relative, so it carries no
  stale sequence claim for `PL-D1RT` to correct. Its own defect is unrelated
  and stays open.

So **both dispositions the error offers are true at once**, which is why it
reads as ambiguous: the work landed (disposition 1, and `PL-PHKP` is what
landed it, incidentally - no session ever held `PL-D1RT`, which is why nobody
closed it), *and* the command never discriminated (disposition 2). Only the
first is what `main` needs; the second is `PL-879R`'s.

**What that makes the remedy.** Close `PL-D1RT` with a rider recording that
its work landed under `PL-PHKP` rather than being done directly. Do **not**
re-point its `verify:` at something only its work creates - there is no such
thing left to name, because the work is already on `main`, and a command
written now could not be run and seen to fail first, which is the rule the
"Done when" above is invoking. A closed item's command is not replayed, so
closing satisfies that condition rather than evading it.

**One addition to this brief's own framing**, and it is stated at the strength
it was actually checked to. This brief cites run 2106 alone. The **three most
recent completed `quality` runs on `main` all concluded `failure`** - 2103
(`52205f6`, #634), 2104 (`ff4be61`, #635) and 2106 (`d7a3b05b`, #636) - which
is the "every merge re-reds main" clause in the title showing up in the run
history, and the argument for scheduling `PL-879R` rather than only filing it.

**Only 2106's failure was read.** Its job log carries this item's error as the
sole entry under "Errors". For 2103 and 2104 the conclusion was read and the
cause was not, so whether they failed on `PL-D1RT` or on something else is
open - three failures in a row is the finding, one confirmed cause is what
supports it. A session acting on this should read those two logs before
treating the streak as one fault, because the alternative - that `main` has
had more than one thing wrong with it since 2026-09-16 - is worse rather than
better.

Runs 2115 (`674a15e`, #637 - the commit carrying this item) and 2116
(`0ba9aa4`, #638) were still in progress and are not counted. Both are
expected red on the same error, since `PL-D1RT` is still `ready` on `main` and
neither diff touches it, but expected is not measured.

**Why it matters.** A red default branch makes every branch's red CI unreadable: a
session cannot tell its own failure from the inherited one without reading the job
log. It is also `CLAUDE.md`'s silent-wrong-answer test exactly - `make check`
passes while the guarantee it stands for is void - and the population is every
session rather than one.

---

**Done, 2026-09-16. `main` is green**, run `#2134` on `262b38b`, the first since
`#2102`. The `Done when.` above is met in its first branch: `PL-D1RT` was closed
in `#645` with a replacement command that was run against `57fdb8c` - the last
green commit - and seen to fail there on both greps before being recorded, and
`PL-D1RT`'s brief carries the clause-by-clause table saying why closing was chosen
over re-pointing.

**One claim in this brief was wrong, and the correction is worth keeping.** It
said the negated `grep` "was already true when the command was recorded". It was
not: the command pins a citing *phrase*, not the row heading, and that phrase was
present **twice** in `ROADMAP.md` at `57fdb8c` and **zero** times from `52205f6`
(`#634`) onward. So the command discriminated correctly until `#634` removed the
phrase - it was invalidated by another item's work rather than written away from
its own. `PL-KND7` carries the full count. The difference matters because the two
readings imply different fixes, and only the second identifies the absence
sentinel as the hazard.

**Everything else here held**, including the half `PL-KND7` first got wrong: the
pull-request scoping is deliberate and measured (`PL-SDHR`, `PL-P3B6`), not a gap,
and `PL-879R` is where the structural rule belongs.
