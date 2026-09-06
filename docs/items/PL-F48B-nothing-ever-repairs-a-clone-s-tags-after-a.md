---
id: PL-F48B
title: Nothing ever repairs a clone's tags after a history rewrite: fetch_remote runs git fetch without --tags --force, so release tags keep pointing at purged commits
priority: P3
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, .claude/hooks/docket-digest.sh
added: 2026-09-06
---

**Problem.** `vcs.fetch_remote` runs `git fetch --quiet origin`, which will not
move a tag the clone already has. After a history rewrite the release tags keep
pointing at pre-rewrite commits, so the purged content stays reachable in every
clone that held the tags before - `git log --all` is what shows it. Observed
2026-09-06 across `v0.3.7` to `v0.4.4`, with the remote already clean
(`PL-YGF3`).

**Why it matters.** A history rewrite done to remove publisher-copyright
material is not finished in the clones that held the tags: the purged commits
stay reachable through `v0.3.7` to `v0.4.4` in any checkout that fetched them
before the force-push, and `git log --all` is the only thing that says so.
Nothing computes a wrong answer from it, so the cost is not a wrong value - it
is that a removal believed complete is not, and that the repair now lives in
two prose lines which fire only where somebody is already looking at the right
branch.

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

**Decision needed.** Should anything force tags across automatically, and
where? `vcs.fetch_remote` is the natural place and the one fetch every command
runs, so forcing there moves local tags without asking; the session-start hook
is the other candidate, already running a conditional `--unshallow` once per
container. Against both: a clone whose tags are stale produces no wrong answer,
only holds bytes it should not, so the two prose lines `PL-YGF3` added may be
the whole answer this deserves.
