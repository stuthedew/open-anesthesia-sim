---
id: PL-D2GW
title: The session digest offers a release whose version names a milestone whose gate is still open
priority: P2
effort: S
status: ready
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_release.py -k gate
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

**Triaged 2026-08-31. It is live in every session right now, and it is the
most consequential of the nine captures triaged that day.** This session's own
digest read `Releasable: 30 finished item(s) since 0.2.7 ... Offer 0.2.8
before taking new work` above `Beat  clear the gate - 2 entries of 22 still
open`. Cutting the release that line offers would ship v0.2.8 without `PL-NSN9`
(a self-gating milestone reports the wrong beat when its gate clears) and
`PL-1CYR` (nothing re-checks the branch against `main` mid-session), under a
title that says the workflow works.

P2, `defect`/`infra`, `release-roadmap-seam` beside `PL-8HJ2` (`make release`
stops mid-way on the ROADMAP table it does not write): both are the release
path acting on a document it has not read.

**The window is narrow now and reopens permanently.** Two entries from the
gate closing, the wrong advice becomes right, so the exposure on *this*
release is small. It is not a one-off: every release from here that records a
gate - v0.3.0 shipping Gate 0, v0.5.0 shipping Gate 1, v0.6.0 shipping Gate 2 -
reproduces the same collision between the mechanical patch guess and a version
`ROADMAP.md` has already scoped and named. Fix it before v0.3.0 is cut rather
than before v0.2.8 is.

Not admitted to v0.2.8's frozen list, and the near miss is worth recording.
`PL-NSN9` is the adjacent entry and this looks like its other half - both are
the digest misdirecting a session about a self-gating milestone. They are not
the same mechanism: `PL-NSN9` is `wave()`'s `shipping_the_gate` comparison and
fires when the gate is *clear*, this is `readiness` never consulting the
roadmap at all and fires while the gate is *open*. `PL-NSN9` can close
correctly and completely with this bug untouched, so admitting it would be
adding scope under a rule written for completions. `ROADMAP.md`'s "What the
freeze closes, and what it does not" sends it to the queue instead. The
countervailing case - that a release named "the workflow works" should not
ship with its own digest recommending a wrong release - is real, and is the
owner's to weigh rather than a session's.

**Admitted to v0.2.8's frozen list, 2026-08-31, reversing the paragraph
above,** under the scope test now recorded in `ROADMAP.md`'s "What the freeze
closes". The paragraph above is right that this is not `PL-NSN9`'s other half
and right that the exposure on *this* release is small; both are answers to
the completion question, which is no longer the test. The digest and the
release script are two of the six pieces of machinery the release's goal
names, and the deferral it proposed — fix it before v0.3.0 is cut rather than
before v0.2.8 — put the fix outside the release whose title claims the
workflow works, on the strength of a window it also says "reopens
permanently".
