---
id: PL-W7WL
title: bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it
priority: P2
effort: S
status: ready
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-20
payoff: stops an item that merged just before a cut shipping a release note with no route back to the change that made it
verify: grep -q 'def test_a_cut_backfills_a_pull_request_number' subprojects/docket/tests/test_release.py
---

**Problem.** bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it

**Observed 2026-09-20, cutting v0.4.32 (`PL-V3GD`).** `PL-TGFY` merged as #745
minutes before the cut, so it carried no `pr:` when `make release
VERSION=0.4.32` generated `docs/releases/v0.4.32.md`. Its notes line shipped as

```
- PL-TGFY PL-Z34C is a frozen gate entry ... so the gate holds an entry nothing can clear
```

while its five siblings all carry `— #742`, `— #743`, `— #739`, `— #740` and
`— #744`. `bin/docket record` then wrote `pr: 745` onto the item correctly, but
the notes were already on disk and `bin/docket release --dry-run` answers
`Nothing to release: no finished work since 0.4.32`, so there is no supported
way to regenerate them. The line was corrected by hand on that branch.

**The documented procedure is what produces it.** The `docket` skill's release
mode, and `PL-V3GD`'s own brief, both order the steps `make release` first and
`bin/docket record` second. That order is right for everything else — `record`
wants the merge on the base — but it guarantees this outcome for any item that
merged between the previous cut and this one without its number being
backfilled first.

**Why it matters.** The notes are the permanent record of what shipped where,
and `pr:` is how a reader gets from a released item back to the change that
made it. A missing number is not wrong, but it is unrecoverable through the
tool: the one command that would rewrite the line refuses, correctly, because
re-cutting a shipped release is what leaves two sets of notes disagreeing about
the same items (`PL-1MKQ`'s territory).

**Two candidate fixes, and the cheap one looks right.** Either `bin/docket
release` runs the same backfill `bin/docket record` does before it writes the
notes — it already fetches, so the information is in hand — or the documented
order is swapped so `record` runs first. The first is better: it removes the
failure rather than asking every future cut to remember, which is `CLAUDE.md`'s
preference for deterministic tooling over a rule a session has to hold.

**Done when.** A cut whose finished set includes an item that merged without a
`pr:` still writes that item's pull request number into the release notes, with
a test driving that case.

**This mechanism has now been filed four times, and the other three are closed
into this one** (`PL-JKML`'s duplicate sweep, 2026-09-20). `PL-66X4` was
dropped into `PL-2M5T` before this item existed; `PL-2M5T` and `PL-3HMQ` are
dropped here. Four sessions diagnosed one defect from four cuts, none of them
able to see the others, which is the cost `PL-TZ7T` names for `bin/docket new`
filing a near-duplicate without noticing. The evidence each of them paid for is
carried below rather than lost with the item.

**How much of a release it takes, from `PL-2M5T` (measured 2026-09-14).**
`docs/releases/v0.4.22.md` carries fifteen item bullets and **nine of them name
no pull request at all**. So this is not an edge case that catches the
occasional late merge: it took the majority of one release's notes, and the
items it takes are systematically the most recently finished - the ones a
reader is most likely to be looking up.

**Two more releases, from `PL-3HMQ` (2026-09-20).** `v0.4.33` shipped without
`PL-LPLD`'s `#758`, and `v0.4.34` would have lost three more had they not been
caught by hand at the cut.

**The second half `PL-2M5T` carried, and it is a decision rather than code.**
A cut release's notes are never regenerated - `bin/docket release --dry-run`
answers `Nothing to release` once the version is cut, correctly, because
re-cutting a shipped release is what leaves two sets of notes disagreeing
(`PL-1MKQ`'s territory). So the numbers already missing from `v0.4.22`,
`v0.4.32` and `v0.4.33` do not come back when this is fixed. Either those files
are repaired by hand as part of this item, or the item records why a shipped
release's notes are left standing as they were published. Decide it here; do
not leave it to be rediscovered a fifth time.
