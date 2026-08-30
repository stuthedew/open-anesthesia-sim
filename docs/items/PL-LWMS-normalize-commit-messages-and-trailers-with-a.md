---
id: PL-LWMS
title: Normalize commit messages and trailers with a commit-msg hook
status: untriaged
feature: public-history
touches: tools, Makefile, .github/workflows/quality.yml, .mailmap
added: 2026-08-30
---

**Problem.** Commit-message shape is set by whichever harness wrote the commit,
and the harnesses disagree. The web session, the CLI and a GitHub Action each
inject their own trailers, so no convention survives across sessions by
agreement alone. Three specific drifts are already in the history: subjects run
to 126 characters against a median of 61; bodies run past the change into
session reporting addressed to the reviewer of the moment (`Captured: PL-0MLQ
(...)`, "`docket verify PL-VP7N --base origin/main` rejects for maintainer
review, as it should"); and all 139 co-author trailers read `Co-Authored-By:
Claude Opus 5`, which forks a new contributor identity on every model change.
The project owner also appears as two contributors, `stuthedew@users.noreply.github.com`
and `stuart.feichtinger@gmail.com`.

**Why it matters.** The commit body is where a reader who was not there learns
why a change exists, and this repository writes unusually good ones - the
problem is only that they do not stop when the change has been explained.
Session reporting has a home already: the pull request description, which is
addressed to exactly the reader it was written for. And per the repository's
own rule, all of this is decidable by reading the message, so it belongs in a
script rather than in a convention every session has to remember.

**Where.** A `commit-msg` hook under `tools/`, standard library only so a bare
checkout can run it, wired into `make check` and `.github/workflows/quality.yml`
in the same shape as `tools/doc_check.py`. Plus a `.mailmap` collapsing the
owner's two addresses.

**Approach.** Check form, never judgment - the doc_check.py line. In scope:
subject length, blank line after the subject, body wrapped at 72, a
well-formed trailer block whose author/co-author combination is one of the
permitted set, a stable `Claude <noreply@anthropic.com>` identity with the
model recorded under its own key rather than fused into the name, and a
forbidden-pattern check for the session-report sections above.

Out of scope, deliberately: whether the rationale in the body is any good, and
whether a `Co-authored-by` claim is accurate. Those are the project owner's at
review time, which the PL-S4M2 approval gate now makes a real step.

**Must not fabricate a review.** The hook must never insert `Reviewed-by:`. A
trailer asserting review by default is false by default; it is added at merge,
when the review has actually happened.

**Depends on** PL-XH1D (state how the project is developed, and what each
attribution trailer means) for the permitted trailer combinations - the hook
enforces that document's rule, so the rule has to be written first.

**Done when.** A commit violating any checked rule is refused locally and in
CI, the existing history is not rewritten, `.mailmap` collapses the owner to
one identity, and the hook has tests covering each rule and a well-formed
message that passes.
