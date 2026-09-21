# docket: ideas

Read this when the project owner is describing something they want, raising
an idea mid-task, or when the queue has thinned and a planned milestone is
worth scoping.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: turn an idea into work

Triggered by the owner describing something they want — a feature, a problem,
a direction. **They describe the outcome; decomposing it is yours.**

**Design first, items second. Do not create anything on first contact.** An
idea arrives half-formed by nature, and the first exchange is where it changes
shape most. Items written then get rewritten, re-scoped and deleted across the
next three replies, which fills the queue's history with churn and buries the
one version that mattered. Worse, "I created PL-B1C2, PL-C3D4" as a first
response reads as a decision already taken, when what the owner wanted was to
think it through.

So the first reply proposes. It creates nothing.

1. **Say what you understand the request to be**, in your own words. A misread
   surfaces here, cheaply, or it surfaces after the work is done.
2. **Ask what genuinely needs deciding** — the questions where different
   answers produce different software. Ask them together so they can be
   answered in one pass, and only the ones you cannot resolve from the code or
   from sensible defaults.
3. **Say how you would build it.** A few sentences of approach, and where it
   touches the existing design. This is the part the owner is here for.
4. **Propose the breakdown** — the items you would create, by title, with a
   size each, and which are decisions rather than code. Proposed, not created.

Then stop and let them react. Expect the shape to change; that is the point of
proposing it. Iterate in conversation, where revising costs a sentence.

**Create the items once the design has settled**, in one call, and say that is
what you did:

```bash
docket new --feature run-scrubbing \
  "Keep the full run in the controller's history buffer" \
  "Add a scrub control to the chart axis" \
  "Decide what the readouts show while scrubbed away from now"
```

Never hand the decomposition back. Working out what the idea breaks into,
naming the feature and writing the briefs is the job being delegated — asking
"which items should this be?" or "what should we call the feature?" returns it.
Propose an answer and invite correction; do not ask an open question.

**Where a thing lands depends on how ready it is, not on how big it is.**

| What the owner said | Where it goes |
| --- | --- |
| "Make this specific change" | A queue item, now. It is actionable already. |
| "I want this feature eventually" | One line of intent in `ROADMAP.md`'s "Planned milestones". No items. |
| "Let's build this" | The design round above, then items once settled. |

The middle row is the one that goes wrong. An aspirational feature filed as an
`L` queue item is work that cannot be worked: it sits at the bottom of the
queue being skipped by every session that reads past it, while looking like
something anyone could pick up. `ROADMAP.md` keeps such items deliberately
unspecified — no goal, no scope, no definition of done — until someone is
ready to scope one, which is exactly the right shape for intent.

## Mode: an idea arrives mid-task

Triggered by the owner raising a new feature while something else is underway.

Ideas arrive faster than they can be built, and the owner has asked to be kept
on task rather than followed down each one. Neither dropping the current work
nor quietly filing the idea is right — the first loses the thread, the second
loses the idea's placement to a decision they never got to make.

> "That fits — I'd put it in Phase 2, next to the settings panel, since it is
> the same consolidation problem. Parking it there unless you want it sooner;
> we are two items from finishing the halted-step decision."

Name where it would go and why, say what it would displace, and go back to
what you were doing. Place it on the roadmap once they agree.

**This is a nudge, not a gate.** If they want to switch, switch — it is their
project, and an idea that will not wait is sometimes the one to follow. The
obligation is to make the trade visible, not to win it.

## Mode: bring the roadmap back into the queue

Triggered by the queue thinning out, by a release shipping with little left
behind it, or by the owner asking what is next when nothing pressing is open.

**Offer this; do not wait for it.** Intent parked on the roadmap is only worth
parking if something brings it back. The digest's plan line says which beat is
due — it does not say that a planned milestone is worth scoping now, which is
the judgment this mode exists for.

> "v0.2.4 is out and what is left is four small items. The next planned
> milestone is the anesthesia-machine abstraction — the interlock baseline
> everything else on the list builds on. Want to scope it? That is a design
> round, and it would come out as items."

Then run the design round: goal, required scope, definition of done, and an
explicit out-of-scope list, written into `ROADMAP.md` per the development
rules there — *then* the items. A milestone is scoped before implementation
begins, not discovered during it.

**The exception is a session that is about to end with the thread open.** A
design still under discussion when the session stops is lost like anything
else, so capture what has been agreed as one untriaged item naming the open
questions, rather than letting a good conversation evaporate.
