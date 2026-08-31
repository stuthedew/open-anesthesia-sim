---
id: PL-5YK8
title: The `verify:` advisory nags about 39 grandfathered items, so it can never reach zero
priority: P2
effort: S
status: needs-decision
classes: infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, docket.toml, .claude/skills/docket/SKILL.md
added: 2026-08-30
---

**Problem.** `docket check` raises one grooming advisory on every run: 39
`ready` items predate `verify_required_from` (2026-08-30) and name no command
that would prove them done. The advisory is correct and cannot be discharged
by anything short of writing 39 commands, so every session sees it, and the
count moves only when an unrelated item happens to close.

**Why it matters.** `docket.toml` records the intent — "Moving this date
earlier is how the backlog is closed out; it is a burn-down, not a permanent
exemption" — but nothing burns it down, and an advisory that cannot reach zero
is one every session learns to skim. The cost of that is not the 39: it is the
next advisory, which will be read the same way. `docket check`'s advisories
are the only channel grooming has.

**Decision needed.** Three dispositions, and they are not equally good:

- **Backfill all 39.** A session of judgment producing no product change, and
  most of the commands would be written for items nobody has picked up — the
  exact case where "run the command before you write it down" is hardest to
  honour, because there is no work in flight to run it against.
- **Grandfather them and narrow the advisory** to the items `docket next`
  would actually offer, so it reports what a session is about to trip over
  rather than the whole backlog. Recommended: a `verify:` belongs to scoping
  an item at the moment it is started, which is where the skill's triage mode
  already puts it.
- **Drop the advisory** and rely on the per-item error at `ready`. Cheapest,
  and loses the only signal that the backlog exists.

**Decided 2026-08-31 (project owner): narrow it, and carry the count.** The
second disposition, with the addition that the message states how many remain,
which answers the only real cost of narrowing - losing sight of the size of the
set. The advisory now fires only when an item `docket next` is about to offer
names no command, so on a normal day there is none at all.

Backfilling was rejected on correctness rather than cost. The skill's own rule
is to run the command before writing it, and an item nobody has started offers
nothing to run it against; all six commands this store ever carried that were
written that way were wrong. Backfilling 39 would convert a known gap - "no
command names this" - into 39 false claims that fail only after a worker has
done the work. Dropping the advisory was rejected because it would make
grandfathering permanent by default while `docket.toml` still recorded it as a
burn-down.

Two facts that made the decision easier, measured on the day: the set is closed
and can only shrink, since the test is the capture date and all 39 were
captured between 2026-08-23 and 2026-08-26; and 6 of the 12 open v0.2.8 gate
entries are in it, so clearing the gate drains a sixth of it as a side effect.

**Where.** `subprojects/docket/src/docket/checks.py` raises it;
`verify_required_from` in `docket.toml` sets the cutover; `_offered` in
`cli.py` supplies the ranking to the three commands that show advisories.

**Done when.** The advisory names only the grandfathered items `docket next`
is about to offer, states how many remain, and is silent when those items name
a command - so it can reach zero on a normal day; `check`, `digest` and `next`
agree on it, none of them reporting a count another would contradict; and
`docket.toml` records the burn-down as happening at the moment an item is
started rather than by moving the cutover date.
