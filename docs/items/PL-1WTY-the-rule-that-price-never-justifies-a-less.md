---
id: PL-1WTY
title: The rule that price never justifies a less correct model or effort (PL-2D28) is absolute: no finite measurement can show a cheaper setting is no less correct, so it forbids every cheaper setting for good and made any rise in failures worth acting on; the owner asked on 2026-11-24 for a form that keeps its spirit
status: untriaged
feature: model-evidence
added: 2026-11-24
filed-pr: 2318
---

**Problem.** The rule that price never justifies a less correct model or effort (PL-2D28) is absolute: no finite measurement can show a cheaper setting is no less correct, so it forbids every cheaper setting for good and made any rise in failures worth acting on; the owner asked on 2026-11-24 for a form that keeps its spirit

**What the rule says now.** `docs/maintainer.md` § "Match model capability to
the work": "Price, even a price of zero, does not justify a model or an effort
level that may be less correct. ... So a cheaper model or a lower effort is
used only where a measurement shows that it is no less correct at the task"
(project owner, 2026-10-19). `docs/dead-ends.md` repeats it under "A cheaper
model or lower effort for a subagent", and `.claude/rules/apparatus-standard.md`
applies it to the effort of a subagent.

**Why it is too rigid.** No finite measurement can show that two settings are
equally correct. The FDA's guidance says a non-inferiority trial "will only
rarely support a conclusion that the drug is 'equivalent' or 'similar' to the
active control" (*Non-Inferiority Clinical Trials to Establish
Effectiveness*, November 2016, section III.F,
https://www.fda.gov/downloads/Drugs/Guidances/UCM202140.pdf, sections I to
IV.C read by a subagent of `PL-JT1C`). `PL-G2D4`'s note of 2026-10-19 found the
same: 60 searches with no misses bound the excess miss rate below about 1 in
20, not at zero. So the rule's own condition for reopening can never be met.
In the effort trial it made any rise in failures worth acting on, which set
the target hazard ratio at 1.3 and the sample at 476 failures (`PL-JT1C`,
decision 6). The owner's own default already departs from it: every session
opens at `high` on the owner's judgement (`PL-6XZG`), although `xhigh` may be
more correct.

**The spirit, as the record shows it.** Correctness comes before cost. The
cheaper setting carries the burden of proof, so the stronger one stays until a
measurement says otherwise. Work under the safety-critical standard is never
traded.

**Proposed form (recommended).** Medicine accepts a cheaper or easier
treatment without proving it identical through a non-inferiority comparison
against a margin set in advance. The FDA defines the margin M2 as "the largest
clinically acceptable difference (degree of inferiority) of the test drug
compared to the active control", says "The choice of M2 is a matter of
clinical judgment", that "a larger value for M2 may be justified clinically, if
the test drug were shown to have some important advantage", and that the
margin "is specified in advance" (sections III.A and III.C). Althunian et al.
(Br J Clin Pharmacol 2017;83(8):1636-42, doi:10.1111/bcp.13280, full text
through PMC5510081) name the use, a new drug that "offers safer, more
cost-effective or easier treatment options", and list "the seriousness of the
outcome measure" among the factors that set the margin. The margins in their
Table 1 run from a hazard ratio of 1.08 to 2.75. Proposed wording for
`docs/maintainer.md`:

> **Correctness comes before cost** (project owner, DATE, revising
> 2026-10-19). A cheaper model or a lower effort is used for a kind of work
> only after a measurement shows that it is not worse than the stronger
> setting by more than a margin the owner set before the measurement began.
> Until then the stronger setting stays. For work under the safety-critical
> standard the margin is zero, so that work always gets the strongest setting.

**The margin is the owner's judgement.** The table applies it to the effort
trial's outcome, a fix that did not hold within 30 days, at the 5.9% failure
rate seen before the trial.
The failure counts are those needed for 80% power over six monthly looks.

| Margin (hazard ratio) | `high` may fail up to | Failures needed if the two are truly equal | If the true ratio is 1.3 |
| --- | --- | --- | --- |
| 1.25 | 7.4% | 658 | cannot be met |
| 1.5 | 8.8% | 200 | about 1,600 |
| 2.0 | 11.5% | 69 | about 180 |

With Projects threads in the trial, about 600 implementation items merge a
month, so 200 failures take about 7 months and 69 about 3; cloud sessions
alone take about 36 and 13. The ratio of 1.3 is Anthropic's benchmark gap
(`PL-JT1C`, decision 6). **Recommendation: 1.5 outside safety work**, because
it sits in the middle of the margins used in practice and allows about three
more failed fixes per 100 items. This is a judgement the sources leave to the
owner, not one they settle.

**Two consequences to carry into the build.**

1. An analysis by drawn arm is not conservative for this question. The FDA
   says intention-to-treat analyses "are not necessarily conservative in an NI
   study and can lead to an incorrect finding of non-inferiority" (section
   III.E.3). The 22 `xhigh`-arm sessions that ran at `high` (`PL-VGVV`) push
   toward that error, so non-inferiority is concluded only where the analysis
   by drawn arm and the analysis by the level actually run agree.
2. Under either the present rule or this one, the burden of proof sits with
   `high`, which is the default today. Whether the default moves to `xhigh`
   until `high` is shown non-inferior is the owner's to decide, and the reply
   that asks about the margin says so.

**Decided** (project owner, 2026-11-24, ratified: "Agree with best
practixe", over margins of 2.0 and 1.25 and over keeping the rule absolute):
the non-inferiority form above, with a margin of a hazard ratio of 1.5
outside safety-critical work and zero within it. The decision card recorded
the answer from the owner's words rather than a tap. Consequence 2, whether
sessions open at `xhigh` until `high` passes, is still open and goes to the
owner with this item's build, together with how the trial treats
safety-critical work (`PL-C38D`, point 3).

**Done when.** The owner has chosen the form and the margin, and
`docs/maintainer.md`, `docs/dead-ends.md`, `.claude/rules/apparatus-standard.md`
and the trial's analysis plan in `docs/model-review.md` say it.
