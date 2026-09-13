---
id: PL-T6F9
title: "Cut v0.4.15: the release where the checks stopped over-reaching, and Gate 1 passed half"
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-13
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.15"' pyproject.toml && test -f docs/releases/v0.4.15.md
---


**Problem.** Cut v0.4.15: the release where the checks stopped over-reaching, and Gate 1 passed half

**Why it matters.** A release is how this project's work becomes legible to
its own future sessions: the version table is what `bin/docket wave` reads to
say where the plan stands, and the baseline prose is the only record of what a
range of work was *for*. Thirty-three finished items are currently unnamed by
any release, so the queue reports them as done and nothing says what they
amounted to. Cutting also unblocks the next one - `bin/docket release` refuses
while the previous version is untagged, and the same refusal applies to a
range never cut at all.

**Prerequisite, and it is a hard one.** `#508` must be merged first. It writes
the `pr` numbers that `#505`, `#506` and `#507` owed to fifteen closed items,
and this release stamps `milestone:` onto those same items while its notes
cite the pull request that closed each one. Cut before `#508` lands and the
notes cite nothing for fifteen entries. Check with `git log --oneline -3
origin/main` before starting.

**What the release is for.** Name it in the baseline prose rather than listing
items - the version table already lists them. Three threads run through the
range, and the first is the one worth leading with:

1. **The checks stopped over-reaching.** Five separate gate entries turned out
   to be the same defect in different places - a check reaching past what it
   could actually decide and charging a session for the difference. The
   top-band advisory prescribed a demotion `docket check` would itself reject
   as an error (`PL-CW14`, 12 of 12 startable P1 items class-pinned and none
   demotable); `doc_check` read a shell regex in YAML frontmatter as LaTeX
   (`PL-WTQ1`), a quoted measurement as a section citation (`PL-KJ63`), and
   labelled a candidate line by sort order rather than specificity
   (`PL-Z0G0`). Against that, `PL-3833` added the check that was missing: an
   item filename that no longer matches its title, reported as an advisory
   rather than an error precisely because the *remedy* needs judgment the tool
   does not have.
2. **Gate 1 passed half.** 80 of 159 entries cleared, 79 open - the first time
   more than half the frozen list is closed. The `P1` band fell 13 to 8 as the
   docs-accuracy batch closed its safety- and science-classed items.
3. **An item was dropped for being solved another way.** `PL-MGF9` specified
   an advisory that could not fire (74 of 244 open items process-classed
   against a majority of 123) and whose job `bin/docket trend` had already
   taken over, five days after it was captured. The `PL-LKGL` pattern, caught
   and closed honestly rather than built.

Read `bin/docket release --dry-run` for the full set - 33 finished items as of
2026-09-13 - and the individual release notes under `docs/releases/` for how
much prose each of these gets.

**The procedure.** `.claude/skills/docket/SKILL.md` § "Mode: ship a release" is
authoritative; this is the short form.

1. `git fetch origin main` and confirm `#508` merged.
2. Restart the branch on the merged base rather than reusing a merged one:
   `git checkout -B claude/pl-t6f9-cut-v0415 origin/main`.
3. `make release VERSION=0.4.15` - **never** `bin/docket release` alone, which
   bumps `pyproject.toml` and leaves `uv.lock` stale, failing the next `make
   check` on `uv sync --locked` for a reason unrelated to the release.
4. The command stops there and prints what is left: `ROADMAP.md` needs a
   version-table row, the `Current baseline:` heading moved onto it (it is at
   `ROADMAP.md:114`, reading v0.4.14), and a baseline section carrying the
   prose above. Nothing generates that prose.
5. `make check`. Run it only after step 4 - earlier it fails on edits nobody
   has been asked for yet.
6. Commit, push, open the pull request, let CI go green, merge.
7. **Then hand the project owner the tag, filled in - never ask them to "tag
   v0.4.15".** A session cannot push a tag: `git push --dry-run` reports
   `[new tag]` and the real push dies with `send-pack: unexpected disconnect`
   while `git ls-remote --tags` shows nothing (`PL-N936`). Branch pushes from
   the same session work throughout, so this is tag refs specifically. The
   three lines, run straight after the merge while `origin/main` is the merge
   commit:

   ```
   git fetch origin main
   git tag -a v0.4.15 origin/main -m "v0.4.15"
   git push origin v0.4.15
   ```

8. Say the tag is outstanding until they confirm it, and check rather than
   assume: `bin/docket release` refuses to cut the next release while the
   previous one is untagged, and nothing in the tree reports the gap.
   `git ls-remote --tags origin` is what answers - and read it sorted (`| sort
   -V`), because the raw output is lexicographic and `v0.4.9` sorts after
   `v0.4.14`. Every tag through v0.4.14 was present as of 2026-09-13.

**Done when.** `pyproject.toml` reads 0.4.15, `uv.lock` agrees,
`docs/releases/v0.4.15.md` exists, `ROADMAP.md` carries the row, the moved
baseline heading and the baseline section, `make check` is green, the pull
request is merged, and the tag command has been handed to the project owner.
