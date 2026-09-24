---
id: PL-LWMS
title: Check the attribution trailers a pull request's commits carry, if stating PL-B11M's rule where sessions read it (PL-SL16) does not stop model-named co-authors
priority: P3
effort: M
status: blocked
classes: infra
feature: public-history
touches: tools, tests/unit, Makefile, .github/workflows/pr-title.yml
blocked-by: PL-XH1D, PL-SL16
added: 2026-08-30
verify: uv run pytest tests/unit -k commit_msg
---

**Re-confirmed 2026-09-24: changed shape.** The item was filed as a local
`commit-msg` hook that would normalize subjects, bodies and trailers. On
2026-09-24 a re-confirmation re-measured every claim in the original brief
against `origin/main` and the branch commits GitHub keeps for each merged pull
request. It used four auditors, one adversarial verifier each and a
completeness critic. One problem survives, and it is not where the brief put
it. Most of the mechanism was overtaken or is now contradicted. This brief
replaces the old one. Everything dropped, and why, is recorded under "Dropped"
below, so that no session proposes it again without the evidence. The
2026-08-30 text is at `git show
a56c86c4:docs/items/PL-LWMS-normalize-commit-messages-and-trailers-with-a.md`;
the rewrite changed too much for `git log --follow` to pair the two files.

**Problem.** No attribution convention holds across sessions by agreement
alone, and the one the project owner decided is broken in practice. `PL-B11M`
records the decision (project owner, 2026-09-16): the trailer stays
`Co-authored-by: Claude <noreply@anthropic.com>`, "with no model id in any
pushed artifact".

Of the 970 branch commits in the pull requests merged since 2026-09-17, 800
carry a model-named co-author: 469 `Claude Opus 5`, 316 `Claude Opus 5.5`, 14
`Claude Fable 5.1` and 1 `Claude Sonnet 5`, against 152 plain `Claude`
(measured 2026-09-24 over `GET /pulls/N/commits`, and reproduced by an
independent verifier).

The cause is routing, not the absence of a check. Until `PL-SL16`
(2026-09-24), no file a session reads before committing stated the decision;
`CLAUDE.md` § "Name the work after the item" now does. The harness's own attribution reminder
names `Co-Authored-By: Claude Opus 5.5`, and it yields to "a CLAUDE.md or
memory rule". `PL-SL16` carries the evidence and the one-sentence fix.

**Why it matters.** Attribution is provenance, and the owner decided its form
for a provenance reason: a trailer the session writes records the *configured*
model, so it is confidently wrong at exactly the fallback it would be read to
detect (`PL-B11M`). Model-named co-authors also fork one contributor into one
identity per model release, in every pushed branch GitHub keeps against a merged
pull request. A convention broken on 82% of the branch commits pushed since
2026-09-17 is one nobody can cite, so what history says about who wrote what
depends on which harness happened to write each commit.

**This item is the check that stands behind `PL-SL16`, and is built only if
that sentence does not hold.** `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work" says a check earns its place every run or is retired. If
the re-count below comes back at zero, this check would fire on nothing and
should not be built. The re-count is this item's first step: `PL-SL16` closed
on the sentence alone on 2026-09-24 and handed it here, because the count
decides this item and a closed item cannot hold a step that waits.

**Name the number before deciding.** Build only if model-named co-author lines
persist on the branch commits of pull requests merged after `PL-SL16` lands.
Drop this item on the evidence if they do not. Count only pull requests whose
branch was cut from a `main` already holding the commit that closed `PL-SL16`
(its `pr:`), tested as `git merge-base --is-ancestor <that commit> <parent of
the branch's first commit>`: a session keeps the `CLAUDE.md` it launched with,
so a branch cut earlier cannot test the sentence. Take the count once 30 such
pull requests have merged; fewer is not a reading. Re-run `PL-SL16`'s census
over their branch commits - `GET
/repos/stuthedew/open-anesthesia-sim/pulls/N/commits`, co-author lines tallied
by name - and write the count here. The owner's rule says "any", so
any residue is a violation, but a check that refuses a pushed branch also costs
a rewrite of that branch's commits. The session that reads the count weighs
that cost against the residue it finds, and says which way it went.

**What lands on `main`, and so what the check can and cannot reach.** The
repository squash-merges with `squash_merge_commit_title: PR_TITLE` and
`squash_merge_commit_message: PR_BODY`. `main`'s subject and body are therefore
the pull request's title and description. GitHub then appends `Co-authored-by`
lines built from the branch commits' authors and trailers, and drops a
model-named co-author that shares its email with a `Claude
<noreply@anthropic.com>` author. That is why 280 of the 282 co-author lines on
first-parent `main` since 2026-09-18 are plain `Claude`.

A model name reaches `main` only in two cases:

- **The branch is owner-authored**: `#580` to `#582` and `#602`.
- **The message is hand-composed at merge**: `#844` and `#968`, the 2 of 391
  first-parent commits since 2026-09-16.

So the enforcement point is the pull request's own commits, read on the
`pull_request` event. A local hook is not the enforcement point, and neither is
the description: the trailer block on `main` is in neither the title nor the
body. A null-armed auto-merge lands the live title and body (`PL-M7W1`'s
2026-09-23 evidence). A text arm or a hand-composed message stays outside any
pre-merge check.

**Where.** A step in `.github/workflows/pr-title.yml`'s required `pr-title`
job. It reads the trailers of `PR_BASE..HEAD`, which that job already fetches
at full depth. It goes there rather than in `quality.yml` because
`pr-title.yml` also fires on `edited` (`PL-3V8K`). The logic lives beside or
inside `tools/pr_title_check.py`, and also runs under `make check` the way
`--discover` does. Where it lives is the first design choice, and it is taken
when the item is started.

**Approach.** Check form, never judgment: the `tools/doc_check.py` line.

- A `Co-authored-by` value (any case of the key) naming a model is refused,
  because `PL-B11M` decided it.
- The rest of the permitted trailer set comes from `PL-XH1D`, once it states
  what each trailer means and which author/co-author combinations are allowed.
  It has to admit `Claim:` and `Yield:` (`bin/docket claim` and `yield`) and
  the harness's `Claude-Session:` line.
- Whether a `Co-authored-by` claim is *accurate* is out of scope; that is
  judgment. Nothing gates it on the owner reading the diff, either: `main`
  requires no approving review, and sessions arm auto-merge.

**Kept from the original brief.**

- **Never insert `Reviewed-by:`.** A trailer asserting review by default is
  false by default. There are 0 on `origin/main` today.
- **The existing history is not rewritten.** That was already so, and it now
  binds twice over: 604 first-parent commits since `bd874a5c` (2026-09-06) are
  GitHub-signed, and every closed item's `commit:` would dangle.

**Dropped, with the evidence** (all measured 2026-09-24 on `origin/main`
unless noted):

- **A local `commit-msg` hook as the enforcement point.** Nothing in the tree
  installs a git hook or sets `core.hooksPath`. It would check only branch
  commits the squash discards. It would also run on `bin/docket claim`'s
  commits, which go through `git commit` without `--no-verify`. Commit-time
  rules here run as Claude Code `PreToolUse` hooks in `.claude/settings.json`,
  which need no install. That route is still a new check, though.
- **Subject length.** The brief's "126 against a median of 61" does reproduce,
  over 271 commits before 2026-08-30. But the 126 is a two-line first paragraph
  that `%s` joins; the longest real first line was 91. Subjects on `main` are
  now pull request titles, which must lead with every id they close
  (`CLAUDE.md` § "Name the work after the item"). The last 200 have a median of
  101.5. With the id prefix and the " (#N)" suffix removed, 123 of 200 (61.5%)
  are still over 72.
  - No harm from length has been named. The ids tooling reads sit at the front,
    where truncation cannot reach them.
  - So a length rule has no break-even stated. Under `CLAUDE.md`'s "where the
    benefit is unclear, the answer is no", it is dropped rather than parked.
  - Refile it only with a named harm.
- **A blank line after the subject.** Only 4 commits in all history lack one,
  all off the first-parent line; the last is `b725f1a8` (2026-08-30). There is
  nothing to catch.
- **Body wrapped at 72.** The merge path already hard-wraps `main`'s bodies,
  and pull request descriptions are Markdown. That wrap is itself damaging
  tables: `PL-BZHX`.
- **A forbidden-pattern check on session-report sections.** The premise, that
  "session reporting has a home already: the pull request description", has
  inverted. Under `PR_BODY` the description *is* `main`'s commit body.
  `tools/pr_body_check.py`'s docstring keeps "what was refused, what was
  measured, what was filed" as the record. The literal examples ("Captured:",
  "as it should", "for maintainer review") appear 0 times on first-parent
  `main`. Their descendants are house style rather than drift: a narrated
  `docket verify` verdict appears in 114 of the 186 recent non-empty bodies, and
  a "## Verification" heading in 147.
- **A stable identity with "the model recorded under its own key".** `PL-B11M`
  refused a model key outright: no model id in any pushed artifact.
- **`.mailmap`.** The owner's second address authored 9 commits and committed
  8, all dated 2026-08-23 to 2026-08-31, and none since.
  - GitHub already shows one contributor (`stuthedew`) and does not read
    `.mailmap`, so the file would change only local `git shortlog` output for
    those commits.
  - No tool reads author identity.
  - Where the benefit is unclear, the answer is no.
- **"The web session, the CLI and a GitHub Action".** No Action ever wrote
  commits here. The third writer was the Claude GitHub App as `claude[bot]`
  (18 first-parent commits), which stopped on 2026-09-08. Today attribution is
  written by the harness on branch commits, by GitHub's squash composer, and by
  `bin/docket claim` (`Claim:`).
- **"A single-commit pull request still seeds its default message from them."**
  This is false under `PR_TITLE`/`PR_BODY`.
- **`PL-S4M2` as a blocker.** It is done.

**Held by the generator pause.** `CLAUDE.md` § "What this project is" holds "a
new command, check, field or rule" while any open item carries `generator:
live`. `bin/docket generators` showed four heads still generating on
2026-09-24. This is a new check, so it waits for the pause to end or for the
owner to ask. `PL-SL16` is the one part that needs no lift, because it states
a decision already taken.

**`verify:` is still the grandfathered bare `-k`** (`PL-Q8RQ`): it selects
nothing and exits 5. Replace it with a `grep` for the test the work adds, once
the first design choice above has fixed which file that test lives in.

**Done when.** One of two outcomes:

- **Built.** The re-count above is written here and justifies the check. A pull
  request whose commits carry a model-named co-author, or a trailer outside
  `PL-XH1D`'s set, fails `pr-title`. The check has a test for each rule and one
  for a well-formed branch that passes.
- **Dropped.** The item is dropped with that count as its reason.
