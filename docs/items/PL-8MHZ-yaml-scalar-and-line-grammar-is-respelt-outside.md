---
id: PL-8MHZ
title: YAML scalar and line grammar is respelt outside docket.frontmatter and model - required_checks_check's _uncommented, _key and _quoted, rules_paths_check's _unquote, and two block-scalar and node-indicator readers - so [a, "b # c"], 'it''s' and |x each read two ways
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: tools/required_checks_check.py, tools/rules_paths_check.py, tools/doc_check.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/model.py, tests/unit/test_required_checks_check.py, tests/unit/test_rules_paths_check.py, tests/unit/test_doc_check.py, subprojects/docket/tests/test_frontmatter.py, subprojects/docket/tests/test_frontmatter_reference.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1458
payoff: a YAML line or scalar reads the same in docket's front-matter reader and in the checks that read workflows and rules
verify: grep -q 'def test_a_doubled_single_quote_reads_as_docket_reads_it' tests/unit/test_rules_paths_check.py
recurrences: 2026-10-12 PL-4DK2
---

**Problem.** YAML scalar and line grammar is respelt outside docket.frontmatter and model - required_checks_check's _uncommented, _key and _quoted, rules_paths_check's _unquote, and two block-scalar and node-indicator readers - so [a, "b # c"], 'it''s' and |x each read two ways

- Line structure: `required_checks_check._uncommented`, `_closing_quote`, `_item` and `_key` beside `frontmatter.uncommented`, `closing_quote`, `is_item` and `_key`. The quote and item readers agree. On `[a, "b # c"]` frontmatter cuts at `# c"]` and the check keeps the line whole; on `"a\"b": 1` frontmatter names the key `a\"b` and the check raises `Undecidable`; on `[a]: b` frontmatter gives no key and the check `("[a]", "b")`.
- A quoted scalar's value: `model._unquote`, `rules_paths_check._unquote` and `required_checks_check._quoted`. On `'it''s'` model and required_checks read `it's` and rules_paths `it''s`; on `"a\"b"` model reads `a"b`, rules_paths `a\"b`, and required_checks raises.
- Block scalars and node indicators: `model.BLOCK_SCALAR_RE`, `doc_check.BLOCK_HEADER_RE` and `YAML_NODE_INDICATORS`, `required_checks_check.NODE_INDICATORS`. The header grammar agrees; on `|x` required_checks refuses a block scalar while doc_check hands bash the command `|x` and model reads a plain value.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** The two checks read YAML lines and scalars through `docket.frontmatter` and `docket.model`, or `docket` exports what they need, and a test pins each parting input. `fixture_id_check`'s own front-matter readers are `PL-YPLM`'s and `PL-S4JL`'s.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
