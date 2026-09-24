---
id: PL-1T6T
title: Re-test the refusal of compaction now that root CLAUDE.md is known to reload after a compact
priority: P3
effort: S
status: needs-decision
classes: session-cost
touches: CLAUDE.md
added: 2026-09-16
---

> **Evidence added 2026-09-24 by `PL-038`: the reload claim now rests on the
> primary pages.** The memory page: "Project-root CLAUDE.md survives
> compaction: after `/compact`, Claude re-reads it from disk and re-injects it
> into the session. Nested CLAUDE.md files in subdirectories and rules with
> `paths:` frontmatter reload as Claude reads files they apply to"
> ([memory](https://code.claude.com/docs/en/memory)). The context-window page,
> at its compaction step: "System prompt, CLAUDE.md, memory, and MCP tools
> reload automatically. Claude Code also re-reads up to five of the files
> modified most recently and re-injects the skills you invoked. The skill
> listing does not reload"
> ([context window](https://code.claude.com/docs/en/context-window)). Both were
> read 2026-09-24, and Claude Code 2.1.281's binary also lists compaction among
> the events that re-read instruction files. Still open: neither quotation
> names the rules without `paths:`, which load at launch beside `CLAUDE.md`,
> and Anthropic's context-engineering post was not fetched. The decision is
> untouched.

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

**Why it matters.** The grouping in `CLAUDE.md` rests on a premise nobody
tested. If the resident set does reload, what a compact drops is precisely the
accumulated tool output a long session should be shedding - so the standing rule
may be refusing a cheap remedy at the one moment it is most wanted, near a rate
limit, which is the case `CLAUDE.md` § "The queue" names as the worst outcome
available. The rule is resident, so every session carries it and every session
pays for whichever answer is right.

**Done when.** The reload claim is confirmed against the two primary pages
rather than search summaries; the skill-truncation half `PL-2XM2` measured is
priced alongside it, since compaction is lossless for the resident set and lossy
for skills; and `CLAUDE.md`'s sentence either stands with its premise stated, or
is changed in the session that decides it, per `CLAUDE.md` § "A behavior change
takes effect in the session that asks for it".

**Decision needed.** Whether `CLAUDE.md`'s grouping of compacting with continuing
- "start a fresh one for an unrelated topic rather than continuing or compacting
a long one" - survives the reload finding. This changes how every session works,
so it is the project owner's; `PL-H253` records their earlier decision against
four options including a low `/autocompact`, and this item is the one premise
under that decision which was never put to the test.
