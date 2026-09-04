---
id: PL-HKF4
title: doc_check's tag advisory prints `<merge commit>`, which a shell reads as redirection, so pasting it fails with "no such file or directory: merge" instead of tagging
status: ready
added: 2026-09-03
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/SKILL.md
verify: uv run pytest subprojects/docket/tests/test_cli.py && ! grep -rq '<merge commit>' subprojects/docket/src/docket/cli.py .claude/skills/docket/SKILL.md
---

**Problem.** `tools/doc_check.py:1273` prints the tag command as

    git tag -a v0.3.1 <merge commit> -m "v0.3.1"

A shell does not read `<merge commit>` as a placeholder. `<merge` is input
redirection from a file named `merge` and `commit>` is output redirection to a
file named `commit`, so pasting the line verbatim never reaches `git` at all —
zsh answers `no such file or directory: merge`, which names neither git, nor
the tag, nor the thing that is actually missing.

**Why it matters.** The advisory fires at exactly the moment somebody is
copying it, once per release, and the release cannot be finished until the tag
lands: `bin/docket release` refuses to cut the next one while the previous is
untagged. Observed 2026-09-03 on the v0.3.1 cut — the project owner pasted the
line and got the error, which cost a round trip to diagnose. The failure is
also maximally unhelpful for the one thing it is trying to teach: the reader
learns that a file called `merge` is missing.

`.claude/skills/docket/SKILL.md` already says "Never ask the owner to 'tag
vX.Y.Z'. Paste the commands, filled in", so the standard is written down and
the tooling does not meet it.

**Re-scoped by v0.3.4 (triaged 2026-09-03).** This item was written against
two callers. `PL-R7C0` then retired the `doc_check.py` one outright - a local
checkout cannot tell a release never tagged from one tagged since it last
fetched, so the advisory is gone rather than reworded - and with it goes the
half of this item that had the interesting problem in it, resolving the SHA
instead of naming it. What is left is the cheap half, unchanged in substance
and now the whole item: a placeholder no shell mangles. `S`, mechanical, and
still worth doing - it is still printed once per release at the moment somebody
is copying it, and the current text still costs a round trip.

**Where.** Three surviving sites, all printing the same string:

- `subprojects/docket/src/docket/cli.py:637` — fires at `release` time,
  **before** the merge exists. It genuinely cannot know the SHA, so a
  placeholder is correct; it just must not be one a shell mangles.
- `subprojects/docket/tests/test_cli.py:508` — asserts the string verbatim, so
  it changes with it.
- `.claude/skills/docket/SKILL.md:607` — the worked example a session copies.
  Same shape, and worth fixing for consistency, though a session is told to
  fill it in. Line 646's `--merge <merge commit>` is the same hazard in the
  `docket record` example and goes with it.

**Approach.** One change: replace the placeholder everywhere it survives with
something a shell cannot read as redirection. `git tag -a v0.3.1 MERGE_COMMIT -m
"v0.3.1"`, with a line above saying what `MERGE_COMMIT` stands for, fails as
`fatal: Failed to resolve 'MERGE_COMMIT'` - which names the actual problem,
where the current text names a missing file called `merge`. Any token with no
shell metacharacter works; the value is in choosing one whose git error is
self-explaining.

**Found.** Cutting v0.3.1 (2026-09-03), when the project owner hit the error.
Re-confirmed cutting v0.3.4 (2026-09-03): the session wrote the tag command out
by hand as `$(git rev-parse origin/main)` rather than paste what the tooling
prints, which is the workaround this item removes the need for.

**Done when.** No command printed by `subprojects/docket/` or quoted as a
worked example in `.claude/skills/docket/SKILL.md` contains a `<...>`
placeholder a shell reads as redirection, and `subprojects/docket/tests/test_cli.py`
asserts the replacement rather than the old string. `tools/doc_check.py` is out
of scope: `PL-R7C0` retired the advisory that printed it there.
