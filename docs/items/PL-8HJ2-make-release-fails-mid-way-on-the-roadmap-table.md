---
id: PL-8HJ2
title: make release fails mid-way on the ROADMAP table it does not write, so every release ends in a red test
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/roadmap.py, Makefile
added: 2026-08-30
---

**Problem.** Cutting v0.2.7 ran `make release VERSION=0.2.7`, which bumped
`pyproject.toml`, wrote `docs/releases/v0.2.7.md`, stamped `milestone:` on the
fourteen items, ran `uv lock` — and then failed `make check` on
`tests/unit/test_doc_check.py::test_this_repository_is_clean`:

    ROADMAP.md:46: the current baseline row is v0.2.6, but pyproject.toml
    holds 0.2.7

`bin/docket release` does not write `ROADMAP.md`'s version table row or its
"Current baseline" section; `doc_check` catches that they disagree. Both are
working as built. The result is that the documented release command always
ends in a failing test, with the tree half-updated, on a failure that is not a
defect at all.

**Why it matters.** This is the same shape as `PL-674D` (`docket release`
bumps `pyproject.toml` but leaves `uv.lock`), which was fixed by making
`make release` run the whole sequence. That fix left one manual step inside
the sequence, and the sequence does not know about it — so the command reports
failure on success, which is the state that trains a maintainer to read a red
`make check` as normal. It also fires on every release rather than
occasionally.

`ROADMAP.md`'s v0.2.6 paragraph says `PL-N2N1` "stopped leaving this file's
version table and baseline heading to drift". That is true in the sense that
drift is now *caught*; it is not prevented, and the sentence reads as though it
were.

**Where.** `subprojects/docket/src/docket/release.py`, `roadmap.py`, and the
`release` target in `Makefile`.

**Worth deciding.** Whether the table row and baseline section are generated
or merely prompted for. Generating them means composing release prose, which
is judgment and is exactly what `CLAUDE.md` says not to script — the v0.2.7
row and baseline paragraph took real thought about what the release was *for*.
Prompting means `make release` stops cleanly after the mechanical half with
"now write the ROADMAP.md row and baseline section, then re-run `make check`",
which keeps the judgment where it belongs and makes the command honest about
where it ends. The second is probably right, and is much the cheaper.

**Done when.** `make release VERSION=x.y.z` either completes green or stops
with an instruction rather than a test failure, and `ROADMAP.md`'s claim about
what `PL-N2N1` prevents matches what it does.
