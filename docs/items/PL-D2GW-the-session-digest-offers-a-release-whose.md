---
id: PL-D2GW
title: The session digest offers a release whose version names a milestone whose gate is still open
status: untriaged
added: 2026-08-31
---

**Problem.** The digest ends every session with

    Releasable: 16 finished item(s) since 0.2.7, completing
    release-roadmap-seam. Offer 0.2.8 before taking new work.

while `bin/docket wave`, two lines below it, reads

    Step  step 1 of 10: v0.2.8 — the workflow works
    Beat  clear the gate - 9 entries of 18 still open

Both are correct about what they read, and they contradict each other about
what to do. `readiness` counts finished items that carry no `milestone` and
suggests the next patch number; it does not know that `ROADMAP.md` has already
named v0.2.8 and defined it as eighteen specific entries. Cutting the release
the digest offers would produce a v0.2.8 that ships nine of them and is titled
"the workflow works" while half the machinery it names is still broken.

**Why it matters.** The digest is the one thing every session reads before it
does anything else, and this line tells it to convert a "what next" question
into a release. A session that follows it ships a milestone half done under
that milestone's own name — a provenance error of the same kind the release
path already guards elsewhere, and one that cannot be undone once tagged.
Where the two lines disagree, the skill tells a session to follow the beat;
that instruction is doing the work a signal should do for itself.

The mechanical version guess colliding with a planned milestone's name is what
makes it dangerous rather than merely noisy. Had the roadmap named the
milestone v0.3.0, the guess of 0.2.8 would have read as obviously unrelated.

**Where.** `readiness` in `subprojects/docket/src/docket/release.py` computes
it; `render.format_digest` prints it. `roadmap.wave` already knows the step
and the gate split, so the fact needed is available and simply not consulted.

**Done when.** The release line does not recommend cutting a version the
roadmap has scoped and whose frozen list is still open — either by withholding
the offer with the reason, or by saying what it would ship against what that
version is defined to contain. The two lines of the digest must not be able to
recommend opposite actions.
