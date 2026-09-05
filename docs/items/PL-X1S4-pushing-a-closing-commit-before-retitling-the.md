---
id: PL-X1S4
title: Pushing a closing commit before retitling the pull request races pr-title, so a green PR shows a red run that means nothing
priority: P2
effort: S
status: done
classes: defect, infra, session-cost
feature: dev-tooling
touches: .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-05
verify: python3 tools/doc_check.py check && grep -qF 'before pushing the closure' .claude/skills/docket/SKILL.md
---

**Problem.** `pr-title` runs on `pull_request: synchronize` as well as `edited`,
so a push that adds a closure to an open pull request is checked against the
title as it stood *before* the closure existed. The check correctly fails, the
session retitles, and the re-run passes - leaving a red run on the pull request
that means nothing and a green one beside it.

**Observed twice in one session, 2026-09-03/04.** On `#276`, triaging dropped
`PL-PGY4`, which is a closed status, so the title owed an id it did not have. On
`#278`, closing `PL-8BFV` did the same. Both were real failures of a correct
check and both were resolved by a retitle within a minute.

**Why it matters, and why it is small.** Nothing is broken and nothing merges
wrong - the check is doing its job, and the final state is green. The cost is
that a reader (or a later session reading the run history) sees a failed
`pr-title` on a pull request whose title is fine, and has to open the log to
learn it was a race. That is the same shape as an advisory nobody can act on:
a signal that is technically true and carries no information. It also costs a
CI run each time.

**Where.** Not the check - `tools/pr_title_check.py` is right and should not be
loosened. It is a sequencing rule for the session, and triage found it belongs
in two places in `.claude/skills/docket/SKILL.md` rather than the one the
capture named, because the two observed cases came from different modes:

- "Mode: close out an item", step 1, which tells a session to lead the commit
  subject with every id it closes but says nothing about the pull request
  title, which is the half CI reads. That is `#278`.
- "Mode: triage", which sets an item to `status: dropped` and never says that
  `dropped` is one of `CLOSED_STATUSES` in `subprojects/docket/src/docket/model.py`.
  So a triage pass pushed onto an open pull request owes the title an id
  exactly as a close-out does, and a session triaging has no reason to be
  reading the close-out mode. That is `#276`, and the capture's `Where` missed
  it.

**Approach.** Retitle *before* pushing the commit that adds the closure. A
session knows what a commit closes before it pushes it, so the ordering is
always available and costs nothing. One sentence in the close-out mode beside
the existing rule about leading the commit subject, and one in the triage mode
pointing at it.

**Worth considering instead:** whether `pr-title` should be scoped to `edited`
and `opened` only, dropping `synchronize`. That would remove the race outright
but also stop catching the case this is all for - a push that adds a closure to
a pull request nobody retitles, which is exactly `PL-2XTF`'s `#220`. So
probably not; the sequencing rule is the cheaper half.

**Done when.** `.claude/skills/docket/SKILL.md` carries the rule in the
close-out mode - containing the phrase `before pushing the closure`, which
`verify:` greps for - and the triage mode says that dropping an item closes it
and owes the same retitle. `tools/pr_title_check.py` and
`.github/workflows/pr-title.yml` are unchanged.
