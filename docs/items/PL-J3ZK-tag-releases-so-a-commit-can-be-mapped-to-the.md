---
id: PL-J3ZK
title: Tag releases so a commit can be mapped to the version it shipped in
priority: P2
effort: S
status: done
closed: 2026-08-30
commit: 6c6a8af
classes: infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, .claude/skills/docket/SKILL.md, ROADMAP.md, subprojects/docket/tests
added: 2026-08-25
verify: uv run pytest subprojects/docket/tests -k tag
---

**Problem.** `v0.0.1`, `v0.0.2` and `v0.2.3` are tagged; `v0.1.0`, `v0.2.0`,
`v0.2.1` and `v0.2.2` are not. Those four were bumped in `pyproject.toml` and
shipped without a tag, so `git describe --contains` resolves nothing for any
commit between `v0.0.2` and `v0.2.3`, and there is no way to ask which release
a given change in that span went out in. v0.2.3 was tagged at release
(`7494031`), which starts the practice but does not close the gap behind it.

**Why it matters.** It cost real accuracy once already. Backfilling the
`milestone` field on historical items should have been a git query - find the
first tag containing each item's commit - and instead had to fall back to
stamping all of them `v0.2.2`, which is true but coarse: work that actually
shipped in 0.1.0 or 0.2.0 is now recorded as having shipped in 0.2.2. For a
project whose standard is that a displayed value be traceable to the exact
version that produced it, an unreliable version history is a provenance gap,
not a tidiness one.

**Where.** `subprojects/docket/src/docket/release.py` (the release command
already prints the tag to create, but nothing enforces it),
`.claude/skills/docket/SKILL.md`.

**First step.** Decide whether `docket release` should create the tag itself
or keep printing the instruction. Creating it is a write to shared history
from a tool that otherwise only edits files, which argues for keeping the
instruction and adding a check that the previous version was tagged before a
new one is cut.

**The retrospective half: partly unachievable, established 2026-08-25.**
Two passes were needed, and the first one's answer is wrong - recorded here
because it is the answer anyone will reach first.

*Pass one, superseded.* Searching for the version string in `pyproject.toml`
gives `1f655f0` for v0.2.0, whose own message says the file "was still 0.1.0
after v0.2.0 shipped", and `16939cf` for v0.1.0, a root commit that introduced
the file wholesale. Reading release commits by subject instead - the
convention both existing tags follow - gives `875ba08`/`97cc66a` for v0.1.0,
`796bf4f` for v0.2.0, `bc5f823` for v0.2.1 and `3099980` for v0.2.2. That
looked like four tags waiting to be placed. It is not.

*Pass two: the history has three unrelated roots.* `main` contains `80c7aab`
(the v0.0.2 circuit model), `674c8ae` (shared safety-critical instructions)
and `16939cf` (the line carrying the v0.1.0-to-v0.2.0 application work), first
joined at `3ab9459` "Merge remote-tracking branch 'origin/main'" on
2026-08-23. `git merge-base 796bf4f 97cc66a` returns nothing at all: the
v0.1.0 and v0.2.0 work share no ancestor, so neither can contain the other
under any tag placement, and `git log v0.1.0..v0.2.0` would be meaningless
however the two are tagged. The existing `v0.0.2` tag is on a root commit for
the same reason.

So the goal in this item's title - map a commit to the version it shipped in -
is unreachable for anything before `3ab9459`, and no choice of tag commit
changes that. It is a property of the history, not of the tags.

| Version | Commit | Status |
| --- | --- | --- |
| v0.1.0 | `875ba08` or `97cc66a` | pre-graft; tag would not answer `describe --contains` |
| v0.2.0 | `796bf4f` | pre-graft; same |
| v0.2.1 | `bc5f823` | post-graft, ordered after nothing tagged but before v0.2.2 |
| v0.2.2 | `3099980` | post-graft, ordered correctly against v0.2.1 and v0.2.3 |

**Recommendation.** Tag `v0.2.1` at `bc5f823` and `v0.2.2` at `3099980`; leave
v0.1.0 and v0.2.0 untagged and state why in `ROADMAP.md`'s versioning table.
Those two tags are monotonic against each other and against `v0.2.3`, so from
v0.2.1 onward the history answers version questions properly - which covers
every commit the milestone backfill mis-stamped. Tagging the pre-graft two
would put a version marker on a line that cannot be compared with any other,
which reads as provenance and is not: worse than the gap it appears to close,
per this project's own preference for an obvious absence over a plausible
answer.

The alternative is grafting the roots together with `git replace` or a history
rewrite. That buys a coherent `describe --contains` across the whole history
and costs every existing commit hash, including the ones this queue, the
release notes and `ROADMAP.md` now cite correctly. Not worth it for a
provenance question that only affects four weeks of prehistory - but it is the
only thing that would actually close the gap, so it is the decision, not a
detail.

**Done when.** Cutting a release either creates the tag or refuses while the
previous version is untagged; `v0.2.1` and `v0.2.2` are tagged at the commits
above; and `ROADMAP.md`'s versioning table records that v0.1.0 and v0.2.0 are
deliberately untagged, with the unrelated-roots reason.

**Context.** Found while inverting the milestone model so that a release
records what shipped rather than planning what will. The backfill is recorded
in the commit that introduced it.

**Pass three, 2026-08-30: pass two was measured in a shallow checkout, and its
central claim is false.** The mechanism half is built and the two recommended
tags are placed; what changed is the reason the other two were ruled out.

`git clone --depth` marks boundary commits as parentless, so a shallow
checkout reports them as roots and `git merge-base` returns nothing across the
boundary. That is what pass two was reading. After `git fetch --unshallow` in
the same repository:

- `git rev-list --max-parents=0 --all` returns **one** root, `0ba1ab5`.
- Each of the three commits pass two named as a root has a parent:
  `80c7aab`←`b64d768`, `674c8ae`←`ca85e21`, `16939cf`←`7daa5b6`.
- `git merge-base 796bf4f 97cc66a` returns `97cc66a` — v0.1.0's work is an
  ancestor of v0.2.0's, not unrelated to it.
- `97cc66a` → `796bf4f` → `bc5f823` → `3099980` → `v0.2.3` is a straight
  ancestry chain, each confirmed with `git merge-base --is-ancestor`.

So tagging v0.1.0 and v0.2.0 *would* answer version questions, and the
paragraph above headed "the history has three unrelated roots" is an artifact
of how the repository was fetched rather than a property of the history. It is
left in place rather than deleted, because a superseded analysis that is not
recorded gets re-derived — and because this is the second time the same
question has been answered wrongly with confidence.

**Decision needed.** Whether to tag v0.1.0 and v0.2.0 retrospectively now that
the objection to doing so has dissolved. The remaining question is only which
commit v0.1.0 belongs on: `875ba08` ("Build v0.1.0 sevo patient simulation")
or `97cc66a` ("Close v0.1.0 doc/test gaps"), the latter being the last commit
of that release's work and the one the release-commit-by-subject convention
points at. v0.2.0 is unambiguous at `796bf4f`.

```bash
git tag -a v0.1.0 97cc66a -m "v0.1.0"
git tag -a v0.2.0 796bf4f -m "v0.2.0"
git push origin v0.1.0 v0.2.0
```

Nothing is lost by deciding later: both are ordinary ancestors of `main` and
can be tagged at any time. That is the opposite of the situation for a release
cut *from now on*, which is why the refusal below was built rather than left
to memory.

**Blocked on the owner: this environment cannot push tags.** `git push origin
v0.2.1 v0.2.2` returns HTTP 403 while a branch push from the same session
succeeds, so the credentials are scoped to `refs/heads/claude/*`. The two tags
were created locally and verified — `git describe --contains 655e429` resolves
to `v0.2.1~1` — but a local tag in an ephemeral container is not a tag. These
two commands place them, and they are the whole of the retrospective half that
is not a decision:

```bash
git fetch --unshallow          # bc5f823 is beyond a shallow clone's boundary
git tag -a v0.2.1 bc5f823 -m "v0.2.1"
git tag -a v0.2.2 3099980 -m "v0.2.2"
git push origin v0.2.1 v0.2.2
```

**Closed, 2026-08-30. Every version is tagged.**

The owner placed the last four tags: v0.2.1 (`bc5f823`), v0.2.2 (`3099980`),
then v0.1.0 (`97cc66a`) and v0.2.0 (`796bf4f`). All eleven released versions
now carry annotated tags, which closes both halves of this item - the practice
going forward and the retrospective gap behind it.

The open decision is resolved rather than deferred: v0.1.0 and v0.2.0 were
recorded here as untaggable on a shallow-checkout measurement, and in the full
history `97cc66a` is an ancestor of `796bf4f`, so the tags went where the
release commits are. `git describe --contains` was then checked across all 214
commits on `main`: it resolves for every one except the nine unreleased
commits after v0.2.7, which is the expected boundary rather than a gap.

- The two tags above are decided and their commits confirmed; both are now
  pushed.
- `docket release` refuses to cut while the version it is releasing *from*
  carries no tag, and prints the three commands to place it rather than the
  instruction to. A project holding no tags at all is exempt: emptiness there
  says the project does not tag releases, and adopting the practice is its
  decision rather than this tool's. `--dry-run` warns and continues, since
  withholding the notes would not make the tag appear.
- `docket release`'s closing line now prints the `git tag`/`git push` pair
  with the version filled in, and the skill's release mode says never to ask
  for a tag without them.
- `ROADMAP.md`'s versioning section records which versions are tagged, which
  two await the commands above, and why the other two are an open decision —
  the corrected reason, not the superseded one.
