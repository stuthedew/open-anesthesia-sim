---
id: PL-32Z9
title: main is red: PL-D1RT's verify: command already passes on a tree carrying none of its work, and only the push-to-main --verify sweep can see it, so no pull request will go red and every merge re-reds main
status: untriaged
added: 2026-09-16
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
