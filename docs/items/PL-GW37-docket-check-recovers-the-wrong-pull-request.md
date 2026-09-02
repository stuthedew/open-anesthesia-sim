---
id: PL-GW37
title: docket check recovers the wrong pull request for an item closed as a rider on another item's PR, and advises writing that number in
status: untriaged
added: 2026-09-02
---

**Problem.** `docket check` recovers a closed item's pull request number by
taking the newest commit on the default branch whose subject names the item's
id (`subprojects/docket/README.md`, "the newest such commit wins"). For an
item closed on its own pull request that is right. For an item closed as a
*rider* on another item's pull request it is wrong, because the closing
commit's subject leads with the other item's id and so does not name this
one — leaving the item's own triage or capture commit as the newest match.

Observed 2026-09-02. `PL-YLZQ` was closed in `#204` alongside `PL-026`, whose
id leads that commit's subject. `docket check` advised:

    PL-YLZQ: marked done on `origin/main` and records no `pr`, but #159 is
    recoverable from its merge commit; write `pr: 159` into the item so the
    file carries it too

`#159` is `fce85ff`, the commit that *triaged* `PL-YLZQ` into the queue. The
correct number is `204`.

**Why it matters.** The advisory does not merely fail to find a number, which
would be harmless — it names a specific wrong one and instructs a session to
write it into the item. `subprojects/docket/README.md` says a closed item's
whole traceability is the pointer from it to the work, so obeying the
advisory replaces "no provenance" with *false* provenance, which is worse:
a reader following `pr: 159` lands on a triage commit that contains none of
the work, and has no cue that they are in the wrong place. A session has no
reason to doubt the advisory, because the number it prints is real and
resolvable.

The blind spot is the same shape. `PL-KQKM` was closed in `#204` too and got
no advisory at all, because no commit subject names it. That half is safe —
silence, not a wrong answer.

Rider closures are not an edge case here: `CLAUDE.md`'s capture rule and the
`docket` skill both direct that a finding an in-progress item needs in order
to be properly finished is worked with it, on one branch, closed together.
That is exactly the shape that produces them.

**Where.** The recovery lives in `subprojects/docket/src/docket/`; the rule is
documented in `subprojects/docket/README.md` under the `pr` field. The three
items it fired on are `PL-026`, `PL-YLZQ` and `PL-KQKM`, all closed in `#204`
and all now carrying `pr: 204`, verified against `git log origin/main` rather
than taken from the advisory.

**Approach (one option, not a decision).** The check already knows the item
is `done` on the default branch. Rather than trusting the newest id-matching
commit, it could require that the matching commit also *closes* the item —
that the commit's diff sets the item's `status: done` — and stay silent when
no commit satisfies that, the way it already does for `PL-KQKM`. Silence is
the safe failure here; a confident wrong number is not. Whether that is
affordable against the shallow-clone constraints the surrounding code is
built around is the design question this needs.

**Done when.** `docket check` either recovers a rider-closed item's real
pull request number or says nothing, and never advises writing in the number
of a commit that does not contain the item's work. A regression test covers
the rider shape: an item marked done in a commit whose subject leads with a
different item's id, with an older commit naming this one.
