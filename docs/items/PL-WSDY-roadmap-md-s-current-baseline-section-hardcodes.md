---
id: PL-WSDY
title: "ROADMAP.md's current-baseline section hardcodes 'Gate 1 remains open at 92 of its 121 entries', which the gate section's own convention forbids and which is now wrong twice over"
priority: P3
effort: S
status: done
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-09-08
closed: 2026-09-13
verify: python3 tools/doc_check.py check && ! sed -n '/^## Current baseline/,/^## /p' ROADMAP.md | grep -qE 'Gate [0-9]+ (remains|stands) open at|[0-9]+ of its [0-9]+ entries'
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

**Closed 2026-09-13. The sentence left with the section that held it.** The
offending line was the last paragraph of § "Current baseline: v0.4.10", and the
v0.4.11 cut replaced that whole section with its own (`PL-R3Y3`, #486); v0.4.12
through v0.4.14 rotated it three times more. So the count was not repaired, it
was rotated out - which is the convention working, since the gate section's rule
is precisely that a release narrative should not carry a count that outlives its
release.

**The second half of the done-when was swept and holds.** § "Current baseline:
v0.4.14" is 99 lines and names no gate count at all; no other release narrative
in the file carries one. One live count survives outside the release
narratives - "Gate 1 stands at 132 entries ... with 89 still open", in the
declined-to-Gate-2 argument, now 159 and 94 - and it is *not* fixed here. It is
the recorded arithmetic of a decision taken on 2026-09-08, so whether it should
read as a dated fact or be restated is a judgment about somebody's argument
rather than a stale statistic, which is a decision and therefore an item
(`PL-B8V1`).

**The `verify:` command was replaced before closing, and the reason is
`PL-MMWX`'s.** As written it was `! grep -q '92 of its 121 entries' ROADMAP.md`,
run against the whole file - and the frozen gate list's entry for this item *is
its title*, which contains that phrase. So the command could never pass from the
moment the item was listed, however carefully it was run beforehand: it was
failing on its own name, not on the defect. The replacement scopes the grep to
the current-baseline section and generalises the pattern to what the convention
actually forbids. Confirmed both ways: exit 1 against `42981fb^`, the tree that
still carried the sentence, and exit 0 today.
