---
id: PL-0C6W
title: Triage the fourteen captures open on the morning of 2026-09-16
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.26
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 611
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-2B7B, PL-Q2PX and PL-LYX2)
---

**Problem.** Triage the fourteen captures open on the morning of 2026-09-16

**Why it matters.** An untriaged item is in no band, so `bin/docket next`
cannot offer it and `bin/docket gate` cannot count it as debt: fourteen of them
is a second queue nobody reads, and `docket.toml`'s `untriaged_stale_days = 14`
exists to stop that becoming permanent. Most of this batch carries a debt class
or reaches `needs-decision`, so it is what the *next* gate counts - Gate 1 is
frozen under v0.5.0, and a finding made after a freeze goes to the following
gate unless its problem predates it.

Filed before the pass began, per `CLAUDE.md`'s housekeeping rule: a triage pass
takes a branch and a commit of its own, and every in-flight guard this project
has matches a `PL-` id, so unfiled it would read as nobody's work to all of
them and keep reading that way after the push.

**Done when.** Every capture in the batch carries `priority`, `effort`,
`classes`, `touches` and a `feature`; each is at `ready` with a `verify:`
command that has been run and watched fail for the right reason, at `ready`
with a `not-delegable` reason where no command can prove it, at
`needs-decision` with a `**Decision needed.**` section stating the question, or
`dropped` with a `reason` and a `closed` date; each brief carries
**Problem.**, **Why it matters.** and **Done when.**; and `make docket` and
`make check` pass.

Two of the fourteen are deliberately not this pass's. `PL-SYG4` and `PL-2M4X`
were being triaged concurrently by another session (branch
`claude/quirky-newton-tf1moa`), which the in-flight mark cannot see because a
triage pass writes nothing outside `docs/items/` - the `PL-N1JK` case. They are
left to that session and stay untriaged here.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it. This item is also named in paragraphs quoted in the briefs of `PL-Q0J1` and `PL-TH35`.

> **Seven more from the 2026-09-16 triage pass** (`PL-0C6W`), over the fourteen captures open that morning. All seven were captured on 2026-09-15 or 2026-09-16, nine and ten days after the 2026-09-06 freeze. So "The gate is a snapshot" already places them in the next gate. They are written down because each is debt. Five are classed `defect`, and `PL-6QZP` and `PL-PFK1` are debt by their `needs-decision` status. Without this note, a reader who found one open would have to work out why it is absent from a gate this size. `PL-1RTM`, `PL-6QZP`, `PL-7CSP`, `PL-99YZ`, `PL-PFK1`, `PL-Q8RQ`, `PL-Z9K5`.

> **The arithmetic has changed under this section, and the ground is stated on what is true now rather than recited.** The paragraphs above decline on a gate that is "not draining" and then "finally draining". Today `bin/docket wave` reports it at **170 entries, 165 cleared, 5 open - and 0 that this gate can clear**. All five are blocked on work outside the gate. So the refilling-queue argument no longer fits the facts, and a weaker version of it should not be borrowed. What applies instead is simpler: the gate has done its job. Admitting seven post-freeze apparatus findings would re-open a cleared gate. It would hold v0.5.0, a simulator milestone, behind workflow-lane debt. That is the outcome the snapshot rule exists to prevent. The timeline also puts v0.4.26 ahead of v0.5.0, so this gate is not even the beat that is due.

> **Three of the seven describe problems that are themselves new**, so the snapshot rule defers them by its own terms rather than by any exception. `PL-6QZP` and `PL-PFK1` are second-order consequences of `PL-69JZ` and `PL-7XTS` (closed 2026-09-12 and 2026-09-15). `PL-Z9K5` is a residual gap inside the exemption that `PL-ZYQC` produced (closed 2026-09-12). The other four (`PL-1RTM`, `PL-7CSP`, `PL-99YZ`, `PL-Q8RQ`) describe problems that predate the freeze and pass the presence test squarely. They are declined on the ground stated above, and this is said plainly rather than blurred.

> **Six sit wholly in the workflow lane**, where the groups before them sit. They are apparatus held to `.claude/rules/apparatus-standard.md`'s lower bar, and none of them can affect a reader of the simulator. `PL-1RTM` is the exception, and it is named here rather than quietly counted with them. Its `touches` includes `docs/ARCHITECTURE.md`, which `docket.toml` deliberately keeps out of `workflow_paths` because that file is written for a reader of the simulator. The product-lane half of `PL-1RTM` is one sentence describing what a tooling check covers. It is not anything a clinician could read a number from, so it is declined with the rest.
