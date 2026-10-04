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
verify: grep -q 'def test_candidates_find_a_title_cited_across_a_line_wrap' tests/unit/test_doc_check.py && grep -q 'def test_each_reader_reads_its_formats_continued_statement_whole' tests/unit/test_doc_check.py && grep -q 'recipe commands, ' tests/unit/test_doc_check.py && grep -q 'workflow commands, ' tests/unit/test_doc_check.py && grep -q '^generator: spent' docs/items/PL-R417-readers-take-a-physical-line-for-the-statement.md
root-cause-of: PL-Q9LK, PL-6P6H, PL-G2FY, PL-Z8RS, PL-6SRZ, PL-RR1N, PL-MFVV, PL-TMX9
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

**Slice 1, Markdown (`#1332`, 2026-10-04).** Done: `format_candidates`
through `mentions`, `_without_code` and `_marks_code`, `check_named_tests`
(every `DOC_GLOBS` document, names read from `_code_spans`),
`check_bound_families` (members sliced by docket's own `list_entry_lines`, a
lazy continuation declined by name), `MARKER_RE`, `LINK_RE`, `_gate_groups`
and `_withheld_counts` (and through them `check_self_cleared_group`), and the
two HTML-comment markers, declined by name when split. One `SOFT_BREAK` and
`GAP` definition in `tools/doc_check.py` serves every phrase reader,
`STATEMENT_RE` reads a logical line, and `UnreadStatement` carries a decline;
the guard is `CONTINUED_STATEMENTS` in `tests/unit/test_doc_check.py`, keyed
by reader, which each later slice extends. `verify:` was rewritten to require
the guard's `recipe commands, ` and `workflow commands, ` cases, because slice
1 alone passes the command triage wrote and `docket check` refuses an open
item whose command passes; so the Makefile slice keys its cases `recipe
commands, ...` and the YAML slice `workflow commands, ...`. Left: the Makefile
readers (`PL-G2FY` and the sweep's Makefile line) and the YAML readers
(`PL-6P6H` and the sweep's YAML line), one pull request each; `PL-RR1N` keeps
its own fix. The slice also found `PL-MFVV`: docket's own list walker, which
`_list_members` now shares, ends an entry at a lazy continuation line, and its
other readers do not decline it.

**Slice 2, Makefile (`#1338`, 2026-10-04).** Done: `_make_lines` reads a
Makefile's logical lines as GNU make 4.3 does - a recipe line keeps each
backslash-newline and loses each continuation's leading tab, any other line
becomes one, and a comment ending in a backslash takes the next line with it.
`_recipe_commands`, `_target_recipes` and `make_targets` read through it, so
the coverage gate, gate parity and `check_make_targets` read a continued
statement whole. `check_ruff_cache` now reads the shell's words for `ruff
check` and its flag, since a continuation between the two left a pattern over
the text matching nothing, and `_make_mentions` reads a fence through
`script_lines`, falling back to a line at a time where bash cannot read it. The
guard gained eleven cases, each failing on main's reader, one pinning
that a coverage run split in the Makefile alone is still a drift. Closes `PL-G2FY`. Left:
the YAML readers (`PL-6P6H` and the sweep's YAML line), and `PL-MFVV`; `PL-RR1N`
keeps its own fix.

**Slice 3, YAML (`#1339`, 2026-10-04).** Done: `workflow_commands` reads a
step's value through `_run_script`, which reads the two forms the workflows
write - a plain scalar on the key's line, and a literal block (`|`) with its
header's indentation and chomping indicators and comment honoured, ended at the
first line indented less than its content, so a sibling key such as `shell:`
is no longer a line of the script - and declines every other form by name: a
folded block (`>`, `PL-6P6H`), a plain scalar carried onto the next line or
opening on the line after the key, a quoted scalar, and an anchor, alias, tag
or flow collection. The three checks that read it say which step went unread,
and the coverage gate and gate parity draw no conclusion from a side a decline
left incomplete. `_gates_pull_requests`, and `required_checks_check._triggers`,
refuse an `on:` flow collection carried past its line; `_frontmatter` and
`rules_paths_check.frontmatter` close only on a `---` that opens its line;
`rules_paths_check.entries` reads a list past a comment line and refuses a
flow collection or a glob YAML carries onto another line. The guard gained
fifteen cases, each failing on main's readers, and the 66 commands the six
workflows hold read the same before and after. Closes `PL-6P6H`. The slice also
found `PL-TMX9`: `required_checks_check._jobs` reads a job's `name:` from the
key's line, a reader the sweep missed, now a member. Left: `PL-MFVV` (after
`PL-DSMK`'s blank line), `PL-TMX9`, and `PL-RR1N`'s own fix. `verify:` gained
`grep -q '^generator: spent'` on this file, since the YAML slice's guard cases
were the last thing it asked for and `docket check` refuses an open item whose
command passes; `generator:` is rewritten `spent` only when those three close,
so the command passes then and no sooner.

**Done when.** Every reader the table and the sweep name reads its format's
statement whole or declines it by name, each pinned by a test; the guard test
fails a reader that takes a physical line for a continued statement; and
`generator:` is rewritten `spent` with the reason, naming `PL-RR1N` if it is
still open.

**Generator check.** The head: one fact misread by six items, which no head's
`misread:` stated on 2026-10-04 (`PL-JCS3`).
