---
id: PL-DG84
title: docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy
priority: P2
effort: M
status: needs-decision
classes: docs, session-cost
feature: dev-tooling
touches: docs/WORKING_NOTES.md
added: 2026-09-13
---

**Problem.** docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy

**Notes.** `docs/WORKING_NOTES.md`'s own header states the policy: "When a
thread here is fully resolved (implemented, tested, and merged), its outcome
belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as appropriate, and its
entry here should be deleted rather than left stale." Nothing reads it. The file
is 93 KB over 1,536 lines with no archive and no length check, and roughly eight
of its twenty-one sections lead with a settled status word (`Settled:`,
`Decided:`, `Measured and answered:`, `Built and measured:`).

This is the systemic item; the instances are already filed one thread at a time,
which is the evidence that the policy has no reader: `PL-5748` (the PL-009
playback thread states a pre-`PL-010` frame cost as current), `PL-60CQ` (the
PL-024 entry states a venous pool of 1.0 L that `PL-8ZJQ` replaced with
1.222 L), `PL-BHJW` (says `rules_paths_check.py` is wired into CI's floor job,
which `PL-D551` folded away), `PL-C92D` (a Flet frame table measuring a tree that
no longer exists), and `PL-75R0` (a thread headed "Open: the repository has no
README" a week after `PL-N092` shipped one). All five are individually true and
none of them stops the sixth.

`PL-7QKY` is the adjacent decided question — discovery rather than deletion — and
its brief establishes the parse any mechanism here would need: every one of the
ids this file cites resolves to a real item file. `PL-6ZQY` is the same claim
applied to the queue rather than to this file, with 43 of 134 open items measured
dead or overstated.

**Where.** `docs/WORKING_NOTES.md`; a carrier to be decided at triage —
`tools/doc_check.py`'s `candidates` mode is the candidate that already runs at
close-out and could name a thread all of whose cited ids have closed, but a
one-off pruning pass may be the honest answer instead. Do not build a check that
fires every run without changing a decision.

**Why it matters.** The file exists "so that a new conversation can pick up
context without re-deriving it", so a stale thread in it is not merely unread -
it is read and acted on. `PL-75R0` is the sharp case: a thread headed "Open: the
repository has no README" a week after one shipped. The five filed instances are
each individually true and none of them stops the sixth, which is what makes this
the systemic item rather than a sixth instance.

**Decision needed.** Which carrier, and the question is whether anything here
should run every time. Three candidates, and they are not equivalent:

- **A `tools/doc_check.py` `candidates`-mode line.** It already runs at
  close-out, and it could name a thread all of whose cited `PL-` ids have closed.
  `PL-7QKY`'s brief establishes the parse: every one of the ids this file cites
  resolves to a real item file. The risk is `CLAUDE.md`'s own retirement test - a
  thread can legitimately outlive its items, which is one of the three things the
  file's header says belongs in it, so this would fire on correct content and
  train a session to skim it.
- **A grooming advisory**, alongside the existing ones, so it surfaces on a pass
  that is already about queue hygiene rather than on every close-out.
- **A one-off pruning pass and no mechanism at all**, on the ground that the
  decidable half here is small and the judgment half - whether a thread still
  earns its place - is the whole of it.

The answer rests on a rule this repository already states rather than on what the
project is for, so it is a session's to settle with the counts in front of it,
not the owner's. What it must not become is a check that fires every run without
changing a decision.

**Done when.** The carrier above is chosen and recorded here with its reasoning,
and either it is built or the item says why no mechanism earns its place - and in
either case `docs/WORKING_NOTES.md` no longer carries a thread whose every cited
id has closed.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository.
