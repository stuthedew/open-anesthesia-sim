---
id: PL-F7Z6
title: docket's vcs._superseded and _standing call a change that only removes lines removals-only, so a ref that cuts a line out of a continued paragraph or a bracketed list reads as superseded or behind though it holds a statement the base lacks; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests, subprojects/docket/README.md, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's change-record slice, 2026-10-05
added: 2026-10-04
closed: 2026-10-05
pr: 1379
payoff: a branch whose copy cut a line out of a paragraph or an element out of a bracketed list is still reported as holding work, by orphaned, stranded and the already-edited mark, instead of read as holding nothing the base lacks
verify: grep -q 'superseded, a line cut out of a continued paragraph' tests/unit/test_doc_check.py && grep -q 'standing, a line cut out of a continued paragraph' tests/unit/test_doc_check.py
---

**Problem.** docket's vcs._superseded and _standing call a change that only removes lines removals-only, so a ref that cuts a line out of a continued paragraph or a bracketed list reads as superseded or behind though it holds a statement the base lacks; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

The compared file's own format decides what a statement is: a CommonMark paragraph continues across lines (§ 6.7), and a Python bracket joins its lines (Language Reference § 2.1.6). Both docstrings state the line test as their rule ("deletes lines and adds none, so the base holds everything the ref holds and more").

- `_standing`: base "**Decision.** Run the full suite", "before every commit,", "except a commit touching only docs/items/."; a ref that drops the middle line reads `behind`, though it now holds a different rule the base does not.
- `_superseded`: a ref dropping that middle line, or `"b",` from `ALLOWED = (` / `"a",` / `"b",` / `)`, reads both paths as superseded.

Callers: `stranded`, `orphaned`, `landed_whole` (which feeds the RESTART or MERGE call) and `claims._editing`. **The fix is to decline, not to compare statements:** comparing statement sets says `ahead` wrongly for nine live copies (`PL-YBFB` on eight refs, `PL-JW9J` on one) where the base inserted lines into an existing paragraph, and content alone cannot tell a ref that cut a line from a base that extended the statement. The readers' own cost model settles the direction - "a path wrongly called superseded would hide work nothing merged" - so where the line test says removals-only but the ref holds a statement the base lacks, the answer is outstanding. Latent: of 236 removals-only copies on today's refs, none holds a statement the base lacks, and none of the nine reaches `_standing`.

**Why it matters.** Three reports read either answer as "the base already
has this": `orphaned`, which names a branch whose work the base took only part
of; `stranded`, which names an item whose substance sits on a branch; and
`claims._editing`, the "already edited on" mark that tells a triage pass to
leave an item to the branch holding it. A ref that cut a line out of a
paragraph or an element out of a bracketed list - a rule narrowed, an
exception dropped, an allowed value withdrawn - drops out of all three
silently, which is the direction both docstrings say the reading must never
fail in: a path wrongly called superseded hides work nothing merged, where one
wrongly left outstanding costs a reader one diff. `landed_whole` calls
`_superseded` as well, but its verdict reads only the landed half, so no
answer of it moves.

**Reproduced 2026-10-05, at triage.** On `main` at `b67dace8`, under python3
3.11.15 and git 2.43.0: the item paragraph above, against a copy dropping its
middle line, gave `_standing` `behind`; with both copies committed, beside an
`allowed.py` whose ref drops `"b",` from `ALLOWED = (` / `"a",` / `"b",` /
`)`, `_superseded` gave both paths superseded. The nine copies are the
closure case's, not the removal case's: eight still stand (`PL-YBFB` on seven
refs, `PL-JW9J` on one), each differs from the base in `status:` alone and in
no line the base lacks, and each reads `behind` by closure, while holding one
paragraph the base has since extended.

**Done when.** `_superseded` calls a path whose change from the base only
removes lines superseded only where every statement the ref's copy holds is
one the base's copy holds too, read in the path's own format: a Markdown
file's front-matter fields as `docket.model` folds them and its body's
statements as `docket.markdown.statement_lines` reads them, each fence whole
and each under the list items holding it; a Python file's statements as the
parser reads them, each under the clauses holding it. A ref that deleted the
path holds nothing and stays superseded. A format none of those readers
reads, a copy its reader declines (a front-matter line no field reads, a
block list or a block scalar, source the parser refuses) and a blob git does
not answer for each leave the path outstanding. `_standing` answers `behind` by removal on the same
test, and `ahead` where the ref's copy holds a statement the base's lacks.
Its closure case stays a line read: it is a reading of fields rather than of
a removal, and a statement read there would call the eight copies above
`ahead` the moment one reached it. `PL-R417`'s guard gains a case per reader
and form, each failing on main's reader, and one per reader pinning a whole
statement's removal as superseded and behind.

**As built, 2026-10-05.** `vcs._holds_nothing_more` reads both copies of a
path whose tip diff only removes lines, and `_superseded` calls the path
superseded only where every statement of the branch's copy is one of the
base's; `_standing`'s removal case asks the same of an item's two copies, and
its closure case stays a line read. Each statement is read in its place, which
the triage's line reads did not reach. A Markdown body statement carries the
marker line of every list item holding it (CommonMark 0.31.2 § 5.2), so a
sub-item whose parent's line was cut reads as moved. A Python file is read with
`ast` rather than `docket.python`'s logical lines: each statement whole, under
the header and clause of every compound statement holding it (Language
Reference § 8), because a logical line at its indentation cannot see an
`else:` cut from over its suite, which moves the suite into the clause above,
or a decorator cut from its definition. The parser refuses syntax newer than
the interpreter running it, which reads as a decline: 2 of the repository's
226 Python files under 3.11. Nothing a caller answers moved: on the 9 refs of
2026-10-05, `stranded`, `orphaned`, `claims.holdings`' editing marks and
`landed_whole` print the same under main's reader and this one. Of the 2,522
removals-only copies between main and those refs, 63 now read outstanding (47
Python, 7 Markdown, 9 in a format no reader here reads), each a statement the
base has extended since or an unread format, and none is a path a caller asks
about. `PL-R417`'s guard gained eight cases that fail with main's `vcs.py`
swapped in and three pins that pass on both; `test_vcs.py` holds each silence
of the read to an outstanding path, and a deleted copy to a superseded one.
The `orphaned` test of supersession on the base now hands its fake git both
copies, where it had passed on a `show` the fake never answered.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
