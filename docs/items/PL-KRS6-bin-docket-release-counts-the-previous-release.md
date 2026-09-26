---
id: PL-KRS6
title: bin/docket release counts the previous release's own cut item as releasable work, so every session after a release is offered an empty one
priority: P2
effort: S
status: ready
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, .claude/skills/docket/modes/release.md
added: 2026-09-07
verify: grep -q 'def test_a_release_cut_item_belongs_to_the_version_it_cut' subprojects/docket/tests/test_release.py && uv run pytest -q subprojects/docket/tests/test_release.py
---

**Problem.** `bin/docket release --dry-run`, run 2026-09-07 immediately after
v0.4.7 merged, printed:

    1 finished item(s) since 0.4.7:
      PL-H1GH "Cut the v0.4.7 release: the supported run length, the tolerance
               gate, and traces you can tell apart"
    Completes: release-process

`PL-H1GH` *is* the item that cut v0.4.7. It closes in the release commit, so it
is stamped with no `milestone:` of its own and reads as finished work belonging
to the *next* release. The offer is therefore for a release whose whole content
is the previous release's cut, and the session-start digest repeats it —
`Releasable: 1 finished item(s) since 0.4.7, completing release-process. Offer
0.4.8 before taking new work.`

**Why it matters.** It fires in every session from the moment a release merges
until the next real item closes, and the instruction attached to it ("before
taking new work") is the strongest form the digest has. A session that follows
it cuts an empty 0.4.8; a session that does not learns that the line can be
wrong, which is the cost `CLAUDE.md` names for an advisory nobody acts on. It is
the same family as `PL-D2GW` (done) — the digest offering a release that should
not be cut — but a different cause: `PL-D2GW` was the version naming a
milestone whose gate was open, this is the releasable *set* being non-empty when
it should be empty.

**Where.** `subprojects/docket/src/docket/release.py` computes the finished-set;
`render.py` and the digest print it. The decidable rule is small and exact: an
item whose closing commit is the release cut for version *V* belongs to *V*, not
to the release after it. `docs/items/PL-*-cut-the-v*.md` is a closed set of
eight such items, all sharing the `release-process` feature and a
`Cut the v… release` title, so there is more than one way to identify them —
prefer the structural one (closed by the commit that wrote the version) over
matching the title.

**Done when.** With `main` at a freshly merged release and nothing else closed
since, `bin/docket release --dry-run` reports no releasable work and the digest
prints no `Releasable:` line; and `.claude/skills/docket/modes/release.md` no
longer says the next release ships the cut's own item. (Rewritten 2026-09-26 with
the decision below: the line this named, `No release to offer`, is the
reserved-version sentence and does not print in this state.)

**Blocked.** 2026-09-25, on the slam-dunk run's `claude/pl-batch-01-s8d258`.
Still real on `origin/main` at `7018ef1d`: `bin/docket release --dry-run
--no-fetch` lists `PL-DRRG` ("Cut v0.5.11 from the 16 items finished since
v0.5.10") among the 14 finished items since 0.5.11, and of the 46 items titled
as a cut, none carries the version it cut: 44 are stamped with the next one,
`PL-DRRG` is unstamped and `PL-Z0C7` was dropped. It cannot be done as written,
for three reasons:

1. The structural rule the brief prefers, closed by the commit that wrote the
   version, is a history read, and `release.py` reads no git; the declared
   `touches` (`release.py`, `test_release.py`) do not reach `cli.py`, where the
   git reads are.
2. `.claude/skills/docket/modes/release.md` says of the release item, at line
   100, "It carries no `milestone:`, so the next release ships it, like
   anything else finished after a cut", which is the convention this item
   reverses, in a file outside `touches`.
3. The second half of **Done when** names a line that does not print in this
   state: with nothing releasable the digest prints no `Releasable:` line at
   all, and `No release to offer` is only the reserved-version sentence
   (`render._reserved_refusal`).

**Decision needed: which rule marks the cut's own item, and where it belongs.**

- **A. The release-train claim.** Since `PL-331V` a cut refuses a branch
  holding no train claim (`cli._no_train_refusal`), so every cut is made under
  exactly one item carrying `resource: release-train`, and that item closes in
  the cut's own pull request after the notes are written. `unreleased()` leaves
  out a `done` item carrying the resource. Structural, on a field the cut
  already requires; the item then carries no `milestone:`, so no release's
  notes name it (today the next release's do, and never its own, since it
  closes after they are written). Only `PL-DRRG` carries the field, so nothing
  historical moves. Widens `touches` by `release.md`, and **Done when** becomes
  "reports no releasable work, and the digest prints no `Releasable:` line".
- **B. Stamp it at the cut.** `cmd_release` stamps the branch's own train item
  with the version it cuts, so it belongs to that version literally. It is
  still open then, so the notes do not name it, and
  `checks._check_release_notes`, which holds each release's notes to the items
  stamped with it, would report it; needs `cli.py`, `checks.py` and
  `release.md`.
- **C. Match the title** (`Cut vX.Y.Z ...`). The brief already prefers against
  it: a title is prose.

**Recommendation: A**, the smallest change that makes the rule structural, on a
field the cut already requires, with one sentence of `release.md` to change.

**Decided: A** (project owner, 2026-09-26, ratified, over B, stamping the item
with the version it cuts, and C, matching its `Cut vX.Y.Z` title). `unreleased()`
leaves out a `done` item carrying `resource: release-train`, so a cut's own item
belongs to no release's count and appears in no release's notes. `touches` and
**Done when** above are widened and rewritten to match. The brief is no longer
blocked; the work is `S` and ready for a session to claim.
