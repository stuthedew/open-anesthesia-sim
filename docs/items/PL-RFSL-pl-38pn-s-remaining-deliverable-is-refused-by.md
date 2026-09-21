---
id: PL-RFSL
title: PL-38PN's remaining deliverable is refused by .claude/rules/citation-drift.md's closed-brief clause: both briefs it repoints (PL-VM40, PL-L2F2) closed done on 2026-09-04 and 2026-09-07, and its 2026-09-19 still-real sweep note predates PL-G424's ratified rule by 80 minutes
priority: P2
effort: S
status: done
classes: docs
feature: closed-item-claims
touches: docs/items
added: 2026-09-20
closed: 2026-09-21
payoff: PL-38PN stops being offered as startable work whose whole deliverable a ratified rule already refuses
verify: grep -qF 'citation-drift' docs/items/PL-38PN-stale-source-line-citations-in-pl-vm40-and-pl.md
---

**Problem.** PL-38PN's remaining deliverable is refused by .claude/rules/citation-drift.md's closed-brief clause: both briefs it repoints (PL-VM40, PL-L2F2) closed done on 2026-09-04 and 2026-09-07, and its 2026-09-19 still-real sweep note predates PL-G424's ratified rule by 80 minutes

**Found by `PL-JKML`'s duplicate sweep, 2026-09-20**, as a by-product: the pair
`PL-38PN`/`PL-JXVD` was judged complementary and then refuted on review, and
the refutation turned on this rather than on the pairing.

**The evidence, as the reviewer laid it out.** `PL-38PN`'s entire remaining
deliverable is correcting `line 943` in `PL-VM40` and `:24`/`:63` in `PL-L2F2`.
Both of those items are `status: done` - closed 2026-09-04 and 2026-09-07 - and
the stale strings are still in place. `.claude/rules/citation-drift.md`, which
`PL-G424` landed under `#725` and which the project owner ratified 2026-09-19,
says: drift in a `done` or `dropped` brief "is **not a finding**: do not repair
it, do not file an item about it, and do not count it when sizing a cluster."

**The timing is what makes this worth an item rather than a reading.**
`PL-38PN` carries a 2026-09-19 sweep note declaring the remainder still real.
That note is commit `8845c09d` at 14:53:22 (`#719`); the rule that voids it is
`074722b4` at 16:13:37 (`#725`), the same day, eighty minutes later. So the
item's own most recent evidence of being live predates the decision that
retires it, and nothing in the store says so - which is exactly the shape a
staleness sweep is built to catch and this one was not run against.

**A second finding sits inside it, and it is not about citations.**
`PL-38PN`'s `verify:` is `! grep -q 'line 943' ...`, which goes green the
moment the original number disappears whatever replaces it - including a fresh
wrong number. That is a false-pass command rather than a citation problem, so
it survives whatever is decided about the first half.

**Done when** `PL-38PN` is either dropped with `.claude/rules/citation-drift.md`'s
closed-brief clause as the reason, or its brief records why the clause does not
reach it - and its `verify:` is repointed either way, since a command that
cannot fail once the string moves proves nothing about the item.

**Why it matters.** `PL-38PN` is `status: ready`, so `bin/docket next` can
offer it, and the work it would hand over is refused by a ratified rule the
session taking it has no reason to read. The cost is a whole item's work
discovering that the item is void - and the store says nothing, because
`PL-38PN`'s own most recent evidence of being live is eighty minutes older than
the decision that retires it. That is the silent-wrong-answer shape
`CLAUDE.md` names first among its compounding-friction tests, arriving through
a timestamp rather than through a check.

**Verified 2026-09-20.** `PL-38PN` is `status: ready`, `classes: docs`, and its
`touches` names exactly the two item files it would repair: `PL-VM40` and
`PL-L2F2`, both `status: done`.

**Done when.** `PL-38PN` is either dropped with
`.claude/rules/citation-drift.md`'s closed-brief clause as the recorded reason,
or its brief records why that clause does not reach it - and its `verify:` is
repointed either way, since `! grep -q 'line 943'` goes green the moment the
number moves whatever replaces it.

**Delivered by `PL-PT7M`'s re-judging pass, 2026-09-21.** `PL-38PN` is
`status: dropped`, `closed: 2026-09-21`, with
`.claude/rules/citation-drift.md`'s closed-brief clause quoted in its `reason:`
alongside the two `done` items it would have repointed - which is the first of
the two endings this brief offers.

**The `verify:` half is moot rather than skipped, and the reason is this
brief's own.** It asked for the command to be repointed "either way, since the
item is open". The item is no longer open: `bin/docket check` replays a stored
command only under `--verify`, which nothing passes, and `bin/docket verify`
prints an exemption for a `dropped` item rather than running its command
(`PL-L4KX`). So the false-pass command can no longer pass anything, and
rewriting it would be an edit to a closed brief - which is the clause this
item's own case rests on.

