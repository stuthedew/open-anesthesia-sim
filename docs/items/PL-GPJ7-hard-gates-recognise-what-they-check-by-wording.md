---
id: PL-GPJ7
title: Hard gates recognise what they check by wording - a quote near see or above, a PL- prefix, a cue word near an id - where CLAUDE.md reserves hard failure for exact rules, so each heuristic form refuses correct prose in its own way and each refusal arrives as its own item
priority: P2
effort: L
status: ready
classes: defect
feature: exact-gates
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py, tests/unit/test_doc_check.py, subprojects/docket/tests/test_checks.py, docs/MODEL.md, ROADMAP.md, docs/ARCHITECTURE.md, docs/WORKING_NOTES.md, docs/machine-survey.md, docs/maintainer.md, README.md, docs/interface-provenance.md, docs/resident-instructions.md, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a correct sentence stops failing make check for its wording, and the bare section citations - 264 by the stress test count, two stale today, one in docs/MODEL.md - are checked instead of passing unread
verify: grep -q 'def test_a_bare_section_mark_citation_is_checked' tests/unit/test_doc_check.py
root-cause-of: PL-YSMV, PL-QQCD, PL-HVST, PL-L8VP, PL-XGYH, PL-HJ8G, PL-VH5V, PL-SN2T, PL-NQ3X, PL-FKH6, PL-6G8T
generator: live - every heuristic form is still in its hard gate, reproduced 2026-09-25 against 46954a81, and ordinary writing still meets them: PL-6G8T was filed from ordinary work on 2026-09-07 and PL-YSMV on 2026-09-21, and PL-XGYH was refused by the check it reports while being written
misread: Whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording
---

**Problem.** Hard gates recognise what they check by wording - a quote near see or above, a PL- prefix, a cue word near an id - where CLAUDE.md reserves hard failure for exact rules, so each heuristic form refuses correct prose in its own way and each refusal arrives as its own item

The fuzz harness injected correct-but-tricky prose into real documents and ran each check the way `make check` does. Heuristic recognition in a hard gate produced every false refusal found. The deciding number: on all 1,647 item briefs, which doc_check has never filtered, the see/above/below citation forms matched 10 times and found 0 real stale citations; in the documents, dropping them costs 150 one-time rewrites to `§ "X"` and brings 264 bare `§` citations, unchecked today, under checking - 2 of them stale (PL-QQCD). 7 of doc_check's 65 commits were false-positive repairs. Google's Tricorder holds a code-review analyzer to an effective false-positive rate under 10% or it is disabled (Sadowski et al., CACM 2018).

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Every hard gate is an exact rule: recognition by explicit syntax (`§ "X"`, a front-matter field, a backticked path, the store's id grammar - and where an id attributes work, as a branch name or a subject's leading id does, an id the store holds, per PL-SN2T), with anything that needs wording to recognise demoted to an advisory; the members close or are dropped against that rule. One form has no exact spelling, and is this head's to settle under that rule: an escaped bracket pair reads the same whether it means literal brackets or display math GitHub will not render - the characters that `test_math_latex_block_delimiters_are_reported` pins as refused - so whether the math-delimiter check keeps refusing it as a hard error is decided here. PL-XGYH kept only its indented-code half for that reason (triage, 2026-09-25).

Reproduced 2026-09-25 against 46954a81, both directions, in scratch roots: a document sentence reading See "docket check: 0 errors" for what a clean run prints fails `check_citations` as a section no document has, and a bare `§` citation naming a heading that exists nowhere passes both `check_citations` and `check_quoted_sources` unread. `CITATION_RE` matches 161 times in the documents today - 105 in `docs/MODEL.md`, 44 in `ROADMAP.md`, 12 across eight others - which is the one-time rewrite this route costs, so those files are now in `touches`. That puts the head across the lane boundary, as `PL-4FBP` was: the rewrite is citation phrasing in product documents.

**Membership, triaged 2026-09-25.** Four members leave `root-cause-of`, because this head's fact is not what their gates misread and its rule would not close them. PL-YKBF's prose-prerequisite rule has been an advisory since #935 - `_undeclared_prerequisites` reports through `brief_contradictions` into the advisories, and `test_an_undeclared_prerequisite_never_fails_the_build` pins it - so the title's third example, a cue word near an id, is not a hard gate today. PL-HRTH reads the Symbols table by exact GFM syntax and splits it without honouring the escaped pipe: it misreads which cell holds the claim, not whether a claim is made. PL-5XKP decides whether a string reaches a reader by AST structure, default-deny by its stated design, and both of its reproductions turn on dataflow a static walk cannot follow. PL-JYX9 is an advisory rather than a hard gate, misfiring because a thread outlived its items. Each carries its own one-off answer. PL-VH5V and PL-SN2T stay, although PL-ZJ6X's fact (which strings are valid item ids) sits next to theirs: both gates apply the store's grammar correctly - `PL-CTRL` and `PL-HTML` are mintable - and what they misread is whether an English word or a PL-prefixed phrase is meant as an id at all, which is this head's fact. PL-6G8T joins: `_section_text` takes a required marker quoted at the start of a wrapped line for the section itself, the false-pass side of PL-NQ3X's fenced template, and filed from ordinary work on 2026-09-07 it is the oldest instance here. PL-3NKZ, the items-side twin of PL-HJ8G, is not added: doc_check does not read briefs, so nothing there misreads anything yet.

**Generator check.** This is the head for its fact, and no other head's `misread:` states it. The nearest, PL-4FBP and PL-G424, state a document sentence's link to the tree fact it restates: drift, which these gates exist to catch, rather than whether a sentence makes the claim at all.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
