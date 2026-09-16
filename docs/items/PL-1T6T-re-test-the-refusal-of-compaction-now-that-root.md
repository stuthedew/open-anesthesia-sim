---
id: PL-1T6T
title: Re-test the refusal of compaction now that root CLAUDE.md is known to reload after a compact
status: untriaged
added: 2026-09-16
---

**Problem.** `CLAUDE.md` § "Session and tool-use efficiency" groups compacting
with continuing as the wrong move — "start a fresh one for an unrelated topic
rather than continuing or compacting a long one" — and `PL-H253` put a low
`/autocompact` among four options the project owner declined in favour of the
habit alone. That is a recorded decision rather than an oversight. But one
premise under it looks false, and it was never the thing tested.

Root `CLAUDE.md` reloads after a compact, so the resident set survives. What
compaction drops is accumulated tool output — file reads, test runs, greps —
which is the part worth dropping. Anthropic's long-horizon guidance treats
compaction, structured note-taking and multi-agent decomposition as
complementary techniques rather than as a failure mode.

**The qualifier that makes this non-obvious, and why it is not a duplicate.**
`PL-2XM2` measured the other half: an invoked skill body is re-injected after
compaction "capped at 5,000 tokens per skill and 25,000 tokens total", keeping
the start of the file, and `.claude/skills/docket/SKILL.md` is ~18,100 tokens,
so about 27% survives. So compaction is lossless for the resident set and lossy
for skills. Any re-test has to price both, and `PL-2XM2`'s reordering is
plausibly a precondition rather than a parallel item.

**Not yet verified.** Both primary pages — Anthropic's context-engineering post
and the Claude Code context-window doc — were blocked by the session
environment's egress proxy on 2026-09-16, so the reload claim rests on search
summaries. Confirm against the docs before anything is rewritten. `PL-2XM2`
cites the context-window doc directly and is the better starting point.

**Sequencing.** Raised alongside `PL-NW76`, which reshaped the cap into a
starting budget. Worth answering after that lands, since the cap's shape
decides how much a compaction option would even buy.
