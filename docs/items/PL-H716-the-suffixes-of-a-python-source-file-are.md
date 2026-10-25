---
id: PL-H716
title: The suffixes of a Python source file are spelled twice, as docket.verify.QUOTING_SUFFIXES and tools/doc_check.py PYTHON_SUFFIXES, both ('.py', '.pyi'); decide whether they are one fact (found measuring PL-3PKN)
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: subprojects/docket/src/docket/python.py, subprojects/docket/src/docket/verify.py, tools/doc_check.py, subprojects/docket/tests/test_verify.py, tests/unit/test_doc_check.py
added: 2026-10-25
closed: 2026-10-25
pr: 1821
payoff: which files are Python source is answered in one place, so a suffix added there reaches verify's suppression and quoting readers and doc_check's removed-definition reader together
verify: uv run pytest -q subprojects/docket/tests/test_verify.py tests/unit/test_doc_check.py -k 'python_source_suffixes or python_source_is_named'
reenters: PL-3PKN
---

**Problem.** The suffixes of a Python source file are spelled twice, as docket.verify.QUOTING_SUFFIXES and tools/doc_check.py PYTHON_SUFFIXES, both ('.py', '.pyi'); decide whether they are one fact (found measuring PL-3PKN)

**What was done.** Both tuples answer one question, which files are Python
source. `docket.verify.QUOTING_SUFFIXES` names the files whose quoting rules
are Python's, and `tools/doc_check.py`'s `PYTHON_SUFFIXES` named the files
whose definitions are read as Python statements. Both mean a module or a type
stub. The fact now lives in `docket.python.SOURCE_SUFFIXES`, beside the
readers of Python source. `QUOTING_SUFFIXES` is an alias of it, kept because
its comment explains why the quoting strip reads fewer suffixes than the
suppression check. `SUPPRESSION_BEARING_SUFFIXES` is built from it, and
`doc_check` imports it.

The 32 bare `".py"` literals in the apparatus were left alone. Each asks a
narrower question, such as whether a file is a module rather than a stub, and
changing one is a decision about that reader, not a copy of this fact.

**Generator check.** Found while measuring `PL-3PKN`'s rule, which compares
plain strings but not tuples. Recorded as `reenters: PL-3PKN`. The tuple
measurement found 2 shared tuples on 2026-10-25, and this was the only one
that was one fact, so comparing tuples would buy one finding for one exemption.
