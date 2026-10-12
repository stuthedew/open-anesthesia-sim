---
id: PL-S0D4
title: GitHub's file view shows an Error in user YAML box on 656 of 2,124 item files, since their front matter is deliberately not YAML, and docket's README does not say so
priority: P3
effort: S
status: done
classes: docs
touches: subprojects/docket/README.md
added: 2026-10-10
closed: 2026-10-12
pr: 1435
payoff: a reader who meets GitHub's Error in user YAML box on an item finds the README saying it is expected and that docket reads the file as written
verify: grep -qF 'Error in user YAML' subprojects/docket/README.md
---

**Problem.** GitHub's file view reads an item's front matter as YAML, and on
656 of the 2,124 item files on `main` that block is not valid YAML, so the view
shows "Error in user YAML" and the fields as raw text instead of the table it
draws when the block parses. The format is deliberately not YAML
(`subprojects/docket/README.md` § "What the front matter is, exactly"): a value
runs to the end of its line, so a colon and a space inside it are text to
docket and a second key to YAML. Docket reads every such file as written; only
GitHub's display is affected, and the README does not say so, so a reader who
opens an item on GitHub meets an error with nothing to explain it.

**Found 2026-10-10 in `PL-R417`'s closing sweep thread** (link 23), when the
owner asked about the error on GitHub's view of `PL-R417`'s own brief. Its
front-matter line 12 is the `verify:` field, and column 357 is the colon in a
shell-quoted `generator: spent` pattern, which YAML does not read as quoted
because the value does not open with the quote.

**Reproduced 2026-10-10** on `main` at `75e1700d`: PyYAML 6.0.1's `safe_load`
on each item's front matter fails on 656 of 2,124, `PL-R417`'s at line 12,
column 357, with "mapping values are not allowed here", the place and the error
GitHub's view reports.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `safe_load` refuses 681 of
the 2,188 item front matters, and `subprojects/docket/README.md` § "What the
front matter is, exactly" still says nothing of GitHub's view.

**Why it matters.** Everyone who opens an item on GitHub meets an error box on
about a third of the store with nothing saying it is expected, and the natural
reading is that the file is broken; the owner asked about it on `PL-R417`.

**Generator check.** Not a member of `PL-R417`: GitHub reads the block as
another format altogether, not a statement of docket's format across lines, and
the reader is GitHub's, outside the tree.

**Done when.** Docket's README says, beside the format, that GitHub's file view
reads the block as YAML and shows this error where a value is not valid YAML,
while docket reads the value as written. Making the store valid YAML instead
would be a format change across those 656 files and a check to hold it, a new
mechanism the pause holds while a generator is live (`CLAUDE.md` § "What this
project is").
