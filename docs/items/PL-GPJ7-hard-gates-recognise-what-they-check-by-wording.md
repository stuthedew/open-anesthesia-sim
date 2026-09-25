---
id: PL-GPJ7
title: Hard gates recognise what they check by wording - a quote near see or above, a PL- prefix, a cue word near an id - where CLAUDE.md reserves hard failure for exact rules, so each heuristic form refuses correct prose in its own way and each refusal arrives as its own item
status: untriaged
feature: exact-gates
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py, tests/unit/test_doc_check.py, subprojects/docket/tests/test_checks.py
added: 2026-09-25
root-cause-of: PL-YSMV, PL-QQCD, PL-HVST, PL-L8VP, PL-XGYH, PL-HJ8G, PL-HRTH, PL-5XKP, PL-VH5V, PL-SN2T, PL-NQ3X, PL-YKBF, PL-JYX9, PL-FKH6
generator: live - PL-YSMV is open and the 2026-09-25 stress test reproduced 35 false refusals across 9 checks; every heuristic form still admitted to a hard gate will hand over another
misread: Whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording
---

**Problem.** Hard gates recognise what they check by wording - a quote near see or above, a PL- prefix, a cue word near an id - where CLAUDE.md reserves hard failure for exact rules, so each heuristic form refuses correct prose in its own way and each refusal arrives as its own item

The fuzz harness injected correct-but-tricky prose into real documents and ran each check the way `make check` does. Heuristic recognition in a hard gate produced every false refusal found. The deciding number: on all 1,647 item briefs, which doc_check has never filtered, the see/above/below citation forms matched 10 times and found 0 real stale citations; in the documents, dropping them costs 150 one-time rewrites to `§ "X"` and brings 264 bare `§` citations, unchecked today, under checking - 2 of them stale (PL-QQCD). 7 of doc_check's 65 commits were false-positive repairs. Google's Tricorder holds a code-review analyzer to an effective false-positive rate under 10% or it is disabled (Sadowski et al., CACM 2018).

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Every hard gate is an exact rule: recognition by explicit syntax (`§ "X"`, a front-matter field, a backticked path, the store's id grammar), with anything that needs wording to recognise demoted to an advisory; the members close or are dropped against that rule.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
