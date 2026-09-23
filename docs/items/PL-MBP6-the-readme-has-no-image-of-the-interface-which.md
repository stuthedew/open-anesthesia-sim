---
id: PL-MBP6
title: The README has no image of the interface, which is the largest remaining gap for both of its audiences
priority: P2
effort: M
status: ready
classes: docs, ux
feature: project-introduction
touches: README.md, assets/branding
blocked-by: PL-YCWZ
added: 2026-09-06
payoff: gives a clinician deciding whether to put this in front of a resident a picture of the interface, which is the whole of what they can see while there is no packaged build
verify: grep -qF '](assets/' README.md
---

**Problem.** `README.md` describes the interface in prose - the readouts, the
two units, the chart, the wash-in panel, the control marks - and shows none of
it. `assets/branding/` holds only a `.gitkeep`.

**Why it matters.** Both of `PL-RM83`'s audiences are answering a question a
picture answers faster than a paragraph. Audience B, the clinician-user, is
deciding whether this is a teaching tool they would put in front of a resident,
and cannot run it at all today - there is no packaged build - so the README is
the *whole* of what they get. Audience A, the contributor, is deciding whether
the interface is worth extending. A screenshot is the single highest-value
addition left to the document, and it is the one thing prose cannot substitute
for.

It also carries a safety-adjacent load that the prose currently carries alone.
`docs/MODEL.md` § "Interface boundary" requires the playback rate on screen
wherever simulated time is, and requires the agent identified by name and ISO
5360 colour; an image showing both is a stronger statement that the display
conventions are real than a sentence asserting them.

**Where.** `README.md`, between § "What it simulates" and its diagram or
immediately after the opening; `assets/branding/`, or a new `assets/` path for
screenshots.

**Two things to decide, and they are not the same question.**

1. *How the image is produced.* `PL-7J96` (make the interface renderable in a
   check so a session can look at it) is the means: its option 1 is a
   `make screenshot` target that serves the app and captures it at the
   breakpoint widths. That item is about a tooling gate; this one is about the
   README, and this one should wait for it rather than grow a second
   screenshot mechanism.
2. *What the image must show, and what it must not.* A screenshot is a
   displayed clinical value under `CLAUDE.md`'s standard, frozen and shipped:
   whatever agent, rate and settings it captures will be read as
   representative. It has to show the agent name, the 1 MAC divisor and the
   playback rate, and it must not be cropped in a way that separates a number
   from its units or its model identity. A stale screenshot is worse than
   none - it asserts a display that no longer exists - so it needs a stated
   rule for when it is retaken.

**Done when.** The README carries at least one current image of the running
interface, with alt text that says what is being shown, and the project has
recorded how it was produced and when it is retaken.

**Notes.** Found 2026-09-06 while writing the README under `PL-N092`. Not done
there: producing a screenshot needs the app rendered, which is `PL-7J96`'s
open decision, and the item was the document rather than the tooling under it.

[superseded 2026-09-15: `PL-YCWZ` is done; promoted to `ready` below]
**Blocked on `PL-YCWZ`** (headless rendering tests over the real Qt interface),
re-pointed 2026-09-13 when `PL-7J96` was dropped as superseded by it. The
reasoning is unchanged: producing the image needs the app rendered, and growing a
second screenshot mechanism here is the outcome this brief refuses.

[superseded 2026-09-20: the port has landed; promoted to `ready` below]
**What the re-point changes, and it is not nothing.** `PL-7J96` would have
rendered the *shipped* Flet interface, so this item could have been worked before
the port. `PL-YCWZ` renders Qt, and a README image is - by this brief's own
paragraph 2 - a displayed clinical value that "will be read as representative",
so a Qt screenshot cannot ship while the built interface is Flet without
asserting a display that does not exist yet. In effect this item now waits for
the Qt port to *land*, not merely for `PL-YCWZ` to be built.

**One route does not wait, and is not taken here.** This item's "Done when" asks
that "the project has recorded how it was produced and when it is retaken" - not
that a tool produced it. The project owner can run `make run` and capture the
shipped interface by hand today, which satisfies that wording and needs no
mechanism. That is a live option for the owner rather than a decision this
re-point takes: `PL-2QMK` records that no session in the web container can render
Flet at all, so no session can do it for them.

## Promoted 2026-09-20 under `PL-JFQ3`: the re-point's own objection has lapsed

**`PL-YCWZ` is `done`** (`2026-09-15`, `pr: 588`), so headless rendering over
the real Qt interface exists and decision 1 — how the image is produced — is
answered by it rather than by a second mechanism.

**The re-point's remaining objection no longer holds.** It said "this item now
waits for the Qt port to *land*, not merely for `PL-YCWZ` to be built", because
"a Qt screenshot cannot ship while the built interface is Flet without asserting
a display that does not exist yet". The port has landed. Checked 2026-09-20:
`pyproject.toml`'s dependency list is `PySide6-Essentials` and `pyqtgraph` with
no `flet`, `grep -rn flet src/` returns nothing, and
`tools/import_boundary_check.py` permits `flet` and `flet_charts` in no module
under `src/` at all. Qt *is* the shipped interface, so a Qt screenshot is the
honest one.

**The route this brief left open for the project owner is also no longer the
only one.** It noted that `PL-2QMK` records no session in the web container
being able to render Flet, so a hand capture was the owner's alone. That was a
fact about Flet; `PL-YCWZ`'s headless Qt rendering is what changes it.

**One stale line, corrected here rather than left to mislead.** The brief says
"`assets/branding/` holds only a `.gitkeep`". There is no `assets/` directory in
the tree at all as of 2026-09-20. Paragraph 2's requirements are unaffected —
the image still has to show the agent name, the 1 MAC divisor and the playback
rate, uncropped — and the `verify:` now recorded pins the README referencing an
image under `assets/`, which is the path this brief names.
