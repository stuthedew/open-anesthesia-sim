---
id: PL-DXQC
title: The v0.4.0 Goal section states two problems in the present tense that are now fixed
priority: P2
effort: S
status: needs-decision
classes: docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-09-04
---

**Problem.** `ROADMAP.md`'s "Next milestone: v0.4.0 - the teachable case"
opens with a Goal section listing "three measurable reasons" the model's
lessons are unreachable, in the present tense. Two of the three have since
been fixed and the prose still asserts them:

- The second bullet says the chart is "scaled to the vaporizer's dial
  maximum, so a 1 MAC run occupies the bottom quarter of the plot". `PL-CC23`
  replaced that with a fixed 0-3 MAC axis.
- The third says "every value is a percentage of an atmosphere, so three
  agents whose MACs differ threefold are displayed as though their numbers
  were comparable". `PL-DHV7` added MAC multiples across every readout and
  both chart axes, shipped in v0.3.6.

The first bullet, 1x real-time playback, is still true.

**Why it matters.** A reader cannot tell which sentences are the scoping-time
record and which are current state, and the section reads as current state.
`CLAUDE.md` treats stale documentation as a safety issue rather than
tidiness, and this is the milestone section a session reads to find out what
the interface currently does wrong.

**Decision needed.** Whether a milestone's Goal is a *historical
record* frozen at scoping - in which case it needs a dated marker saying so,
once, and nothing else changes - or a *live description* that each closing
item updates. Both are defensible and the project has not chosen. The
question generalizes: v0.5.0 and every milestone after it will have the same
section with the same problem, so the answer belongs in `ROADMAP.md`'s own
development rules rather than in one edit to one section.

Found while sweeping the docs for `PL-CC23`; `PL-DHV7`'s bullet had already
been stale for two releases, which is the evidence that no convention exists.

**Done when.** `ROADMAP.md` states which of the two a Goal section is, and
the v0.4.0 section conforms to it.
