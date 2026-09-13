---
id: PL-DXQC
title: The v0.4.0 Goal section states two problems in the present tense that are now fixed
priority: P2
effort: S
status: done
classes: docs
feature: planning-cadence
milestone: v0.4.18
touches: ROADMAP.md
added: 2026-09-04
closed: 2026-09-13
pr: 524
verify: python3 -c "import pathlib; t=' '.join(pathlib.Path('ROADMAP.md').read_text().split()); raise SystemExit(0 if 'Goal is frozen at scoping and dated there' in t else 1)"
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

**Decision needed — ANSWERED 2026-09-13, see below.** Whether a milestone's Goal is a *historical
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

**Answered 2026-09-13 (project owner): a Goal is the frozen historical
record.** Written into `ROADMAP.md` § "Development rules for scientific
milestones" as a bullet of its own, so it governs v0.5.0 and everything after
rather than being re-derived per milestone.

**The question was already settled in the tree, which is why this needed no
fresh judgment.** The v0.4.0 Goal has carried the frozen reading in its own
prose since `0ef128c` (`PL-RCTQ`, merged 2026-09-05): "They are stated below as
they stood on 2026-08-25 and are not amended as the milestone closes them: a
Goal records the problem a release was taken on to solve, and rewriting it into
the past one clause at a time would leave the section describing neither the
problem nor the product." v0.5.0's Goal, scoped the day after, repeats the
pattern — "Stated as they stand on 2026-09-06, the day this milestone was
scoped". So both live milestone sections already conform; what was missing was
the *rule*, without which the third milestone inherits a habit and the fourth
breaks it. The two v0.4.0 bullets this item was filed on therefore stay exactly
as written, which is the point of the answer rather than an omission from it.

**The live reading was rejected on cost as well as on shape.** It would put an
edit to `ROADMAP.md` on the critical path of every closing item — a file eleven
other open items already declare in `touches` — to produce a section that
describes neither the problem the release was taken on to solve nor the product
that resulted.
