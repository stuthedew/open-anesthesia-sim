---
id: PL-LPWK
title: A release note cites the pull request that closed an item, not the one that carried its code, whenever the two differ
priority: P2
effort: S
status: ready
classes: defect, docs
feature: commit-provenance
touches: subprojects/docket/src/docket/release.py, subprojects/docket/README.md, subprojects/docket/tests/test_release.py
added: 2026-09-06
verify: grep -q 'names the pull request whose merge closed the item' subprojects/docket/README.md
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

**Decision needed.** Which of the three options above, and the item argues they
are not close: recording the work's own pull request alongside the closure adds
a field to every item to serve a case the close-out rule forbids; leaving the
rendering and recording in `subprojects/docket/README.md` that the notes are
only as good as that rule is the cheapest and is right if `PL-HB58` stays the
only instance; and changing `docket record` to prefer the oldest subject naming
an id touches a recovery rule `PL-S5LB` and `PL-GW37` each tuned for a
different reason, so it is the one to be most careful about.

**Recommendation (design round, 2026-09-25, with `PL-HMZZ`).** The second
option, with the field's meaning stated: `pr` names the pull request whose
merge closed the item. Under the same-commit closure rule that is the pull
request that carried the work, and `PL-HMZZ`'s recommendation makes it a fact
the closing branch writes and the pull request's own check enforces, rather
than a number inferred afterwards. A closure split from its work is then a
rule violation visible in that pull request's own diff, the notes cite the
closure honestly, and the item's body is where the work's pull request is
named in prose when that happens. Recording a second field for a case the
rule forbids (the first option) is refused; preferring the oldest subject (the
third) reads history the head retires. `PL-HB58` in `docs/releases/v0.4.6.md`
stays as it shipped: a released bullet is not rewritten.

Done, under this answer, when `subprojects/docket/README.md` states that
meaning beside the `pr` field; `release_notes()` is left as it is, and
`subprojects/docket/tests/test_release.py` needs no change.

Not recommended now: a check on the pull request that a closure's diff
intersects the item's `touches` - the `PL-GJPD` reading moved before the
merge. It would catch the split shape, but it rests on a declaration that
drifts, and the same-commit rule and review carry that shape today.

**Decided 2026-09-25: the second option, with the field's meaning stated**
(project owner, 2026-09-25, ratified, with `PL-HMZZ`, over recording a second
field and over preferring the oldest subject).
