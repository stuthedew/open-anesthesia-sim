---
id: PL-F48B
title: Nothing ever repairs a clone's tags after a history rewrite: fetch_remote runs git fetch without --tags --force, so release tags keep pointing at purged commits
status: untriaged
added: 2026-09-06
---

**Problem.** Nothing ever repairs a clone's tags after a history rewrite: fetch_remote runs git fetch without --tags --force, so release tags keep pointing at purged commits

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `vcs.fetch_remote` runs `git fetch --quiet origin`, which will not
move a tag the clone already has. After a history rewrite the release tags keep
pointing at pre-rewrite commits, so the purged content stays reachable in every
clone that held the tags before - `git log --all` is what shows it. Observed
2026-09-06 across `v0.3.7` to `v0.4.4`, with the remote already clean
(`PL-YGF3`).

**What exists now.** `PL-YGF3` put `git fetch --tags --force origin` into the
rewrite-recovery block `docket branch` prints, and into the `docket` skill's
ref-clearing recipe. Both are prose a reader has to act on, and both fire only
where somebody is already looking at the right branch.

**The decision.** Whether anything should force tags across automatically, and
where. `fetch_remote` is the natural place and is also the wrong one if a
forced tag update is ever unwanted - it is the one fetch every command runs,
and forcing tags there moves local tags without asking. The session-start hook
is the other candidate: it already runs a conditional `--unshallow`, and it
runs once per container. Against both: a clone whose tags are stale is not
producing wrong answers, only holding bytes it should not, so this may be worth
nothing more than the two prose lines it already has.

**Done when.** Either something refreshes tags where a rewrite has happened, or
the decision not to is recorded here with its reasoning.
