---
id: PL-1Y3L
title: tools/doc_check.py's bound-family check declines a paragraph whose code only an unparsable file may define, and no test pins that path
priority: P3
effort: S
status: ready
classes: test
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-11-10
payoff: a change that lets the documentation check pass a paragraph it could not read fails a test
verify: grep -q 'def test_a_bound_family_paragraph_whose_code_only_an_unparsable_file_defines_is_declined' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's bound-family check declines a paragraph whose code only an unparsable file may define, and no test pins that path

**Why it matters.** `tools/doc_check.py` reports a bound family's paragraph as declined, not passed, when the only Python file that could define a code name it cites does not parse. The code-name reader catches the `SyntaxError`, records the file as unread, and adds every identifier in it to the names it cannot rule out. No test builds that case: on 2026-11-11, `tests/unit/test_doc_check.py` mentioned an unparsable file once, outside the bound-family tests. A change to that branch could turn the decline into a silent pass, and the check would then report a family as held to the tree when it read nothing.

**Done when.** A test in `tests/unit/test_doc_check.py` builds a tree whose only definition of a bound family's code name sits in a file that fails to parse, and asserts that the check declines the paragraph and names the file.

**Generator check.** A one-off: a test gap on one branch of one check. The fact is which code names the tree defines, `doc_check`'s reader is its one home, and no head's `misread:` states a gap in it.
