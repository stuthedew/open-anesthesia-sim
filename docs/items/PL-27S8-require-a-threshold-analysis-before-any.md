---
id: PL-27S8
title: "Require a threshold analysis before any tightening proposal: name what the suppressed side would have to be worth, and count it"
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
touches: .claude/rules/expert-review.md
added: 2026-09-12
closed: 2026-09-12
pr: 499
verify: python3 tools/doc_check.py check && grep -qF 'Name the number that would change your mind' .claude/rules/expert-review.md
---

**Problem.** Require a threshold analysis before any tightening proposal: name what the suppressed side would have to be worth, and count it

**Asked for by the project owner, 2026-09-12**, and the edit was made in the
same session under `CLAUDE.md`'s behavior-change rule: an item alone changes
nothing, because it sits untriaged and invisible to `bin/docket next` while
every session in the meantime keeps doing the thing that was just corrected.

**The trigger is narrow and recognizable:** a session about to propose that
something be tightened - a bar, a filter, a threshold, a scope cut, a check
retirement. The rule asks one thing of it, before the proposal is made rather
than after: name what the suppressed side would have to be worth for the
proposal to be wrong, then go and count it.

**Why it is resident rather than routed.** The three cheaper dispositions do
not reach the moment. A check cannot decide whether a proposal weighed its
unmeasured side - that is the judgment half, which `CLAUDE.md` says not to
script. A skill loads on its own trigger and this one has none: the moment is a
reply. A path-scoped rule loads when a session *reads* a matching file, and a
tightening is proposed in a design round that no read precedes - which is the
same argument that already puts `expert-review.md` in the resident set
(`PL-WWDT`).

**What it cost, stated by its own discipline.** +2255 characters on a resident
budget of 47523, so +4.7% - against an estimate of ~1400 given to the owner
before it was written, which was wrong by 60% and is recorded here because the
rule is about not trusting the comfortable number. It is worth that only if a
tightening is proposed more than about monthly. On the session that produced
it: two in one afternoon (the apparatus capture bar, and retiring
`vcs.orphaned` in favour of the exact check), and the first was wrong.

**The evidence, verified rather than recalled.** Chang LW, Kirgios EL,
Mullainathan S, Milkman KL. "Does counting change what counts? Quantification
fixation biases decision-making." *PNAS* 2024;121(46):e2400215121 -
https://doi.org/10.1073/pnas.2400215121 - abstract read directly via PubMed; 21
preregistered experiments, N = 9,303 main text plus 13,936 supplement, with
comparison fluency identified as the mechanism. OMB Circular A-4 (September 17,
2003) - the project owner supplied the PDF and the quoted passage was read from
it, not from a search summary.

