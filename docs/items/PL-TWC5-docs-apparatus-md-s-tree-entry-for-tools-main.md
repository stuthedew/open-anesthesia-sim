---
id: PL-TWC5
title: docs/apparatus.md's tree entry for tools/main_ci_status.py and its paragraph listing the lines the script prints both leave out the failed drift.yml line PL-JTWV added; left out of PL-JTWV because the other workflow thread's #1601 holds docs/apparatus.md
priority: P3
effort: S
status: done
classes: docs
touches: docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-19
payoff: docs/apparatus.md lists every line the session-start CI script prints, the drift line included
verify: grep -q 'PL-JTWV' docs/apparatus.md
---

**Problem.** docs/apparatus.md's tree entry for tools/main_ci_status.py and its paragraph listing the lines the script prints both leave out the failed drift.yml line PL-JTWV added; left out of PL-JTWV because the other workflow thread's #1601 holds docs/apparatus.md

**Why it matters.** `docs/apparatus.md` is where a session looks up what the
session-start digest's lines mean. Both places list the lines
`tools/main_ci_status.py` prints, so a reader meeting the drift line finds no
entry for it there, and the paragraph's list reads as complete without it.

**Done when.** The tree entry at the top of `docs/apparatus.md` and the
paragraph that begins "`tools/main_ci_status.py` gates nothing" each name the
line for a failed `drift.yml` run, with `PL-JTWV` beside it. Start it only
once #1601 has merged.

**Generator check.** Not an instance of a closed head's fact: a docs sweep held back by a file another open pull request holds, not a reader inferring a fact.
