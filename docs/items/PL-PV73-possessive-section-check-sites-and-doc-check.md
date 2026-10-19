---
id: PL-PV73
title: possessive_section_check.sites and doc_check.check_quoted_sources number a docstring citation's line by counting newlines in the evaluated string, so a backslash-newline inside the docstring reports the line above and a newline escape the line below; latent
priority: P3
effort: M
status: done
classes: defect
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit/test_doc_check.py, tests/unit/test_possessive_section_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
closed: 2026-10-19
pr: 1634
payoff: a docstring finding from the possessive, quoted-source and host-claim checks names the source line the citation or claim stands on, so a session fixing it edits the right line
verify: grep -q 'def test_a_citation_below_a_backslash_newline_is_reported_on_its_own_line' tests/unit/test_possessive_section_check.py && grep -q 'def test_a_citation_below_a_newline_escape_is_reported_on_its_own_line' tests/unit/test_possessive_section_check.py && grep -q 'def test_a_host_claim_below_a_backslash_newline_is_reported_on_its_own_line' tests/unit/test_doc_check.py
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16: a
scratch `tools/m.py` citing `docs/SRC.md`'s heading on source line 5 below a
backslash-newline is reported at line 4, and one citing it on line 4 below a
`\n` escape is reported at line 5.

**A third caller numbers the same way, found at triage 2026-10-11.**
`check_host_claims` adds the row `_docstrings` gives to the line within the
evaluated docstring, so a host claim on source line 5 below a
backslash-newline is reported at line 4. All three read
`_docstrings`, which yields only where each docstring starts.

**Why it matters.** A finding that names the wrong line sends the reader to a
line that does not hold what the message describes, and these are hard
errors a session is told to fix. Latent: three tracked docstrings now
evaluate to a different number of lines than they span, all through newline
escapes (`docket.model`'s `front_matter_spans` and `_read_back`, and
`test_a_cited_section_title_that_wraps_across_lines_is_checked`), and none
holds a finding any of the three checks reports.

**Generator check.** Not a member of `PL-R417`: each citation is read whole,
and only the line the report names is wrong.

**Done when.** Both checks number a finding from the source text rather than
the evaluated value, since the tokenizer gives each string token's own start
and end, pinned by a test with a backslash-newline and one with a newline
escape above a citation. Added at triage 2026-10-11: `check_host_claims`
numbers a docstring's claim from the source text the same way, pinned by a
test with a backslash-newline above the claim.

**Closed 2026-10-19.** `doc_check._docstrings` now gives each docstring with
its lines laid out as the source lays them out. `_string_tokens` collects the
file's string tokens, and `_source_lined` rebuilds the docstring one source
row at a time from them. A backslash-newline keeps its row, and a `\n` escape
stays inside its row. The rebuild falls back to the evaluated value whenever
its text does not match that value exactly, so no finding can come from text
the docstring does not hold. Over the tree on 2026-10-19 no docstring fell
back, and four differ from their evaluated value, all through escapes. The
three callers (`possessive_section_check.sites`, `check_quoted_sources` and
`check_host_claims`) are unchanged and now name the source line. The three
tests the `verify:` names fail on the old code and pass on the new.
