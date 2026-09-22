---
id: PL-7TVT
title: bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: carrier-detection
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
root-cause-of: PL-N2PP, PL-HX5C, PL-99YZ, PL-X3NY, PL-Q664
generator: live - in-flight state is read only from pushed refs, so a session that has not pushed yet is invisible to flight, show, next, concurrent and the digest, and a ref whose session has ended still reads as live; on 2026-09-22 a session reported PL-0HPV unstarted while another was running it, 20 minutes before that session's first push (PL-KVDK)
---

**Problem.** bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'

**Why it matters.** `bin/docket flight` is the guard that stops two sessions
starting the same item, and its output is written in the imperative - "do not
start these again". Commit age is the only signal it has for telling a live
session from an abandoned branch, so for the first hour of a branch's life the
two are indistinguishable and the guard reads as a claim it cannot support:
PR #757 sat green and unclaimed for 25 minutes after its session was archived
with its three items still reserved. The failure is silent and it is in the
direction of *withholding* work rather than duplicating it, which is why it has
never announced itself - a session told not to start an item simply picks
another one.

**Reproduced 2026-09-20.** `bin/docket flight` reads commit timestamps and
branch refs only; nothing in `subprojects/docket/` reads a session's state, and
nothing can, since `bin/docket` is required to run from a bare checkout with no
virtualenv and no network.

**Decision needed.** What signal, readable from a bare checkout, separates a
live session from an abandoned branch inside the first hour - or whether the
honest answer is that none exists and `flight`'s wording should stop implying
one.

**Recommended:** change the wording, not the signal. Nothing git can see
distinguishes the two cases, and the two candidate signals both fail the bare
checkout requirement: session state needs the harness, and a merged-or-closed
pull request needs the network. So the cheap, honest repair is for `flight` to
say what it actually knows - a branch exists and carries commits for this item,
last commit N minutes ago - and to stop issuing an instruction it cannot back.
A reader who sees "claimed 3 minutes ago" and knows the claim may be stale
behaves correctly; one told "do not start these again" cannot tell the two
apart at all.

**Done when.** `bin/docket flight`'s output either carries a signal that
distinguishes a live session from an abandoned branch, or states what it knows
without instructing on what it does not - and a test under
`subprojects/docket/tests/` drives a branch whose last commit is minutes old.
