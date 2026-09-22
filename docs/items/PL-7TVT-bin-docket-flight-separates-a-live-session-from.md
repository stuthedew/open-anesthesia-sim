---
id: PL-7TVT
title: bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: carrier-detection
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, .claude/skills/docket/modes/start.md, .claude/rules/instruction-writing.md
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

**Design round, 2026-09-22 (the session that recorded the generator).** The
generator has two faces, and they want different fixes.

- **Live work nobody has pushed reads as startable** (`PL-N2PP`, `PL-HX5C`,
  `PL-99YZ`; `PL-0HPV` on 2026-09-22). No signal git can see precedes a
  session's first push, so the only deterministic fix is to make that push come
  first. It needed no code: `_annotates_only` already reads a commit with no
  diff as a claim, so `git commit --allow-empty -m "PL-K7QX: start"` and a push
  claim an item before any work. `.claude/skills/docket/modes/start.md` now
  says so, both at the start and when a second item is picked up (the rider and
  mid-session shapes of `PL-N2PP` and `PL-HX5C`), and
  `test_an_empty_commit_leading_with_an_id_claims_the_item_before_any_work`
  pins what that rests on. Rule 14's session-list bullet in
  `.claude/rules/instruction-writing.md` covered only work with no id, because
  it assumed the ref guards cover work that has one. This generator is what
  breaks that assumption, so the bullet now covers recommending an item to start
  as well. That is the reading-side backstop for a session that did not claim.
- **A ref whose session has ended still reads as live** (this item's own
  instance, `PL-X3NY`, `PL-Q664`). Not yet addressed, and it is why the verdict
  stays `live`. `flight` already reads the two pieces of evidence it needs and
  throws most of it away:
  - the commit timestamp: `COMMIT_FORMAT` carries it in full (`%cI`), but
    `_since` prints the day. So "last commit today" cannot separate three
    minutes from twenty hours, and across midnight a fresh branch reads as a
    day old (`PL-3QM9`).
  - the open-pull-request lookup `PL-Q664` added (`open_pull_requests_command`),
    which `flight` asks only about settled candidates.

  **Next:** carry the timestamp through `Branch.last_commit` and `_since` to
  the minute, and print each live row's pull-request state wherever the forge
  answered. That meets this item's **Done when.** and `PL-3QM9`'s together.
  Then decide `PL-X3NY` on the same lookup: its brief predates `PL-Q664`, which
  made route 1's "new network dependency" an existing one. Set the verdict to
  `spent` only once a ref whose session has ended can no longer read as someone
  working on it.
- `PL-N2PP` and `PL-HX5C` meet their **Done when.** through the start rule
  above, and close out next session. `PL-99YZ` (fresh ids for one subject) is
  out of reach of any claim keyed on an id, and keeps its own count-first brief.
