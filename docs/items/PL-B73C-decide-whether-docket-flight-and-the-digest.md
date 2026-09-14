---
id: PL-B73C
title: Decide whether docket flight and the digest should name unlanded refs carrying no item id at all
priority: P3
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-04
closed: 2026-09-14
verify: grep -q 'def test_a_ref_naming_no_item_anywhere_is_reported_as_unattributed' subprojects/docket/tests/test_vcs.py && uv run pytest subprojects/docket/tests/test_vcs.py -q -k attribut
---

**Problem.** `branches_in_flight` walks every unlanded ref, looks for an id in
the branch name and at the front of each commit subject, and silently drops the
ref when it finds neither. `FlightReport` has `branches` and `unreadable`; there
is no third field for *read successfully, and attributable to nothing*. So the
report is complete about what it could read and silent about work it read
perfectly well and could not name — which is the literal reading of `PL-CP74`'s
title, and the half that item deliberately did not build.

**Why it matters.** `PL-CP74` closed the writing side: `tools/branch_id_check.py`
refuses a branch of one's own that carries no id, and `CLAUDE.md` plus the
`docket` skill say to file housekeeping before doing it. Both act on the session
creating the branch. Neither helps a session looking at a branch somebody else
left, which is what `flight` is for.

**Why it was declined rather than built.** The digest is resent on every turn of
every session, and `CLAUDE.md`'s own test is that a check firing every run
without changing a decision is a defect in the check. Today the repository has
exactly one such ref — `origin/Review_articles`, `PL-JX2T` — and naming it would
put a line nobody acts on into every session for as long as the branch exists.
That is the advisory-nobody-reads failure arriving by construction rather than by
drift.

So the design question is not whether the information exists but what suppresses
it: age, like the abandoned-branch qualifier `flight` already carries; a
push-date floor; naming it in `flight` (asked deliberately) but never in the
digest (resent unasked); or an allow-list of refs a person has already decided
about, which is `PL-JX2T`'s output. The last is the most promising and the most
machinery.

**Where.** `subprojects/docket/src/docket/vcs.py` (`FlightReport`,
`branches_in_flight`), and whatever renders `flight` and `digest`.

**Done when.** Either the report names unattributed unlanded refs with a
suppression rule that keeps the digest quiet in the steady state, or this item
records the decision not to and why, so it is not rediscovered.

**Decision needed.** Whether `flight` and the digest should name an unlanded ref
attributable to no item at all, and if so what keeps the steady state quiet:
age, as the abandoned-branch qualifier already does; a push-date floor; naming
it in `flight`, which is asked for deliberately, but never in the digest, which
is resent unasked; or an allow-list of refs somebody has already decided about,
which is the most promising and the most machinery. Answering "no" is a
legitimate outcome and closes the item, provided the reason is recorded here so
it is not rediscovered.

## Worked 2026-09-14: yes, name them - in both places, with no suppression rule, because the premise of the decline expired

**Decided and built: `flight` and the digest name an unlanded ref attributable
to no item, and none of the four suppression designs was needed.** The decline
of 2026-09-04 was right on the evidence it had and is wrong on today's, which
is the cleanest reason to revisit a decision.

**What changed is a count, not an argument.** The decline rested on one
sentence: "Today the repository has exactly one such ref - `origin/Review_articles`
- and naming it would put a line nobody acts on into every session for as long
as the branch exists." Re-measured today against `git ls-remote --heads origin`:

| | 2026-09-04 | 2026-09-14 |
| --- | --- | --- |
| unlanded heads on the remote | — | 10 |
| ...carrying no id in the name | — | 10 |
| ...carrying no leading id in any subject | 1 | **0** |

`PL-JX2T` closed `origin/Review_articles` in `v0.3.7` and the branch is gone.
Every one of the ten live heads leads a commit subject with a `PL-` id,
including the nine whose whole diff is inside `docs/items/`. So the steady
state is silence, and there is nothing for an age qualifier, a push-date floor,
a flight-only rule or an allow-list to suppress. The most promising of the four
was also the most machinery, and it would have been machinery for an empty set.

**What holds the steady state empty is a check rather than luck.** `PL-CP74`
built `tools/branch_id_check.py`, which fails `make check` and CI on a branch
ahead of `main` that carries no id in its name and leads no commit subject with
one. It binds the `claude/*` namespace (`PL-8P6D`), which is where sessions
work. So the write side is guarded and this is the read side of the same rule:
what escaped the guard, for refs pushed from outside it or from before it.

**The reading, and the one line it turns on.** A ref is unattributed when the
walk read its commits and found no leading id in any of them, and its name
carries none either. The discriminator is that **bookkeeping is attributable**:
a capture, a triage pass and a `docket record` write all lead with the id of
the item they concern, so `_annotates_only` withholds their *claim* while the
ref stays nameable. Without that distinction the line would fire on the most
routine push this project makes - nine of today's eleven unlanded refs are
queue-only - which is the "advisory nobody reads" outcome arriving by
construction. `_Walk.named` is the new reading, credited before the annotation
test rather than after it.

**Two ways it refuses to overclaim.** An *unread* ref is never called
unattributed: a walk that stopped at a truncated history contributes no
subjects, so the absence of an id was never established, and asserting it would
be the same overclaim `unreadable` exists to prevent. And a local branch and
its tracking ref collapse through `_preferred` before they are compared -
`--source` credits a commit to whichever ref git reached first, and without the
collapse the session running this check reported **its own branch** as nameless.
That was a live bug caught on the first run against the real tree, not a
hypothetical.

**Where it prints.** `bin/docket flight` gains a section; `format_digest` gains
one line - "Unlanded and attributable to no item: ... Nothing names it, so no
guard here can see it - file an item or delete the branch." The digest was the
half the decline worried about most, and it is included deliberately: every
session reads the digest and few run `flight`, which is the same argument that
already puts the unread line there. Should a line ever start appearing that
nobody acts on, `CLAUDE.md`'s retirement test governs this like any other
check, and the item recording that is this one.

**Eight tests**, each a defect the absence would let through: the nameless ref
is reported; a queue-only push naming its item is not; a ref named for its item
is not; an unread ref is not; a branch and its tracking ref are one line; the
`flight` section prints; the digest line prints; the digest stays silent when
every ref names something.
