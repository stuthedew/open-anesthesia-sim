---
id: PL-RCQM
title: "PL-4L6Z's verify: command is killed at check --verify's 120s limit, so the sweep claims nothing about it"
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: verify-command-health
touches: docs/items
added: 2026-09-16
closed: 2026-09-17
reason: duplicates `PL-6YWK` (PL-4L6Z's verify: runs the whole reference suite, so it is killed at docket check's 120s limit and nothing is claimed about the item on any run), which is the same finding written better: it carries the `LANDED_TIMEOUT` reasoning this one lacks - the limit is 'long enough for a project's own suite, short enough that one wedged command cannot hang make check', so raising it for one item spends that guarantee on the item least able to justify it - and a `Done when` that names the paired shape the replacement command must take. Nothing in this brief is outstanding that `PL-6YWK` does not carry, except the two measurements now cross-referenced there
---

**Problem.** `bin/docket check --verify` runs every open item's `verify:`
command against a 120s per-command limit. `PL-4L6Z`'s is

```
uv run pytest tests/reference/ && grep -rq 'def
test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value'
tests/reference/
```

Its first half is a whole test directory, and the sweep kills it:

```
Not checked (this checkout cannot answer; nothing is claimed):
  PL-4L6Z: `verify:` command killed at the 120s limit, so nothing is claimed
  about it - the command is either too slow for a check that runs on every
  `make check`, or it hangs
```

So the one item in the store whose command is never evaluated is also the one
whose command cannot be shown to discriminate. `docket verify` would ACCEPT a
branch that did none of `PL-4L6Z`'s work and nothing would say so, which is the
failure the `already passes` error exists to catch - reached from the other
direction, by never running at all.

**It is not why `main` is red, and this item said otherwise when it was filed.**
The tail of run #2104's log names `PL-4L6Z` immediately before the non-zero
exit, which is what the first version of this brief read it as. The full log of
run #2106 (job 104908108502) settles it: the sweep reports `1 error, 14
advisories, 1 not checked`, the error is

```
PL-D1RT is open but its `verify:` command already passes (1 of 164 checked)
```

and `PL-4L6Z` is the *not checked* line, which claims nothing and fails nothing.
`PL-32Z9`, on `origin/claude/gifted-fermi-m1cksg`, carries the red. Fixing this
item alone would leave `main` red.

**Why it is worth fixing anyway.** `check --verify` cost 233.8s for 164 commands
on that run, and this one is the single command that cannot complete inside the
per-command limit - so every whole-store sweep spends 120s on it and learns
nothing. The per-command budget also has no headroom left: the slowest command
that *did* finish was `PL-P1P6` at 97.2s against the 120s limit.

**Found 2026-09-16** while implementing `PL-83LS`, from the session-start
digest's `main's quality run #2104 ... concluded failure` line. The
misattribution above was corrected the same evening, from the full job log.

**Where.** `docs/items/PL-4L6Z-*.md`'s `verify:` field.

**Options, not yet decided.** Narrow the command to the one reference test the
item adds, paired with a `grep`, as `.claude/skills/docket/SKILL.md`'s own table
prescribes for a single-behavior item - `tests/reference/` as a whole is the
shape that table reserves for the coverage case. Or record `not-delegable:` and
drop the command. The first looks right and is `PL-4L6Z`'s own author's to
confirm: the test it names does not exist yet, so whoever writes it decides what
proves it.

**Related.** `PL-32Z9` (`PL-D1RT`'s command already passes) is the actual red and
is on another session's branch. `PL-0HPV` (`make check` omits the verify replay)
is why no local run sees either. `PL-FSH9` (no workflow sets `timeout-minutes`)
is the other half of a hung command. `PL-SDHR` measured the replay's cost.

**Why it matters.** One item in the store has a command the sweep can never
evaluate, and it is therefore the one command that cannot be shown to
discriminate: `bin/docket verify` would `ACCEPT` a branch that did none of
`PL-4L6Z`'s work and nothing would say so. That is the failure the `already
passes` error exists to catch, reached from the other direction - by never
running. Every whole-store sweep also spends the full 120s on it and learns
nothing, and the per-command budget has no headroom left: the slowest command
that did finish was 97.2s.

**Done when** `bin/docket check --verify` returns a verdict for `PL-4L6Z` inside
the per-command limit - by narrowing its command to the one reference test the
item adds, paired with a `grep` for that test, which is the shape
`.claude/skills/docket/SKILL.md`'s table prescribes for a single-behaviour item -
or `PL-4L6Z` records `not-delegable:` and carries no command. The first looks
right, and the test it names does not exist yet, so whoever writes it decides
what proves it.

**Dropped at triage, 2026-09-17, as a duplicate of `PL-6YWK`** (project owner).
Both items describe `PL-4L6Z`'s `verify:` being killed at `check --verify`'s
120 s per-command limit; they were filed a day apart by sessions that each found
it from a different direction, which is the re-discovery the capture rule's
`feature:` grouping exists to prevent and which nothing caught here because
neither carried one.

Two measurements in this brief are not in `PL-6YWK` and are cross-referenced
there rather than left to be re-taken: the sweep cost **233.8 s for 164
commands** on run #2104, and the slowest command that *did* complete was
`PL-P1P6` at **97.2 s against the 120 s limit** - which is the evidence that the
budget has no headroom to give, and so that narrowing `PL-4L6Z`'s command is the
only available remedy.
