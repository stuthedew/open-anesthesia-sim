---
id: PL-Q8QX
title: `docket check` cannot recover a pull request number when the squash-merge subject differs from the pull request title
status: dropped
closed: 2026-09-02
reason: Duplicate of PL-2XTF, which covers the same #220 incident with a fuller brief. Restored as a record rather than as work, because its file was removed by a merge resolution rather than closed by a decision, and an item that simply vanishes teaches nothing - PL-P0QT is the check that now catches it.
added: 2026-09-02
---

**Problem.** `docket check` recovers a closed item's `pr` from the newest
commit subject *naming that id*. A GitHub squash merge takes its subject from
whatever the merger typed, which need not be the pull request title, so an id
that led every commit on the branch and led the pull request title can still
be absent from the one subject that lands on `main`.

**Why it matters.** Nothing is lost by dropping it: `PL-2XTF` was filed for the
same `#220` incident by a session that could not see this one, reached the same
conclusion, and carries the prevention half as well.

**Why the file is here at all.** This item is the instance `PL-P0QT` was filed
for. It was captured on the v0.3.0 release branch in `ce090b4`, was present in
`d7d5272`, and is absent from `24cbed1` — the merge that brought `main` into
that branch — and therefore from `main`. No commit in the branch's history
deletes it; the merge's own tree does, as part of a conflict resolution, which
is why `git log --diff-filter=D` over the path returns nothing.

That is the contrast worth keeping. `PL-9GCV` was dropped as a duplicate by a
decision in `#224`, with a `reason:` recorded and its file still in the store,
and it stays legible afterwards. This one was removed by a merge and left no
trace a reader would find. Restoring it as a `dropped` record makes the two
look the same from the store's side, which is what the capture rule promises.

**Done when.** Nothing further. `PL-2XTF` carries the work; `PL-P0QT` carries
the check that would have caught the loss.
