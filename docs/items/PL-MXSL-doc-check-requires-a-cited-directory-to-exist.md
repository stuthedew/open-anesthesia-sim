---
id: PL-MXSL
title: doc_check requires a cited directory to exist with no exemption for one .gitignore covers, so documenting a generated directory fails CI while make check passes locally the moment anything has created it
status: done
closed: 2026-09-15
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_cited_path_gitignore_covers_is_not_required_to_exist' tests/unit/test_doc_check.py
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-15
---

**Problem.** doc_check requires a cited directory to exist with no exemption for one .gitignore covers, so documenting a generated directory fails CI while make check passes locally the moment anything has created it

**Observed 2026-09-15**, closing `PL-CNJ1`. That item gave generated output one
home, `out/`, ignored by `.gitignore`. Documenting it in `docs/worker.md` as

    `out/` is the one directory generated files go in

turned CI red in 24 seconds:

    docs/worker.md:50: cites `out/`, which does not exist

**The check is right and the prose was wrong**, which is why this is a gap
rather than a bug. `out/` genuinely does not exist in a fresh checkout, so a
trailing-slash citation of it asserts something false. The gap is that the
repository now has a category the checker has no way to express: a path that is
*meant* to be absent, named in documentation on purpose.

**Where.** `tools/doc_check.py:2213`, `_is_path_citation`:

    if token.endswith("/"):
        return True

then `_resolves` requires it to exist. There is no exemption, and the two
neighbouring escapes are accidents rather than design - `out/dashboard.png`
passes only because `.png` is not in `PATH_SUFFIXES` (line 239), and `out`
without the slash passes only because it has no suffix at all. So the honest
workaround, taken in `PL-CNJ1`, is to write `out` and never `out/`, which is a
rule no reader of either file can discover.

**The expensive half is that `make check` disagreed with CI.** The local run
passed, because testing the screenshot had *created* `out/` minutes earlier. A
session that documents a generated path and exercises it in the same sitting
gets a green `make check` on a tree CI rejects, and the error names a line the
session is confident about. That is `CLAUDE.md`'s first compounding-friction
test - a check passing while the guarantee it stands for is void - and it is
the same shape as `PL-QSJM` (a stale `__pycache__` keeping ruff green locally
while CI failed), reached through a different mechanism. Two instances now.

**Shape of a fix, decidable and therefore code rather than prose.** A cited
path that `.gitignore` covers is not required to exist: `git check-ignore -q
--no-index <token>` answers it exactly, deterministically, and with no judgment
in it. The narrower form - exempt any token matching an anchored directory rule
in `.gitignore` - avoids shelling out per citation. Either way the rule states
itself where a reviewer can read it, and the wrong-answer case closes: a
generated path is documentable, and a path that is neither generated nor
present still errors.

Worth measuring first, per the principle this repository already applies: how
many existing citations `.gitignore` covers. If the answer is one, this is a
comment in `doc_check.py` rather than a code change.

**The count, run 2026-09-15.** Over the documents `check_citations` reads
(`DOC_GLOBS`): 205 distinct path citations, 1,279 occurrences, and
**`.gitignore` covers none of them**. Widening the probe to every code span
that would be ignored if written as a directory finds three, none of which the
checker examines:

| Span | Where | Why it escapes today |
| --- | --- | --- |
| `` `out` `` | `docs/worker.md:50` | no suffix and no trailing slash, so `_is_path_citation` declines it - the `PL-CNJ1` workaround |
| `` `out/dashboard.png` `` | `docs/worker.md:40` | `.png` is not in `PATH_SUFFIXES` |
| `` `build/v0.1.0-sevo-patient` `` | `docs/WORKING_NOTES.md:65` | a git branch name rather than a path; `.gitignore`'s `build/` matches it by coincidence |

So the exemption would take **no existing citation out of the check**, and the
population it would newly admit is one line of prose. **The count is a
selection artifact and should not be read as demand**: the only citation that
ever wanted the exemption was reworded to dodge the checker before this item
was written, so counting survivors of the dodge measures how well the dodge
worked. The item's own threshold - one means a comment - was therefore met by
construction on the day it was written.

**What the count does not capture, reproduced 2026-09-15.** With the citation
written as `` `out/` ``, one tree gives two verdicts, decided by whether the
directory happens to be on disk:

    $ rm -rf out && python3 tools/doc_check.py check
    docs/worker.md:50: cites `out/`, which does not exist
    $ mkdir -p out && touch out/dashboard.png && python3 tools/doc_check.py check
    (no finding)

That is a property of `_resolves`, which answers from the working tree, and it
holds for **every** path `.gitignore` covers - `out/`, `.venv/`, `build/`,
`htmlcov/` - not only for the one instance counted above. A path git will never
track is one the working tree can only ever answer wrongly about in one of the
two environments, which is the case the exemption closes by construction. A
path that is merely uncommitted is different and benign: CI's disagreement
resolves when it is committed.

**One implementation note, measured rather than assumed.** `git check-ignore
--stdin` **aborts the whole batch** on the first malformed path: fed this
store's citation tokens it died on `fatal: //: '//' is outside repository` after
49 of 1,549 answers, having reported nothing about the rest. That is
`PL-0M7L`'s shape exactly - one token's failure swallowing every other
citation's verdict - so the call is per-token, and cheapest consulted only for
a citation that has already failed to resolve, which on a green run is none.
`git check-ignore` is also what reads this `.gitignore`'s negations
(`!.vscode/settings.json`) correctly, where the narrower "parse the anchored
directory rules" form would report a re-admitted file as exempt.

**Why it matters.** `docs/worker.md` is the file every delegated worker reads,
and the one directory it now has to name is the one the checker forbids it to
write. The cost per incident is small - a red CI in 24 seconds - but the
failure is of the shape this project treats as expensive: `make check` passes
on a tree CI rejects, so the session is confident in a line that is about to
fail, and the only way to comply is a rule (`out`, never `out/`) that no reader
of either file can discover.

**Decision needed.** Whether documentation may name a path `.gitignore` covers.
Three dispositions, all costing about the same to build except the third:

1. **Exempt it.** A citation that fails to resolve is checked against `git
   check-ignore -q --no-index`; ignored means not required to exist. `out/` is
   then writable as prose, and the verdict stops depending on the working tree
   for every ignored path. Cost: a typo landing inside an ignored directory
   goes unreported - measured blast radius today is nil, since no existing
   citation is covered.
2. **Report it better.** Same `git check-ignore` call, opposite verdict: still
   an error, but the message names `.gitignore` as the reason and says to drop
   the trailing slash. Documentation still may not name a generated directory;
   the local/CI divergence stays.
3. **Comment only**, as the threshold above suggests. The weakest of the three:
   the reader who is stuck is editing `docs/worker.md`, and a comment in
   `tools/doc_check.py` is not where they are.

**Decision taken 2026-09-15** (project owner): disposition 1, exempt it.

`_covered_by_gitignore` asks `git check-ignore -q --no-index` about a citation
that has **already failed to resolve**, so a run with nothing wrong in it
starts no subprocess at all and the cost falls on the findings rather than on
the 1,279 citations around them. Git answers rather than a parser reading the
anchored directory rules, because this `.gitignore`'s negations are
load-bearing - `.vscode/*` excludes the directory's contents and
`!.vscode/settings.json` re-admits the tracked project settings, which the
narrower form would have called exempt. One call per token rather than
`--stdin`, for the batch-abort reason measured above. Every way git can decline
- no checkout, a path outside the repository, no git on `PATH` - is read as
*not* covered, so the exemption is granted only on a positive answer and a
braced token needs one for every expansion.

`docs/worker.md:50` now reads `` `out/` ``, and the two verdicts agree: with
the directory absent and with it present, `doc_check check` reports nothing.
A directory that is neither ignored nor present still errors.

**This also answers `PL-F933`** (doc_check resolving a path citation against
the working tree), which is the same defect found two days earlier from the
other end - a `.venv/` citation in `subprojects/docket/README.md` green locally
and red in CI. It proposed the opposite mechanism, refusing an ignored citation
whether or not it resolved; the goal both state is one answer in both places,
and exempting reaches it while leaving documentation able to name the
directories it is documenting. Closed together on this branch.

**Done when.** `docs/worker.md` can name `out/` with its trailing slash and
`make check` agrees with CI on a clean checkout, or the decision not to change
the checker is recorded here with the count behind it.
