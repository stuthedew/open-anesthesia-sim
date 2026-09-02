---
id: PL-QTSB
title: A grooming advisory hands a session an item to edit with no in-flight check, which is the PL-5KR2 gap on a third surface
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, .claude/skills/docket/SKILL.md
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_advisory_names_an_item_in_flight' subprojects/docket/tests/test_checks.py
---

**Problem.** `PL-5KR2` found that `plan.recommend` excludes in-flight ids, but
only `docket next` reads it — so the project owner naming an item skipped the
guard entirely. The fix routed the answer into `show` and later `triage`. A
third surface was missed: a **grooming advisory** names an item and tells a
session to edit it, and nothing on that path checks whether another session is
already doing so.

**Observed 2026-09-02, and this session caused it.** `docket check` on `main`
raised "`PL-2XTF`: marked done on `origin/main` and records no `pr`, but #227
is recoverable from its merge commit; write `pr: 227` into the item". This
session read that, wrote the line, and opened `#230`. Another session read the
same advisory, computed the same answer, and opened `#229` — one file, one
insertion, the identical `pr: 227`.

The guard was never run, by either session. Not skipped in error: the
advisory is not the "start an item" path, and nothing about reading a
`docket check` line suggests that a check meant for starting work applies.
`#229` merged first, `#230` merged after, and git auto-merged them because the
content was byte-identical.

**Why it matters.** Harmless here, and that is the whole reason to record it.
The advisory-driven edit is the *most* deterministic work this project has:
`docket check` computes it, names the item, and states the exact line to
write. Every session that runs `make check` gets the same instruction, so the
collision rate approaches one whenever two sessions are open, and the outcome
happens to be idempotent only because the tool dictated the content. An
advisory whose fix required any judgment — a `verify:` command to write, a
`touches` to fill, an item to reprioritize — would have produced two different
answers to merge.

This is also the case `PL-MC8Z` (the start-an-item guard never asks the
file-overlap question) would not have caught, because neither session was
"starting an item", and `PL-D4MZ`'s reservation-at-recommendation-time would
not have caught either: the recommendation came from a tool both sessions ran
locally, not from a reply anyone could have reserved against.

**Where.** `.claude/skills/docket/SKILL.md`. Two candidate shapes, and the
second is probably right:

- Tell the skill that acting on an advisory is starting work, and run the
  guard. Correct, and asks a session to remember a rule at the one moment it
  has been handed something that looks like a chore rather than an item.
- Have `docket check` mark an advisory whose item is in flight, the way
  `show` and `triage` already mark one. The answer is already computed —
  `checks.py` receives the flight report for `_offered` — so this is wiring
  rather than a new read, and it fires without anyone remembering anything.
  `PL-3576` already established that `check` reads that report and must say
  when it is partial.

**Done when.** A session told by `docket check` to edit an item can tell
whether another branch is already editing it, without having to know that a
guard documented elsewhere applies.

**Confirmed from the other side, minutes later.** `docket check` then raised
the same advisory for `PL-D1ST` (`write pr: 231`). This session ran the guard
before acting — `git fetch origin` then `bin/docket show PL-D1ST` — and got
`IN FLIGHT on a branch - do not start PL-D1ST again`. Another session was
already on it, and the backfill was not done.

So both halves are measured rather than argued. Unguarded, the advisory
produced a duplicate (`#229` and `#230`); guarded, it prevented one. Nothing
about the advisory itself changed between the two, which is the case for
moving the answer into `docket check` rather than into a rule a session has to
remember: the information was available both times and only reached the second
attempt because a session happened to think of it.

It also settles the shape. `show` already computes this answer, so the second
option under **Where** is wiring an existing read into an existing output, and
the marked advisory would read the way `triage`'s already does.
