---
id: PL-L1D3
title: docs/WORKING_NOTES.md says PL-NGF7 is deferred to the Qt port, which dissolves it, and that its expected disposition is dropped, but PL-NGF7 closed done in v0.4.26 having measured that premise and found it false
priority: P3
effort: S
status: ready
classes: docs
feature: closed-item-claims
touches: docs/WORKING_NOTES.md
added: 2026-09-20
payoff: the UI-structure thread records what PL-NGF7 measured and shipped, rather than the prediction it disproved, so no session concludes a live check does not exist
verify: grep -qF 'check_disabled_states_are_the_style_s' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md says PL-NGF7 is deferred to the Qt port, which dissolves it, and that its expected disposition is dropped, but PL-NGF7 closed done in v0.4.26 having measured that premise and found it false

**Found 2026-09-20 while closing `PL-KF0T`** (item 33's structural-half
paragraph), which cited `docs/WORKING_NOTES.md` as already recording the three
dispositions correctly. Two of the three it does; this one it does not.

**Where.** `docs/WORKING_NOTES.md` § "Shelved, then resumed: UI structure/form
mockups", the sentence beginning "Of the three named above" - and the earlier
one in the same thread listing the three in the present tense (`PL-2CS8`
consolidates, `PL-NGF7` decides, `PL-B9PY` is the seam), all three of which are
closed.

**Why it matters.** It is a prediction that reads as a record. `PL-NGF7`'s own
item is headed *"Measured 2026-09-16: the port does not dissolve this, and the
deferral's premise is false"*, and it closed `done` in `v0.4.26` having scoped
what the stylesheet owns and added
`check_disabled_states_are_the_style_s`, which fails the build when a module
under `app/` writes a colour outside that scope. A session reading the note
would conclude the check does not exist and that the item is awaiting a drop.

`PL-KF0T` could not fix it: its `touches` is `ROADMAP.md`, and `CLAUDE.md`'s
fix-now test 2 refuses a file outside the current item's declared set. The
ROADMAP half was corrected there and does not repeat this claim.

**Done when.** The thread states what `PL-NGF7` actually did and in which
release, rather than what its deferral predicted, and the present-tense listing
of the three says they are closed.

