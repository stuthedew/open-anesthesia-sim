---
id: PL-V5XM
title: The session-start digest offers v0.2.8 as a release while the line below it says v0.2.8's gate has 8 entries open
status: untriaged
added: 2026-08-31
---

**Problem.** The session-start digest offers v0.2.8 as a release while the line below it says v0.2.8's gate has 8 entries open

**Why it matters.**

**Where.**

**Done when.**

**Problem.** The session-start digest prints these two lines together, today:

    Releasable: 18 finished item(s) since 0.2.7, completing
    release-roadmap-seam. Offer 0.2.8 before taking new work.
    Plan: 0.2.7, step 1 of 10 (v0.2.8 - the workflow works). Beat: clear the
    gate - 8 entries of 18 still open.

The gate with 8 open entries is the one recorded under "Next release: v0.2.8",
so the first line instructs every session to offer the release of a milestone
the second line says is less than two-thirds cleared.

**Why it comes out that way.** `release.readiness()` computes
`suggested_version` from `suggest_version(current_version, shippable,
minor_classes)` - the classes of the finished items and nothing else. It has
no access to the gate, so it names the next version after 0.2.7 without
knowing that version is a gated milestone. `is_worth_cutting` gates whether
the line prints at all, on item counts and completed features, by the same
blind measure.

**Why it matters.** `CLAUDE.md` tells a session to offer the release without
waiting to be asked, and the digest is the channel that prompt arrives
through, so a session that follows both is led to propose cutting v0.2.8 with
its gate half open. This is not `PL-NSN9` (a milestone that gates itself
reports 'implement' when its gate clears): that one is `step` disagreeing with
`beat` inside `wave()`. This is the *release* line disagreeing with the gate,
computed in a different module that never sees one.

**Where.** `subprojects/docket/src/docket/release.py` (`readiness`,
`is_worth_cutting`) and `subprojects/docket/src/docket/render.py`
(`format_digest`, around line 154).

**Corrected 2026-08-31, the same day this was filed.** It was filed as though
the offer itself were the defect. It is not: `ROADMAP.md`'s "The cadence" says
outright that "`docket release` will offer one as soon as a few gate items are
finished - decline it, or the gate work scatters across patch releases and the
milestone ships carrying only its feature work." The offer is expected
behaviour with a documented answer.

What remains is a session-cost defect rather than a correctness one, and it is
still worth fixing. The digest is the one channel that reaches a session before
it reads anything, and on that channel the line says "Offer 0.2.8 before taking
new work" with no hint that the roadmap's standing answer is to decline. The
rule that resolves it lives 1,180 lines into `ROADMAP.md`, in a section a
session has no reason to open, so every session either offers a release the
project has already decided against or spends the reading to find out it
should not. `CLAUDE.md` tells sessions to make the offer unprompted, which
makes the wrong half the one that gets acted on.

**Worth deciding as part of it:** suppress the line while the suggested
version's gate is open, or keep it and carry the answer ("18 finished item(s)
since 0.2.7 - not releasable: v0.2.8's gate has 8 entries open"). The second is
better: the finished-work count is the thing the line exists to surface, and a
session that can see both facts can still raise it if the owner asks.

**Done when.** The digest cannot tell a session to offer a release the roadmap
says to decline, the finished-work count stays visible either way, and a test
covers a gate recorded under the suggested version.
