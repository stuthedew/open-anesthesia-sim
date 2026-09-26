---
id: PL-QYN4
title: A § citation qualified by an item id in a code span, such as PL-MB2W § "Design round, 2026-09-24", is read by no check: check_citations leaves a code-spanned qualifier to containment and QUOTED_SOURCE_RE only reads a .md document, so the three such citations in docs/resident-instructions.md, the start mode and the docket README resolve against nothing
priority: P2
effort: S
status: done
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
payoff: a section mark after an item id, such as the seven citing PL-MB2W's brief, fails make check when the brief stops holding the words, instead of passing unread under a report that every citation resolved
verify: grep -q 'def test_a_marked_citation_of_an_item_is_held_to_its_brief' tests/unit/test_doc_check.py
---

**Problem.** A § citation qualified by an item id in a code span, such as PL-MB2W § "Design round, 2026-09-24", is read by no check: check_citations leaves a code-spanned qualifier to containment and QUOTED_SOURCE_RE only reads a .md document, so the three such citations in docs/resident-instructions.md, the start mode and the docket README resolve against nothing

**Reproduced 2026-09-26 at `324ce685`.** With the quoted section of `docs/resident-instructions.md`'s citation of `PL-MB2W`'s brief changed to words that brief does not hold, `python3 tools/doc_check.py check` exited 0 and said nothing about it. Counted the same day over what `check_quoted_sources` reads - the documents, the live briefs and the docstrings - there are seven such citations, every one of `PL-MB2W`'s brief and every one holding its words today: the three the title names, and four in docstrings, in `subprojects/docket/src/docket/arming.py`, `subprojects/docket/src/docket/claiming.py`, `subprojects/docket/src/docket/claims.py` and `tools/branch_id_check.py`.

**Why it matters.** The mark claims the named source holds the section, and after a document `check_quoted_sources` holds that claim by containment; after an item id nothing does, so `make check` reports the citations resolved while seven went unread. That is a partial reading handed over as a complete one, which `.claude/rules/apparatus-standard.md` § "The floor: an answer has to be true, or has to say it could not answer" refuses. None of the seven has drifted, since all cite a closed brief and a closed brief is a record that is not rewritten. What goes unread is the next one: a mistyped section, or a section of an open item's brief, which triage and the start mode rewrite as the work comes into focus.

**Done when.** `tools/doc_check.py` holds a section mark whose source is a code-spanned item id to that item's brief by containment, as `check_quoted_sources` holds one naming a document: a quotation the brief does not contain is an error, and so is an id no file under `docs/items/` holds. Only the mark is read after an id. There `under "X"` names a heading the item is listed under elsewhere, as both such sites did on 2026-09-26, and a bare quotation after an id is prose, so neither claims the brief holds the words. `tests/unit/test_doc_check.py` pins a citation that resolves, one that has drifted, one naming no item, and an `under` that is not read.

**Generator check.** One-off. The fact misread is which of `doc_check`'s readers answers a section mark whose source is code-spanned: `check_citations` hands every one to containment, and `check_quoted_sources` took only a `.md` document, so an item id fell between them. `PL-QQCD` (a section mark read wherever it stands) wrote the gap down as a decision rather than misreading it, and no head's `misread:` states this fact. `PL-GPJ7`'s, whether a sentence makes the claim a gate checks, is about recognising the claim, which the mark already does here.

**The possessive is left out, and filed as `PL-RX0W`.** After an item id it stood eleven times that day, and the one miss is a faithful quotation across emphasis that `_comparable` does not fold, so reading it needs the comparison changed first.

**Joined the Fix generators project's list 2026-09-26** (project owner, 2026-09-26). Asked in the project timeline whether anything else was left for generators, the coordinator named the seven items filed overnight, this one among them, as staying out of scope unless the owner added them, and the owner answered "Add them". Recorded here by the thread that took it.
