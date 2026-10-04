---
id: PL-J503
title: docket's verify.sanctioned_queue_edit compares a recurrences: value one diff line at a time, so a capture's append to a value continued on an indented line reads as an ordinary edit outside touches and fails verify; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1353
payoff: a capture's recurrence appended to a value continued on an indented line is read as the append it is, so following the capture rule never fails verify
verify: grep -qF '"queue edit, ' tests/unit/test_doc_check.py
---

**Problem.** docket's verify.sanctioned_queue_edit compares a recurrences: value one diff line at a time, so a capture's append to a value continued on an indented line reads as an ordinary edit outside touches and fails verify; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. In a temporary repository, the append `with_front_matter_field(append=True)` makes lands on the continuation line, so the diff `-  2026-09-03 PL-CCCC` / `+  2026-09-03 PL-CCCC, 2026-10-04 PL-DDDD` reads as '' rather than 'recurrence', an ordinary edit outside `touches` (its verify failure by reading). `parse_item` reads all three entries both ways. Latent: 77 items carry `recurrences:`, all on one line.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, in a temporary repository whose item carries `recurrences: 2026-09-01 PL-AAAA, 2026-09-02 PL-BBBB,` continued by `  2026-09-03 PL-CCCC`, the append `with_front_matter_field(append=True)` makes lands on the continuation line, and `sanctioned_queue_edit` returns `''` where `'recurrence'` is meant; `parse_item` reads all four entries after it.

**Why it matters.** `bin/docket new` appends that entry to whichever item a capture matches, and `CLAUDE.md` makes the capture unconditional, so the first `recurrences:` value continued on an indented line turns a worker following the capture rule into a `REJECT` for an edit outside `touches` - the refusal of correct work `PL-66PR` and `PL-X5JR` each removed once.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `sanctioned_queue_edit` reads the item before and after each of the scope's changes through docket's own front-matter reader, and sanctions a change only where `recurrences:` gained entries at its end and nothing else that reader returns moved, whatever lines carry the value; a `queue edit, ...` case in `CONTINUED_STATEMENTS` pins it.

**Built 2026-10-04 (`#1353`).** `sanctioned_queue_edit` reads each of the
scope's changes to the item - each commit naming it against its first parent,
or the branch against its fork point where none does - as two whole copies,
through `_front_matter_pairs` and `_split_list`, the fold `parse_item` uses
(`_recurrence_appended`, `_recurrences_grew`). It sanctions a change only where
`recurrences:` gained whole entries at its end, each matching
`RECURRENCE_ENTRY`, the earlier ones unchanged, and no other field, unread line
or body line moved; `RECURRENCE_LINE_RE` is gone. Two guard cases, `queue edit,
...` in `CONTINUED_STATEMENTS`, the first failing on main's reader, and
`test_an_append_onto_a_value_continued_on_an_indented_line_is_sanctioned` in
docket's tests, which also holds a second append in its own commit and an
append beside a status edit.
