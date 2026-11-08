---
id: PL-73G8
title: The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it
priority: P3
effort: S
status: done
classes: defect, docs
feature: pr-body-integrity
milestone: v0.5.12
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, docs/pr-bodies
added: 2026-09-20
closed: 2026-09-26
pr: 1068
payoff: a recovery file says when its body was fetched and fails loudly when its anchor sha stops resolving, so the archive's provenance claim is one the repository can honour
verify: grep -q 'def test_a_recovery_file_whose_commit_sha_no_longer_resolves_is_reported' tests/unit/test_pr_body_check.py
---

**Problem.** The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it

**Why it matters.** The header is a provenance claim about a document nobody
can re-derive. `docs/pr-bodies/` exists so that a body GitHub's own blob view
silently rewrites is recoverable, and the recovery is worth exactly what its
header says it is: "the body verbatim" is a claim about the moment of merge,
while what was fetched is the body as the API serves it today - which an edit,
a bot comment rewrite, or a later `update_pull_request` moves. Beside it the
`commit:` sha is the one field that could anchor the document to a tree, and
nothing checks that it still resolves, so a rewrite of history leaves the
header asserting a provenance the repository cannot honour. `PL-TDBT` measured
30 unresolvable shas across the corpus; this is the check that would have
caught each as it was written.

**Reproduced 2026-09-20.** `tools/pr_body_check.py` has no clause that resolves
a recovery file's `commit:` sha, and no test under
`tests/unit/test_pr_body_check.py` names one.

**Done when.** A recovery file's header states when the body was fetched rather
than claiming it verbatim from the merge, and `tools/pr_body_check.py` fails on
a `commit:` sha that no longer resolves, with a test under
`tests/unit/test_pr_body_check.py` holding it.

**Closed 2026-09-26 with `PL-979D`'s build (#1068).** A recovered file's header
carries `recovered: DATE`, the day the body was fetched, and no longer claims it
verbatim from the merge. `python3 tools/pr_body_check.py --anchors` runs in
`make check` and fails on a `commit:` that is not a first-parent commit of the
default branch, which covers a sha that no longer resolves; the test is
`test_a_recovery_file_whose_commit_sha_no_longer_resolves_is_reported`. Forward
only: the 201 files written before this rule keep their old header, and the
commit that added each one dates its fetch.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-73G8 (S) a recovery file's header claims the body verbatim when it is the body as GitHub serves it today, and its `commit:` sha dangles after a history rewrite with nothing checking it
