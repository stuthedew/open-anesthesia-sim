---
id: PL-MXSL
title: doc_check requires a cited directory to exist with no exemption for one .gitignore covers, so documenting a generated directory fails CI while make check passes locally the moment anything has created it
status: untriaged
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

**Done when.** `docs/worker.md` can name `out/` with its trailing slash and
`make check` agrees with CI on a clean checkout, or the decision not to change
the checker is recorded here with the count behind it.
