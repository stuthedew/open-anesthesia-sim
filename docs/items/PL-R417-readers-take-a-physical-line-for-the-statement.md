---
id: PL-R417
title: Readers take a physical line for the statement of a format that continues one across lines - a shell script, a Makefile recipe, a folded YAML block, a wrapped Markdown code span or phrase - so each format's continuation rule is met one capture at a time
priority: P1
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tools/required_checks_check.py, tools/rules_paths_check.py, tests/unit, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head by PL-JCS3
added: 2026-10-04
payoff: a statement a shell script, Makefile, workflow or Markdown document continues across lines is read as the one statement its format makes it, or refused by name, so the close-out sweep and the checks stop answering from fragments
verify: grep -q 'def test_candidates_find_a_title_cited_across_a_line_wrap' tests/unit/test_doc_check.py && grep -q 'def test_each_reader_reads_its_formats_continued_statement_whole' tests/unit/test_doc_check.py
root-cause-of: PL-Q9LK, PL-6P6H, PL-G2FY, PL-Z8RS, PL-6SRZ, PL-RR1N
generator: live - six readers misread it in fifteen days, three on 2026-10-03 alone, each fix taught one reader one format's rule, and the 2026-10-04 sweep found readers no item names in every format the members cover, one live today: format_candidates misses 448 wrapped section citations
misread: Where one statement ends, in a format that lets a statement continue across physical lines
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

**Sweep 2026-10-04: readers no item names.** Classified by a read-only pass
over `tools/doc_check.py`, every case reproduced in memory on a minimal input;
`format_candidates` was then confirmed by reading it and by count. One is live,
the rest latent - no instance in the tree today:

- **Live: `format_candidates`**, the close-out sweep's `candidates` list,
  matches each term against one physical line at a time, so a heading title
  cited across a soft line break is on no line: 448 of the 2,180 `§ "..."`
  citations in the tracked Markdown wrap (counted 2026-10-04). The sweep
  leaves them out, or prints that nothing mentions the term.
- **Markdown, latent:** `_headings`' `MARKER_RE` (a wrapped `**Bold.**` title is
  no section title); `LINK_RE` (wrapped link text goes unchecked);
  `check_gate_counts`, its `_withheld_counts`, and `check_self_cleared_group` (a
  group heading, its count or a `not-delegable` sentence wrapped by a soft
  break); an HTML-comment marker split across lines in `check_prose_provenance`
  and `_absent_paths`; `_list_members` on a lazy continuation line.
- **Makefile, latent:** `make_targets` and `_target_recipes` read a rule's
  prerequisites from its first line only; `check_ruff_cache` reads through
  `_recipe_commands`, so it shares `PL-G2FY`'s fault; `_make_mentions` misses
  `make` continued by a backslash in a shell fence.
- **YAML, latent:** `workflow_commands` reads only a plain multi-line scalar's
  first line, and takes a block header carrying an indicator or a comment
  (`run: |2`, `run: | # why`) for the command; `_gates_pull_requests` misreads
  a flow sequence across lines; `_frontmatter` closes on an indented `---`.
  Outside `doc_check`, `required_checks_check._triggers`, and
  `rules_paths_check.entries` and its own `frontmatter`, have the same shapes.
- **For `PL-6SRZ`:** `check_bound_families` receives test names that
  `list_entries` joined with a space, so a fix that only lets `NAMED_TEST_RE`
  cross a newline does not reach it.

**How the build runs.** One format per pull request, each closing its members:
Markdown first, since `format_candidates` is the one misread live today, then
the Makefile, then YAML. A latent reader may take the decline route - say by
name what it could not read - where reading the form whole costs more.

**Done when.** Every reader the table and the sweep name reads its format's
statement whole or declines it by name, each pinned by a test; the guard test
fails a reader that takes a physical line for a continued statement; and
`generator:` is rewritten `spent` with the reason, naming `PL-RR1N` if it is
still open.

**Generator check.** The head: one fact misread by six items, which no head's
`misread:` stated on 2026-10-04 (`PL-JCS3`).
