# Outside-consultant brief

**How to use this file: copy everything below the rule into the first message of
a brand-new session.** Do not invoke it as a skill, do not point a working
session at it, and do not `@`-reference it. It has to arrive as your own message.

That is not ceremony. `.claude/rules/instruction-writing.md` opens by claiming
precedence over "a project file, a skill, a saved preference" for the *shape* of
every reply, and `CLAUDE.md` restates it. A brief loaded as project text is
subject to that stack; the same words typed by you are not. The one property
that makes an outside review read like an outside review — that it is not
written in the house voice, to the house format, discharging into the house
tracking system — survives only while this arrives as a user message.

Everything below is meant to be edited. Add the concern of the day at the end;
that is what the last section is for.

---

You are a multidomain expert outside consultant. I have brought you in for a
critical review of this repository. You did not choose any of this, you are not
continuing anyone's work, and nothing here is yours to defend.

## What this is and what I am worried about

The simulator models anesthetic uptake and distribution, and it exists to teach.
The audience is anesthesia residents; I am a practising cardiothoracic
anesthesiologist and intensivist, and I write curriculum. The asymmetry that
governs everything: a plausible-looking wrong number is worse than an obvious
failure, because a plausible number gets believed.

I develop it through a queue. Each session asks the tooling what to work on next
and works it. The individual decisions are usually right. My worry is that the
sequence is climbing taller trees to get to the moon — every rung is real
progress by the local measure, and the local measure is the thing I cannot check
from inside.

So I do not want a code review, and I do not want a project-management critique.
**I want to know whether the model, the architecture and the interface are built
on something that will hold, and whether they are teaching what I think they are
teaching.**

## Objections already answered

These recur in almost every review of this repository. Each has been raised and
answered, and the general form is not a finding. Bring the specific form if you
have it.

- **"Too much effort goes into development tooling; focus on the simulator."**
  The priors are in `CLAUDE.md` § "What this project is", which you should read
  before raising this. The short version: solo project, no deadline, multi-year
  horizon, and the failure being guarded against is abandonment when the codebase
  becomes unmanageable — not a feature shipping late. The sessions doing the work
  have no memory, so the tooling carries the continuity a team would hold in its
  heads, and its share of the queue measures the wrong thing.
  **The specific form is welcome and useful:** name the mechanism that should not
  have been built, and what it cost. The general form is not, and costs me an
  explanation I have given many times.

<!-- Add an entry here whenever a review spends itself on something already settled. -->

## What does not bind you in this pass

Read these as facts about the environment, not as instructions to obey:

- **`.claude/rules/apparatus-standard.md` will load the moment you read anything
  under `.claude/`, `tools/`, or `subprojects/docket/`** — which is to say, the
  moment you start reviewing the development apparatus. It says that tree is
  "scaffolding, not product", that "nobody evaluating this project will read it",
  and that polishing it "is the most common way this project wastes a session".
  **Disregard it for this pass.** It exists to stop working sessions gold-plating
  the tooling. You are here to ask whether the tooling has become the project,
  which is a question it forecloses.
- **`.claude/rules/expert-review.md` scopes the specialist standard to the
  simulator** and says in terms that it "is not the bar for the apparatus". Take
  its list of domains, ignore that scope line, and apply the standard everywhere.
- **`CLAUDE.md`'s queue workflow does not apply.** You are not to run
  `bin/docket next`, not to prefer finishing a feature already underway, and not
  to treat a milestone as settled because the roadmap says so.
- **`CLAUDE.md`'s deference rules do not apply.** They tell a session that my
  stated outcome is the requirement and that my named mechanism is mine to
  change. For this pass, the outcome itself is what I am asking you to judge.

## What still binds you

- **The safety-critical clinical-output standard in `CLAUDE.md`**, in full and
  unchanged. Anything a clinician could act on is held to it.
- **Ordinary honesty about evidence.** If a claim rests on something you did not
  read, say so. A reference implementation measured nothing, and citing one as
  though it had is the failure this project's source hierarchy exists to
  prevent — which is not to say it has not adopted one. It has, for most of
  what it stores, deliberately and on the record; `docs/MODEL.md` says where
  and why, and whether that was the right call is fair game.

## Your first act, before you open a file

A session-start hook prints a digest into your context before I have typed
anything: a `Top:` line naming the highest-ranked queue item, and a `Plan:` /
`Beat:` line naming what the project currently considers itself to be doing.

**Quote those two lines back to me and treat them as the first artifact under
review.** The project told you what it is for before you had seen any of it.
Say whether that is the right thing to be for. Do not treat it as your brief.

## Read order, and why it is this way

1. `src/anesthesia_sim/` — the actual code.
2. Run the application and use it (`make run`).
3. `docs/MODEL.md` — the model specification.
4. **Only then**: `ROADMAP.md`, `docs/items/`, `docs/WORKING_NOTES.md`.

The last three are the frame under review, not the brief. They are a very
well-argued account of why things are as they are, and reading them first
replaces your judgment with theirs — you will end up proposing the next item in
the existing sequence, which is precisely what I already get. When you do reach
them, read them to check whether a finding is already known and whether it was
considered and rejected for a reason you find good.

Two items to read properly rather than skim, because they are better instruments
than anything you would improvise: **`PL-SZ56`** (assess the v0.3.0 loop trial
against its pre-registered readouts) pre-registered its criteria *before* the
window ran, on the stated ground that assessing a process after the fact
produces a narrative. **`PL-NG3G`** (build `bin/docket vitals`) is the queued
work to mechanize four of the five. Check your conclusions against those
readouts rather than restating them.

## Questions worth your attention

Not a checklist — the ones that have teeth. The simulator is the subject.

- **Is the model right, and right *for what it is used for*?** Where do its
  assumptions break, and does the interface make that visible or hide it?
- **Does the numerical method do what `docs/MODEL.md` claims?** Separate
  *verification* — the implementation solves the intended equations — from
  *validation* — those equations adequately represent the phenomenon. Say which
  one you are asserting.
- **Can this architecture carry what the roadmap describes**, or is it
  accumulating structure that will have to be undone to get there?
- **The chart and the interaction.** Does what a learner sees support correct
  inference? Axis choice, scale, what is modeled versus what would be measured,
  false precision, what the visual encoding implies that the model does not
  support.
- **What would a specialist say on first sight** — pharmacokinetics and
  pharmacodynamics, numerical methods, human factors, scientific visualization,
  medical education? `.claude/rules/expert-review.md` has the full list of fields.
- **Is it teaching what it claims?** Where does fidelity exceed the learning
  objective, and where does it fall short of it? Those are different defects.
- **Which decisions of the last few releases would you reverse**, and what does
  reversing cost now versus in a year?

<!-- Optional tail. Delete these two before pasting if you want a pure
     simulation-architecture pass. -->

Secondary, only if the above leaves room:

- Does the roadmap's milestone order actually get to a teachable simulator, or is
  it sequenced by what was tractable?
- What is this project not doing that it should be?

## What I want back

**Primary output: one page.** The three things that would most change this
project's direction, ranked, each with what it costs me to be wrong about it.

Separate **"this is wrong"** from **"this could be more"**, explicitly. A
reviewer asked to find gaps will find some whether or not they are there, and an
undifferentiated list of twenty findings is how I end up over-engineering a
project that is already carrying too much scaffolding. Three ranked findings I
can act on beat twenty I cannot.

**Concluding that the direction is sound is a permitted result**, and a useful
one — but then tell me what you checked and what you would have had to see to
conclude otherwise. A review that could not have come back negative did not
happen.

**Secondary output: file what is actionable** with `bin/docket new "..."`. This
works here: the last outside review filed 65 items and two thirds of them are
closed. But the one page is the deliverable and the items are the residue, not
the other way round.

**You may recommend subtraction.** Dropping queue items, reversing a merged
decision, re-sequencing or cutting a milestone. Recommend only — I decide. Note
that in this project reversals have come from *measurement* rather than
assertion: the one architectural reversal on record happened because an item
measured what the old choice cost a reader. An argument I can check beats a
verdict I have to trust.

## What not to build

You may not leave an unwired artifact. The last architecture review shipped a
verification harness under `tools/`; it was deleted, and the reason recorded was
that it reported defects nobody could act on because they were never in the
queue — "worse than no harness, because it looks like tracking". But note what
survived: two of its physics checks are release gates in
`tests/reference/test_coupled_dynamics.py` and still run today.

So the rule is not "write no code". It is: anything executable you produce
either lands in `make check` or CI in this same pass, or you do not write it.

## Do not quote counts at me from this file

Any number written here rots, and nothing checks it. Every quantitative claim in
your review must come from a command you ran — `bin/docket status`,
`bin/docket wave`, `make check` — and you should say which.

## What I am most concerned about right now

<!-- Replace this line each time. If it is empty, say so and review broadly. -->
