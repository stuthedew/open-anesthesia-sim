---
id: PL-8HJ2
title: make release stops mid-way on the ROADMAP table it does not write, so every release ends in a red test
priority: P2
effort: S
status: done
classes: defect, infra
feature: release-roadmap-seam
milestone: v0.2.8
touches: subprojects/docket/src/docket/release.py, Makefile, subprojects/docket/tests/test_release.py, ROADMAP.md
added: 2026-08-30
closed: 2026-08-31
commit: f9f5226
pr: 100
not-delegable: proving this means cutting a release, so no check can run beforehand - the same reason PL-674D carried
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

**Where.** `subprojects/docket/src/docket/release.py` and the `release` target
in `Makefile`, with tests in `subprojects/docket/tests/test_release.py`.

**Decided 2026-08-30: prompt, do not generate.** The open question was whether
`make release` should write the version-table row and baseline section itself.
It should not. Composing them means writing release prose - the v0.2.7 row and
baseline paragraph took real thought about what the release was *for* - and
that is precisely the judgment half `CLAUDE.md` says not to script. So
`make release` stops cleanly after the mechanical half and says what is left
to do by hand, which keeps the judgment where it belongs and makes the command
honest about where it ends. It is also much the cheaper of the two.

Scope is narrowed accordingly: `roadmap.py` is dropped from `touches`, since
nothing generates the row.

**The other half of the seam.** `PL-M5FK` (`ROADMAP.md`'s tag statements go
stale on every release and no check reads them) carries the same decision from
the other side: the release path touches `ROADMAP.md` in three places - the
version-table row, the baseline section, and the tag statements - and writes
none of them, so `doc_check` grows the checks that catch the omission rather
than `make release` growing the prose. Do the two together; they share the
`release-roadmap-seam` feature.

**Done when.** `make release VERSION=x.y.z` stops with an exit status and a
message naming the `ROADMAP.md` edits still owed and the re-run of
`make check`, rather than dropping into a test failure with the tree
half-updated; and `ROADMAP.md`'s claim that `PL-N2N1` "stopped leaving this
file's version table and baseline heading to drift" is reworded to say that
the drift is caught rather than prevented.
