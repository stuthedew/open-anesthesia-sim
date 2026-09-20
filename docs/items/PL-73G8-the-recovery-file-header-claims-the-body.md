---
id: PL-73G8
title: The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it
priority: P3
effort: S
status: ready
classes: defect, docs
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, docs/pr-bodies
added: 2026-09-20
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
