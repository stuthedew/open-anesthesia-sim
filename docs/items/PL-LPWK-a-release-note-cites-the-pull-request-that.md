---
id: PL-LPWK
title: A release note cites the pull request that closed an item, not the one that carried its code, whenever the two differ
status: untriaged
added: 2026-09-06
---

**Problem.** `release_notes()` in `subprojects/docket/src/docket/release.py`
renders each entry as `— #{item.pr}`, and `pr` is written by `bin/docket
record`, which recovers the number from the newest commit subject naming the
id. When an item closes in the same commit as its work - the normal case, and
what the close-out rule requires - those are the same pull request and the link
is right. When the closure lands separately, they are not, and the notes cite
the closure.

`PL-HB58` in `docs/releases/v0.4.6.md` is the live instance: it reads `— #412`,
which is a two-file change to a queue item, while the release's actual content -
the washout validation, a test module and a `docs/MODEL.md` section - arrived in
`#408`. A reader following the link from the release notes lands on a status
change and learns nothing about the release.

**Why it matters.** The release notes are the one document a reader outside the
queue consults to find out what a version contains, and the link is the only
route from a one-line summary to the change itself. A link that resolves to the
wrong thing is worse than none, because it does not read as broken.

The frequency is low and bounded by discipline rather than by the tool: it can
only happen when a closure is split from its work, which the close-out rule
already forbids. So this is the second-order cost of that rule being broken, and
it is worth weighing against how much machinery a fix would need.

**Where.** `subprojects/docket/src/docket/release.py` (`release_notes`), and
whatever records the work's own pull request if the answer is to keep both.

**Options, none of them obviously right.**

- Record the pull request that *carried the work* alongside the one that closed
  the item, and render the first. Correct, and it adds a field to every item to
  serve a case the close-out rule says should not arise.
- Leave the rendering and let the close-out rule carry it, recording here that
  the notes are only as good as that rule. Cheapest, and the answer if the
  instance above stays the only one.
- Have `docket record` prefer the oldest subject naming the id over the newest
  when a closure lands late. Changes a recovery rule that `PL-S5LB` and
  `PL-GW37` both tuned for other reasons, so it is the one to be most careful
  about.

**Done when.** Either the notes cite the pull request that carried the work, or
it is recorded in `subprojects/docket/README.md` that they cite the closure and
why that was accepted.
