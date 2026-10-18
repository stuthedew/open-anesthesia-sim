---
id: PL-0GWD
title: CLAUDE.md's product-focus paragraph says root causes are worked by the PL-NZC0 Projects trial's coordinator, and instruction-writing.md rule 14 says to start nothing its Order list reserves while it runs, but the owner archived and paused that project on 2026-10-01, so who works a root cause now is unstated
priority: P2
effort: S
status: done
classes: docs
touches: CLAUDE.md, .claude/rules/instruction-writing.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-18
pr: 1539
payoff: a head found in a product session has a named worker whether or not the Projects trial is running, so no session hands it to nobody
verify: grep -qF 'while the trial is paused' CLAUDE.md
---

**Problem.** CLAUDE.md's product-focus paragraph says root causes are worked by the PL-NZC0 Projects trial's coordinator, and instruction-writing.md rule 14 says to start nothing its Order list reserves while it runs, but the owner archived and paused that project on 2026-10-01, so who works a root cause now is unstated

**Why it matters.** `CLAUDE.md` is resident in every session, and its product-focus paragraph sends root causes to a coordinator that is not running, so a generator found in a product session has no worker named and the session either hands it to nobody or improvises. The pause is not in the tree: it is taken from the capture, and `PL-Y7WF` is the only item describing pausing the project.

**Done when.** `CLAUDE.md`'s product-focus paragraph says who works a root cause while the trial is paused, per the answer below, and rule 14's Order-list sentence agrees with it.

**Decision needed.** Who works a root cause while the `PL-NZC0` trial is paused: (a) the second ending `CLAUDE.md` already gives heads found in product work - the reply ends with a ready-to-paste prompt and the owner starts that session when they choose; (b) `PL-2866`'s recorded fallback, the alternation built into `bin/docket next`; or (c) the product session works it after its product item. **Recommended: (a)**, written as a condition on the coordinator sentence (while the trial runs, the coordinator; while it is paused, the prompt). It needs no new mechanism, it is what the generator rule already prescribes, and resuming the trial undoes it by deleting a clause; (b) is the owner's answer for a trial that fails, and a pause is not that.

**Generator check.** The fact is whether the `PL-NZC0` trial is running, which lives in the owner's Projects settings and nowhere in the tree, and one resident sentence restates it unconditionally. One-off: no other item misread it, and `PL-4FBP`'s and `PL-G424`'s fact is a sentence restating a *tree* fact, which this is not.

**Decided** (2026-10-12, in the first batched design round, a session's call
under rule 14 of `.claude/rules/instruction-writing.md`): (a). Of the three
options, two are already refused by a recorded decision: (b) is `PL-2866`'s
fallback for a trial that fails its own bar, and a pause is not that; (c) is
what `PL-2866` was ratified over ("working each root cause in the owner's own
session right after the product item"). (a) is what `PL-2866` part 3 already
prescribes for a product session - it ends with the ready-to-paste prompt, and
during the trial the head waits for the coordinator's list - so the edit adds
the condition that paragraph lacks and chooses nothing new. Reopening it is on
ordinary evidence, since it rests on a ratified decision.

The trial was running again by 2026-10-03 (the v0.6.0 Project's Order records
picks from that date), so the sentence is true today and the clause is for the
next pause. The build is one clause in `CLAUDE.md`'s product-focus paragraph,
which is resident, so the commit names what it replaces or says why nothing
can be cut (`CLAUDE.md` § "The queue, and how the project owner works"). It
repairs a resident sentence that is wrong while the trial is paused - a defect
in what exists rather than a new mechanism - so the pause on new workflow
mechanisms does not hold it.

**Built 2026-10-18.** `CLAUDE.md`'s product-focus paragraph now names the
coordinator only while the trial runs, and says a product session that finds a
root cause while the trial is paused ends its reply with a ready-to-paste
prompt. Nothing resident was cut to pay for the 198 characters: the clause
corrects a sentence that was wrong whenever the trial is paused, and no other
sentence states that case. Rule 14's Order-list sentence in
`.claude/rules/instruction-writing.md` already reads "while `PL-NZC0`'s
Projects trial runs", so it agrees and was left as it is.
