---
id: PL-F933
title: doc_check resolves a path citation against the working tree, so a citation to a gitignored path passes locally and reddens CI
status: untriaged
added: 2026-09-13
---

**Problem.** doc_check resolves a path citation against the working tree, so a citation to a gitignored path passes locally and reddens CI

**Why it matters.** `tools/doc_check.py`'s path-citation check is one of the
strongest things in this repository: it decides, rather than guesses, whether a
cited path exists. But it resolves against the **working tree**, and a
developer's working tree contains ignored paths a clean checkout never has - a
virtual environment being the obvious one. So a citation to such a path is
green on the machine that wrote it and red in CI, which is the one direction
this project cares most about: `make check` passing while the guarantee it
stands for is void, in the session that is about to push.

It is not that the check is wrong. A path that resolves only sometimes is a bad
citation and refusing it is correct. The finding is that the *local* run cannot
see the problem, so the author gets no signal until a CI cycle is spent - and
the fix is obvious only once the CI log names it.

**Observed 2026-09-13, and it cost a cycle.** `PL-8PT6` added a paragraph to
`subprojects/docket/README.md` naming what a wrong `uv` invocation leaves
behind. It cited the environment directory as a code span. `make check` locally
reported `documentation: 0 errors` because this checkout has a root virtual
environment; CI reported

    subprojects/docket/README.md:1874: cites `.venv/`, which does not exist

and failed in nine seconds, before any test ran. The paragraph was reworded to
name both artifacts in prose instead, so the citation cannot resolve
conditionally.

**Where.** `tools/doc_check.py`, the path-citation check and whatever it uses
to decide a citation's existence.

**Decision needed.** Whether the check should consult `.gitignore` - treating a
citation to an ignored path as an error *regardless* of whether it happens to
exist, which makes the local and CI answers identical and names the real
problem ("this path is not part of the repository") rather than the accidental
one ("it does not exist here"). The alternative is to leave it: the class is
narrow, CI catches it, and reading `.gitignore` correctly is more work than it
looks - patterns, negations, and nested ignore files.

Worth weighing against how often it can fire. Most citations are to tracked
source paths, which cannot drift this way; the exposure is prose about build
artifacts, caches and environments, which is rare but is exactly what a
`## Running the tests` section is made of.
