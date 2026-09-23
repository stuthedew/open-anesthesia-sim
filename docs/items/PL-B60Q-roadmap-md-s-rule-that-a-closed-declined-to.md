---
id: PL-B60Q
title: ROADMAP.md's rule that a closed Declined-to-Gate entry carries the release that took it is stated only inside v0.5.0's own subsection, so the release mode never reads it and v0.6.0's first closed deferral will go unmarked exactly as PL-0VFF's three did
priority: P2
effort: S
status: done
classes: defect, infra
feature: gate-list-integrity
milestone: v0.5.7
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/README.md, ROADMAP.md
blocked-by: PL-J6HP
added: 2026-09-22
closed: 2026-09-23
pr: 937
payoff: a Declined-to-Gate entry that has shipped stops reading as outstanding debt, so v0.6.0's deferral list stays true as its entries close
verify: grep -q 'def test_wave_prints_each_deferral_with_its_state_and_release' subprojects/docket/tests/test_roadmap.py
---

**Problem.** ROADMAP.md's rule that a closed Declined-to-Gate entry carries the release that took it is stated only inside v0.5.0's own subsection, so the release mode never reads it and v0.6.0's first closed deferral will go unmarked exactly as PL-0VFF's three did

**Found 2026-09-22 while closing `PL-Z891`**, which is the first entry in
v0.6.0's `### Declined to Gate 2, because every one was captured after this
list was frozen` to close, so the convention applies there for the first time
and there is nothing to apply it.

**The rule.** `ROADMAP.md` § "Declined to Gate 2 on the refilling-queue ground"
(v0.5.0) states it: "A closed entry carries the release that took it, and the
open count is not recorded here" (`PL-0VFF`) - a release name for one that
shipped, the date for one dropped. No entry is ever removed, because the
permanence is what "the gate is a snapshot" means, so the mark is the only
thing separating an outstanding entry from a shipped one.

**Where it is not.** Nothing carries it to the moment it fires. Measured
2026-09-22: `.claude/skills/docket/modes/release.md` contains none of
`Declined`, `deferr`, `closed in v` or `snapshot`; no script under `tools/` or
`subprojects/docket/src/docket/` writes or reads the mark; and the rule's own
text sits inside a v0.5.0 subsection a release session has no reason to open.
So the rule is enforced by a session happening to have read the paragraph that
states it, which is how `PL-0VFF`'s three unmarked entries happened in the
first place.

**Why it matters.** The failure is the one `PL-0VFF` already paid for and is
silent: an entry listed as deferred that shipped two releases ago reads as
outstanding, and the heading's total then overstates the deferral by however
many have closed. A reader cannot tell without going to the queue for every id,
which is the lookup the mark exists to remove.

**Done when** the rule reaches the moment it fires. The cheapest sufficient
tier decides the shape rather than this brief: a line in the release mode's
close-out is one answer; a `doc_check` advisory naming deferral entries whose
ids are closed and unmarked is the deterministic one, and it is decidable -
the ids are in the subsection, their statuses are in the store, and the mark
is a literal. Whichever lands, `PL-Z891` is the entry waiting for it.

**Premise re-read 2026-09-22 (`PL-14QR`, triage).** `PL-Z891` is `done`. Its entry at
`ROADMAP.md` line 5704 still reads `**deferred 2026-09-21.**` with no release
beside it. `release.md` matches none of `Declined`, `deferr`, `closed in v` or
`snapshot`. **Triage chose the `doc_check` route** for the `verify:` below. The
brief shows the rule is decidable, and `CLAUDE.md` gives deterministic tooling
standing approval over a prose line a release session would have to remember.
`PL-Z891` then shipped in v0.5.4 (`#903`, merged while this pass was open).
Its entry is still unmarked, so the check's first finding already exists.

**Blocked 2026-09-23 on `PL-J6HP`'s decision, which re-scopes this item.** The
mark this item asks a check to enforce copies a field the store already holds.
Across v0.5.0's refilling-queue list and v0.6.0's two deferral subsections, 82
entries have closed. The 48 that carry a mark all equal the item's `milestone:`
field, and 34 carry none. The re-scope recommended there is to have `bin/docket
wave` print each deferral's state and release from the store, and to drop the
rule that asks for a hand-written mark. The check as filed would instead demand
34 hand edits at once, and more on every release after. It is blocked rather
than left `ready` so that no session builds the filed form while the decision
is open. The re-scope is the same under either route `PL-J6HP` weighs.

**Re-scoped 2026-09-23 by `PL-J6HP`'s decision** (project owner, ratified, over
the doc_check advisory triage chose). This item is built on `PL-J6HP`'s branch
and closes with it. `bin/docket wave` prints each current-gate deferral's state
and release from the store, and v0.5.0's marking rule becomes a pointer to that
output. No check that demands a hand-written mark is built. The `verify:` above
belongs to the filed form, and that build rewrites it. The item stays blocked on
`PL-J6HP`, so that no session starts it on its own.


**Built and closed 2026-09-23 with `PL-J6HP`, in the re-scoped form.**
`bin/docket wave` prints a `Deferred` block for the current gate: each deferral
entry's leading ids, grouped as open (with the item's status), shipped (with
its `milestone:`), done but not yet released, dropped (with its `closed:` date)
and not in the store. v0.5.0's marking rule is now a pointer to that output,
and `ROADMAP.md` § "Recording it" says not to write the mark. Re-counted before
retiring it: all 48 marks written equal a store field (38 a `milestone:`, 10 a
drop date equal to `closed:`), and 36 of the 84 closed entries carried none.
The `verify:` now names
`test_wave_prints_each_deferral_with_its_state_and_release`, which the filed
form's `test_a_closed_declined_entry_without_its_release_is_reported` replaced,
since no check demanding a hand-written mark was built.
