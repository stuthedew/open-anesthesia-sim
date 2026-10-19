---
id: PL-FYV7
title: verify.py sanctioned_queue_edit guesses which tool wrote a queue edit outside touches from the diff's shape and respells the pr:/recurrences: grammar in its own regexes, where a trailer that record and new stamp on their commits would be a record
priority: P3
effort: M
status: ready
classes: defect
feature: recorded-not-inferred
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the audit reads which command wrote a queue edit from the commit that wrote it, so a new write shape costs no item
verify: grep -q 'def test_a_recurrence_append_is_judged_by_the_models_grammar' subprojects/docket/tests/test_verify.py
---

**Problem.** verify.py sanctioned_queue_edit guesses which tool wrote a queue edit outside touches from the diff's shape and respells the pr:/recurrences: grammar in its own regexes, where a trailer that record and new stamp on their commits would be a record

**Recorded alternative, from the 2026-10-01 survey.** Have `docket record` and `docket new` stamp their commits with a trailer the audit reads. Shape A: the tool that wrote the edit is known at the write and recorded nowhere.

**Why it matters.** `sanctioned_queue_edit` admits a queue edit outside an item's `touches` when the diff looks like what `docket record` or `docket new` writes, so it respells the `pr:` and `recurrences:` grammar in its own regexes and each new write shape costs an item per audit - `PL-MB2W`'s mechanism on a different fact. The fact, which command wrote the edit, is known at the write and recorded nowhere.

**Reproduced 2026-10-01.** `subprojects/docket/src/docket/verify.py:1805-1846` reads `PR_LINE_RE`, `RECURRENCE_LINE_RE` and `RECORD_NAME_RE` over the added lines to name the writer.

**Checked 2026-10-19, and re-scoped.** A worker sent to build the trailer
stopped, and the reasons hold on a read of the tree. First, `docket new` and
`docket record` write files and make no commit, so there is no commit for
them to stamp. Making them commit would change the capture and close-out
workflow, which is far more than this item is worth. Second, anyone who writes
a commit can type a trailer, the worker being audited included. If the audit
trusted the trailer ahead of the diff, a worker could sanction any edit
outside its `touches`, such as a `status` change. If the audit still checks
the diff, the trailer adds nothing. So the trailer route is refused. The
grammar half is mostly done already: #1389 (fe2e5132) removed `PR_LINE_RE`
and `RECURRENCE_LINE_RE`, and the audit now reads both copies of an item
through the item parser. One copy is left. `RECURRENCE_ENTRY` in
`subprojects/docket/src/docket/verify.py` spells the `recurrences:` entry
grammar again, beside `model.recurrences_of` and `model.recurrence_faults`,
which `CLAUDE.md`'s one-source-of-truth rule refuses. This session decided the
re-scope itself, because its blast radius is one item's disposition.

**Done when.** `verify.py`'s recurrence-append check judges each entry by the model's own reading (`recurrences_of` and `recurrence_faults`, or one strict predicate added beside them in `model.py`) instead of `RECURRENCE_ENTRY`, which is deleted. A test pins an append the model reads as a filing, a withdrawn entry followed by a new one, and an entry with an invented clause, which is still refused.

**Generator check.** A one-off. No head's `misread:` states the fact (which command wrote a queue edit) and it has one reader; the mechanism, a reader deriving from diff shape what the writer knew, is `PL-MB2W`'s, but heads compare at the fact. It waited on `PL-KGYT` while that head was live, since the trailer is a new record, which `CLAUDE.md` § "What this project is" captures and does not build while any open item carries `generator: live`; `PL-KGYT` closed spent on 2026-10-01 with no other head live, so nothing holds it now.
