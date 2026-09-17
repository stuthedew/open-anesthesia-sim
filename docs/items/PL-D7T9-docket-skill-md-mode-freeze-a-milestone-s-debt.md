---
id: PL-D7T9
title: docket SKILL.md § 'Mode: freeze a milestone's debt gate' says 'v0.4.26 and v0.6.0 are both in that state' of the freeze-on-ship exception, but v0.4.26 shipped 2026-09-17 and ROADMAP's own cadence says it took no gate by a different exception, so a session reading it is told to wait for a freeze that is neither pending nor v0.4.26's
status: untriaged
added: 2026-09-17
---

**Problem.** docket SKILL.md § 'Mode: freeze a milestone's debt gate' says 'v0.4.26 and v0.6.0 are both in that state' of the freeze-on-ship exception, but v0.4.26 shipped 2026-09-17 and ROADMAP's own cadence says it took no gate by a different exception, so a session reading it is told to wait for a freeze that is neither pending nor v0.4.26's

**Found 2026-09-17** in `PL-TM9J`'s close-out docs sweep, cutting v0.4.27.

**The sentence.** `.claude/skills/docket/SKILL.md:1039`, closing the paragraph
that states the freeze-on-ship exception: "v0.4.26 and v0.6.0 are both in that
state."

**Two things are wrong with it, and they are independent.**

1. **It is stale.** v0.4.26 shipped on 2026-09-17 (`PL-06YW`), so whatever
   freeze it was waiting for is not pending. A session reading this in a
   gate-freezing pass is told to look for a milestone whose predecessor has not
   shipped, and one of the two named has.
2. **It may never have been right.** `ROADMAP.md` § "The debt gate" → "The
   cadence" says, in the paragraph immediately under the exception: "v0.4.26
   took no gate **by its own exception** and v0.6.0 takes this one." Those are
   two different exceptions, and the skill folds them into one state. If the
   roadmap is right, only v0.6.0 was ever in the freeze-on-ship state.

**Why it matters.** This is the skill's own statement of *which milestones a
session should be looking at*, in the one mode where getting it wrong freezes a
gate at the wrong moment or fails to freeze one at all - and a gate frozen early
holds none of the findings it exists to hold, which is the failure the exception
was written to prevent. It is also the kind of sentence nothing can check:
`doc_check` validates that a cited section exists, never that a claim about
which milestone is in which state is still true.

**Sequence it with `PL-KKRP`**, which asks whether the exception's trigger
should be reworded at all - the paragraph ends by saying not to reword it here.
Fixing the example is not rewording the trigger, so this can land first, but
whoever takes `PL-KKRP` will be in the same paragraph.

**Done when.** The sentence names only milestones actually in the
freeze-on-ship state, and says which exception v0.4.26 took if it names it at
all; the skill and `ROADMAP.md` § "The cadence" agree.
