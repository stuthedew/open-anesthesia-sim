---
id: PL-BKDP
title: "A v0.4.8 tag exists on the commit that closed PL-0GTC and PL-SR8F, but no release was cut there: pyproject.toml still reads 0.4.7, there is no docs/releases/v0.4.8.md, and doc_check fails on the missing version-table row"
priority: P1
effort: S
status: done
classes: defect, planning
feature: release-process
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases, docs/items/
added: 2026-09-07
closed: 2026-09-07
verify: grep -q '^version = "0.4.8"' pyproject.toml && test -f docs/releases/v0.4.8.md && grep -qF '## Current baseline: v0.4.8' ROADMAP.md && grep -qF '| v0.4.8 | Completed / current baseline |' ROADMAP.md
---

**Problem.** `git ls-remote --tags origin` holds `v0.4.8` at `3ddea5c`,
dereferencing to `b03a7d0` — the merge commit of `#432`, which closed
`PL-0GTC`, `PL-CL8J` and `PL-SR8F` and turned main's verify replay green. No
release was cut at that commit:

- `pyproject.toml` on `main` reads `version = "0.4.7"`;
- there is no `docs/releases/v0.4.8.md`;
- `ROADMAP.md`'s version table has no `v0.4.8` row, and its current baseline is
  still v0.4.7.

`tools/doc_check.py check` therefore fails on clean `main`, verified 2026-09-07
by stashing all local changes:

```
ROADMAP.md: git holds v0.4.8, but no row of the version table marks v0.4.8
completed; a release that shipped is one this table has to name
```

**Why it matters, and why it is P1 despite changing no displayed value.** Main
had been red for six merges on the `PL-0GTC`/`PL-SR8F` verify replay; `#432`
fixed exactly that and run 1548 went green at 17:11. This puts it straight back
to red on the next push, for a different reason, and the gate that is red for
two unrelated reasons in one afternoon is the gate a session learns to skim -
which is the failure mode `CLAUDE.md` names when it says a check that fires
without changing a decision is a defect in the check.

It also leaves the release train describing something untrue. A tag is what
`bin/docket release` reads to decide whether the previous release shipped, so
`v0.4.8` existing means the *next* cut will believe 0.4.8 already went out and
number itself accordingly, while nothing in the tree records what 0.4.8 was.

**This is a decision rather than a fix, and it is the project owner's**, because
both routes need a tag operation and a session cannot push tag refs here
(`PL-N936`).

1. **Delete the tag, then cut 0.4.8 properly.** `git push origin :refs/tags/v0.4.8`,
   then `make release VERSION=0.4.8` with its `ROADMAP.md` row and baseline, then
   re-tag at that merge commit. Leaves the train correct and the notes describing
   the nine-plus items that have accumulated since 0.4.7. Costs one destructive
   remote operation.
2. **Cut 0.4.8 and let the tag stand where it is.** Cheaper, and wrong in a way
   that is permanent: the tag would sit *behind* the commit that cut the release
   it names, so `git describe --contains` would place the release's own cut
   outside it and the notes would list work the tag does not span. `PL-028F` is
   already open on exactly this class of mismatch - work inside a tag's span but
   absent from its notes - so this route creates a second instance of a defect
   already filed.

Route 1 is recommended. Route 2 is recorded so the cheaper option is visibly
considered and rejected rather than silently skipped.

**How it probably happened, stated as a guess and not as a finding.** The
v0.4.7 cut (`PL-H1GH`) ended with three tag commands for the owner to run, and
v0.4.7 was tagged correctly at `888c1f4`. A second tag at the next number,
pushed onto the next merge, is the shape of those commands being re-run with the
version incremented. If that is right, the durable fix is that the tag step
should name the commit the release was cut at rather than `origin/main`, whose
meaning moves - worth considering when this is resolved, and filed here rather
than separately because it is the same event.

**Decision needed.** Which of the two routes above, and it is the project
owner's alone because both need a tag push that a session cannot make
(`PL-N936`). Route 1 - delete `v0.4.8`, cut the release properly, re-tag at the
cut's own merge commit - is recommended. Route 2 - cut 0.4.8 and leave the tag
where it is - is cheaper and leaves the tag permanently behind the commit that
cut the release it names.

**Done when.** `tools/doc_check.py check` passes on clean `main`: either
`v0.4.8` no longer exists and the next release is cut under its own number, or
a v0.4.8 release has been cut with its version-table row, its baseline section
and its `docs/releases/v0.4.8.md`, and the tag agrees with it.

**Found 2026-09-07** by `tools/doc_check.py` while closing `PL-JX0Z`, and
confirmed against clean `main` rather than against a working tree carrying local
edits.

## Resolved 2026-09-07: the decision was overtaken before it was answered

**The tag was withdrawn from `origin` between this item being written and being
worked, so there was no decision left to make.** Measured at the start of the
session that cut the release: `git ls-remote --tags origin` returns 68 refs and
none of them is `v0.4.8` - the newest is `v0.4.7` at `888c1f46`. The premise in
the Problem statement above, that `origin` holds `v0.4.8` at `3ddea5c`, was true
when it was written and is not now.

That makes Route 1 what actually happened, with its destructive step already
taken by the project owner rather than by this session, and Route 2 impossible:
there is no tag left to leave standing. What remained was the ordinary release
cut, which is what this item closes on.

`PL-B1DQ` - the fifth independent capture of the same tag condition, dropped as
a duplicate - is where the withdrawal is recorded, and `PL-LT77` (a tag deleted
on origin keeps failing doc_check in every checkout that already fetched it) is
the same condition diagnosed one layer down. This checkout was cloned after the
deletion and never held the tag, so `tools/doc_check.py check` reported `0
errors, 0 advisories` before any of this release's edits - the "Done when"
condition was already half satisfied by the withdrawal, and cutting 0.4.8 under
its own number satisfies the rest.

**The durable fix the Problem statement guessed at still stands, and is not
done here.** The tag step should name the commit the release was cut at rather
than `origin/main`, whose meaning moves. That is what produced a tag one commit
ahead of any release in the first place, and nothing in this release changes it.

**One consequence of re-using the number, measured rather than assumed.**
`v0.4.8` now names a *different* commit from the one the withdrawn tag named,
and a checkout that fetched the withdrawn tag before it was deleted - the
project owner's own machine being the one that is never re-cloned - will not
pick the new one up on an ordinary fetch. Reproduced 2026-09-07 in a scratch
pair of repositories, tagging `v0.4.8` at commit A, cloning, then deleting and
re-tagging at commit B on the origin:

| In the warm clone | Result |
| --- | --- |
| `git fetch --tags origin` | `! [rejected] v0.4.8 -> v0.4.8 (would clobber existing tag)`; tag still at A |
| `git fetch --tags --force origin` | `t [tag update] v0.4.8 -> v0.4.8`; tag at B, `refs/remotes/*` untouched |

So the refusal is **loud rather than silent**: git prints the rejection and
exits **1**. What it does not do is fix anything - the tag is still at A when
the command finishes, so a reader who takes the non-zero status for a network
hiccup and moves on keeps a `v0.4.8` pointing at a commit that never carried a
release. And the commands actually run day to day are quieter still: `git pull`
and `git fetch origin main` do not attempt the tag at all, so they leave it
stale and say nothing. That is why the handover for this release leads with the
forcing form rather than a bare fetch.

**`--prune-tags` is the wrong instrument here and the repository refuses it.**
`.claude/hooks/no-prune-guard.sh` rejects the call, correctly: this checkout is
one the digest currently reports two stranded items against (`PL-LT77`,
`PL-T7VS`), and a stale `origin/<branch>` ref can be the only surviving copy of
one. `--tags --force` is what updates a moved tag without touching a
remote-tracking branch ref, and the table above is the evidence that it does.
