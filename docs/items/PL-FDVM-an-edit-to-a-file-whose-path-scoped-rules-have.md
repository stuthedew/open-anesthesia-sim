---
id: PL-FDVM
title: An edit to a file whose path-scoped rules have not loaded since the last compaction could be refused by a PreToolUse guard, where the digest's compact line only asks for the re-read
status: untriaged
feature: compaction-reset
added: 2026-09-27
---

**Problem.** `PL-384P` closes the restored-file gap with one advisory line,
printed by `.claude/hooks/docket-digest.sh` when a compaction lands: read a
restored file again before the first edit to it. An advisory is followed most
of the time and not always: the session-rename rule measured about three in
four over twenty sessions (2026-09-02, `.claude/skills/docket/modes/start.md`).
A miss here is an edit under `src/` written without `sources-and-docstrings.md`
and `core-domain.md`.

**What a deterministic version would be.** Claude Code has an
`InstructionsLoaded` hook that logs "which `CLAUDE.md` and rules files are
loaded, when they load, and why"
([memory](https://code.claude.com/docs/en/memory), under "Claude isn't
following my CLAUDE.md"). Three hooks would make the re-read a gate rather than a
reminder:
- `InstructionsLoaded` records each rule the session loads.
- `SessionStart` on `compact` clears that record, as compaction clears
  `loadedNestedMemoryPaths`.
- A `PreToolUse` guard on `Edit|Write|MultiEdit` refuses an edit to an
  existing file under a rule's `paths:` when that rule is not in the record,
  and names the file to Read.

**Why `PL-384P` did not build it.**
- It answers from harness internals: the `InstructionsLoaded` input schema, and
  `paths:` glob matching that has to agree with Claude Code's own.
- A wrong refusal is a hard gate refusing correct work, which is the kind of
  apparatus finding that stops a product session. A new file has no rule
  loaded until some matching file is read, so the guard must pass files that
  do not exist yet.
- It runs on every edit.
- It is a different deliverable from the one `PL-384P` described, so building
  it was the owner's call.

**The number that would justify it.** A session seen editing a
compaction-restored file before any Read of it, after `PL-384P`'s line landed.
None has been observed. Until one is, the line is the cheaper sufficient tier.
