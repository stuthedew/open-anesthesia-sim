---
id: PL-LCBQ
title: doc_check's _defined_tests and _changed_definitions take docket.python's reading of a file at face value on the 3.11 floor, where an f-string nesting its own quote around an unmatched bracket mis-tokenizes without an error and merges the statements after it, though python.py's docstring asks a caller to name such a file; latent
status: untriaged
added: 2026-10-06
---

**Problem.** doc_check's _defined_tests and _changed_definitions take docket.python's reading of a file at face value on the 3.11 floor, where an f-string nesting its own quote around an unmatched bracket mis-tokenizes without an error and merges the statements after it, though python.py's docstring asks a caller to name such a file; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.python`. Its module docstring says a formatted string nesting its own
quote (PEP 701, Python 3.12) mis-tokenizes on 3.11 without an error, so a
caller that could not parse a file names it on its page even where this read
it. `verify` does so. `doc_check`'s `_defined_tests`, which lists the tests a
file defines, and `_changed_definitions`, which names the definitions a diff
changed, use the reading and name nothing.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15:

```text
x = f"{"(" + s}"
def test_ghost(): pass
y = f"{")" + s}"
```

`read_logical_lines` returned the three statements as one logical line with no
error, so `test_ghost` is not a definition, where `ast.parse` refuses the file
on 3.11 and 3.12 and later read three statements. Latent: all 226 tracked
Python files read identically on 3.11 and 3.14, and CI runs `doc_check` under
the project's 3.14 as well as at the floor.

**Generator check.** Not a member of `PL-R417`: the cause is a construct the
floor tokenizer does not support, as in `PL-C45K`, and the module already
declares it.

**Done when.** Both callers name a file `ast` cannot parse on the running
interpreter, as `verify` does, pinned by a test with the input above that
expects the name on 3.11.
