---
id: PL-WXX8
title: Eleven merged items owe a pr number and no session claims the work, because docket record's advisory assumes a commit is already being made
priority: P2
effort: S
status: ready
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/release.py, .claude/skills/docket/SKILL.md, subprojects/docket/tests
added: 2026-09-16
verify: uv run pytest -q subprojects/docket/tests/test_release.py && grep -q 'def test_release_writes_the_pr_numbers_the_base_is_owed' subprojects/docket/tests/test_release.py
---

**Problem.** `bin/docket check` on `main` at `6114ce8` names eleven items
marked done that record no `pr`, each recoverable from its merge commit:
PL-5D2R and PL-H253 (#622), PL-L9RD, PL-NGF7 and PL-W8DQ (#621), PL-LKFP
(#620), PL-8PSW and PL-LH18 (#618), PL-C92D and PL-Q0J1 (#617), PL-SMN4
(#615). It was three at 03:00Z on 2026-09-16 and eleven by 04:00Z.

**Why nobody picks it up, which is a design property rather than neglect.**
The advisory's own remedy is "let it ride the commit you are already making
rather than composing one". That is right whenever a session is mid-work, and
it is precisely wrong at the moment the backlog grows: a `pr` number becomes
owed when a pull request *merges*, and the session that owned it has by then
finished, pushed and usually archived. The session best placed to record the
number is the one least likely to still be running.

So the work has no id until somebody files one, and `CLAUDE.md` § "The queue"
names the consequence exactly: "Every in-flight guard matches a `PL-` id, so
unfiled work reads as nobody's to all of them and keeps reading that way after
both sessions have pushed."

**Observed, not inferred.** A session at 03:06Z read another session's
`task_summary` as "Checking whether the merged items owe a PR number" and
recorded in #622's body that the work was covered. That session archived
without doing it. At 03:59Z no session's `post_turn_summary.needs_action`
mentioned it. The cross-session check that `.claude/rules/instruction-writing.md`
rule 14 prescribes worked as designed — it warns and never certifies — and a
`task_summary` naming an intention is weaker evidence than that rule's own
`needs_action` field, which is the part worth learning.

**Candidate fixes, in the order this project's doctrine prefers them.**

1. **A CI job on `main` that runs `docket record` after a merge.** Blocked, and
   the reason is already recorded: `PL-N5WZ` established that a push made with
   `GITHUB_TOKEN` starts no workflow, so a protected default branch never sees
   required checks report. Named here so it is not re-derived.
2. **Fold it into the release cut**, where a commit to `main` is being composed
   anyway and the advisory's "let it ride" premise finally holds. Cheapest of
   the live options and needs no new mechanism.
3. **Promote the advisory to an error above a threshold.** Rejected on
   `CLAUDE.md` § "A check earns its place every run": a hard failure that no
   session can clear without composing the very commit the advisory tells it
   not to compose is a check that fires without changing a decision.

**Recommendation: option 2.** Not started here — the session that found it was
at 264,817 tokens, past the 150,000-token handoff cap `PL-H253` landed the same
hour, and composing the commit is more than a capture.

**Why it matters.** A missing `pr` is provenance lost rather than a cosmetic gap.
`docket check` recovers the number from the merge commit that named the id, so it
is recoverable only while that commit is the newest one naming it; past that the
field cannot be written by command at all, because `bin/docket record` refuses to
guess, and the route back to the tree a closure was proved on is a hand search of
the history.

The backlog also grows monotonically by construction, which is what makes it an
item rather than a habit. Every merge adds to it; nothing removes from it except
a session that goes looking. And the advisory is addressed to the one population
that by definition is not holding the debt - sessions mid-work - while the
session that owed the number has finished and usually archived. Three owed at
03:00Z and eleven by 04:00Z is one hour of ordinary merging.

**Done when.** A merged closure's `pr` is written by a mechanism that runs without
a session noticing it is owed - candidate 2 above, folding `docket record` into
the release cut, unless a cheaper one is found - and `docket check`'s advisory
reports zero owed on a base where a release has since been cut. The eleven named
above are backfilled as part of it.
