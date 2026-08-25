---
id: PL-038
title: Verify what a mid-session `CLAUDE.md` edit actually invalidates
priority: P2
effort: S
status: ready
classes: session-cost, docs
feature: dev-tooling
touches: CLAUDE.md
added: 2026-08-24
---

**Problem.** `CLAUDE.md`'s "Session and tool-use efficiency" section says to
edit `CLAUDE.md` and the core docs in their own session, because "they sit in
the cached prefix of every request, so editing one partway through a session
invalidates that cache for the rest of it." Anthropic's documentation
describes a different mechanism: `CLAUDE.md` is read at session start and
delivered as a user message, and is re-injected from disk only after
compaction. On that description an edit to the file on disk does not alter
the copy already in the message history, and so does not invalidate the
prefix mid-session.
**Why it matters.** If the claim is wrong it is costing sessions directly, in
the least visible way: it pushes work onto a second session — a cold cache
and a re-read of the same files — to avoid a penalty that may not exist. The
advice is also load-bearing for how this repository schedules its own
process work.
**Where.** `CLAUDE.md`, "Session and tool-use efficiency", the bullet
beginning "Edit `CLAUDE.md` and the core docs in their own session".
**First step.** Check the current Claude Code documentation on how memory
files are loaded and what survives compaction, then edit a `CLAUDE.md`
mid-session and compare reported cache-read and cache-write token counts on
the turns either side of the edit.
**Done when.** The bullet states what actually happens, and either keeps the
same-session recommendation with a correct reason or drops it.
**Context.** Raised by the punch-list workflow review of 2026-08-24, which
relied on the same documentation while assessing what is resident in context.
