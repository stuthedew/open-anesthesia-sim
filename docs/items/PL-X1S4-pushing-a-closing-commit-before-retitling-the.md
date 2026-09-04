---
id: PL-X1S4
title: Pushing a closing commit before retitling the pull request races pr-title, so a green PR shows a red run that means nothing
status: untriaged
feature: dev-tooling
added: 2026-09-04
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
loosened. It is a sequencing rule for the session:
`.claude/skills/docket/SKILL.md`, "Mode: close out an item", which tells a
session to lead the commit subject with every id it closes but says nothing
about the pull request title, which is the half CI reads.

**Approach.** Retitle *before* pushing the commit that adds the closure. A
session knows what a commit closes before it pushes it, so the ordering is
always available and costs nothing. One sentence in the close-out mode, beside
the existing rule about leading the commit subject.

**Worth considering instead:** whether `pr-title` should be scoped to `edited`
and `opened` only, dropping `synchronize`. That would remove the race outright
but also stop catching the case this is all for - a push that adds a closure to
a pull request nobody retitles, which is exactly `PL-2XTF`'s `#220`. So
probably not; the sequencing rule is the cheaper half.

**Done when.** A session closing an item on an open pull request retitles
before pushing, and the skill says so.
