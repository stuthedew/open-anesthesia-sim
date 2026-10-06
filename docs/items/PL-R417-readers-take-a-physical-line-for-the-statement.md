---
id: PL-R417
title: Readers take a physical line for the statement of a format that continues one across lines - a shell script, a Makefile recipe, a folded YAML block, a wrapped Markdown code span or phrase - so each format's continuation rule is met one capture at a time
priority: P1
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tools/required_checks_check.py, tools/rules_paths_check.py, .claude/hooks/shell_split.py, tests/unit, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head by PL-JCS3
added: 2026-10-04
payoff: a statement a shell script, Makefile, workflow or Markdown document continues across lines is read as the one statement its format makes it, or refused by name, so the close-out sweep and the checks stop answering from fragments
verify: grep -q 'def test_candidates_find_a_title_cited_across_a_line_wrap' tests/unit/test_doc_check.py && grep -q 'def test_each_reader_reads_its_formats_continued_statement_whole' tests/unit/test_doc_check.py && grep -q 'recipe commands, ' tests/unit/test_doc_check.py && grep -q 'workflow commands, ' tests/unit/test_doc_check.py && grep -q '^generator: spent' docs/items/PL-R417-readers-take-a-physical-line-for-the-statement.md
root-cause-of: PL-Q9LK, PL-6P6H, PL-G2FY, PL-Z8RS, PL-6SRZ, PL-RR1N, PL-MFVV, PL-TMX9, PL-B1D0, PL-F5B9, PL-XYJF, PL-CL8R, PL-XW87, PL-J503, PL-CFWP, PL-3DD9, PL-2S1G, PL-TY1Z, PL-YSMD, PL-HKHP, PL-5NC3, PL-WF35, PL-FP7J, PL-BLKJ, PL-J0C6, PL-GMR6, PL-VQBY, PL-4ZDZ, PL-GT0J, PL-KT0H, PL-FBWD, PL-F7Z6, PL-V2HK, PL-TC2D, PL-S3XS, PL-4T49, PL-PPNV, PL-97CF, PL-2JYP, PL-WG6S, PL-4MLK, PL-4ZVH, PL-T1X0, PL-BYJ5, PL-0Y7J, PL-T73L, PL-TDVJ, PL-BMZN, PL-P00H, PL-BM8T, PL-HKR5, PL-CK3F, PL-2MLT, PL-CZ28, PL-Z1R7, PL-V7CG, PL-JZNV, PL-B47B, PL-K77Q, PL-X43T, PL-M2J4, PL-5ZZT, PL-YCJJ, PL-24MT, PL-M890, PL-CXK6, PL-FCQP, PL-B83V, PL-2CDW, PL-VJPH, PL-VQ50, PL-M3M4, PL-QSN5
generator: live - every pass over its reach has found readers the last one missed: PL-MFVV after slice 1, PL-TMX9 after slice 3, eight after the TMX9 link, PL-2S1G in link 6, and twenty-five in the last slice's sweep of 2026-10-04, PL-WF35 among them missing an advisory until link 8, then PL-T1X0 and PL-BYJ5, which that day's triage pass put to it, PL-0Y7J and PL-T73L in link 11, PL-TDVJ in link 15, and PL-BMZN, filed beside it and re-read as one by that day's second triage pass; and twenty-five more in the closing sweep of 2026-10-06, PL-P00H and PL-CK3F among them in code merged after the head was filed
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
| `PL-RR1N` | a `verify:` command's `grep -qF` | a paragraph's soft line breaks (CommonMark § 4.8, § 6.8) |

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

**Link 5, `PL-TMX9` and the close-out sweep (`#1349`, 2026-10-04).** Done:
`PL-TMX9`, `required_checks_check._job_name` reading a job's `name:` whole or
refusing it by name, with five `required checks, a job name ...` guard cases,
four failing on main's reader. Not done: the close-out. Before writing why the
mechanism could hand the store no more members, a read-only sweep covered
every reader the 2026-10-04 sweep had not reached - 92 readers across
`tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, and 18 more
modules that read no text in these formats - and reproduced eight more that
take a physical line for a statement their format continues, now members:
`PL-B1D0` (`instructions.parse`, reading live input in `CLAUDE.md`),
`PL-F5B9` (`dead_ends`), `PL-XYJF` (`checks._passage`), `PL-CL8R` (the
release-notes bullet readers), `PL-XW87` (the citation patterns, inside a
blockquote), `PL-J503` (a continued `recurrences:` in `verify`), `PL-CFWP`
(`is_suppression_line`, Python) and `PL-3DD9` (`version_in`, TOML). So
`generator:` stays `live`, and the slice-3 note's "`generator:` is rewritten
`spent` only when those three close" no longer says when the head closes: two
of the three closed, and the sweep added eight.

**Link 6, the Markdown slice (`#1352`, 2026-10-04).** Done: `PL-B1D0`, `PL-F5B9`,
`PL-XYJF`, `PL-CL8R` and `PL-XW87`, and `PL-2S1G`, which the slice found. It
built `roadmap.statement_lines`, one walker of where a CommonMark paragraph
ends, holding the context a pattern cannot see: the list item a line sits in,
a delimiter row under a pipe line, an HTML block's end marker. Checked against
markdown-it-py 4.2.0 over the 2,380 tracked Markdown files, it agrees on every
paragraph but three front-matter blocks markdown-it reads as tables. The
instruction audit and `checks._passage` read through it, `dead_ends` and the
release-notes readers through `document_entry_lines`, the list walker run under
every heading, and the citation patterns through `GAP`. Checking the walker
found `PL-2S1G`: `CONTINUED_LINE` refused every `<` and every run of three
backticks, which split 33 paragraphs of the tracked documents. The guard gained
twenty cases, nineteen failing on main's readers; the twentieth pins a list
nested under a notes bullet, which main read right by reading one line. Over
the tree, doc_check, the possessive check and `bin/docket check` report as
before, and the dead-ends digest is byte-identical. `generator:` stays `live`,
its reason now naming `PL-2S1G`.

**Link 7, the last slice (`#1353`, 2026-10-04).** Done: `PL-J503`, `PL-CFWP`
and `PL-3DD9`, with eight `CONTINUED_STATEMENTS` cases. `sanctioned_queue_edit`
reads an item's `recurrences:` through `parse_item`'s fold; the suppression
check reads a Python file's logical lines through `tokenize`, falling back to a
line at a time, named, for a file the running interpreter cannot parse; and
`version_in` reads through `tomllib`. Then the sweep the next steps asked for:
eight read-only auditors over every reader in `tools/`,
`subprojects/docket/src/docket/` and `.claude/hooks/`, holding the Markdown
readers to `statement_lines`, each case reproduced on bare python3 3.11.15 and
checked against bash and dash, markdown-it-py or PyYAML. It found twenty-five
more readers that take a physical line for a statement their format continues,
now members: in Markdown `PL-TY1Z`, `PL-YSMD`, `PL-HKHP`, `PL-5NC3`, `PL-WF35`,
`PL-FP7J`, `PL-BLKJ`, `PL-J0C6`, `PL-GMR6`, `PL-VQBY`, `PL-4ZDZ`, `PL-GT0J`,
`PL-KT0H` and `PL-FBWD`; in Python `PL-V2HK` and `PL-TC2D`; in YAML `PL-S3XS`,
`PL-4T49` and `PL-PPNV`; in shell `PL-97CF`, `PL-2JYP` and `PL-WG6S`; in a
Makefile `PL-4MLK`; and in a change or a commit record, `PL-F7Z6` and
`PL-4ZVH`. One changes an answer today: `PL-WF35`'s cue patterns miss a wait
wrapped before its id, so `PL-KZ99`'s wait on a done item raises no advisory.
Five are live in form with no wrong verdict (`PL-YSMD`, `PL-VQBY`, `PL-V2HK`,
`PL-FP7J`, `PL-J0C6`) and the rest are latent, so `generator:` stays `live` and
the head stays open. Fifteen other findings are filed outside this head:
`PL-P95F`, `PL-K1D6`, `PL-LRBV`, `PL-BYJ5`, `PL-LNDJ`, `PL-MR8Z`, `PL-GZXY`,
`PL-PZP7`, `PL-T1X0`, `PL-XG77`, `PL-0779`, `PL-WJM4`, `PL-K23D`, `PL-GWQ7` and
`PL-PXT7`. `BRIEF_HEADING` reading a brief's heading by line was weighed and
not filed, since the item format defines those headings by line (`PL-6G8T`).
`docket new` matched twenty of the filings to an item sharing a path. Eighteen
were another reader's fault or another fact, and are withdrawn on this item's
reading. The two onto `PL-848V` were the same fact misread again, so they stand,
and `PL-848V` is recorded as the head they surfaced, for which events a
workflow's `on:` names; `PL-4T49` and `PL-S3XS` are members of both heads.

**Link 8, the Markdown members (`#1358`, 2026-10-05).** Done: the fourteen
Markdown members link 7 found, `PL-TY1Z`, `PL-YSMD`, `PL-HKHP`, `PL-5NC3`,
`PL-WF35`, `PL-FP7J`, `PL-BLKJ`, `PL-J0C6`, `PL-GMR6`, `PL-VQBY`, `PL-4ZDZ`,
`PL-GT0J`, `PL-KT0H` and `PL-FBWD`. It built `docket.markdown`, one
container-aware block reader that reads a document as CommonMark 0.31.2's
appendix "A parsing strategy" does, with GitHub Flavored Markdown 0.29's
tables, and put every Markdown reader the members name onto it:
`statement_lines` and `fences`; `roadmap`'s list, table and heading walkers and
the working-notes threads; the brief prose `checks` reads for labels, markers
and cues; the Symbols table `core_vocabulary_check` reads; and `doc_check`'s
code spans, gate groups, tags region, section titles, markers, links, version
claims and make mentions. It agrees with markdown-it-py 4.2.0 on 2,425 of the
2,428 tracked Markdown files. The other three are front matter whose `verify:`
line holds a pipe, which markdown-it reads as a table over the closing `---`
and cmark-gfm, which this reader follows, as a setext heading, since the two
rows' cell counts differ (GFM 0.29 § 4.10). `PL-WF35`'s cue patterns now read a
wait wrapped before its id, which raised the three advisories triage predicted,
answered on this branch in `PL-KZ99` and `PL-BYMX`. Every other answer over
the tree is as before but the ones the members were filed to change:
`doc_check` reads 68 fewer section titles, each a bold run opening a wrapped
line inside a paragraph, and no citation rested on one; it reads whole the one
DOI link in `docs/MODEL.md` that holds a pair of parentheses; notes by version
claims the same 1,387 ids across the 79 notes files; and the vocabulary check
reads the same 25 Symbols rows. Read through the block reader, `notes_bullets`
raised `StopIteration` on a bullet holding only its marker; it passes over one
now, with a case. The guard gained 58 cases, 47 failing on main's readers; the
other eleven pin a reading main already gave. The 2026-10-04 triage pass
(`#1362`) put two of link 7's other filings to this head, and both are
recorded members: `PL-T1X0`'s fence half, `_hash_headings` reading a `#` line
inside a fence as a heading, which `PL-HKHP` was in docket; and `PL-BYJ5`,
`POSSESSIVE_RE` quoting across a paragraph break, which link 7 placed outside
as the opposite direction, though `PL-4ZDZ` and `PL-FP7J` read past a
statement's end the same way. `generator:` stays `live`.

**Link 11, the last two Markdown members (`#1371`, 2026-10-05).** Done:
`PL-T1X0` and `PL-BYJ5`. `_hash_headings`, and so `_headings`, reads its
headings through `markdown.headings`, as docket's walkers have since
`PL-HKHP`, with a frontmatter block read as nothing, since GitHub renders it as
a table where cmark-gfm reads its close as a setext underline. So a `#` line
inside a fence or a comment answers no `§` citation, and a setext heading
answers one. A link's anchor is held to those headings alone, so one naming a
`**Bold.**` marker is reported, `PL-T1X0`'s other half and not this head's
fact. `POSSESSIVE_RE` reads its quotation a `QUOTATION_CHAR` at a time, any
character but its mark or a line end, or a `SOFT_BREAK`, so it stops at a
paragraph end in a blockquote or out of one. Nothing over the tree moved: the
38 documents keep their 501 headings and 2,325 section titles, and the quoting
sources, none declined under the project interpreter, keep their 14
possessive quotations. The guard gained ten cases, four `section titles, `,
one `links, ` and five `possessive citations, `; six fail on main's readers,
and four pin a reading main already gave, the frontmatter and the possessive's
soft break, blockquote and list-item wraps. It found two more members, filed
and recorded here: `PL-0Y7J`, six more `doc_check` heading readers that match
`HEADING_RE` a line at a time, and `PL-T73L`, the four section and
quoted-source patterns that quote across a blank line as `POSSESSIVE_RE` did,
where a bound alone would leave an unclosed quotation unread, so its fix needs
a refusal by name. Filed beside them and not a member: `PL-9XP0`, an anchor
slug that is not GitHub's. `generator:` stays `live`.

**Link 12, the Python slice (`#1374`, 2026-10-05).** Done: `PL-V2HK` and
`PL-TC2D`. It built `docket.python`, docket's one reading of where a Python
statement starts and ends: `read_logical_lines` reads source into logical
lines through `tokenize`, each string one piece however the tokenizer split it,
and raises where the tokenizer refuses, an error token included, which 3.11
hands back where 3.12 raises. `doc_check`'s test definitions and changed
definitions read a Python file's `def` and `class` statements through it, so a
`def` inside a string is none, an `async def` test is one, and a changed row
counts toward the definition whose statement spans it, a wrapped signature's
continuation line included. A citation only a file the tokenizer refuses may
define is declined, and the candidates sweep reads such a file's changed lines
a line at a time and says so. `verify`'s assertion check reads a file the
running interpreter cannot parse through the tokenizer, every version alike
(project owner, 2026-10-04, ratified, over keeping the line fallback), and the
suppression check reads every file's logical lines through it, parsing only to
name the file; both name such a file read through the tokenizer, and only a
file the tokenizer refuses is read line by line. Nothing over the tree
moved: the tokenizers of 3.11, 3.12, 3.13 and 3.14 split the 225 tracked Python
files into the same 67,740 logical lines and 8,272 definitions, the statement
reader and `ast` find the same 11,007 assertions under 3.14, and the test
suites define the same 4,563 test names read either way. Replayed under 3.11
over `main`'s 15 non-merge commits that change `app_metadata.py` or
`bookmarks.py`, both checks give `main`'s verdict and page on every one, but
for the label on the nine that read a copy 3.11 cannot parse. The guard gained
ten cases, three `assertions, `, one `suppressions, `, three
`test definitions, ` and three `changed definitions, `, each failing on main's
readers. No new member was filed. `generator:` stays `live`.

**Link 13, the YAML slice (`#1376`, 2026-10-05).** Done: `PL-S3XS`'s run-step
half and `PL-PPNV`. `required_checks_check.steps` is the one reader of a
workflow's steps, beside `triggers` for its `on:`: it walks `jobs:` to each
job's `steps:` list, passing every value over by its indentation alone, and
gives each step's keys with the line and column each opens on. `doc_check`'s
`workflow_commands` reads a `run:` there and nowhere else, so a `run:` inside
another key's block scalar, an action's `with:` or `defaults:` is no step. A
step written as a flow mapping is refused by name, as is a job or a `steps:`
written on its key's line, and the steps around it are read on. Where the jobs
open and what key a block mapping's line opens are each read by one function
the older job and trigger readers now share. `rules_paths_check.entries`
refuses by name a `- ` line under `paths:` at another indentation than the
list's first item, which YAML joins into the glob above it or refuses. Nothing
over the tree moved: the six workflows' 66 commands read the same, none
declined, and `.claude/rules/` keeps its 25 globs. The guard gained three
cases, two `workflow commands, ` and one `rules paths, `, each failing on main's
readers. Filed beside it and not a member: `PL-GVDP`, a trailing comment read
into a `paths:` glob, which is where a value ends on its line rather than
across lines. `generator:` stays `live`.

**Link 14, the shell slice (`#1377`, 2026-10-05).** Done: `PL-97CF`,
`PL-2JYP` and `PL-WG6S`, each against bash 5.2.21 and dash 0.5.12. Both shell
lexers, the hooks' `.claude/hooks/shell_split.py` and docket's `shell.py`, read
an operator a backslash-newline splits as the one operator, an unquoted
here-document's body in logical lines, bash followed where dash compares the
first physical line, and a `${...}` to the `}` that closes it. docket's also
reads `case`, `(( ))`, `$(( ))` and `[[ ]]` carried across lines, and hands
`fixture_id_check` the text of a `.sh` file as bash reads it. The two lexers
were fixed in place, and merging them is filed beside the fix as `PL-JNYL`
(project owner, 2026-10-05, ratified, over merging them in `#1377`). Nothing
over the tree moved: the 1,611 `make` mentions in tracked Markdown, the 66
workflow commands and the 1,645 `verify:` fields read the same; the five fence
lines whose words moved are GitHub `${{ }}` expressions in two item briefs, none
a command; and no tracked `.sh` file holds a backslash-newline bash removes.
The guard gained sixteen cases, eight `hook commands, `, seven `shell lines, `
and one `fixture ids, `, each failing on main's readers, and the three guards'
tests run the reshaped commands end to end. No new member was filed.
`generator:` stays `live`.

**Link 15, the Makefile slice (`#1378`, 2026-10-05).** Done: `PL-4MLK`.
`_make_lines` reads a `define` directive, after any modifier GNU make 4.3 takes
ahead of it (`export`, `override`, `private`), through the `endef` closing it as
one statement, its body in logical lines as `do_define` in make 4.3's
`src/read.c` reads them, so no rule, recipe line or command in a body reaches
`make_targets`, `_target_recipes` or `_recipe_commands`. A `define` no `endef`
closes, one naming no variable and one led by a tab are declined by name, and
the four checks reading the Makefile say what went unchecked. Nothing over the
tree moved: the Makefile holds no `define`, and its 477 logical lines, 10
targets and 37 recipe commands read the same. The guard gained thirteen cases,
three `make targets, `, three `target recipes, `, four `recipe commands, ` and
three `make lines, `, ten failing on main's reader and three pinning a reading
main already gave, and a test holds each of the four checks to its decline. One
member was filed, `PL-TDVJ`: `make_targets` ends a rule at a comment line,
where make and `_target_recipes` read on. `PL-BMZN`, a tab-led line outside any
rule read as a recipe line, was filed beside it as a one-off, and `PL-M2RB` was
dropped as `PL-GZXY`'s duplicate, its two further readers folded into that
brief. `generator:` stays `live`.

**Link 16, the change-record slice (`#1379`, 2026-10-05).** Done: `PL-F7Z6`
and `PL-4ZVH`. docket's `_superseded` and `_standing` read a change that only
removes lines as the base holding more only where the branch's copy holds no
statement the base's lacks, each read in its place: a Markdown statement under
the list items holding it, a Python one under the clauses holding it, read with
`ast`, and a format no reader here knows the statements of left outstanding.
`_standing`'s closure case stays a line read. `pr_body_check` reads a recovered
record through `docket.model`'s fold, names a record whose `commit:` it cannot
read, and strips a trailer with the lines git folds into it. Nothing a caller
answers moved: on the day's 9 refs every answer of `stranded`, `orphaned`,
`claims.holdings` and `landed_whole` is the same under main's readers and these,
and the 265 records read the same. The guard gained thirteen cases: seven
`superseded, `, one `standing, `, one `recovered records, ` and one `appended
trailers, ` fail on main's readers, and three pin a whole statement's removal
as superseded or behind. No new member was filed; `PL-BMZN` joined `root-cause-of:`, re-read as
a member at the day's second triage pass (`#1380`). `generator:` stays `live`.

**Link 17, the Markdown members (`#1382`, 2026-10-05).** Done: `PL-0Y7J` and
`PL-T73L`. The six other `doc_check` heading readers walk `markdown.headings`,
and `_provenance_rows` takes its table from `markdown.tables` inside the section
docket's `roadmap._section_end` bounds, so a `#` line or a table that a fence
or a comment holds opens, ends and fills no section; the gate count check takes
docket's `roadmap._subsection_end`, its own copy deleted. `HEADING_RE` and
`TABLE_ROW_RE`, read by nothing after that, left `docket.roadmap`.
`QUOTATION_CHAR` moved from `possessive_section_check` to `doc_check`, and the
four section and quoted-source patterns read their quotations through it, so
each ends with its paragraph; one its paragraph never closes takes the
pattern's `unclosed` branch and is refused by name, at the severity the closed
form carries. Nothing over the tree moved: `doc_check check` reports the same
under main's readers and these, the provenance table reads the same 37 rows,
and over every quoting source, none declined, the five quotation patterns make
the same 1,029, 126, 509, 15 and 14 matches, none of them unclosed. The guard
gained eighteen cases, eight for the heading readers and ten for the
quotations, each failing on main's readers. No new member was filed;
`PL-WJF2`, a closed quotation longer than its pattern's bound passed over
without a word, was filed beside them and is not one. `generator:` stays
`live`.

**Link 18, the Makefile members (`#1384`, 2026-10-06).** Done: `PL-TDVJ` and
`PL-BMZN`. `_make_lines` holds which rule is open, as `eval` in GNU make 4.3's
`src/read.c` does: a rule line opens one as `_rule_opened` reads it, and an
assignment, a `define` or a directive ends it, assignments read by ports of
make's `parse_var_assignment` and `parse_variable_definition`. A line led by a
tab is a recipe line only while a rule is open; outside one it is the line its
words make, joined as one, so a `define` led by a tab, which link 15 declined,
opens a variable outside a rule and is a recipe line inside one, as make reads
it. A comment, a blank line and a conditional's directive end
no rule and come back as no statement, so `make_targets`, `_target_recipes`
and `_recipe_commands` end every rule at the same line, where make ends it. A
conditional is read with every branch taken in turn. Two declines are new: a
tab-led line where no rule is open, which make refuses, and one after a branch
that changed which rule is open. Nothing over the tree moved: the Makefile's
477 logical lines are 51 statements, and its 10 targets, 37 recipe commands
and each target's recipe and prerequisites read the same, as does `doc_check
check`; 97 Makefile forms run through make 4.3 read as make reads them. The
guard gained fourteen cases, three `make targets, `, one `target recipes, `,
five `recipe commands, ` and five `make lines, `, thirteen failing on main's
reader and one pinning a reading main already gave, and `make lines, a define
led by a tab` became a reading instead of a decline. A test holds the three
readers to the same recipe lines over six Makefiles, four of which they read
differently on main. No new member was filed: `PL-HR4V`, `PL-GSJ6` and
`PL-HSB3`, filed beside them, read a rule line's grammar, a recipe prefix and a
conditional's branches, none of them where a statement ends. `generator:`
stays `live`.

**Link 19, the closing sweep (`#1386`, 2026-10-06).** Done: the one more sweep of the
same reach the next steps asked for, ten read-only slices over `tools/`,
`subprojects/docket/src/docket/` and `.claude/hooks/`, with the workflows'
`run:` scripts, the Makefile's recipes and the commands in
`.claude/settings.json`, each finding reproduced on `main` at `a76cbf67`
against a reference reader - markdown-it-py 4.2.0, PyYAML 6.0.3, bash 5.2.21
and dash, GNU make 4.3 or `tomllib`. It found twenty-five readers that take a
physical line for a statement their format continues, every one latent, filed
as members with `feature: one-answer`. Thirteen read Markdown: `PL-Z1R7`,
`PL-JZNV`, `PL-B47B`, `PL-K77Q`, `PL-M2J4`, `PL-5ZZT`, `PL-YCJJ`, `PL-M890`,
`PL-B83V`, `PL-2CDW`, `PL-VQ50`, `PL-P00H` and `PL-V7CG`. Six read YAML or
TOML: `PL-BM8T`, `PL-2MLT`, `PL-CZ28`, `PL-CK3F`, `PL-24MT` and `PL-FCQP`. Six
read a shell script, or a format a line-at-a-time tool was pointed at:
`PL-VJPH`, `PL-M3M4`, `PL-QSN5`, `PL-X43T`, `PL-CXK6` and `PL-HKR5`. Two are
in code written after the head was filed, `PL-P00H` (`#1345`) and `PL-CK3F`
(`#1366`), so the head is still being handed members; most of the rest are
forms a link's fix left in the reader it changed, or readers fed by the
head's shared ones, and the remainder older stock no pass had reached.
Thirteen findings were filed beside them and are not members, each a misread
within a line or of the wrong kind of block: `PL-1R9S`, `PL-B53Y`, `PL-HTHC`,
`PL-PV73`, `PL-K02Q`, `PL-1D89`, `PL-JTCQ`, `PL-LCBQ`, `PL-KR6M`, `PL-Y6LP`,
`PL-QYF4`, `PL-CQC9` and `PL-4CJ8`; `PL-1R9S` and `PL-B53Y` read the item
front-matter value grammar, `PL-HXJY`'s fact, and carry its feature. Two more
were folded into the member whose fix removes them: a diff header misread
into `PL-24MT`, and a `*` bullet read as emphasis into `PL-YCJJ`. Under
`PL-61FT`'s rule for gaps found by probing outside a guard's promise, three
were recorded rather than filed: the list of what `shell_split.py` does not
read now says that a `#` inside a backtick opens a comment, a `<<` there a
heredoc of the command around it, and a case pattern's `)` inside a
double-quoted `$( )` ends the substitution, and the floor guard's
`KNOWN_GAPS` holds a heredoc handing the interpreter its script. A newline
after `{` read as `;`, a false refusal of the gate guard's fallback reader, is
left for a session to meet, as that guard's header asks. `docket new` matched
eight of these filings to open items by a path this branch changes rather
than by their problem - `PL-BM8T` to `PL-GVDP`; `PL-X43T`, `PL-VJPH`,
`PL-QSN5` and `PL-1R9S` to `PL-P95F`; `PL-JTCQ` to `PL-PXT7`; and `PL-CZ28`
to `PL-RX0W` - and each was withdrawn because of this paragraph: where a pair
shares a reader, it misreads a different fact. The comment above
`SOFT_BREAK`, which named a list walker that no longer reads `CONTINUED_LINE`,
was fixed in passing, and `PL-4CJ8` holds the four other comments citing
§ 6.7 for a soft break. `generator:` stays `live`.

**Next steps (recorded 2026-10-04, revised by links 8, 11 to 18 and 19, and
on 2026-10-06).** The members the table and the first sweeps named are built
but `PL-RR1N`; the closing sweep's twenty-five are not, so the head is not
spent and keeps its rank. Build them as the earlier links were, a format per
pull request, by moving each caller onto its format's one shared reader rather
than patching a line walk of its own: by their finish lines, nineteen of the
twenty-five route a caller through a shared reader or the standard library's
`json` or `tomllib`, four are defects inside a shared reader, and two are
one-offs. The Markdown thirteen go first, since each reads through
`docket.markdown`'s blocks and statements and the accessor `PL-YCJJ` asks for,
a statement's text with its container markers blanked, serves several. With
them lands `PL-0C2S`, a test holding `docket.markdown` to markdown-it-py in the
test environment, so that the next defect inside the shared reader fails CI
rather than waiting for a sweep (project owner, 2026-10-06, ratified, over the
one comparison of 2026-10-04). Then the YAML and TOML six, each reading its
front matter through one parse, the rule files' through one reader that
`rules_paths_check.entries` and `instructions.parse` both take, for `PL-BM8T`
and `PL-2MLT` (project owner, 2026-10-06, ratified, over patching each reader
in place). Then the shell six, opened by `PL-JNYL`'s merge of the hooks' and
docket's two shell readers, so that `PL-VJPH` and `PL-QSN5` are each fixed
once, in the merged reader (project owner, 2026-10-06, ratified, over keeping
both readers and fixing each, as on 2026-10-05). The readers stay on the
standard library: vendoring markdown-it-py into the tree would replace only
the shared reader, the nineteen callers need moving onto it either way, and
`docket.markdown` was already checked against it on every tracked Markdown
file (project owner, 2026-10-06, ratified, over vendoring it); `PL-0C2S`
failing on the hand-written reader again and again would reopen that. Then
one more sweep of the same reach, with `generator:` rewritten `spent` only
when a sweep finds nothing (the coordinator's brief, 2026-10-04). The head
closes without waiting for `PL-RR1N`, naming it in the reason as Done-when
says (project owner, 2026-10-04, ratified, over waiting for it).

**Done when.** Every reader the table and the sweep name reads its format's
statement whole or declines it by name, each pinned by a test; the guard test
fails a reader that takes a physical line for a continued statement; and
`generator:` is rewritten `spent` with the reason, naming `PL-RR1N` if it is
still open.

**Generator check.** The head: one fact misread by six items, which no head's
`misread:` stated on 2026-10-04 (`PL-JCS3`).
