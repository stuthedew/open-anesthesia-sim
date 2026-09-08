---
id: PL-WSDY
title: "ROADMAP.md's current-baseline section hardcodes 'Gate 1 remains open at 92 of its 121 entries', which the gate section's own convention forbids and which is now wrong twice over"
priority: P3
effort: S
status: ready
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && ! grep -q '92 of its 121 entries' ROADMAP.md
---

**Problem.** `ROADMAP.md` § "Current baseline: v0.4.10" ends with "Gate 1
remains open at 92 of its 121 entries, so v0.5.0 - the case you can branch - is
still behind it." Both numbers are wrong: the list stands at 132 entries (the
timeline's own v0.5.0 row says so) with 89 open as of 2026-09-08.

It is wrong by construction rather than by accident. The gate section states
the convention the sentence breaks, in terms: "How many are *closed* is
deliberately not recorded here, for the reason the v0.4.0 section gives: a
count written into a document goes stale the next time an item closes.
`bin/docket wave` reads these against `docs/items/` and reports the split."

**Why it matters.** It is the only place in the file that states the gate's
size and progress together, so it is what a reader sizing the remaining work
would take the numbers from — and it understates the list by eleven entries
while overstating what is left to do. `PL-KTKP` closed on the same file for the
same reason: a count that is right about the document and wrong about the
project.

**Where.** `ROADMAP.md` § "Current baseline: v0.4.10", the final paragraph of
"What this release does not do".

**Done when.** The sentence states that Gate 1 is still open and that v0.5.0 is
behind it, without a count — the shape the gate section's own convention asks
for — and no other release narrative in the file carries a live gate count.
