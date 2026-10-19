---
id: PL-S7LT
title: Quotations of code.claude.com pages go stale as the pages change and nothing compares them again: PL-124X found the WebFetch quotation in webfetch-quote-note.sh, read from the page's .md on 2026-10-01, no longer on the page on 2026-10-19
priority: P3
effort: S
status: ready
classes: housekeeping
touches: tools, .github/workflows/drift.yml, docket.toml, docs/apparatus.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
payoff: a rule resting on a sentence of Claude Code's documentation is told when that sentence leaves the page
verify: grep -q 'doc_quote_check' .github/workflows/drift.yml && grep -q 'tests/unit/test_doc_quote_check.py' docket.toml
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

- [superseded 2026-10-19: the decision below keeps the script and moves when
  it runs, and how it finds the quotations.] **Recommended: a hand-run script,
  `tools/doc_quote_check.py`, run at each release cut.** It finds each quoted string beside a code.claude.com link in
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

[superseded 2026-10-19: the decided Done when is below.] **Done when.** The
decision is recorded here, and either the script exists and the release mode
names it, or this item is dropped with the reason.

**Generator check.** Its reader misread whether a quotation of a living page is
still on the page. No head names that fact. `PL-124X` is the one backfill, and
it is not a member of anything, so this is an ordinary item.

**Decided 2026-10-19: build the comparison, run it weekly in `drift.yml`, and
read the quotations from a record.** This was decided in the design round
(Order item 36) as an obvious call and was not put to the project owner.
Accepting the drift is the weaker option. PL-124X found 4 of 16 quoted strings
gone from their pages, so drift recurs, and whether a string is still on a page
is decidable by a script. `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work" already gives standing approval for that. The generator
pause does not hold: `bin/docket generators` showed no head still generating on
2026-10-19. Two parts of the recommendation above change.

1. **It runs as a weekly job in `.github/workflows/drift.yml`, not at each
   release cut.** Twenty releases were tagged from 2026-09-27 to 2026-10-19
   (v0.5.16 to v0.5.35), ten of them on 2026-10-18 and 2026-10-19 alone. The
   pages change over weeks: the fastest change seen took 18 days. So a release
   step would run between about 18 and 90 times for each page change, and
   each run costs a step in a release thread. `drift.yml` already
   has a weekly schedule (the `order` job's Monday 06:00 UTC cron), already
   reports without gating, and already needs the network. And
   `tools/main_ci_status.py` already names each red `drift.yml` job in every
   session's start digest (`PL-JTWV`), so a page change reaches every session
   within a week without anyone remembering to run anything. The script still
   runs by hand from a clone, for a session about to rely on a quotation.
2. **It reads the quotations from a record, not by searching for quoted text
   near a link.** The record is a small data file under `tools/`. Each entry
   names the file, the page and the quoted string. A search guesses which
   quoted strings are quotations, and this repository quotes its own terms
   often, so the search would raise false alarms or miss a quotation whose link
   sits a paragraph away. `CLAUDE.md` § "Architecture and development
   discipline" says to write the one record and read it rather than a sharper
   heuristic. The script checks each entry in both directions: the string is
   still in the file, and it is still on the page after whitespace, links,
   backticks and emphasis are normalized. So a quotation edited in the file
   without its entry is reported too. PL-124X's 16 strings, as corrected, seed
   the record.

What the job reports is a lead and not a verdict. When it goes red, a session
reads the page and decides whether the rule that rests on the quotation still
holds. A quotation the page changed is corrected, or its claim is withdrawn,
under an item of its own.

**Done when (decided).** `tools/doc_quote_check.py` and its record exist, with
PL-124X's 16 strings as the record's entries. A `doc-quotes` job in
`drift.yml` runs it on the weekly schedule and on `workflow_dispatch`. Its unit
test, `tests/unit/test_doc_quote_check.py`, is listed under `workflow_paths` in
`docket.toml` and runs on fixture pages without the network. `docs/apparatus.md`
lists the script.
