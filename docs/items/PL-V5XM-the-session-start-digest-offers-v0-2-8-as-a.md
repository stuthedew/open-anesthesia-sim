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

**Worth deciding as part of it:** whether the right answer is to suppress the
offer while the suggested version's gate is open, or to keep offering and say
so in the line ("Offer 0.2.8 once its gate clears - 8 entries open"). The
second keeps the finished-work count visible, which is the thing the line
exists to surface.

**Done when.** The digest cannot instruct a session to offer a release whose
own gate is open, and a test covers the case with a gate recorded under the
suggested version.
