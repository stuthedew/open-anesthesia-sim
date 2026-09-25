---
id: PL-HJ8G
title: doc_check's code-span path check fails a document that names a file which deliberately does not exist - 'This project has no `setup.py`', a planned tool in ROADMAP.md, a deleted file - the documents' twin of PL-3NKZ
status: untriaged
feature: exact-gates
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-25
---

**Problem.** doc_check's code-span path check fails a document that names a file which deliberately does not exist - 'This project has no `setup.py`', a planned tool in ROADMAP.md, a deleted file - the documents' twin of PL-3NKZ

Reproduced four: a negated mention, a planned `tools/unit_suffix_check.py`, a deleted file, and `package.json`. PL-3NKZ covers the same class in items only.

**Why it matters.** The check infers an existence claim from a code span; a sentence saying a file does not exist is the opposite claim.

**Done when.** A documented marker, or a negation/plan cue read as an advisory rather than an error, lets these pass; a test holds each.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
