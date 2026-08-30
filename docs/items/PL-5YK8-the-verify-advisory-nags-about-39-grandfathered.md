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

**Where.** `subprojects/docket/src/docket/checks.py` raises it;
`verify_required_from` in `docket.toml` sets the cutover.

**Done when.** The advisory reports something a session can act on in the
session that sees it, and the store's grandfathered items are either burned
down or recorded as deliberately exempt with the reason.
