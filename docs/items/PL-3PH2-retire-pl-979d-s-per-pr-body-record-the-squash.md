---
id: PL-3PH2
title: Retire PL-979D's per-PR body record: the squash commit on main is the record of a pull request's body again, a body a merge drops is recovered in one batch at each release, and no pull request runs --record or pr-title's body check
priority: P2
effort: M
status: ready
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, .github/workflows/pr-title.yml, .claude/hooks/docket-digest.sh, .claude/skills/docket/modes/release.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/capture.md, .claude/skills/docket/modes/start.md, docs/maintainer.md, docs/ARCHITECTURE.md, ROADMAP.md, docket.toml, tools/fixture_id_check.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, docs/items/PL-979D-the-squash-commit-on-main-is-composed-by.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-26
payoff: no pull request carries a record step or a body check, and a body a merge drops still reaches the tree at the next release
verify: ! grep -q pr_body_check .github/workflows/pr-title.yml && grep -q pr_body_check .claude/skills/docket/modes/release.md && ! grep -q -- '--record' .claude/skills/docket/modes/close-out.md
---

**Problem.** Retire PL-979D's per-PR body record: the squash commit on main is the record of a pull request's body again, a body a merge drops is recovered in one batch at each release, and no pull request runs --record or pr-title's body check

**Why it matters.** `PL-979D` (#1068) put a step on every pull request -
`tools/pr_body_check.py --record` once it is open and again after any edit to
its body, often a push of its own - and a required check that holds the merge
until the tree holds the body. It was built against a 27.4% loss (187 of 683
squash bodies empty, `PL-843V`) that came from one merge client, the GitHub
iPhone app, which the owner stopped merging in on 2026-09-22. Measured
2026-09-26 over the first-parent squash commits on `origin/main`: 2 empty of
the 149 merged after `#918` (the last phone merge) up to `#1068` - `#1015` and
`#1044`, both reported by the offline advisory and recovered by `--recover`
under `PL-HZ0M` - and 0 of the 39 since. In its first day the record produced
four items: `PL-F6MM` (P1, claimless queue branches refused, fixed in #1077),
`PL-K9XQ` (a red `pr-title` run and a CI-failure wake on every draft opened
with a description), `PL-7VWK` and `PL-X2XP`. And no established practice
archives every pull-request body in the tree: the kernel asks that a patch
description be understandable "without external resources"
(`Documentation/process/submitting-patches.rst`, "Describe your changes"),
Go's GerritBot imports the PR title and description as the commit message,
and GitHub's squash default "pull request title and description", which this
repository uses, makes the commit message the record. towncrier's per-PR
files are the nearest shape, and `towncrier build` removes them with `git rm`;
git-appraise keeps review data in `refs/notes/devtools`, not the tree.

**Decided 2026-09-26** (project owner, 2026-09-26, ratified, over keeping the
per-PR record behind `pr-title`'s required check and fixing `PL-K9XQ`, and over
recording every body in one batch at each release). The squash commit's body
on `main` is the record of a pull request's body again. `docs/pr-bodies/`
holds only the bodies a merge dropped, recovered in one batch at each release;
nothing runs per pull request, and the files already there stay. Accepted as
properties of the record rather than defects: a hard-wrapped table
(`PL-BZHX`), a body edited after auto-merge was armed landing as armed
(`PL-M7W1`'s body half), and a merge that sends a different non-empty message
(`#744`'s kind), which nothing detects offline and `--compare` measures by
hand. Counted against it: the 44 bodies recorded under `PL-979D` are not
copies - a median 91% of each body's 8-word runs appear nowhere else in the
tree - which is why a dropped body is still recovered rather than let go.
What would reopen it: merges dropping bodies again at anything like the
phone's rate, for instance if merging from the phone resumes. The case was
put in the reply that proposed it, on `claude/pr-body-storage-cnnpme`.

**Build plan** (the build's own calls, inside the decision):

1. `.github/workflows/pr-title.yml`: remove the `pr_body_check.py --check`
   step and its `PR_BODY` environment.
2. `tools/pr_body_check.py`: remove `--record` and `--check` and what only
   they use; keep the default mode, `--recover`, `--compare` (hand-run) and
   `--anchors` (`make check`). Rewrite the docstring's opening to the decision
   above and keep the measured history below it. `tests/unit/test_pr_body_check.py`
   follows; check `tools/fixture_id_check.py`, `docket.toml` and
   `subprojects/docket/src/docket/vcs.py`, which also name the tool.
3. `.claude/hooks/docket-digest.sh`: stop running the default mode at session
   start. Between a drop and the next release it would fire in every session
   with nothing a session should do, which `CLAUDE.md` calls a defect in a
   check; the release step replaces it.
4. `.claude/skills/docket/modes/release.md`: before the release commit, run
   `python3 tools/pr_body_check.py`; where it lists commits, run `--recover`,
   and the files ride the release's pull request.
5. `.claude/skills/docket/modes/close-out.md` step 1 and `capture.md`'s
   "Before arming, record the body" paragraph: remove the `--record`
   instructions; `start.md` too if it names them.
6. `docs/maintainer.md` § "Merge on the Mac or by auto-merge, never in the
   GitHub app", `docs/ARCHITECTURE.md`'s line for the tool and `ROADMAP.md`'s
   mention: the squash commit is the record, and `docs/pr-bodies/` holds
   recovered drops. The never-merge-in-the-app rule protects the record again.
7. docket: `verify.py`'s `record` kind sanctions a branch-added file with a
   `recorded:` header, which no branch adds now, while a release adds
   `recovered:` files - the build decides whether the kind takes those or
   retires, with `test_verify.py`. `arming.py`'s and `claims.py`'s `RECORDS`
   stay unless the build finds them dead.
8. Items: `PL-K9XQ`, `PL-X2XP` and `PL-7VWK` close `dropped` against this
   decision. `PL-979D` gets a "Superseded 2026-09-26" note, and its
   `generator:` reason, which names the `--record` step and the `pr-title`
   hold, is rewritten to say the squash commit is the record with each merge
   path's rewrites accepted except a dropped body, which the release recovers.

**Done when.** No pull request runs a body check or a record step, the release
mode recovers dropped bodies, every document above says the squash commit is
the record, the three follow-ons are closed, and `make check` is green.
