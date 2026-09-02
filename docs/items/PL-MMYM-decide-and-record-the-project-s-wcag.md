---
id: PL-MMYM
title: Decide and record the project's WCAG conformance target and which criteria bind
priority: P2
effort: S
status: done
classes: docs, ux
feature: presentation-safety
touches: docs/MODEL.md
added: 2026-09-02
closed: 2026-09-02
pr: 183
verify: python3 tools/doc_check.py check && grep -qF 'The target is WCAG 2.2 Level AA' docs/MODEL.md
---

**Problem.** The project applies WCAG in three places and has never stated what
it is conforming to. `app/theme.py:53-56` says each agent fill/foreground pair
"exceeds WCAG 2.2's 4.5:1 minimum for normal text" and links SC 1.4.3.
`PL-GVXP` (separate the six chart traces by more than colour) holds the traces
to "WCAG's 3:1 minimum for non-text graphical objects", SC 1.4.11.
`ROADMAP.md:1727` parks accessibility generally as Phase 2 item 20. No document
says which version, which level, or which criteria the interface is held to, so
each item re-decides it locally and the three answers agree only by luck.

**Why it matters.** A conformance target is what makes the other items in this
feature checkable rather than negotiable. Without it "meet contrast minima" is
one item's opinion; with it, a session picking a colour has a number to hit and
a reviewer has something to fail the change against. It also decides scope: AA
and AAA differ by nearly 2x on text contrast (4.5:1 vs 7:1), which is the
difference between the current palette passing and most of it failing.

**Decision to make.** Version, level, and the exceptions in both directions.

Recommended: **WCAG 2.2 Level AA as the floor**, plus two named places the
project holds itself higher, and no pursuit of WCAG 3.0.

- *Version.* WCAG 2.2 is the current W3C Recommendation (published 2023-10-05).
  WCAG 3.0 is a Working Draft, last revised 2026-03-03, with a Candidate
  Recommendation anticipated Q4 2027 and Recommendation status not expected
  before 2028. Its scoring model (Bronze/Silver/Gold outcomes) replaces
  pass/fail entirely, so nothing designed against it today is checkable today.
  Target 2.2; revisit when 3.0 reaches CR.
- *Level.* AA. WCAG 2.2 is backward compatible with 2.1, so conforming to 2.2
  AA also satisfies the WCAG 2.1 AA that EN 301 549 and the 2024 ADA Title II
  rule embed, and the WCAG 2.0 AA that Section 508 references. None of those
  instruments binds a solo educational project, so the reason to target AA is
  that it is the right engineering bar for a teaching tool, not a compliance
  obligation - and it is the level `theme.py:53-56` already claims to meet. The
  one criterion 2.2 drops, 4.1.1 Parsing, is moot here: it concerns
  author-written markup, and this interface is drawn to a canvas.
- *Higher than AA, case 1: chart trace discriminability.* WCAG has no criterion
  for how far apart two adjacent data series must be — 1.4.11 only asks 3:1
  against the *background*. For a chart whose entire lesson is reading one
  compartment against another, background contrast is necessary and nowhere
  near sufficient. `PL-GVXP` already asks for pairwise trace-to-trace ratios and
  a non-colour channel; that is the right bar and AA does not supply it.
- *Higher than AA, case 2: colour is never the sole channel.* SC 1.4.1 (Level A)
  already requires this, but the project's ISO 5360 reasoning in
  `theme.py:30-37` is stronger — displaying a colour obligates displaying the
  *right* one — and that reasoning should be the stated rule, not 1.4.1's floor.
- *Explicitly out of scope for now.* The criteria that need a settled interface
  before they can be answered: 2.4.11 Focus Not Obscured, 2.5.8 Target Size,
  1.4.10 Reflow, 1.4.12 Text Spacing. Name them as deferred rather than leaving
  them unlisted, so the deferral is visible.

**Where.** `docs/MODEL.md` already carries the agent-colour contrast analysis
(around `:1126-1135`) and is the natural home for the target statement.
`README.md` if the claim should be user-facing. `ROADMAP.md:1727` (item 20)
should point at whatever this decides rather than restating it.

**Done when.** One document states the version, the level, the two
higher-than-AA cases, and the deferred criteria; `theme.py` and `PL-GVXP` cite
it rather than each naming a number; and `ROADMAP.md` item 20 references it.

**Blocks.** `PL-1MK1` (compute contrast ratios in `make check`) and `PL-HC9P`
(make the target fire when a session picks a colour) both need the number this
decides. Neither is blocked on the *whole* decision — the AA floor is enough to
start either — but the higher-than-AA cases change what the checker asserts.
