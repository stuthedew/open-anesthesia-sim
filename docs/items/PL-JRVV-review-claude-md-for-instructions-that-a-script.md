---
id: PL-JRVV
title: Review CLAUDE.md for instructions that a script, hook or check now enforces, and retire them to cut the resident set and the risk of context rot
priority: P1
effort: M
status: ready
classes: session-cost
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-10-20
payoff: every session loads shorter resident instructions, so the rules that only judgment can apply are less likely to be missed
not-delegable: deciding whether a check fully enforces a rule, and so whether its prose can go, is judgment that no command can make
---

**Skeleton, to be fleshed out** (project owner, 2026-10-20). Priority P1 is the
owner's (project owner, 2026-10-20).

**Problem.** `CLAUDE.md` is 56,157 characters on 2026-10-20 (`wc -c`), and it
loads in full in every session. Some of its instructions may now be enforced
by a script, a hook or a check. Examples include `tools/literal_home_check.py`,
`tools/fact_home_check.py`, the pipe-guard hook on `bin/docket check` and
`bin/docket arm`, and `bin/docket check` itself. Prose that restates what a
check already refuses costs context in every turn and enforces nothing.

**Why it matters.** Long resident instructions dilute attention. A rule buried
in a long file is likelier to be missed, which is the context rot the owner
wants to reduce. `CLAUDE.md` already says that a rule whose failure a check
now catches is retired rather than kept, on the test in
`docs/resident-instructions.md` (`PL-NJTZ`). This item applies that test to the
whole file.

**Method sketch.** For each block in `CLAUDE.md`, name the script, hook or
check that would refuse a violation, if one exists. Then sort the block into
one of three groups: retire it because a check enforces it fully; shorten it
to a pointer because a check enforces part of it; or keep it because only
judgment can apply it. Record the result in `docs/resident-instructions.md`.

**Related.** `PL-6VJ3` (the resident set's growth to 90,700 characters) moves
three generator paragraphs to the docket skill. That item routes prose
elsewhere, while this one deletes prose that a check makes redundant. Settle
both together, so a paragraph is not moved and then deleted.

**Done when.** Every block in `CLAUDE.md` is recorded in `docs/resident-instructions.md` as retired, shortened to a pointer, or kept, with the check that justifies each retirement. The retirements are made, and the resident character total that `make check` reports is lower.

**Questions to settle when this is fleshed out.**

- Whether to include the resident `.claude/rules` files
  (`instruction-writing.md`, `plain-writing.md`, `expert-review.md`) as well
  as `CLAUDE.md`.
- What evidence makes a check count as enforcing a rule: a test that shows it
  refuses a violation, or reading its code.
- Whether the generator pause applies. Retiring prose builds no new
  mechanism, but any gap the review finds and wants a new check for would be
  captured, not built, while the pause holds.

**`PL-S2NL` went first, 2026-10-24.** It moved `CLAUDE.md`'s pull request procedure, the commit-and-push and base-merge bullets, into `.claude/skills/pull-request/SKILL.md`, and left one trigger bullet in their place. `docs/resident-instructions.md` § "The pull request procedure, routed to a skill 2026-10-24" records what stayed and why. Measure this item's cut against that smaller `CLAUDE.md`. The `bin/docket arm` rules this review might have retired from `CLAUDE.md` now live in the skill, which loads only when used, so they no longer cost resident context.

**`PL-6VJ3` went first, 2026-10-24.** It moved the reasoning and history of `CLAUDE.md`'s generator bullet, its `impairs-generators` paragraph and the generator pause into `.claude/skills/docket/modes/triage.md` § "Generators, how they rank, and the pause they set". It applied this item's retirement test to those paragraphs as it went, so this review can skip them. Two short paragraphs stay resident: the two endings a generator takes, and the pause. Neither restates a check: no check can enforce how a reply ends, or whether a change is a new mechanism. `docs/resident-instructions.md` § "The generator rules, routed to the triage mode 2026-10-24" records the test and the cut. Measure this item's cut against `CLAUDE.md` at 49,234 characters.

**Done 2026-10-24.** Every `CLAUDE.md` block was checked against the scripts, hooks and checks in the tree, and `docs/resident-instructions.md` § "The check-enforced review, 2026-10-24" records each outcome. Two sentences were retired, and § "What was routed out" names the check that now enforces each. One was the rule that a new tool uses only the standard library, which `tests/unit/test_tools_portability.py` enforces. The other was the rule that a commit closing several items leads with all their ids, which `tools/pr_title_check.py` enforces on the squash subject. That rule's stated reason had also lapsed with `PL-HMZZ`. Every other block is kept, because a check covers only part of it or none. `CLAUDE.md` went from 49,234 to 48,842 characters, and `tools/doc_check.py` reports the resident total 392 characters lower than `origin/main`.

The three open questions were settled as follows, each the session's call under rule 14 as an internal method choice. The review covered `CLAUDE.md` alone, as the done-when says, because the three resident rules files govern a reply's shape, its wording and design judgment, which no check reads. A check counted as enforcing a rule only when a run against a violation was seen to fail: a probe for the standard-library test, and the title check's own tests. The generator pause did not apply, because retiring prose builds no mechanism, and the review found no gap worth a new check.
