---
id: PL-B60Q
title: ROADMAP.md's rule that a closed Declined-to-Gate entry carries the release that took it is stated only inside v0.5.0's own subsection, so the release mode never reads it and v0.6.0's first closed deferral will go unmarked exactly as PL-0VFF's three did
status: untriaged
feature: gate-list-integrity
added: 2026-09-22
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
