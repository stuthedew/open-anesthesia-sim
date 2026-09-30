---
id: PL-2FY6
title: Every release needs a second item, a second pull request and four pasted commands only to record the owner's tag push; a workflow that tags the cut's merge commit when it lands on main would make the release item and its one pull request the whole release
priority: P2
effort: M
status: done
classes: infra
feature: release-process
touches: .github/workflows/, tools/tag_release.py, tests/unit/test_tag_release.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/, subprojects/docket/README.md, .claude/skills/docket/modes/release.md, docs/worker.md, docs/ARCHITECTURE.md, docket.toml, ROADMAP.md
deferred-from: v0.6.0 - filed 2026-09-30, after the gate froze: a release-process decision rather than debt the milestone's work created, so it goes to the next gate
added: 2026-09-30
closed: 2026-09-30
pr: 1250
payoff: a release is one item and one pull request, and the tag lands on the cut's merge commit with nothing for the owner to paste
verify: grep -q "contents: write" .github/workflows/tag-release.yml && ! grep -q "git tag -a" subprojects/docket/src/docket/release.py && ! grep -q "git tag -a" .claude/skills/docket/modes/release.md
---

**Problem.** Every release needs a second item, a second pull request and four pasted commands only to record the owner's tag push; a workflow that tags the cut's merge commit when it lands on main would make the release item and its one pull request the whole release

**Why it matters.** Every cut costs a second item, a second pull request, a
CI run and a paste the owner has to remember, and a tag item left open with a
passing command turned `main` red once already (`PL-6TQH`).

**Done when.** `.github/workflows/tag-release.yml` tags the commit that adds
each new `docs/releases/v*.md` on `main`, `bin/docket release` prints a
confirmation command in place of the four-line tag block, release mode files
no `Tag vX.Y.Z on ...` item, and the first release cut after it merges is
tagged with nothing pasted.

**Asked 2026-09-30, by the project owner:** can all the utility commits for a
new version go on one pull request - one self-contained item that both cuts
the release and tags it, rather than a cut item followed by a tag item?

**Why the literal version cannot be one pull request.** The tag has to sit on
the squash-merge commit that lands the cut on `main` (`f52adae` for v0.5.19),
and that commit does not exist until the pull request merges; tagging the pull
request's head instead leaves `git describe` resolving nothing on `main`. And
no session here can push a tag ref (`PL-N936`). So some step has to happen
after the merge, and today that step is the owner's paste followed by a
tag-step item closed in its own pull request: 15 of them since v0.4.21 (v0.4.21
to v0.4.23, v0.4.30, v0.5.9 to v0.5.19), most with a pull request of their own
(`#1096`, `#1121`, `#1143`, `#1192`, `#1208`, `#1244`, and `#1248` for
v0.5.19). `PL-08D4`'s Generator check already names it as a design recurring
rather than a defect. Keeping the one release item open until the tag lands
still needs a second commit on `main` to close it; that commit either takes its own
pull request or waits for the next cut, with the item open and the paste still
the owner's.

**Decision needed.** Build the tag-on-merge workflow and retire the tag step,
or keep the owner's paste and the tag-step item as they are.

**Answered 2026-09-30: build it** (project owner, 2026-09-30, ratified, over
keeping the owner's four-command paste and a tag-step item closed in its own
pull request after every cut). The workflow tags the cut's merge commit, and
the tag step is retired from `bin/docket release`'s output and release mode.

**Recommendation: tag on merge in CI, and retire the tag step.** A workflow on
`push` to `main`, with `permissions: contents: write` and nothing else, that
for each `docs/releases/v*.md` added in the pushed range with no tag on origin
creates the annotated tag on the commit that added it - the lookup the pasted
block already uses, `git log --first-parent --diff-filter=A` - and pushes it
with the token `actions/checkout` persists. It exits at once on a push that
adds no notes file, and fails red where the tag exists on another commit. Then
`bin/docket release` prints a confirmation command instead of the four-line
block, release mode stops filing `Tag vX.Y.Z on ...`, and the release item and
its one pull request are the whole of a release; the owner's merge stays the
human gate, since `bin/docket arm` holds every release pull request for a
read. `bin/docket release`'s refusal to cut past an untagged release stays as
the backstop for a run that failed.

**What it costs.**
- The tagger becomes `github-actions[bot]` rather than the owner. The tags are
  unsigned today (`git cat-file -p v0.5.19` shows no signature), so no
  signature is lost.
- It adds a workflow holding write access to the repository's contents, which
  runs for a few seconds on every push to `main`.
- A tag pushed with `GITHUB_TOKEN` starts no workflow (GitHub Docs, "Triggering
  a workflow from a workflow"). Nothing here triggers on tags today, but a
  later `on: push: tags` workflow would need a different token.
- The repository's one ruleset, `Base`, targets branches only (GET
  `/repos/stuthedew/open-anesthesia-sim/rulesets`, 2026-09-30), so nothing
  blocks the push. A tag ruleset added later would need a bypass for GitHub
  Actions.
- Effort M: the workflow, `release.py` and `render.py`'s printed tag step and
  its tests, and release mode's tag sections.
- Undoing it is cheap: delete the workflow and restore the paste.

**Sources.** GitHub Docs, "Workflow syntax for GitHub Actions" § `permissions`:
"`contents: write` allows the action to create a release", and "If you specify
the access for any of these permissions, all of those that are not specified
are set to `none`."
https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
GitHub Docs, "Triggering a workflow" § "Triggering a workflow from a
workflow": "events triggered by the `GITHUB_TOKEN` will not create a new
workflow run", with named exceptions.
https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow
`actions/checkout` README, `persist-credentials` (default `true`): "The auth
token is persisted in the local git config. This enables your scripts to run
authenticated git commands." https://github.com/actions/checkout

**Generator check.** This is `PL-08D4`'s recurring design, the tag step, which
this item retires rather than a new head; no open item carries `generator:
live`, so the pause on new workflow machinery does not hold it, and the
owner's question lifts it for this request in any case.

**Done 2026-09-30.** `.github/workflows/tag-release.yml` runs
`tools/tag_release.py --apply` on each push to `main` that changes a release's
notes, and on dispatch. The script reads the version `origin/main` declares,
finds the commit that added its notes through `vcs.find_cut`, and where origin
lacks the tag, tags that commit and pushes the tag - then reads it back from
origin before reporting success, because a session's tag push exits clean and
lands nothing (`PL-N936`). It declines, red, where git will not answer, the
clone is shallow, the notes were added more than once, or origin holds the tag
on another commit. `bin/docket release` ends with `git ls-remote --tags origin
refs/tags/vX.Y.Z` in place of the four pasted lines; its refusal to cut past an
untagged release names the workflow run, the owner's, as the way back; release
mode files no tag-step item; and the `[TAGGED: ...]` mark `status` drew on one
went with `release.asked_tag`, since nothing can file one again. The draft was
written in the session that filed this item and handed over on 2026-09-30; this
session reviewed it, added the read-back after the push with its test, retired
the mark, and re-ran the gate. The last "Done when" clause - the first cut after
this merges is tagged with nothing pasted - can only be seen at the next
release. The merge of this pull request changes no notes file, so the
workflow's first run is a dispatch by the owner (Actions, then tag-release,
then Run workflow), expected to end green with `v0.5.19 is already on its cut
... nothing to do`, which proves the checkout, fetch and ls-remote steps and not
the push; v0.5.20's merge proves the push.
