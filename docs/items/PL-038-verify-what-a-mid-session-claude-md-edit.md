---
id: PL-038
title: Verify what a mid-session `CLAUDE.md` edit actually invalidates
priority: P2
effort: S
status: done
classes: session-cost, docs
feature: dev-tooling
milestone: v0.5.10
touches: CLAUDE.md, docs/items/PL-1T6T-re-test-the-refusal-of-compaction-now-that-root.md
added: 2026-08-24
closed: 2026-09-24
pr: 984
verify: ! grep -q 'invalidates that cache' CLAUDE.md && ! grep -q 'despite the cache cost' CLAUDE.md && grep -q 'resident rule mid-session invalidates no cache' CLAUDE.md
---

**Resolved 2026-09-24: the claim was false, and the bullet now says what
happens.** Editing `CLAUDE.md` or a resident rule mid-session invalidates
nothing. Measured on Claude Code 2.1.281 from this session's own transcript -
the per-request `usage` records `tools/context_reading.py` reads, split by
field - by appending a marker line to the file on disk and reading the next
request:

| File edited | Previous request's context | Next request, read from cache | Next request, written |
| --- | --- | --- | --- |
| `CLAUDE.md` | 132,307 | 132,305 | 2,811 |
| `.claude/rules/instruction-writing.md` | 135,965 | 135,963 | 2,545 |

Both times the whole previous context came back from cache and only the new
tool output was written. The session's first request shows where a real
invalidation would have cut: it read 39,385 tokens, the system prompt and
tools, and wrote 44,140, the resident set and the digest. A change inside the
resident set would have read back about 39,000 and re-written the rest.

**Why.** "CLAUDE.md content is delivered as a user message after the system
prompt, not as part of the system prompt itself", and it is "loaded at launch"
([memory](https://code.claude.com/docs/en/memory), read 2026-09-24). Nothing
re-reads it when a turn starts or the file changes. The 2.1.281 binary names
the events that re-read instruction files: session start, compaction, a
managed-settings change, a working directory added, a settings sync, an
account change, a plugin asking for it, and an organization policy arriving. A
re-read that finds a change appends a message headed "These instruction files
changed", or "Instruction files were re-read (...); these differ from their
earlier copies", carrying the changed files, and leaves the launch copy where
it is. The in-turn result above is measured; that a new user message does not
re-read either rests on that list, because this session measured inside one
turn.

**What changed.** The bullet in § "Session and tool-use efficiency" states the
mechanism and drops the own-session recommendation, which rested on nothing
else; the behaviour-change bullet's "despite the cache cost noted above" went
with it. The one real consequence of a mid-session edit is that the session
keeps its launch copy until a re-read, and the bullet says that instead.

**What would make this wrong.** A Claude Code release that re-reads
instruction files per turn and rewrites the first message. Re-check it the same
way: append a line, then compare the next request's `cache_read_input_tokens`
with the previous request's total.

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed, unchanged.** The claim is
> still in `CLAUDE.md` § "Session and tool-use efficiency", the bullet
> beginning "Edit this file and the core docs in their own session", and the
> behaviour-change bullet's "despite the cache cost noted above" leans on it,
> so every session that must edit `CLAUDE.md` mid-session pays, or does not
> pay, a cost nobody has measured. No later item answers it. The instrument
> now exists: `tools/context_reading.py` reads the session's own transcript,
> which carries `cache_read_input_tokens` and `cache_creation_input_tokens`
> per request, so the **First step** measurement is a read of the requests
> either side of one edit.

**Problem.** `CLAUDE.md` § "Session and tool-use efficiency" section says to
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
