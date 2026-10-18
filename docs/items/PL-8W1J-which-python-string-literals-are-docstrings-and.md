---
id: PL-8W1J
title: Which Python string literals are docstrings and which modules a Python file imports are each decided twice or more - glyph_check, fixture_id_check and doc_check on docstrings, arming.imported_modules and import_boundary_check.module_imports on imports - and an attribute docstring and importlib.import_module each read two ways
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.28
touches: tools/glyph_check.py, tools/fixture_id_check.py, tools/doc_check.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/python.py, tools/import_boundary_check.py, tests/unit/test_glyph_check.py, tests/unit/test_fixture_id_check.py, subprojects/docket/tests/test_python.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1550
payoff: a Python source's documentation and imports read the same to every check
verify: grep -q 'def test_an_attribute_docstring_is_read_as_the_other_checks_read_it' tests/unit/test_glyph_check.py
---

**Problem.** Which Python string literals are docstrings and which modules a Python file imports are each decided twice or more - glyph_check, fixture_id_check and doc_check on docstrings, arming.imported_modules and import_boundary_check.module_imports on imports - and an attribute docstring and importlib.import_module each read two ways

- Which string literals are docstrings: `glyph_check.documentation`, `fixture_id_check.without_docstrings` and `doc_check._docstrings`. On an attribute docstring (`X = 1` followed by `"""See PL-K7Q."""`) glyph_check reads documentation, fixture_id_check scans it as a value and reports `PL-K7Q`, and doc_check reads no citation in it.
- Which modules a file imports: `arming.imported_modules` and `imports_product` beside `import_boundary_check.module_imports`. On `importlib.import_module("anesthesia_sim.core")` the check reads the import and arming does not.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each fact has one reader the others call (`docket.python` is the natural home), and a test pins the attribute docstring and the `importlib` form.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
