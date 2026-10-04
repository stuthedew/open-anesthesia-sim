---
id: PL-J0C6
title: docket's fences.blocks takes a fence-shaped line at any indentation and tracks no container, so a backtick run indented four or more inside a paragraph opens a fence, a fence in a list item runs past the item's end, and a fence behind a block quote's > opens none; live in PL-9TNJ's brief, nothing fires today
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/fences.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: every check that skips a fenced literal skips exactly the fences GitHub renders, inside block quotes and list items as outside them
verify: grep -qF '"fences, ' tests/unit/test_doc_check.py
---

**Problem.** docket's fences.blocks takes a fence-shaped line at any indentation and tracks no container, so a backtick run indented four or more inside a paragraph opens a fence, a fence in a list item runs past the item's end, and a fence behind a block quote's > opens none; live in PL-9TNJ's brief, nothing fires today

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark 0.31.2 § 4.5: a fence's opening and closing lines carry at most three spaces of indentation relative to their container, and the block ends where the container ends; § 4.4, § 5.1, § 5.2. `OPEN_RE` and `CLOSE_RE` accept any indentation by design, and `blocks` tracks no container:

- "See" over "    ```", "make check", "    ```" and "before every commit." gives `Block(1, 3)`, where markdown-it-py 4.2.0 reads one paragraph; with `~~~`, `without_fences` blanks a `docs/NOSUCH.md` citation on the middle line, so the path checks never see it.
- An over-indented closer: "```", "code", "    ```", "more code", "```" closes at line 2, so the literal reads as prose.
- "- an item" over "  ```", "  code" and "A paragraph after the item." runs the fence to the next one: the paragraph is lost and the real code read as prose.
- **Live:** a fence behind a block quote's `>` opens nothing, so `docs/items/PL-9TNJ-report-the-i001-plus-cache-interaction-to.md`:77-85, 94-107 and 111-114 are read as prose by every consumer, though nothing fires on them today. It is the only disagreement between `fences.blocks` and markdown-it across the 2,383 tracked `.md` files; a container prefix rather than a continuation, filed here because the fix is the same container.

Consumers: `checks.py` (278, 376, 418, 3306), `instructions.py`:144, and `tools/doc_check.py` at eight sites. `statement_lines` alone agrees with markdown-it on each input; its callers pass `skip=fenced_lines`.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `fences.blocks` returns `[Block(start=1, end=3)]` for "See" over a four-space-indented fence pair inside the paragraph, `[Block(start=0, end=2)]` for a fence whose over-indented line cannot close it, `[Block(start=1, end=5)]` for a fence in a list item that the item's end closes, and `[]` for a fence behind a block quote's `>`.

**Why it matters.** `fences` is the one reading every reader that skips a literal takes - `checks.py`, `instructions.py` and eight sites in `tools/doc_check.py` - so a fence read in the wrong place blanks prose those checks should hold to the tree, or hands them a literal as prose; `PL-9TNJ`'s quoted fences are read as prose today.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `fences.blocks` reads a fence as CommonMark 0.31.2 § 4.5 does - opened and closed at most three columns into its container, inside a block quote or a list item as readily as outside, and ended by its container's end - and keeps the module's one refusal, that a fence nothing closes before the document ends is read as written; `fences, ...` cases in `CONTINUED_STATEMENTS` pin each form.
