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
verify: grep -q 'def test_a_queue_edit_is_sanctioned_by_its_trailer' subprojects/docket/tests/test_verify.py
---

**Problem.** verify.py sanctioned_queue_edit guesses which tool wrote a queue edit outside touches from the diff's shape and respells the pr:/recurrences: grammar in its own regexes, where a trailer that record and new stamp on their commits would be a record

**Recorded alternative, from the 2026-10-01 survey.** Have `docket record` and `docket new` stamp their commits with a trailer the audit reads. Shape A: the tool that wrote the edit is known at the write and recorded nowhere.

**Why it matters.** `sanctioned_queue_edit` admits a queue edit outside an item's `touches` when the diff looks like what `docket record` or `docket new` writes, so it respells the `pr:` and `recurrences:` grammar in its own regexes and each new write shape costs an item per audit - `PL-MB2W`'s mechanism on a different fact. The fact, which command wrote the edit, is known at the write and recorded nowhere.

**Reproduced 2026-10-01.** `subprojects/docket/src/docket/verify.py:1805-1846` reads `PR_LINE_RE`, `RECURRENCE_LINE_RE` and `RECORD_NAME_RE` over the added lines to name the writer.

**Done when.** `docket record` and `docket new` stamp their commits with a trailer naming the write, the audit reads the trailer ahead of the shape, and a test pins an edit the trailer sanctions and one it does not.

**Generator check.** A one-off. No head's `misread:` states the fact (which command wrote a queue edit) and it has one reader; the mechanism, a reader deriving from diff shape what the writer knew, is `PL-MB2W`'s, but heads compare at the fact. It waited on `PL-KGYT` while that head was live, since the trailer is a new record, which `CLAUDE.md` § "What this project is" captures and does not build while any open item carries `generator: live`; `PL-KGYT` closed spent on 2026-10-01 with no other head live, so nothing holds it now.
