---
id: PL-J2VF
title: The drift workflow's doc-quotes job failed on main on 2026-11-09 and no item records it: docs/resident-instructions.md quotes a sentence about rules without a paths field that the Claude Code memory page no longer contains
priority: P3
effort: S
status: done
classes: defect, docs
touches: docs/resident-instructions.md, tools/doc_quotes.toml
deferred-from: v0.7.0 - a new problem, not present at the freeze: the drift job first failed on 2026-11-09; apparatus documentation, so the release does not wait on it
added: 2026-11-10
closed: 2026-11-14
pr: 2153
payoff: the drift report on main is green or names only failures an item records, so a new failure is noticed
verify: ! grep -qF 'field are loaded unconditionally' docs/resident-instructions.md
reenters: PL-4FBP
---

**Problem.** The drift workflow's doc-quotes job failed on main on 2026-11-09 and no item records it: docs/resident-instructions.md quotes a sentence about rules without a paths field that the Claude Code memory page no longer contains

**Checked 2026-11-10:** the session-start digest reports that the drift workflow's "doc-quotes" job failed on `main` in run #15 on 2026-11-09 (https://github.com/stuthedew/open-anesthesia-sim/actions/runs/42570703414). `docs/resident-instructions.md` quotes Claude Code's documentation: "Rules without a `paths` field are loaded unconditionally and apply to all files". The audit's reviewer ran `python3 tools/doc_quote_check.py`, which exited 1 and reported that the memory page on code.claude.com no longer contains that sentence. The filing session did not rerun it. No open item names the failure. The three other failing jobs in the digest are from run #11 on 2026-11-01, and `PL-CSK0`, `PL-R74V`, `PL-ZH36` and `PL-DPDG` (done 2026-11-02) record them; they read as failing because those monthly jobs have not run on `main` since.

**Why it matters.** The drift report does not gate anything, so a failure that no item records stays red, and the next real failure looks the same as the old one. The quoted sentence is also this repository's evidence for which rules load in every session.

**Done when.** The quote in `docs/resident-instructions.md` matches what the page says now, or the sentence states the fact without quoting, and the drift workflow's doc-quotes job passes on `main` when run by hand.

**Generator check.** An instance of `PL-4FBP`'s fact (a document sentence against the fact it states), here a quotation of an outside page. The drift job is the check that caught it, so the mechanism worked; the failure only lacked an item.

**Done, 2026-11-14.** The memory page now says "Rules without
[`paths` frontmatter](#path-specific-rules) are loaded at launch with the same
priority as `.claude/CLAUDE.md`." `docs/resident-instructions.md` quotes that
sentence instead, and `tools/doc_quotes.toml` records it. `python3
tools/doc_quote_check.py` reported 15 quotations from 8 pages and 0 problems
on 2026-11-14. The sentence still supports the paragraph's claim that the
three rules without `paths:` load in every session.
