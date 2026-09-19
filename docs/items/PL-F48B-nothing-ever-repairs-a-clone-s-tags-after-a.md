---
id: PL-F48B
title: Nothing ever repairs a clone's tags after a history rewrite: fetch_remote runs git fetch without --tags --force, so release tags keep pointing at purged commits
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.28
touches: subprojects/docket/src/docket/vcs.py, .claude/hooks/docket-digest.sh
added: 2026-09-06
closed: 2026-09-19
pr: 685
not-delegable: The deliverable this item's own "Done when" permits is a recorded decision not to automate, which no command can prove right. The measurement behind it is reproducible - every local tag reachable from origin/main, every tag object identical to the remote - but it describes the checkout a session happens to be in rather than the tree, so it cannot be pinned as a test.
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

**Closed 2026-09-19 under `PL-4Q9B`** (record clone trust and the permitted ref
operations), by the second disposition this item's "Done when" offers: the
decision not to refresh tags automatically, recorded with its reasoning (project owner, 2026-09-19, ratified),
chosen over forcing tags in `vcs.fetch_remote` or in the session-start hook.

**Measured 2026-09-19 in this container.** All 54 tags are reachable from
`origin/main`, and every local tag object is byte-identical to the remote's. So
the condition - a clone holding tags that point into purged history - is not
present here, and nothing in the current tree is producing a wrong answer or
holding bytes it should not.

**Why not `fetch_remote`.** It is the one fetch every command runs, so forcing
tags there moves a session's local tags without asking, on every invocation, to
repair a condition that arises only after a history rewrite. That is a standing
cost against a rare event, and it would also silently discard a tag a session
created locally - which is how `PL-PNW6`'s warm-checkout case gets *worse*
rather than better.

**Why not the session-start hook either.** It is the better of the two - once
per container, already running a conditional `--unshallow` - but it pays a
network round-trip in every session for the same rare event, and the repair it
would perform is one `bin/docket branch` already prints, at the only moment
anybody is looking: on a branch whose history has been rewritten. A check that
fires every run without changing a decision is what `CLAUDE.md` asks to be
retired, not added.

**What reopens this.** A second history rewrite, or any measurement showing a
tag in a working checkout pointing outside `origin/main`'s history. The command
is in the paragraph above and takes seconds; the two prose lines `PL-YGF3` added
remain the remedy.
