---
id: PL-R417
title: Readers take a physical line for the statement of a format that continues one across lines - a shell script, a Makefile recipe, a folded YAML block, a wrapped Markdown code span or phrase - so each format's continuation rule is met one capture at a time
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** Readers take a physical line for the statement of a format that continues one across lines - a shell script, a Makefile recipe, a folded YAML block, a wrapped Markdown code span or phrase - so each format's continuation rule is met one capture at a time

**The mechanism.** Six readers took a physical line for the unit of a format
whose grammar lets one statement continue across physical lines, so each read a
fragment as a statement, or declined what it could have read:

| Item | Reader | The format's continuation rule |
| --- | --- | --- |
| `PL-Q9LK` (done) | `workflow_commands`, through docket's `shell.py` | POSIX shell backslash-newline (§ 2.2.1) and here-documents (§ 2.7.4) |
| `PL-6P6H` | `workflow_commands` | a YAML folded block scalar, `run: >` (YAML 1.2.2 § 8.1.3) |
| `PL-G2FY` | `_recipe_commands` | a make recipe line continued by a backslash (GNU make, "Splitting Recipe Lines") |
| `PL-Z8RS` | `_without_code`, `_marks_code` | a code span across a line ending (CommonMark 0.31.2 § 6.1) |
| `PL-6SRZ` | `check_named_tests`'s `NAMED_TEST_RE` | the same; its other half, which documents it reads, is its own |
| `PL-RR1N` | a `verify:` command's `grep -qF` | a paragraph's soft line breaks (CommonMark § 4.8, § 6.7) |

The Python Language Reference § 2.1 names the distinction: a logical line built
from one or more physical lines. `PL-9HD1` (done 2026-09-21) was the same fault
in one format, the item front matter, recorded at that format's altitude.
`PL-JCS3` holds the case for one head rather than six one-offs.

**Why it matters.** Most members are latent or silent: a continued command
compared as a fragment, a TeX delimiter after a wrapped span never checked, a
dead test name nobody is told about. A check passing while its guarantee is
void is the one thing `.claude/rules/apparatus-standard.md` § "The floor"
refuses. And the fault recurs per reader rather than per format: each fix so
far taught one reader one rule, and `PL-Q9LK`'s filed two of the members that
followed it.

**The fix, decided 2026-10-04 by `PL-JCS3`.** Read each format's statement
from one reader of that format, and decline by name what that reader cannot
place, rather than reading a fragment as a statement:

- **Markdown code spans:** `_code_spans`, which already reads a document's
  prose spans whole (`PL-Z8RS`, and `PL-6SRZ`'s wrapped half).
- **Shell:** `docket.shell.script_lines`, since `PL-Q9LK`.
- **Makefile:** one logical-line reader that joins a backslash-newline as make
  does - outside a recipe into one line, inside one handing the shell the whole
  command less each continuation's leading tab - for `_recipe_commands` and
  whatever else the sweep below names (`PL-G2FY`).
- **YAML `run:` blocks:** refuse by name a block scalar the reader does not
  take, `>` first, which `PL-6P6H`'s own Done-when prefers while no workflow
  folds.
- **`PL-RR1N`** keeps the fix its brief names - a check on the admitted `grep`
  shape, written beside `checks.verify_shape_refusal` - since its reader is a
  `verify:` command rather than `doc_check`.

Then a guard, so the next reader cannot repeat it: a test that hands each
reader its format's continuation forms and requires the continued statement be
read as one or declined by name. Its exact form is the build's.

**Done when.** Every reader the table and the sweep name reads its format's
statement whole or declines it by name, each pinned by a test; the guard test
fails a reader that takes a physical line for a continued statement; and
`generator:` is rewritten `spent` with the reason, naming `PL-RR1N` if it is
still open.

**Generator check.** The head: one fact misread by six items, which no head's
`misread:` stated on 2026-10-04 (`PL-JCS3`).
