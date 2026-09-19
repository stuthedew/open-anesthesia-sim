---
id: PL-2T03
title: Four items re-derive the release train's arrangement by comparing version numbers, though ROADMAP.md's timeline table already records it
priority: P2
effort: M
status: done
classes: defect, infra
feature: timeline-arrangement
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-19
closed: 2026-09-19
pr: 690
verify: grep -q 'def test_the_train_resolves_the_position_once' subprojects/docket/tests/test_roadmap.py && ! grep -q 'supported = plan.beat' subprojects/docket/src/docket/release.py
root-cause-of: PL-Y1L0, PL-J45M, PL-7CSP, PL-B5DW
---

**Problem.** Four items re-derive the release train's arrangement by comparing version numbers, though ROADMAP.md's timeline table already records it

**Split out of `PL-HWW1` on 2026-09-19**, which held these four alongside
three membership items under one diagnosis. They are a different mechanism and
neither decision moves the other, so they rank and are worked apart.

**Why it matters.** `bin/docket wave` is the first thing the `docket` skill
tells a session to read, and these four decide what it says: which milestone
the beat is about, whether a gate's remaining entries are stranded or merely
sequenced, and which row `status` and `wave` each call "the step". `PL-Y1L0`
is the sharp end - a patch cut at the Qt port's own number silently reverses
the owner's placement of that port ahead of v0.5.0, and no advisory reports
it - and `release.py:558` is a workaround already standing in the tree because
the classifier answers "unfinished" when it means "unrecognised".

**The mechanism.** `ROADMAP.md` § "The timeline" is already a *recorded*
structure: a table with a grammar, parsed by `parse_timeline`, whose breaches
come back as `problems` and which `_timeline_order` fails when a row is written
out of sequence. The row order **is** the arrangement. Nothing downstream reads
it. `wave` and its consumers instead compare `(major, minor, patch)` tuples and
take the answer as the arrangement:

- `roadmap.py:1408` - `unreleased = [... if section.version > current]`.
- `_release_due` (`roadmap.py:1310`) - `step.version < gate.milestone.version`
  and `step.version == gate.milestone.version` are two of its three
  arrangements.
- `_due_before` (`roadmap.py:1195`) says so in its own docstring: *"'Before' is
  by version, which the timeline grammar makes agree with row order for
  milestone rows"*.
- `_blocked_outside` (`roadmap.py:1047`) consults arrangement not at all: it
  asks only whether a blocker is itself a gate entry.

So this is not `PL-HWW1`'s *"infers a fact it could have recorded"*. It is the
narrower and more annoying **re-derives a fact it already has**, through a
proxy that agrees with the record until it does not - and every place it
disagrees has been found separately and filed separately.

**Where the proxy breaks, per member.**

| Item | Where | What the version comparison gets wrong |
| --- | --- | --- |
| `PL-Y1L0` | `wave` | A patch cut at `0.4.26` makes the Qt port's own section `version <= current`, so it drops out of the unreleased set and the beat jumps to v0.5.0 - reversing the owner's 2026-09-14 decision to put the port ahead of it, with nothing reporting it. |
| `PL-J45M` | `_release_due` | A gate-only milestone whose frozen list has cleared is reached from a row that is not its own, matches no arrangement, and falls through to `implement`. `release.py:558`'s `supported = ...` is a live workaround that names this item in its comment. |
| `PL-7CSP` | `_blocked_outside` | A blocker the timeline schedules *before* the gate and a blocker nothing schedules print identically as `blocked outside the gate`. It already misled a reader on 2026-09-15. |
| `PL-B5DW` | `render._plan_header` | The reader-visible face: `status` calls the anchor "the step the project is on" while `wave` reports a different row as the step. `Scope.step_label` already carries the row and the header does not read it. |

The first three are the mechanism directly. `PL-B5DW` is what a reader sees
when the anchor and the row are two facts the code holds in one word, which is
the same collapse arriving at the surface.

**Why this is a generator rather than four defects.** Each member has been
patched or worked around at its own site, and the site count is still growing:
`release.py:558` is a guard written *because* the classifier answers
"unfinished" when it means "unrecognised", and it names `PL-J45M` as what would
remove it. Every new consumer that needs to know what comes before what
re-derives it the same way, because there is nothing to read.

**Decision needed.** What object carries the release train's arrangement, and
how it reaches the four call sites above. The likely answer is that `wave` resolves the
project's position on the timeline *once* - the row, the anchor section, and
the order of the rows ahead of it - and hands that down, so "before" is a row
comparison rather than a version comparison and `_blocked_outside` can ask
where the plan places a blocker at all. Named rather than assumed, because the
patch-track rows carry `(major, minor, -1)` and gate rows carry no version, so
a row index is not interchangeable with a version anywhere.

**Not in scope.** Membership - which ids a milestone contains and excludes -
is `PL-HWW1`, and stays there. The two touch `roadmap.py` and will want
sequencing, but neither answer constrains the other.

**Done when.** The four call sites above answer arrangement questions from the
timeline row rather than from a version comparison; `release.py:558`'s
`supported` workaround is removed rather than left standing; and the four
members are closed against it or re-briefed with what is left.

**Decided and closed 2026-09-19, in the session that started it.** The object
is `ReleaseTrain` in `subprojects/docket/src/docket/roadmap.py`, built once by
`release_train` at the top of `wave`: the rows in table order, the position -
the row after the last milestone released, which is still decided by the
version because that comparison is identity rather than arrangement, per
`Scope`'s recorded rule - the unreleased sections in row order (`ahead`), and
`row`, `section`, `places` and `row_placing` for the questions downstream.
The four call sites read it. `_due_before` walks the rows from the position to
the gated milestone's own; `_release_due`'s first arrangement is a row
comparison and its second releases a gate-only milestone from whichever row
the project stands on, so `implement` is returned only where an `own_scope`
counts open work; `gate_status` takes the train and splits `blocked_outside`
into `sequenced_ahead` and `waiting_outside`; `render._plan_header` names the
row apart from the anchor. `release.py`'s `supported` workaround is deleted.

**What the train does not do, deliberately.** It does not move the position off
the version. `PL-Y1L0`'s row above blamed `unreleased`'s comparison, and the
alternative record - the version table - cannot tell a patch cut *at* a
milestone's number from the milestone itself, so it would not have closed that
case either, while changing the answer for every roadmap without a table. What
the train adds instead is the report `PL-Y1L0` asked for: `ReleaseTrain.stale`
carries a milestone row the project's version has passed with no release of
that number in the version table, and a section no row bears; `format_wave`
prints them under their own heading, the digest's plan line flags them,
`bin/docket wave` exits non-zero on them, and `outstanding_roadmap_edits`
states the reached-or-passed number at the hand-off. Measured on the live tree
before building: no statement fires today.

Members closed against it: `PL-Y1L0`, `PL-J45M`, `PL-7CSP`, `PL-B5DW`. Two
residuals are filed under the same feature: the hand-off cannot tell a
legitimate milestone release from a patch taking its number without the beat,
and `wave` does not report a released milestone row whose section's `Required
scope` is still open - the cut-at case, once the hand-off has scrolled by.
