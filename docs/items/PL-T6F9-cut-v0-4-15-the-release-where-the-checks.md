---
id: PL-T6F9
title: "Cut v0.4.15: the release where the checks stopped over-reaching, and Gate 1 passed half"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.16
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-13
closed: 2026-09-13
pr: 511
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

**The procedure.** `.claude/skills/docket/modes/release.md` § "Mode: ship a release" is
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

**Closed 2026-09-13.** `pyproject.toml` reads `0.4.15`, `uv.lock` agrees,
`docs/releases/v0.4.15.md` names all 33 items, and `ROADMAP.md` carries the
v0.4.15 row, the baseline heading moved off v0.4.14 and the baseline section.
`make check` is green: 2388 tests, 100% coverage, 0 documentation errors, and
`docket check` reporting 0 errors with the one grooming advisory that is
`PL-D4GS`'s.

**The cut had to be run twice, and the first run is now `PL-1MKQ`.** A `make
release` interrupted inside `cmd_release`'s stamp loop left 26 items carrying
`milestone: v0.4.15` with the version unbumped and no notes file. The re-run
saw only the 7 still-unstamped items and produced a perfectly ordinary-looking
7-item release. The repair was to revert (`git checkout -- docs/items
pyproject.toml uv.lock`, plus the untracked notes file and the one item the run
had renamed) and cut once, uninterrupted. What caught it was comparing the dry
run's 33 against the cut's 7; no check did.

**Two numbers in the brief above were wrong, and the measured ones are these.**

- The brief says the `P1` band "fell 13 to 8". Counting open items - status not
  `done` or `dropped` - at the `v0.4.14` tag gives **11**, and the store now
  gives **8**, which matches `docket check`'s own line. 13 was the band's size
  on 2026-09-03, measured in `PL-CW14` and carried forward unchecked.
- The brief says "five separate gate entries" were a check over-reaching and
  then names four. Four is right for `#506` (`PL-CW14`, `PL-WTQ1`, `PL-KJ63`,
  `PL-Z0G0`); the release as a whole holds **ten** such entries, the other six
  being the `vcs.py` cluster in `#504`.

**The gate crossing, measured at both ends rather than asserted.** `bin/docket
wave` run against a worktree at the `v0.4.14` tag reads `158 entries, 56
cleared, 102 open`; run against this cut it reads `159 entries, 80 cleared, 79
open`. So the crossing of half happened inside this range, the gate took one
post-freeze entry, and 24 entries closed. Those numbers are recorded here and
deliberately **not** in `ROADMAP.md`: § "Debt gate: the frozen list" states
that how many are closed is not written into the document, and `PL-WSDY` -
shipping in this same release - closed the last narrative that violated it. The
baseline section states the crossing and points at `bin/docket wave` for the
split.

**Docs swept:** `ROADMAP.md` (the row, the baseline heading, the baseline
section, and a check that no other release narrative gained a gate count),
`docs/releases/v0.4.15.md` (generated; 33 entries verified against the 33
stamped items), `pyproject.toml`, `uv.lock`. `docs/MODEL.md` and `README.md`
need nothing: `src/anesthesia_sim/core/` and `app/` are byte-identical to
`v0.4.14`, and the only change under `src/` in the whole range is one provenance
note's wording, which `PL-S3Q0` made in `#507` along with its `docs/MODEL.md`
half.

**The tag is outstanding** and is the project owner's to push - a session's tag
push fails after reporting `[new tag]` (`PL-N936`).

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.15 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Nothing a learner can observe moved: `src/anesthesia_sim/core/` and `app/` resolve to the same tree objects as at `v0.4.14`, `.github/` is untouched, and the whole of `src/` changes in one string - the `note` on `reference_adult.json`'s Frayn and Karpe entry, which said a review "cannot be the authority for a stored value" where `docs/MODEL.md`'s own source hierarchy admits a tier-2 source on a recorded decision and the entry needed instead to say that no such decision has been taken for this parameter (`PL-S3Q0`). **Ten of the thirty-three entries are one defect in ten places: a check answering a question it could not decide, confidently, and charging a session for the difference.** Four are in the documentation and queue checkers - the top-band advisory prescribing a demotion `docket check` itself rejects as an error, on a band where twelve of thirteen items are class-pinned and one is demotable (`PL-CW14`); and `doc_check` reading a shell regex in an item's `verify:` front matter as LaTeX (`PL-WTQ1`), reading any double-quoted phrase as a section citation, so quoting a measured figure hard-fails (`PL-KJ63`), and attributing a candidate line to the alphabetically first matching term rather than the most specific (`PL-Z0G0`). Six are the `vcs.py` ref-lifecycle cluster, closed as one root-cause round: shipped items reported in flight in every digest because their refs outlived their merges (`PL-6BDX`), a triage skip-mark still firing after the branch it named had merged, which told one pass to skip four of its five items (`PL-8MJ3`), and four ways of calling a branch merged, stranded or left-behind by comparing content that a squash or a history rewrite leaves unchanged (`PL-JBRC`, `PL-XLQ5`, `PL-Y31G`, `PL-YDL6`). **Two sit either side of that line.** `PL-JSRH` closes a gap rather than a false positive - nothing stopped a branch rewriting a closed item's `closed:` or `milestone:`, which are records - and `PL-R6D8` is the same error in prose, a docstring claiming `git log --source` attributes a shared commit to the ref named first, which it does not. **`PL-W1LN` is the judgment running the other way:** the in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path, and the limit was reproduced, accepted and pinned rather than papered over. **`PL-3833` adds the one check that was missing** - an item filename drifted from its title - as an *advisory*, because the remedy needs judgment the tool does not have. **The cluster carried a pre-registered test and rejected its null** (`PL-CSHL`): against the cluster's own spawn rate of 1.05, nine closures predicted 9.5 new items and produced 3, rejecting H0 one-sided at 5% - recorded with the threat to the inference in the same breath, that one session closing nine items has fewer opportunities to file than nine sessions closing one, which this design cannot separate from a root-cause effect. **Nine entries are the documentation stating something untrue**, two safety- and three science-classed: `docs/MODEL.md` still saying all eleven reference-patient parameters are the Gas Man default patient (`PL-7KDC`), naming two mass-balance tolerance constants that do not exist in the code (`PL-L7JB`, `PL-MS54`), omitting lung tissue and pulmonary blood from its known limitations - worth about twenty percent of every agent's fast pool (`PL-Q5NS`) - and this file [`ROADMAP.md`] calling every drawn chart point an M4 representative of a bucket `PL-2FM6` deleted in v0.4.12 (`PL-DZFJ`), and not saying that cardiac-output scaling is planned-milestone item 30's obligation or that weight scaling is only safe as a coupled package (`PL-MMWX`). **Gate 1 passed half inside this range.** `PL-27S8` writes the rule that governs the next proposal to tighten anything - name what the suppressed side would have to be worth for the proposal to be wrong, then go and count it - and `PL-MGF9` is the first thing it would have caught, dropped rather than built because the advisory it specified could not fire and `bin/docket trend` had taken its job five days after it was captured.
