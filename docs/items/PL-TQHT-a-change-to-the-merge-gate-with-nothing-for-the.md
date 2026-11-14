---
id: PL-TQHT
title: A change to the merge gate with nothing for the owner to weigh still waits on the owner, who calls that a rubber stamp: decide whether such a hold stays, and how it is asked (found on PR #2146)
priority: P2
effort: S
status: needs-decision
classes: ux
touches: subprojects/docket/src/docket/arming.py, docs/maintainer.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value
added: 2026-11-14
---

**Problem.** A change to the merge gate's code, or to the tests that fix what it prints, waits on the owner whatever else it does. That stops a session loosening the check that keeps unreviewed work off `main` (`PL-9JHM`, `PL-WW0Q`). Some such changes have nothing for the owner to weigh. `PL-GG4V`'s pull request, #2146, is one: it builds the question form the owner asked for on 2026-11-14, and it waits only because it edits the gate. The question form now requires two options with a real gain each, so a session asking about such a change has to invent one.

**Why it matters.** Every question the owner is sent costs their attention, and a question with nothing to decide teaches them to skim the ones that matter. The hold it would relax guards every other merge.

**Decision needed.** Whether a change to the merge gate with nothing to weigh keeps waiting on the owner, and if so how it is asked.

**What the owner said** (2026-11-14), on being asked "May it merge?" with merging and holding for changes as the options: "I don't find "approval" questions useful. because it seems like you are asking me for a rubber stamp. So either you shouldn't be asking me in the first place because it's not a real question, or you need to tell me what I need to make an informed decision."

**Options.**

1. *Keep the hold, and ask it as the gate as changed against the gate as it was.* The question says what the gate will accept or refuse after the change that it did not before. Gain: no session can loosen the merge gate without the owner seeing what it now lets through. Cost: where the change loosens nothing, the owner is told so and asked to release it, which is close to the sign-off they called a rubber stamp.
2. *Let the session release the hold* when it records why the change cannot loosen the gate. Gain: the owner sees only real choices. Cost: whether a change loosens the gate becomes the judgment of the session whose work the gate checks, and a wrong judgment reaches `main` with only the history to show it.
3. *Send a notice instead of a question*, and merge after a set wait unless the owner objects. Gain: the owner keeps a veto without being asked to decide. Cost: an unread notice merges the change unreviewed, which is what the hold exists to prevent, and the wait is new machinery.

**Recommendation (session's, 2026-11-14): option 1.** The gate keeps every other unreviewed change off `main`, so the one judgment it should not hand to a session is whether a change to the gate itself is safe. What the owner needs in order to decide is what the gate lets through after the change, and option 1 makes the question carry exactly that.

**How often it happens is not known.** A squash merge keeps the pull request body and drops the commit trailers that record the owner's go-ahead, so `main`'s history does not show how many merges waited on the owner for this reason.

**Done when.** The owner's answer is recorded here, and `bin/docket arm`'s instructions and `docs/maintainer.md` say what a session does with such a change.
