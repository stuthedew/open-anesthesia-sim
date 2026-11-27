---
id: PL-MWL0
title: The document check reads no section mark that cites a Python module's docstring heading, such as core/governing_equations.py § "The state vector", nor an item brief's section after a connective other than § or the possessive, so a rename of either strands the citation silently
priority: P2
effort: M
status: done
classes: defect
feature: doc-consistency-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/apparatus.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2336
payoff: renaming a section of a module docstring or an item brief fails the document check at once instead of stranding its citations
tests: tests/unit/test_doc_check.py::test_a_section_mark_after_a_module_is_held_to_its_docstring_headings, tests/unit/test_doc_check.py::test_a_mark_after_a_module_that_is_absent_unparsable_or_quoted_as_an_example, tests/unit/test_doc_check.py::test_a_mark_after_a_connective_that_claims_nothing_names_a_section_of_its_document
reenters: PL-LPCB
---

**Problem.** The document check reads no section mark that cites a Python module's docstring heading, such as core/governing_equations.py § "The state vector", nor an item brief's section after a connective other than § or the possessive, so a rename of either strands the citation silently

Found 2026-11-22 by the first blind review pass on `PL-LPCB`'s change (#2211).
`PL-LPCB` made the document check hold a section mark to the headings of the
`.md` document it cites. A mark after a code-spanned source that is not a `.md`
file is still left alone, as it was before: `QUALIFIED_RE` tells
`check_citations` and the bare-mark loop in `check_quoted_sources` to skip it,
and `QUOTED_SOURCE_RE` names only `.md` documents.

1. A module's docstring is cited by its Markdown headings in this tree:
   `tests/integration/controller/test_controller_stored_states.py` cites
   `core/governing_equations.py` § "The state vector", and
   `src/anesthesia_sim/core/exponential_approach.py` cites `core/__init__.py`
   § "Zero flow is tested with `== 0.0`, never against a tolerance". A probe of
   `` # `core/thing.py` § "No such section" `` gave no error and no advisory.
2. An item id followed by a comma, a colon, a parenthesis or `under`, then the
   mark, is read by nothing either; `ITEM_SECTION_RE` takes only the mark or the
   possessive.

**Done when.** A section mark after a code-spanned Python file is held to the
headings of that file's module docstring, read as Markdown, and a mark after an
item id and any connective is held to that item's brief as `ITEM_SECTION_RE`
holds one.

**Why it matters.** A section renamed in a module docstring or an item brief leaves every citation of it pointing at nothing, and no check says so. The next reader follows the citation and finds no such section.

**Generator check.** An instance of `PL-LPCB`'s fact, which heading a § citation names, filed after that head closed: its fix reads `.md` documents only. Recorded with `reenters`.

**Done 2026-11-27.** The first half was built as the brief asks. A section mark after a code-spanned Python file, or after the file and the possessive, is held to the headings of that file's module docstring, read as Markdown. `MODULE_SECTION_RE` in `tools/doc_check.py` reads it, and `check_quoted_sources` resolves the file the way `QUOTED_SOURCE_RE`'s documents are resolved, so `core/thing.py` finds `src/anesthesia_sim/core/thing.py`. A file that does not exist is an error. A file Python cannot parse is declined, with the parser's reason, because its headings could not be read. A mark inside a code span is an example written out, as this brief's own probe is, and is not read.

The second half was not built as the brief asks, because the tree showed it would be wrong. The brief asked that a mark after an item id and any connective be held to that item's brief. On 2026-11-27 the documents and the Python files held 11 marks after a code span and a connective that claims nothing, and every one named a section of the document around it, not of the code span before it. Two follow an item id: `ROADMAP.md`'s `` `PL-B9PY` under § "Cleared by v0.5.0 itself" `` names a section of `ROADMAP.md`, and `docs/interface-provenance.md`'s `` `PL-3J2P`, § `` mark names one of that document. The other nine follow a symbol, a module or a directory, as in `docs/VERIFICATION.md`'s `` `tests/unit/test_generated_runs.py` (§ "Step-refinement test") ``. Held to the brief, the two item marks would have failed `make check` on correct citations. So `QUALIFIED_RE` now hands a mark on only after a `.md` document and any connective, or after an item id or a Python file and nothing or the possessive. Every other mark is read as a mark of its own document, which is the reading all 11 needed. Before the change no reader held any of the 11. All 11 pass the check now, so a rename of the section they cite fails it.

`check_quoted_sources` had a local variable named `refusal`, which hid the imported `docket.python.refusal` for the whole function, so the new declined line raised `UnboundLocalError`. The local is now `unclosed`.

**Regression.** Seven new cases in `tests/unit/test_doc_check.py` fail against `tools/doc_check.py` at `8f404cfa`: both forms of a module mark, refused once the heading is renamed; a mark after a missing module, after an unparsable one and inside a code span; and four marks after a connective that claims nothing, after an item id, a symbol and a module, each passing while its heading exists and refused once it is renamed. The command was `pytest -q -p no:randomly tests/unit/test_doc_check.py -k "module or connective_that_claims_nothing"`, run with the file at `8f404cfa` put back, and it gave 7 failed.

**Documents checked:** `tools/doc_check.py`'s comments on `QUALIFIED_RE`, `MODULE_SECTION_RE` and `ITEM_SECTION_RE`, and the docstring of `check_quoted_sources`; `docs/apparatus.md`'s line for the check, which now says a mark is held to a module docstring's headings too; `.claude/rules/citation-drift.md`, which describes the line and path citations and not the section marks; and `docs/WORKING_NOTES.md`.

