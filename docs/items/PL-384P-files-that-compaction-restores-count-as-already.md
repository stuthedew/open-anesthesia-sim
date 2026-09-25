---
id: PL-384P
title: Files that compaction restores count as already read, so the first edit to one is written without its path-scoped rules, and a /compact typed after the cache hour re-reads the whole history at full price
status: untriaged
feature: compaction-reset
touches: .claude/hooks/docket-digest.sh, CLAUDE.md, docs/maintainer.md, docs/items/PL-YJG1-reset-a-session-at-the-150k-spend-budget-by.md, tools/context_reading.py
added: 2026-09-25
---

**Problem.** Measured on the first live use of `PL-YJG1`'s reset
(2026-09-25, Claude Code 2.1.282). Two of its claims fail.

**A restored file's first edit skips its path-scoped rules.**
- Compaction brings back "up to five of the files modified most recently"
  ([context window](https://code.claude.com/docs/en/context-window)). Here it
  brought back one, `PL-YJG1`'s item file.
- A restored file counts as already read. An `Edit` probe on it, with a
  string the file does not hold, failed with "String to replace not found".
  An unread file fails with "File has not been read yet".
- Path-scoped rules "trigger when Claude reads files matching the pattern,
  not on every tool use"
  ([memory](https://code.claude.com/docs/en/memory), § "Path-specific
  rules"). `.claude/rules/citation-drift.md` did not come back with the
  restored file. It loaded only on an explicit `Read`.
- So the first edit to a restored file can be written without that file's
  rules. Under `src/` those are `sources-and-docstrings.md`,
  `where-new-code-goes.md` and whichever of `core-domain.md` or the `ui-*`
  rules apply. Auto-compaction does the same, whatever the reset rule says.
- `CLAUDE.md`'s "path-scoped rules re-attaching on the next matching read" is
  true, but it assumes a read comes first. `PL-YJG1`'s "editing an existing
  file after compaction needs a fresh read anyway" is false for a restored
  file.

**A late `/compact` pays for a full read of the history.**
- While the cache is warm, the summarization request "reads your prefix from
  the cache". "After a break longer than the cache lifetime ... [it]
  reprocesses the full history as uncached input"
  ([prompt caching](https://code.claude.com/docs/en/prompt-caching),
  § "Compacting the conversation").
- The main conversation's cache lasts one hour on a subscription within plan
  usage, and five minutes once usage credits are drawn (same page, § "Which
  TTL each request gets").
- A cache read bills at 0.1x base input
  ([API prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
  § "Pricing"). The history here was 248,803 tokens.
- `docs/maintainer.md` presents `/compact` as the reset without saying when a
  fresh session becomes the cheaper one.

**Measured, not defects.**
- Context went from 248,803 tokens (`compactMetadata.preTokens`) to 95,987 on
  the first request after. That is 11,508 over the session's starting floor
  of 84,479.
- So `tools/context_reading.py` reads post-compaction spend as designed.
  Its docstring still says "Untested".
- The summary ran to 15,778 characters, and compaction took 73 s.
- The invoked `docket` skill did not come back. The docs say invoked skills
  are re-injected "capped at 5,000 tokens per skill" (context window page),
  and the binary carries that cap: 5,000 per skill, 25,000 in total.
- But this session had been resumed after 15 idle minutes, just before
  `/compact`. One observation, cause unconfirmed.

**Proposed fix.**
- `.claude/hooks/docket-digest.sh`, on `source: compact`, prints one line:
  read a restored file again before editing it.
- `CLAUDE.md`'s reset sentence says the same, in place of the clause it
  corrects.
- `docs/maintainer.md` says to type `/compact` within the hour. After that, a
  fresh session is cheaper by about one full-price read of the history, when
  the work is pushed and the pull-request watch is not needed.
- `PL-YJG1` takes a dated correction, and the docstring drops "Untested".

**Done when.**
- A compacted session is told to re-read before editing, at the moment
  compaction lands.
- The owner guidance names the timing.
- Both false claims are corrected.
