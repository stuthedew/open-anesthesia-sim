---
id: PL-124X
title: The quotations of Claude Code's documentation already recorded in live documents were never checked against the pages: some came through WebFetch, which returns a model's answer rather than the page (PL-B1BW), so each quotation in the standing documents and open items citing code.claude.com should be compared with the page's .md and corrected where it differs
priority: P3
effort: M
status: done
classes: docs
touches: docs/apparatus.md, docs/maintainer.md, docs/resident-instructions.md, .claude/skills/docket/SKILL.md, .claude/hooks/webfetch-quote-note.sh, docs/items
added: 2026-10-01
closed: 2026-10-19
payoff: the rules resting on Claude Code's documentation rest on what its pages say, not on a summarizing model's paraphrase
verify: grep -qE '^\*\*Compared [0-9]{4}-[0-9]{2}-[0-9]{2}\.\*\*' docs/items/PL-124X*.md
---

**Problem.** The quotations of Claude Code's documentation already recorded in live documents were never checked against the pages: some came through WebFetch, which returns a model's answer rather than the page (PL-B1BW), so each quotation in the standing documents and open items citing code.claude.com should be compared with the page's .md and corrected where it differs

**Why it matters.** Rules here rest on quoted sentences from Claude Code's documentation - the compaction cap opening `.claude/skills/docket/SKILL.md`, the `env` lines in `docs/maintainer.md` - and `PL-B1BW` showed WebFetch can put words into a quote. A rule built on a misquote is obeyed by every session and checked by none.

**Done when.** Each quotation of code.claude.com in the four live files below and in every open item has been compared with the page's `.md`, each that differs is corrected or its claim withdrawn, and the comparison is recorded here under a `**Compared <date>.**` heading with its count.

**Reproduced 2026-10-01.** Four live files outside `docs/items` cite code.claude.com: `docs/ARCHITECTURE.md`, `docs/maintainer.md`, `docs/resident-instructions.md` and `.claude/skills/docket/SKILL.md` (`docs/pr-bodies/733.md` is a record and is left alone). The `.md` form answers from a cloud container: https://code.claude.com/docs/en/skills.md returned HTTP 200.

**Generator check.** `PL-B1BW` (done) fixed how a quote is fetched, and this backfills what was fetched before it: bookkeeping. If the comparison finds two or more misquotes, WebFetch's summary is a fact misread by two or more items with no head, and is recorded as a generator then.

**Re-pointed 2026-10-11 (`PL-KRGY`).** The one quotation `docs/ARCHITECTURE.md`
carried, of Claude Code's protected paths, moved with the hooks section to
`docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)", so `touches` names that
file in its place and the four live files are now it, `docs/maintainer.md`,
`docs/resident-instructions.md` and `.claude/skills/docket/SKILL.md`.
`docs/ARCHITECTURE.md` cites code.claude.com nowhere.

**Re-confirmed 2026-10-19, and widened.** The brief's list of live files was
short. A grep for code.claude.com outside `docs/items` and `docs/pr-bodies` on
2026-10-19 also found `.claude/hooks/` (six files) and
`tools/rules_paths_check.py`. Of those, only
`.claude/hooks/webfetch-quote-note.sh` quotes a page, so `touches` adds it. The
others cite a page for a claim without quoting it.

**Compared 2026-10-19.** Each page was fetched as markdown with `curl` from
`https://code.claude.com/docs/en/<page>.md`, never through WebFetch. A script
then looked for each quoted string in the page after collapsing whitespace and
removing links, backticks and bold markers. 16 quoted strings were compared:
13 in the four live files, and 3 in `webfetch-quote-note.sh`. 12 were on the
page as quoted, and every cited section heading still exists.
`docs/apparatus.md` quotes nothing: its claim about protected paths, that an
allow rule does not lift the check, matches the page. Four strings, in
three passages, were not:

1. `docs/resident-instructions.md`, the constraint that decides most routing
   cases. It quoted a path-scoped rule as one that "triggers when Claude reads
   files matching the pattern, not on every tool use". The memory page now
   says "A path-scoped rule loads when Claude uses the Read, Write, or Edit
   tool on a matching file", and also on a Bash read. Corrected, with one added
   sentence on why the conclusion still holds: a rule that loads with a write
   arrives after that write's content was composed. `CLAUDE.md` repeats the
   old claim, which is filed as `PL-PDBM` because it is a resident-set edit.
2. `docs/resident-instructions.md`, the consistency quotation. It read "if two
   rules contradict each other"; the page says "if two instructions contradict
   each other". Corrected.
3. `.claude/hooks/webfetch-quote-note.sh`. Its two quotations of the WebFetch
   behaviour section, a "small, fast model" and a truncation limit, are gone.
   The page now says the prompt runs "in a separate model call". Corrected in
   the comment. The hook's output still calls the result "most likely a small
   model's answer". That is the hook's message rather than a quotation, and
   its point, that the result is a model's answer and not the page, still
   holds.

The open items were compared too. Two cite code.claude.com: this one, and
`PL-NZC0`, whose claims about the Projects page (the **Merge it** button, the
Overview's states, a new project's low conversation effort) match the page.
Neither quotes it.

**Generator check, answered.** The brief asked for a head if two or more
quotations were wrong. Four strings were, but they are not one misread
mechanism. Passage 3 had been read from the page's own markdown on
2026-10-01, so the page changed under it. That is drift, not a WebFetch
paraphrase. The other two date from 2026-09-15 (#622), before `PL-B1BW`, and
nothing recorded says how they were fetched. No item holds any of the four, so
there are no members for `root-cause-of:`. The WebFetch half is already met
by `PL-B1BW`'s hook. The drift half is filed as `PL-S7LT`, a decision on
whether to compare again at each release.
