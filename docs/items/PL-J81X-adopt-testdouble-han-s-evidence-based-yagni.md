---
id: PL-J81X
title: Adopt testdouble/han's evidence-based YAGNI review step (an evidence test, a simpler-version test and a list of auto-flagged anti-patterns) for simulator or apparatus changes
priority: P3
effort: S
status: dropped
classes: housekeeping
touches: docs/items
added: 2026-10-24
closed: 2026-10-24
reason: Refused by the project owner on 2026-10-24, ratified: han's YAGNI flags conflict with the safety-critical standard and with PL-YJY3 in the simulator, cannot score on PL-TCBJ's defect bar, and would be a new workflow mechanism in the apparatus.
---

**Problem.** Adopt testdouble/han's evidence-based YAGNI review step (an evidence test, a simpler-version test and a list of auto-flagged anti-patterns) for simulator or apparatus changes

**Why it matters.** The project owner asked on 2026-10-24 whether YAGNI was being considered anywhere, and whether `PL-TCBJ`'s reviewer panel was that. It was neither. The comparison with testdouble/han that filed `PL-SN2Z`, `PL-S2NL`, `PL-Z90G` and `PL-TCBJ` did not weigh han's YAGNI rule. Han keeps the rule in `han-coding/references/yagni-rule.md` (https://github.com/testdouble/han, commit `abba73a7`, read 2026-10-24). Every added item must cite one of five kinds of evidence that it is needed now. A strictly simpler version that meets the same evidence replaces it. A list of anti-patterns is flagged automatically. In han's `/code-review`, YAGNI is a checklist step, not a reviewer agent. Its findings go in a section of their own, are advisory, never block a merge, and are skipped when there is no diff (`han-coding/skills/code-review/SKILL.md` and `references/review-checklist.md`).

**Decision** (project owner, 2026-10-24, ratified, over adopting the rule for simulator review, over adding a YAGNI lens to `PL-TCBJ`'s replay, and over filing a replay of a YAGNI step on apparatus pull requests).

- **Simulator.** Four of han's automatic flags would fire on work this project requires. "Defensive code at trusted internal boundaries" conflicts with the safety-critical standard's validation of inputs, units and ranges before calculation. Tests "for code paths that don't exist yet" and completeness tests conflict with its boundary, invalid-input and pathological-input tests. Deferring an abstraction until three uses exist is the deferral `PL-YJY3` refused, recorded in `.claude/rules/expert-review.md` § "Count what undoing it would cost". "Refactor for cleanliness alone is YAGNI" conflicts with `CLAUDE.md` § "What this project is", which makes internal quality worth paying for on a multi-year horizon.
- **Han is stricter than the usual definition.** Fowler limits YAGNI to "capabilities built into the software to support a presumptive feature", and says it "does not apply to effort to make the software easier to modify" (https://www.martinfowler.com/bliki/Yagni.html, 2015). The host refused a fetch from the session's container, so this wording comes from a search result that quotes the page.
- **The scope half of YAGNI is already here.** `CLAUDE.md` forbids building beyond the current milestone, and the roadmap refuses speculative generality (`ROADMAP.md` § "Designed for forking", and `PL-B9PY`).
- **`PL-TCBJ`.** Its pass mark is defects caught. A YAGNI finding is not a defect by design, so it could only add to that replay's noise count.
- **Apparatus.** `CLAUDE.md` already builds tooling only where it "will genuinely run again", retires a check that changes no decision, and pauses new workflow mechanisms while a generator is live. A YAGNI review step would itself be a new workflow mechanism.

**Reopen when** a measurement shows apparatus mechanisms that were later retired unused getting past those gates often enough to matter. The fair test is a replay like `PL-TCBJ`'s, run on merged workflow pull requests whose mechanism was later retired, with its pass mark set before the count.

**Generator check.** None. The owner asked a question about han's YAGNI rule, and no fact was misread to produce this item.
