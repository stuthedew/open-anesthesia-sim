---
id: PL-MWL0
title: The document check reads no section mark that cites a Python module's docstring heading, such as core/governing_equations.py § "The state vector", nor an item brief's section after a connective other than § or the possessive, so a rename of either strands the citation silently
priority: P2
effort: M
status: ready
classes: defect
feature: doc-consistency-checks
touches: tools/doc_check.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: renaming a section of a module docstring or an item brief fails the document check at once instead of stranding its citations
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
