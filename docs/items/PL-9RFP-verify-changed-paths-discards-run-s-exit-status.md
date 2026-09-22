---
id: PL-9RFP
title: verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones
priority: P2
effort: S
status: ready
classes: defect
feature: evidence-declines
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-22
payoff: the commission audit says it could not read the diff when the base does not resolve, instead of auditing git's error text as three edits and missing the real ones
verify: grep -q 'def test_changed_paths_declines_an_unresolvable_base' subprojects/docket/tests/test_verify.py
root-cause-of: PL-19T3, PL-ZPDM, PL-73P0, PL-MM7F
generator: live - git runs through several runners and only vcs.py's has a failure channel; verify._run discards status at seven sites and doc_check turns failure into an empty list (PL-KVDK)
---

**Problem.** verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `verify.changed_paths(<repo root>,
"no-such-base-ref")` returned three "paths":
`'git <command> [<revision>...] -- [<file>...]'`,
`Use '--' to separate paths from revisions, like this:` and
`fatal: ambiguous argument 'no-such-base-ref...HEAD': unknown revision or path not in the working tree.`
The call is `_, committed = _run(["git", "diff", "--name-only", f"{base}...HEAD"], root)`.
The status is bound to `_`, and `_run` returns stdout and stderr together.

**Why it matters.** `changed_paths` feeds the commission audit, which reports
changed paths that fall outside an item's declared `touches`. With the base
unresolved, the audit reports git's usage text as three out-of-scope edits,
which reads as the branch having done something it did not. It also reports
none of the branch's committed edits. So the check that exists to catch work
outside an item's scope passes a diff it never read. This is the same shape as
the rest of `evidence-declines`: a read that could not be taken has to say so,
not return its failure text as data.

**Done when.** `changed_paths` reads git's exit status on each call it makes.
When the base does not resolve it declines rather than answers, and the audit
then says the diff was unread. A test in `subprojects/docket/tests/test_verify.py`
holds it with a base that does not exist.
