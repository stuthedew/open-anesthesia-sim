---
id: PL-2NSX
title: The session-start digest names one Top: item for every session, so two parallel sessions still open on the same id
status: untriaged
added: 2026-09-04
---

**Problem.** `PL-8165` split `docket next` into `product` and `workflow` lanes
so two simultaneous sessions never rank onto the same item. The session-start
digest was left whole, and it is what a session reads *first* — before it would
think to ask for a lane, and before the `docket` skill has loaded. So two
parallel sessions still open on an identical `Top:` line, and the split only
takes effect once somebody remembers to type the lane.

**Why it matters.** The digest is the cheapest possible moment to prevent the
collision, and the one that needs no instruction to be followed. Every guard
downstream of it depends on a session choosing to run something.

**Where.** `subprojects/docket/src/docket/render.py`, `format_digest`, and the
`Top:` line it builds through `recommend`.

The hard part is that the digest cannot know which lane the session is: it is
emitted by a `SessionStart` hook, before anything has been said. Three shapes,
and this is the open question rather than a settled design:

- **Print both lane tops** — `Top (product):` and `Top (workflow):` — so the
  split is visible at startup with nothing to configure. Costs one line in
  every digest, including single-session ones, which is where this project's
  digest budget actually gets spent.
- **Read a lane from the environment**, so a session started for one half can
  be told at launch. Needs a per-session signal the hook can see, and the
  owner has to remember to set it, which is the same failure one step earlier.
- **Leave it whole and say so** — accept that the lane is asked for explicitly,
  and that the digest is a summary rather than an assignment.

**Done when.** Two sessions started for opposite halves of the project do not
read the same recommended id at startup, or the project has recorded that it
accepts them doing so and why.
