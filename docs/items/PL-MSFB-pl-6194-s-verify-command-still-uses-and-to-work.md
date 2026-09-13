---
id: PL-MSFB
title: PL-6194's verify: command still uses [(] and [)] to work around the math check that PL-WTQ1 fixed, and WORKING_NOTES.md:504 still uses backticks to work around PL-KJ63
status: untriaged
added: 2026-09-13
---

**Problem.** PL-6194's verify: command still uses [(] and [)] to work around the math check that PL-WTQ1 fixed, and WORKING_NOTES.md:504 still uses backticks to work around PL-KJ63

**Problem.** Two workarounds were written to satisfy checks that have since
been fixed, and both are recorded in the wrong place — in the prose and the
commands themselves rather than in an item — so nothing says they are no
longer needed.

- `PL-6194`'s `verify:` command writes `[(]` and `[)]` where `\(` and `\)`
  would read more naturally, because `check_math_delimiters` scanned YAML
  frontmatter and read the escapes as LaTeX. `PL-WTQ1` fixed that: the math
  scan now starts below the frontmatter.
- `docs/WORKING_NOTES.md:504` writes a measured figure in backticks where the
  sentence quotes it, because a quoted value followed by `above` was read as a
  section citation. `PL-KJ63` fixed that: the `directed` branch of
  `CITATION_RE` now has to open on a letter or a code span.

**Why it matters.** Small, and deliberately so — both workarounds are correct
and neither is failing anything. The cost is that each reads as a deliberate
style choice to the next session to meet it, and `PL-WTQ1`'s brief says
outright that its own workaround is "recorded in the wrong place". Left
standing, they are two pieces of evidence for a constraint that no longer
exists.

**Where.** `docs/items/PL-6194-…md`'s `verify:` line, and
`docs/WORKING_NOTES.md:504`.

**Careful with the first one.** `PL-6194` is an open Gate 1 entry. A closed
item's `verify:` is a record and is never rewritten, but an open one's is
writable — so this is only doable while `PL-6194` is open, and it belongs to
whoever starts it rather than to a separate pass. Worth folding into that item
rather than doing alone.

**Done when.** Both read as they would have been written had the checks never
over-reached, and `make check` is green.
