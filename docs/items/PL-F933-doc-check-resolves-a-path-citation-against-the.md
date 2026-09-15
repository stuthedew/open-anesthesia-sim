---
id: PL-F933
title: doc_check resolves a path citation against the working tree, so a citation to a gitignored path passes locally and reddens CI
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/README.md
added: 2026-09-13
closed: 2026-09-15
pr: 593
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_the_verdict_is_the_same_whether_the_ignored_directory_is_there_or_not' tests/unit/test_doc_check.py
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

**Done when.** `tools/doc_check.py` gives the same answer on a path citation
in a developer's working tree as it gives in a clean checkout - either by
consulting `.gitignore` and refusing a citation to an ignored path whether or
not it happens to resolve, or by recording in the module that the divergence is
deliberate, what its class is, and what a session meeting the CI failure should
do. A test covers a citation to a path that exists only because it is ignored.

**Answered 2026-09-15, on the other branch of its own Decision needed**, and
closed with `PL-MXSL` (doc_check requiring a cited directory to exist), which
found the same defect two days later from the opposite end: `docs/worker.md`
could not name `out/`, the one directory the repository had just given
generated output.

The decision above offered refusing an ignored citation whether or not it
resolves. The project owner took the other route on 2026-09-15: **exempt it**.
`_covered_by_gitignore` asks `git check-ignore -q --no-index` about a citation
that has already failed to resolve, so the verdict no longer depends on the
working tree - which is this item's Done-when goal - while documentation keeps
the ability to name the directories it is documenting, which refusing would
have taken away. The concern recorded here about reading `.gitignore` being
"more work than it looks - patterns, negations, and nested ignore files" is
exactly why git answers the question rather than a parser.

`test_the_verdict_is_the_same_whether_the_ignored_directory_is_there_or_not`
is the test this item asked for: a citation to a path that exists only because
it is ignored, asserted to give the same answer with the directory present and
absent.

**And the paragraph this item cost has been restored.** `PL-8PT6`'s
`subprojects/docket/README.md` passage was reworded to name the environment and
the lockfile in prose because neither could be cited; it names
`subprojects/docket/.venv/` and `subprojects/docket/uv.lock` again, and the
sentence explaining why it could not has been replaced rather than left
stating a constraint that no longer holds.
