---
id: PL-S7LT
title: Quotations of code.claude.com pages go stale as the pages change and nothing compares them again: PL-124X found the WebFetch quotation in webfetch-quote-note.sh, read from the page's .md on 2026-10-01, no longer on the page on 2026-10-19
priority: P3
effort: S
status: needs-decision
classes: housekeeping
touches: tools, .claude/skills/docket/modes/release.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
payoff: a rule resting on a sentence of Claude Code's documentation is told when that sentence leaves the page
---

**Problem.** Quotations of code.claude.com pages go stale as the pages change and nothing compares them again: PL-124X found the WebFetch quotation in webfetch-quote-note.sh, read from the page's .md on 2026-10-01, no longer on the page on 2026-10-19

**Why it matters.** `PL-124X` compared every quotation of code.claude.com in
the live documents with the pages' markdown on 2026-10-19. Four of the 16
quoted strings, in three passages, are no longer on the pages. One passage, in `.claude/hooks/webfetch-quote-note.sh`,
had been read from the page's own `.md` on 2026-10-01. So that one was not a
WebFetch paraphrase: the page changed under it in 18 days. Claude Code's
documentation changes often, and a rule here that rests on one of its sentences
keeps reading as sourced after the sentence has gone. Nothing would say so
until a session happened to compare the quotation again.

**Decision needed.** Whether to build a hand-run comparison, or to accept the
drift and compare again only when a session relies on a quotation.

- **Recommended: a hand-run script, `tools/doc_quote_check.py`, run at each
  release cut.** It finds each quoted string beside a code.claude.com link in
  the live files, fetches the page's `.md` once, and prints each quotation the
  page no longer contains, after normalizing whitespace and Markdown emphasis.
  It decides nothing about meaning, so it reports a lead for a session to read.
  It needs network access, so it stays out of `make check` and CI. PL-124X's
  comparison found 4 of 16 quoted strings stale, which is enough to recur.
- Accept the drift. Each session that leans on a quotation compares it first,
  as `.claude/hooks/webfetch-quote-note.sh` already tells it to do for a quote
  it fetches. This costs nothing to build, and it misses a quotation nobody
  re-reads.

The script is a new workflow mechanism, so it waits while any open
workflow-lane item carries `generator: live` (`CLAUDE.md` § "What this project
is"). None did on 2026-10-19.

**Done when.** The decision is recorded here, and either the script exists and
the release mode names it, or this item is dropped with the reason.

**Generator check.** Its reader misread whether a quotation of a living page is
still on the page. No head names that fact. `PL-124X` is the one backfill, and
it is not a member of anything, so this is an ordinary item.
