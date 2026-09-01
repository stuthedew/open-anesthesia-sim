---
id: PL-7QKY
title: The working-notes discovery instruction is circular - a session must read the whole file to learn whether its task touches one of its threads
priority: P2
effort: M
status: needs-decision
classes: defect, session-cost
feature: dev-tooling
touches: docs/WORKING_NOTES.md, .claude/hooks, tools/doc_check.py
added: 2026-09-01
---

**Problem.** `docs/WORKING_NOTES.md:17-19` instructs: "Any session working on
this repository should read this file at the start of a task that touches one
of its open threads." The condition cannot be evaluated without doing the
thing it gates. Nothing else names the file either — the session-start digest
reports the queue, the plan and the release state, and `bin/docket next` ranks
items; neither mentions an open thread.

So the instruction resolves in practice to one of two behaviours, and both are
wrong: read the whole file every session (34.5 KB, roughly 8.6k tokens,
against `CLAUDE.md`'s turns-times-context discipline), or read none of it and
lose exactly the cross-session continuity the file exists for.

**Why it matters.** The threads carry measurements and decisions that outlive
their items — the playback-speed thread survives `PL-009` being dropped, and
the scenario-branching thread says outright that its measurements are kept
because a scoped milestone will need them again. Content nothing routes a
session to is content that will be re-derived at full cost, which is the
failure the file was written to prevent.

**Where.** `docs/WORKING_NOTES.md:17-19` is the instruction. The fix is
plausibly not there: the decidable part is *which threads exist and which ids
each concerns*, which a script can read off the `##` headings — every one of
the 52 ids the file cites resolves to a real item file, so the mapping is
already sound enough to key on. A digest or `bin/docket next` line naming the
thread that concerns the item being started would deliver the pointer at the
moment it is needed, at a cost of one line rather than 573.

**Decision needed.** Where the pointer is delivered. Three candidates, and
they differ in when they fire rather than in what they compute:

- **`bin/docket show <id>`** — fires when a session is about to start an item,
  which is the moment the pointer is wanted, and the `docket` skill already
  makes `show` the mandatory pre-start check. Misses a session that edits
  without starting an item.
- **The session-start digest** — fires once per session, unconditionally, so
  nothing can miss it; but it must then name every open thread rather than the
  one that is relevant, since at session start no item has been picked.
- **`bin/docket next`** — fires only on the sessions that let `next` pick, and
  the skill notes an item named by the owner skips `next` entirely.

Recommended: `show`, for the reason its own guard exists — naming an item is
the path with no other check on it. Decide before implementing; the reading of
the `##` headings is the same work under all three.

**Watch for.** Do not solve this by making every session read the file. The
thread-to-id mapping is the cheap half; deciding whether a thread is still
true is not, and must stay with the session.

**Done when.** A session is told which thread concerns the work it is about
to start, without having read the file to find out, and the instruction in
the file states that rather than asking for a judgement it cannot make.
