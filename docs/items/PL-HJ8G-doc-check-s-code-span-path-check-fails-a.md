---
id: PL-HJ8G
title: doc_check's code-span path check fails a document that names a file which deliberately does not exist - 'This project has no `setup.py`', a planned tool in ROADMAP.md, a deleted file - the documents' twin of PL-3NKZ
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a document can name a file that is absent, planned or deleted, in the backticks a path deserves, without failing make check
verify: grep -q 'def test_a_file_named_as_absent_is_not_a_missing_citation' tests/unit/test_doc_check.py
---

**Problem.** doc_check's code-span path check fails a document that names a file which deliberately does not exist - 'This project has no `setup.py`', a planned tool in ROADMAP.md, a deleted file - the documents' twin of PL-3NKZ

Reproduced four: a negated mention, a planned `tools/unit_suffix_check.py`, a deleted file, and `package.json`. PL-3NKZ covers the same class in items only.

Re-confirmed 2026-09-25 against 46954a81 in a scratch root: a document saying the project has no `setup.py` fails `check_citations` with the error that it cites a path which does not exist.

**Generator check.** PL-GPJ7's fact: the gate reads a backticked path as a claim that the file exists, and the sentence's own wording - a negation, a plan, a deletion - makes the opposite claim. The head's rule counts a backticked path as explicit syntax, so of this item's two routes the documented marker is the one that keeps the gate exact; the negation cue would be wording, and only an advisory could read it. PL-3NKZ is the same inference facing briefs, and is cheaper settled in the same change.

**Why it matters.** The check infers an existence claim from a code span; a sentence saying a file does not exist is the opposite claim.

**Done when.** A documented marker, or a negation/plan cue read as an advisory rather than an error, lets these pass; a test holds each.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
