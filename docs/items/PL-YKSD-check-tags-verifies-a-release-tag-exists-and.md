---
id: PL-YKSD
title: check_tags verifies a release tag exists and never that it points at that release's own commit, so a tag pushed before the release merged reads as tagged to every check and lets bin/docket release cut the next version on a false premise
priority: P2
effort: S
status: done
classes: defect
feature: release-process
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-09-22
closed: 2026-09-22
payoff: a release tag pushed at the wrong commit fails make check, instead of reading as tagged to every check and letting the next version be cut on top of it
verify: grep -q 'def test_a_tag_whose_pyproject_version_disagrees_is_refused' tests/unit/test_doc_check.py
---

**Problem.** check_tags verifies a release tag exists and never that it points at that release's own commit, so a tag pushed before the release merged reads as tagged to every check and lets bin/docket release cut the next version on a false premise

**Why it matters.** It gives a wrong answer silently, which is the first of
`CLAUDE.md`'s three compounding-friction tests. `check_tags` reads the set of
tag *names* and reports which releases have one; nothing reads what a tag points
at. So a tag pushed at the wrong commit is indistinguishable, to every check
this project has, from one pushed at the right one - and the consequence is not
cosmetic, because `bin/docket release` refuses to cut the next version while the
previous is untagged and that refusal is the only thing standing between a
mis-tagged release and a second release cut on top of it.

**The instance, 2026-09-22.** `v0.5.3` was pushed before `#888` merged, so it
resolves to `630b915d` - `#887`'s merge, the commit *before* the release. At
that tag `pyproject.toml` reads `version = "0.5.2"` and
`docs/releases/v0.5.3.md` does not exist. `git describe --contains` answers
wrongly for the whole span, and `make check` was green across it. No GitHub
Release object was created, so the repair was a tag move.

**The decidable half, and it is the whole of what is wanted here.** For every
release tag *present in the checkout*, `git show vX.Y.Z:pyproject.toml` must
read `X.Y.Z`. That is a fact about the tree, needs no judgment, and costs one
`git show` per tag. The existing caveat in `check_tags` - a local checkout
cannot tell a release never tagged from one tagged since it last fetched -
applies to *absent* tags only and is untouched by this: a tag that is present
can always be checked against its own content.

**Not `PL-P669`**, which is the same neighbourhood and a different fault: that
one is about release notes not naming the pull request that closed inside their
span. This is about the tag ref's target. `docket new` matched them on the
shared vocabulary; they are worth reading together and should not be merged.

**Done when.** `tools/doc_check.py` fails on a release tag present in the
checkout whose `pyproject.toml` version disagrees with the tag name, a test pins
it with a synthetic tag at the wrong commit, and the message says which commit
the tag points at and what version it holds.

**Premise re-read 2026-09-22 (`PL-14QR`, triage).** `v0.5.3` now resolves to `c2bb1266`,
whose `pyproject.toml` reads `0.5.3`, so the instance is repaired. `check_tags`
(`tools/doc_check.py` line 2719) contains no `rev-parse`, `rev-list`,
`^{commit}` or `pyproject` read, so nothing in it would have seen the wrong
target.

**Done 2026-09-22.** `_check_tag_versions` in `tools/doc_check.py` reads every
release-shaped tag's own `pyproject.toml` through docket's `GitRunner` blob
batch - one `cat-file --batch` process for all 67 tags - with the pattern
`check_baseline` reads the working tree with. A disagreement is an error on the
version table's row, naming the commit the tag peels to and the version its tree
declares; a tree that yields no version is declined rather than refused, since
an empty read cannot tell a file never there from one missing from this clone.

**The premise held for 66 of the 67 tags, not all of them.** `v0.2.0` resolves
to `69a5888c`, the release commit by its subject, whose `pyproject.toml` reads
0.1.0: that release shipped without its bump, which `8687bdf2` "Fix stale app
version" supplied as its direct child and which went out in v0.2.1 (`git
describe --contains 8687bdf2` gives `v0.2.1~8^2~6`). CI checks out with
`fetch-depth: 0`, so the check as briefed would have turned `main` red on its
first run.

**Decided by this session, over moving the tag to `8687bdf2`:** `v0.2.0` stays,
and `ROADMAP.md`'s Tags statement names it in a second exception sentence,
"**One version shipped with a stale version file**", read in the untagged
sentence's count-and-names form and held to the tag in both directions - a
named version whose tag agrees is an error, because an exception left standing
would excuse the next mis-tag. Moving the tag would make `8687bdf2` read as
shipped in v0.2.0, which is the question tags exist to answer, and would take a
force-push of a published tag, which an existing clone's fetch rejects rather
than follows unless forced (git 2.20 onward). `PL-J3ZK`'s placement predates
the ratified/specified record, so its kind is unrecorded; it was reopened on
ordinary evidence here, and the evidence favoured keeping it.

**Not done, deliberately:** `bin/docket release` still refuses a cut only on an
*untagged* predecessor. A mis-tagged one now fails `make check` and CI, which
the cut's own branch runs before it can merge, so a second reading of the tag in
docket would be a copy free to drift from this one for no case it catches.
