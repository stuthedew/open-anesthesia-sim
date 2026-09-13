---
id: PL-WTQ1
title: doc_check's math-rendering check reads a regex in an item's verify: command as LaTeX and hard-fails
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-03
closed: 2026-09-13
pr: 506
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_frontmatter_is_not_scanned_for_math_delimiters' tests/unit/test_doc_check.py
---

**Problem.** `check_math_delimiters()` scans every line of a Markdown document
for `\(` and `\)` and reports each as math GitHub will not render. It does not
skip an item's YAML frontmatter, so a `verify:` command whose regex escapes a
parenthesis is read as LaTeX and fails `make check` as a hard error.

Hit 2026-09-03 while triaging `PL-6194`. This line, a perfectly ordinary shell
command, produced two errors:

```text
verify: uv run pytest && ! grep -rEq '^ +[a-z_]+=\([a-zA-Z_][a-zA-Z0-9_.]*\),?$' src/ ...
```

**Why it matters.** It is a false positive, not strictness: GitHub does not
render YAML frontmatter as prose — it hides it or shows it as a table — so
there is no math there to render wrongly and nothing for a reader to
misread. The check is right about the body of a document and wrong about the
four or five frontmatter lines above it.

Small blast radius, which is why this is `P3` and not raised as compounding
friction: it fires loudly rather than silently, nobody is routing around it,
and it can only affect a `verify:` command that escapes a parenthesis. The cost
is that the item's author contorts a working regex, or worse writes a weaker
command, to satisfy a check that has no claim on the line. `PL-6194` now uses
`[(]` and `[)]` for exactly this reason, which is a workaround recorded in the
wrong place.

By `CLAUDE.md`'s own standard this is the shape to avoid: "a check that fires
every run without changing a decision is a defect in the check". This one does
not fire every run, but when it fires it changes nothing worth changing.

**Where.** `tools/doc_check.py`, `check_math_delimiters()` — it already skips
code spans through `_without_code()`, so the frontmatter skip belongs beside
that.

**Approach.** Skip the frontmatter region when scanning a document that has
one. `_frontmatter()` already exists in the same file and returns the block, so
this is a bounded change: find where the frontmatter ends and start the math
scan there. Add a test asserting that a `verify:` line containing an escaped
parenthesis is clean and that an escaped parenthesis in the body still fails,
so the fix cannot be over-applied.

**Done when.** An item whose `verify:` command escapes a parenthesis passes
`python3 tools/doc_check.py check`, an escaped parenthesis in a document's body
still fails it, and `tests/unit/test_doc_check.py` covers both.

**Found.** Triaging `PL-6194` after `PL-B7ZV`.
