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
whether a `Co-authored-by` claim is accurate. Those are the project owner's to
judge when he reads the diff.

**The hook alone cannot reach what lands on main.** Under PL-S4M2's squash
merge, the commit on main is composed by GitHub server-side from the pull
request title and description; no local hook runs on it, and the branch commits
the hook did check are discarded. So the hook shapes the input and enforces
nothing about the output. The rules therefore need a second enforcement point:
a job on the `pull_request` event checking the title and description, since
those become the squash commit's subject and body. The local hook stays - it is
what keeps branch commits worth reading, and a single-commit pull request still
seeds its default message from them - but it is not where this is enforced.

**Must not fabricate a review.** The hook must never insert `Reviewed-by:`. A
trailer asserting review by default is false by default; it is added at merge,
when the review has actually happened.

**Depends on** PL-XH1D (state how the project is developed, and what each
attribution trailer means) for the permitted trailer combinations - the hook
enforces that document's rule, so the rule has to be written first.

**Done when.** A local commit violating any checked rule is refused by the
hook, a pull request whose title or description violates the same rules fails
CI, the existing history is not rewritten, `.mailmap` collapses the owner to
one identity, and both checks have tests covering each rule and a well-formed
message that passes.
