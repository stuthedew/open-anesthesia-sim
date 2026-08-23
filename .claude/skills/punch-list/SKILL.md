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

1. Read `docs/PUNCH_LIST.md`. Do not survey the codebase first — the file
   exists so that step is unnecessary.
2. Ask how much time or usage is available if it is not obvious, since it
   changes the answer between an `S` and an `M`. Ask once, briefly, and
   only if it is genuinely ambiguous.
3. Recommend in this order:
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
4. Give a short recommendation with the reasoning, not a dump of the file.
   Name the top candidate, one or two alternatives with their effort, and
   what each would take. The project owner picks.
5. If the recommended work is substantial or safety-critical, say that it
   deserves its own fresh session rather than continuing this one, and say
   what that session should read first (`CLAUDE.md`, the entry, and any
   `docs/WORKING_NOTES.md` thread it cites).

## Mode: capture a new item

Triggered by the project owner flagging something, or by a finding a
session makes on its own that will not be fixed in that session.

1. Write the entry in the file's documented format. The brief must let a
   cold reader act: problem, why it matters, where in the code, first step,
   and the condition that closes it.
2. Allocate the next unused `PL-` id — one past the highest that appears
   anywhere in the file, including "Recently completed".
3. Place it at its correct priority, which may demote something else.
   Anything on a safety-critical path per `CLAUDE.md` starts at `P0` or
   `P1`, regardless of how small it is.
4. If the reasoning is longer than the brief holds, put the long form in
   `docs/WORKING_NOTES.md` and cite the `PL-` id in that thread's heading.
5. Do not ask permission to record something. Capture at `P3` rather than
   dropping it, and mention in your reply that you did.
6. Capturing is not doing. Unless the project owner asked for the fix,
   record it and continue the current task.

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

1. Re-read the priorities as a set, not one at a time. Ask whether the top
   `P1` is still the thing that should happen next.
2. Promote `blocked` items whose blocker has landed.
3. Split any entry that has grown two independent halves — a smaller piece
   that fits leftover time is more useful than one large item that never
   gets picked up.
4. Promote `L` items into scoped `ROADMAP.md` milestones, or leave them in
   the icebox with a note saying scoping is the next step.
5. Delete resolved `docs/WORKING_NOTES.md` threads rather than leaving them
   stale, and trim "Recently completed" once it stops being useful history.

## Always

Commit punch-list changes with the work they describe when there is
related work, or on their own when there is not. An uncommitted punch list
is a lost punch list — this session's container is ephemeral.
