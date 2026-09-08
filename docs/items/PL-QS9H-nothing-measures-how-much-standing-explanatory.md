---
id: PL-QS9H
title: Nothing measures how much standing explanatory text the interface carries, so prose accretes between reviews the way contrast claims did before contrast_check
priority: P2
effort: M
status: needs-decision
classes: ux, infra
feature: teachable-case
touches: tools/, src/anesthesia_sim/app/simulation_view.py, .claude/rules/ui-reader.md
added: 2026-09-08
---

**Problem.** The seven standing paragraphs did not arrive at once. Blamed
2026-09-08: 2026-09-03 added two, 2026-09-04 added five, and the run-length
halt banner on 2026-09-07 added five more lines *after* the owner's 2026-09-05
ruling that this reader is not a lay reader. That banner is transient and
safety-bearing, so it is defensible — but the direction is unchanged, and
nothing in `make check` can see it either way.

This is the situation `tools/contrast_check.py` was built for, in its own
words: "Every contrast claim in this repository used to be prose... A color
edit could silently falsify a documented safety claim, and the only thing
between that and a reader was whoever remembered to re-measure." Substitute
"a text edit" and "the panel a reader gets through before the plot" and it is
this item.

**Why it matters.** `PL-B89V` (name the interface's reader in a path-scoped
rule) states the constraint in prose, and prose is what this project has
repeatedly found does not hold on its own: `contrast_check.py`,
`agent_identity_check.py` and `doc_check.py` all exist because a documented
claim went stale while still reading as true. A rule that is followed by every
session that reads it, and silently not by the one that does not open a
matching file first, is the same failure one level up. The measurement is also
what makes the strip work reviewable: right now nobody can say whether the
screen got better between two releases.

**Decision needed.** Which of the two shapes below to build, or neither. Shape
1 costs an allowlist entry per permitted sentence forever; shape 2 costs almost
nothing and probably fails `CLAUDE.md`'s own retirement test; neither is
free, and `CLAUDE.md` says that where the benefit is unclear the answer is no.

**The decidable half.** How much standing text the interface carries, and
whether a given standing block has been declared. Both are `ast` over
`app/simulation_view.py` — the same input `contrast_check.py` and
`agent_identity_check.py` already parse, standard-library only, runnable from a
bare checkout.

**The judgment half, which must not be scripted.** Whether a sentence earns its
place. That stays with a person, in a declaration table, exactly as
`REQUIREMENTS` holds the color pairs a person decided.

**Two shapes, and the choice is the decision.**

1. **Declared-standing-text allowlist.** A table of the standing `ft.Text`
   elements permitted to carry a sentence, each with its reason — the
   educational-use disclaimer, the two reference values. Any standing literal
   containing a sentence and not declared fails. Key each entry on the
   *element* — the attribute or the builder method, in backticks, resolved
   against the source — never on the string text, so rewording a label does not
   churn the table and a new paragraph does fail. This is `contrast_check.py`'s
   own pattern including its cite-by-symbol rule (`PL-GJDW`). Costs an entry per
   permitted sentence, forever.
2. **A bare character budget.** One number: standing `ft.Text` literals under
   `app/` total at most N characters. About 30 lines, no table, no upkeep. It
   cannot tell a legend row from a paragraph, so it fires on a legitimate
   growth and reads as noise the third time — which `CLAUDE.md` calls a defect
   in the check rather than a cost of it.

**The gate this must clear before being built.** `CLAUDE.md`: build where the
work recurs and the answer is deterministic; not for a one-off; not where a
check would fire without changing a decision. The recurrence is evidenced
above. The failure mode to design against is a check that a session answers by
raising the budget, which is why shape 1 keys on elements and shape 2 probably
does not clear the bar.

**Sequenced after `PL-6580`** (strip the concentration chart's explanatory
prose) and `PL-F9TQ` (the wash-in panel's paragraphs). A ratchet declared
against the current screen would freeze the prose it exists to prevent.

**Done when.** A tool in `tools/`, wired into `make check` beside
`contrast_check.py`, refuses an undeclared standing sentence in
`app/simulation_view.py`; `.claude/rules/ui-reader.md` names it the way
`ui-color.md` names `contrast_check.py`; and `tests/unit/` holds it to the
portability rule `tests/unit/test_tools_portability.py` states.
