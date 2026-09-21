---
id: PL-MSFB
title: PL-6194's verify: command still uses [(] and [)] to work around the math check that PL-WTQ1 fixed, and WORKING_NOTES.md:504 still uses backticks to work around PL-KJ63
priority: P3
effort: S
status: ready
classes: defect, docs
feature: dev-tooling
touches: docs/items/, docs/WORKING_NOTES.md
added: 2026-09-13
verify: python3 tools/doc_check.py check && grep -qF '"~88-256 B each" above' docs/WORKING_NOTES.md
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

**Triaged 2026-09-13, and the line number in **Where** was already stale.** The
second workaround is at `docs/WORKING_NOTES.md:524`, not 504 - it reads
`` `~88-256 B each` above `` and should read `"~88-256 B each" above`. Line
numbers in that file moved on 2026-09-13; find it by the figure, not the line.

`PL-KJ63`'s fix is what makes the quoted form safe again: `CITATION_RE`'s
`directed` branch must now open on a letter or a code span, and `~` is neither,
so the quotation is no longer read as a section citation. That is checkable
rather than assumed - the `verify:` command runs `doc_check` alongside both
greps, and was run first: it exits 1 today.

**Sequencing stands as the brief has it.** The `PL-6194` half is only doable
while that item is open, so it rides whoever starts it; the
`docs/WORKING_NOTES.md` half is independent and can land any time.

**Narrowed to the live half, 2026-09-21 (`PL-PT7M`'s re-judging pass).** The
`PL-6194` half is struck, on two grounds that agree. This brief already named
the first: "`PL-6194` is an open Gate 1 entry ... a closed item's `verify:` is a
record and is never rewritten, but an open one's is writable - so this is only
doable while `PL-6194` is open". `PL-6194` has since closed `done`, so the
item's own stated condition has expired. `.claude/rules/citation-drift.md`'s
closed-brief clause reaches it independently: a `done` brief is a historical
record, and a workaround preserved in one records what the checks demanded at
the time, which is the correct meaning to leave in place.

What survives is the `docs/WORKING_NOTES.md` half, unchanged and still failing
its command: the figure at what was `:504` and is now found by searching for
`~88-256 B each` sits in backticks to work around a `CITATION_RE` branch
`PL-KJ63` has since fixed, and should read `"~88-256 B each" above`. The
`verify:` command has been trimmed to that half - its third clause grepped
`PL-6194`'s file and can no longer be satisfied by anything this item should
do. The title still names both halves; this note is the correction, since
renaming an item file breaks the `touches` and `verify:` lines that point at
it from elsewhere.

