---
name: punch-list
description: Read, add to, and triage this repository's development punch list in docs/PUNCH_LIST.md. Use when the project owner asks what to work on next, what is left, what the priorities are, or whether to start the next roadmap milestone; when they have usage time available and no particular plan; when they flag a bug, cleanup, optimization, or idea to track for later; or when a session's own work turns up a finding that will not be fixed in that session. Also use when asked to reprioritize, groom, or close out punch-list items.
---

# Punch list

`docs/PUNCH_LIST.md` is the prioritized queue of discrete development
tasks. `ROADMAP.md` holds releases; `docs/WORKING_NOTES.md` holds the
narrative behind open threads. Read `docs/PUNCH_LIST.md`'s own header for
the entry format and the priority, effort, status, and class definitions —
this skill covers the workflows, not the file format.

The point of the file is that a session can start work cold from an entry
without re-deriving the problem, and that a planning session can name six
things to do without having to do them before it runs out of usage.

## Mode: recommend what to work on

Triggered by "what should we work on next", "I have some time", "what's
left", "are we in a good spot to move on".

1. Run `make punch-list` before anything else. It is instant, and it gives
   exact counts and any pending advisories — more current than the
   session-start digest, which does not know about items added since.
2. **Open the reply with the state of the queue, before naming any task.**
   Two lines at most:
   - How many items are open, broken down by priority.
   - Whether grooming is due. If advisories are pending, say how many and
     what they are about, and offer the grooming pass *before* recommending
     work. Do not skip this because there is appealing work at the top of
     the queue — a stale queue gives bad recommendations, and the project
     owner cannot ask for a pass they were never told was due.

   If the owner would rather get on with the work, that is their call: note
   it and continue to the recommendation. The obligation is to surface the
   state, not to insist on acting on it.
3. Then read `docs/PUNCH_LIST.md` itself. Do not survey the codebase first —
   the file exists so that step is unnecessary.
4. Ask how much time or usage is available if it is not obvious, since it
   changes the answer between an `S` and an `M`. Ask once, briefly, and
   only if it is genuinely ambiguous.
5. Recommend in this order:
   - Any `P0`. These come before feature work; say so plainly and follow
     "Mode: hotfix" below.
   - The highest-priority `ready` item whose effort fits the time
     available. Prefer finishing a priority band before dipping into the
     next one, but do not recommend an `M` when only an `S` fits.
   - If everything that fits is `needs-decision`, offer the decision
     itself as the work — resolving it is usually short and it unblocks
     the item for a later session.
   - If the punch list is in good shape and the question is really "should
     we move on to the next feature", the answer is milestone work: scope
     the next milestone in `ROADMAP.md`. Never start unscoped feature work.
6. Give a short recommendation with the reasoning, not a dump of the file.
   Name the top candidate, one or two alternatives with their effort, and
   what each would take. The project owner picks.
7. **State which model the work warrants, independent of what this
   session happens to be running.** This is not a suggestion to weigh —
   `CLAUDE.md`'s "Session and tool-use efficiency" section states the rule:
   an item tagged `safety` or `science`, or one still at `needs-decision`
   (an unresolved design question is exactly the "ambiguous problem or
   genuine trade-off" that section names), is reasoning-heavy work and
   warrants the strongest available model at a high effort setting — for
   both writing the change and reviewing the final diff — regardless of
   whether the current session is on a cheaper model. Everything else is
   routine execution, where the default model is fine.

   `tools/punch_list.py` encodes this same rule (`Entry.model_guidance`)
   and the session-start digest already applies it to the top P0/P1 lines,
   but check it explicitly for whatever is actually being recommended,
   since the digest may be stale or the recommendation may differ from the
   digest's top pick. Say it plainly: "this is safety/science-tagged (or:
   has an open design decision) — start it in `opusplan` or your strongest
   model at high effort," or "this is routine execution — your current
   model is fine." A model switch mid-session costs a cold cache
   (`CLAUDE.md`), so say this *before* work starts, as part of the
   recommendation, not after.
8. Recommend that the work start in a *fresh session* rather than
   continuing this one whenever either is true:
   - the work is substantial or safety-critical; or
   - this session is already long, or was about something else. This
     includes the session that just finished editing the punch list
     itself, whose context is about the queue rather than about any item
     in it.

   The second case is the one that gets missed. A short item is cheap to
   start, but not at the end of a long session whose whole context is
   resent on every turn and has nothing to do with the item. Recommending
   an item and starting it here are different acts; do not let the first
   slide into the second by default.

   When handing off, say what the fresh session should read first:
   `CLAUDE.md`, the entry itself, and any `docs/WORKING_NOTES.md` thread it
   cites. Entries are written to be actionable cold precisely so that this
   handoff costs nothing. Say to open that session with the item's ID at
   the front of its first message ("PL-013: ..."): per `CLAUDE.md`, the
   session and its branch both lead with the ID, and on a surface that
   derives the branch name from that first message, the handoff is the only
   moment where the branch name can still be set.

## Mode: capture a new item

Triggered by the project owner flagging something, or by a finding a
session makes on its own that will not be fixed in that session.

1. Write the entry in the file's documented format. The brief must let a
   cold reader act: problem, why it matters, where in the code, first step,
   and the condition that closes it.
2. Allocate the next unused `PL-` id — one past the highest that appears
   anywhere in the file, including "Recently completed" and "Archive".
3. Place it at its correct priority, which may demote something else.
   Anything on a safety-critical path per `CLAUDE.md` starts at `P0` or
   `P1`, regardless of how small it is.
4. If the reasoning is longer than the brief holds, put the long form in
   `docs/WORKING_NOTES.md` and cite the `PL-` id in that thread's heading.
5. Do not ask permission to record something. Capture at `P3` rather than
   dropping it, and mention in your reply that you did.
6. Capturing is not doing. Unless the project owner asked for the fix,
   record it and continue the current task.

## Mode: close out a completed item

Triggered whenever work from an entry lands. Run this before reporting the
item done, not after the project owner asks whether the docs were updated.

1. Move the entry to "Recently completed" with its commit reference, and
   delete any now-resolved `docs/WORKING_NOTES.md` thread for it. Leaving
   the thread is what trips the checker's advisory. Never delete the entry
   outright: "Recently completed" is a window on the permanent "Archive"
   ledger, not a substitute for it.
2. Sweep the docs for drift the change just caused, per `CLAUDE.md`'s
   "Sweep the docs before calling an item done." Do not start by grepping:
   two commands do the mechanical half, and doing it by hand at the end of a
   session is what has let drift through before.

   - `make doc-check` decides the three failure modes that need no judgment:
     a module missing from `docs/ARCHITECTURE.md`'s package map or left there
     after deletion, a data-file constant missing from `docs/MODEL.md`'s
     provenance table or carrying a value the JSON no longer holds, and a
     cited path or section heading that resolves to nothing. These are
     errors, so `make check` and CI already refuse the change; fix them.
   - `python3 tools/doc_check.py candidates --base <ref>` prints the
     documentation lines that mention anything this diff touched. That is the
     grep, already run. Read the list.

   Then spend the judgment on what no tool can decide, which is whether each
   statement is still *true*. The recurring failure modes in this repository,
   all of which have actually happened:
   - a shipped feature still described as deferred or out of scope;
   - a `docs/MODEL.md` `must`/`must not` the code no longer satisfies;
   - a `WORKING_NOTES.md` thread describing a problem that has been solved;
   - a paragraph that is accurate about the code but describes it as the
     reason for a decision that no longer applies.

   A finding the checker reports is a defect in one of the two: decide
   whether the document or the code is wrong, and say which, rather than
   editing the document until the tool goes quiet.
3. Fix the drift in the same change as the code. A doc fix deferred to
   "later" is drift that outlives the session that could still explain it.
4. Distinguish history from current state. A completed milestone's
   out-of-scope list is a record of what that milestone chose, and stays as
   written; annotate it with what landed afterwards rather than rewriting
   it. Statements of what the project *is* today must match today.
5. Capture anything found but not fixed as its own entry, per the capture
   rule, rather than leaving it in the reply only.
6. Re-run `make check` after the doc edits — it runs both checkers — then
   say in your reply which files you checked.

## Mode: hotfix a P0

1. Branch rather than working on `main`. Existing conventions in this repo:
   `build/vX.Y.Z-slug` for milestone work, so use `fix/pl-00N-slug` for a
   hotfix.
2. Bump the patch version in `pyproject.toml`. That is the single source —
   `app_metadata.py` resolves the displayed version from package metadata,
   so nothing else needs editing.
3. Add a regression test that would have caught it. This is required, not
   optional, for anything on a safety-critical path.
4. Run `make check` (Ruff format, Ruff lint, strict mypy, pytest) before
   committing.
5. Move the entry to "Recently completed" with its commit reference in the
   same change.

## Mode: groom

Triggered by the session-start digest reporting advisories, by `make
punch-list` output, or by a direct request.

1. Run `make punch-list` first. It reports the mechanical findings, so the
   session spends its judgment on the rest rather than on rereading the
   file. Errors mean the file is broken and must be fixed; advisories are
   the agenda for this pass.
2. Re-read the priorities as a set, not one at a time. Ask whether the top
   `P1` is still the thing that should happen next.
3. Promote `blocked` items whose blocker has landed.
4. Split any entry that has grown two independent halves — a smaller piece
   that fits leftover time is more useful than one large item that never
   gets picked up.
5. Promote `L` items into scoped `ROADMAP.md` milestones, or leave them in
   the icebox with a note saying scoping is the next step.
6. Record every disposal in "Archive"; never delete an entry outright.
   An item dropped, folded into another entry, or superseded gets an
   `Archive` line with the date and a one-clause reason — the reason is
   what stops the next session re-raising the same finding. Trimming
   "Recently completed" also means *moving* its lines to "Archive", not
   deleting them: `ROADMAP.md` and `docs/WORKING_NOTES.md` cite completed
   ids permanently, and the checker errors on a reference it cannot
   resolve.
7. Delete resolved `docs/WORKING_NOTES.md` threads rather than leaving them
   stale.
8. Re-run `make punch-list` before finishing; it should come back clean.

## Always

Run `make punch-list` after editing the file. It is instant, it gates
`make check` and CI, and its errors mean an item is about to be silently
lost.

Commit punch-list changes with the work they describe when there is
related work, or on their own when there is not. An uncommitted punch list
is a lost punch list — this session's container is ephemeral.
