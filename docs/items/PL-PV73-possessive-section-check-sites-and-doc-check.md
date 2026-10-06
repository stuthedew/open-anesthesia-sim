---
id: PL-PV73
title: possessive_section_check.sites and doc_check.check_quoted_sources number a docstring citation's line by counting newlines in the evaluated string, so a backslash-newline inside the docstring reports the line above and a newline escape the line below; latent
status: untriaged
added: 2026-10-06
---

**Problem.** possessive_section_check.sites and doc_check.check_quoted_sources number a docstring citation's line by counting newlines in the evaluated string, so a backslash-newline inside the docstring reports the line above and a newline escape the line below; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/possessive_section_check.py`. `sites` reports each citation at the
docstring's first line plus the newlines before it in the docstring's value,
through `doc_check._line_of`. The value is the evaluated string: a
backslash-newline inside the literal removes a source line from it, and a
newline escape adds one that is not in the source. `doc_check`'s
`check_quoted_sources` numbers its findings the same way, on the same value.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
with a scratch package whose function docstring wraps its first sentence with a
backslash-newline and then, on source line 5, cites another document's section
by a possessive of its path followed by the quoted title: `sites` reported the
citation at line 4. Latent: two tracked docstrings evaluate to a different
number of lines than they span, both through newline escapes, and neither holds
a citation either check reports.

**Generator check.** Not a member of `PL-R417`: each citation is read whole,
and only the line the report names is wrong.

**Done when.** Both checks number a finding from the source text rather than
the evaluated value, since the tokenizer gives each string token's own start
and end, pinned by a test with a backslash-newline and one with a newline
escape above a citation.
