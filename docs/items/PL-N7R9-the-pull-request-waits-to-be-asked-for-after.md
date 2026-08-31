---
id: PL-N7R9
title: The pull request waits to be asked for, after the owner has already agreed to the work
priority: P2
effort: S
status: ready
classes: docs, infra
feature: parallel-sessions
touches: CLAUDE.md
added: 2026-08-31
verify: grep -q 'the pull request arrives with the work' CLAUDE.md
---

**Problem.** `CLAUDE.md` says "Commit and push as you go; open a pull request
only when asked". `PL-Z8SV` established that split on 2026-08-30 and its
reasoning about *pushing* still holds. Its reasoning about the pull request
does not: it kept the ask because a pull request "is the act that asks for
someone's attention and proposes something be merged, so it is the owner's to
invite."

The invitation has already happened by then. The owner approves a design, says
go, and the session builds it — and then asks whether to open a pull request
for the thing that was just agreed. Raised by the owner 2026-08-31: the
question costs a full turn and carries no decision.

**Why it matters.** It is a round trip — the whole context resent — on the
most common way a working session ends, to re-ask a question already answered.
That is the same failure `PL-Z8SV` fixed one clause to the left, left in place
by an argument that does not survive the agreement point moving earlier.

**The owner's stated end state, verbatim in intent.** "I say go, and you do
your thing and give me a pull request at the end of it." Ordering and mechanism
were explicitly left to the session; two replies spent proposing draft pull
requests opened at agreement time were the wrong shape of answer and the owner
said so.

**Two things the wording must get right, or it breaks quietly.**

- **It must not authorize a pull request for a capture-only session.** Pushing
  is continuous, so a session that only files items still has commits on its
  branch. The trigger is "work the owner approved is finished and the checks
  are green", not "the branch has something on it".
- **The web harness instructs sessions not to open a pull request unless the
  owner explicitly asks.** The standing policy *is* that ask, given once as
  policy rather than per pull request. A session reading both without this
  said outright will stall on the apparent conflict, so the rule states it.

`ROADMAP.md`'s "the gate is a snapshot" applies: the problem was present when
v0.2.8's list was frozen, so this re-enters that gate rather than waiting.

**Where.** `CLAUDE.md`, the queue rules — the bullet `PL-Z8SV` last edited.

**Done when.** `CLAUDE.md` says the pull request arrives with the approved
work rather than being asked for; the capture-only exclusion and the
harness-conflict resolution are both stated; and no other file still says a
pull request waits to be invited (check `docs/worker.md` and the `docket`
skill).
