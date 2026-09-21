---
id: PL-0GMC
title: The durable-versus-cheap trade reaches a session only when the project owner types it into the chat, so every design round that happens without them picks the cheap route unopposed
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
touches: .claude/rules/expert-review.md, docs/resident-instructions.md, docs/items/
added: 2026-09-21
closed: 2026-09-21
verify: grep -q 'Count what undoing it would cost' .claude/rules/expert-review.md && grep -q 'PL-0GMC' docs/resident-instructions.md
---

**Problem.** The project owner reports that one thing they say in chat keeps
working: *of these options, which will we be glad we implemented in five
years?* It lands because it arrives at the fork, while the options are still
on the table. Nothing resident carries it, so it reaches the design rounds
they are present for and no others — and a session alone at a fork has every
local incentive to take the route that clears the immediate obstacle.

**Why it matters.** The store shows the fork is common and the answer is
already being reached inconsistently. 74 of the 345 open items carry an
`**Approach**` or `**Decision needed**` section (measured 2026-09-21,
excluding `done` and `dropped`). Two in flight on the day this was filed are
the shape exactly: `PL-316G` (convert the 150 possessive-form citations) puts
"convert nothing, adopt `§` for new citations only" third and calls it honest
only if paired with saying so — a loan whose principal grows with every
citation written afterwards; `PL-L609` (the fixture-id check's blind spot)
reaches the right answer unprompted, "the third is the only one that removes
the form rather than policing it," which is this rule being re-derived from
scratch by a session that had no carrier for it.

**Approach, and why it is not a statement of the philosophy.** A value can be
agreed with and not applied, which is how a resident rule rots. A *count*
cannot: either a number was produced or it was not, and the reply shows
which. So the rule is written as a forcing question — name what would have to
change to switch routes later, and count what is already downstream — with
the owner's five-year form carried as the tie-breaker for where the count
genuinely cannot be taken.

The count is deliberately symmetric. A mechanism with nothing downstream
fails it as surely as a stop-gap under a thousand call sites passes it, which
is what stops it being quoted as licence to over-build and what keeps it from
colliding with `.claude/rules/apparatus-standard.md`, which argues the other
way on the apparatus paths. Reversibility rather than size or effort is the
discriminator, which is Bezos's Type 1 / Type 2 split; Cunningham's own
reading of the debt metaphor supplies the other half, that the loan is sound
taken deliberately and repaid.

**Carrier.** Resident, in `.claude/rules/expert-review.md`, as a third
heuristic beside § "Name the number that would change your mind, then go and
count it" and § "Say what would falsify it, then record the instance rather
than the rule". The other three dispositions were tested and lose:

- **A check** cannot decide which route is durable; `CLAUDE.md` § "Prefer
  deterministic tooling over repeated model work" forbids scripting the
  judgment half. The decidable sliver — presence of a count on an item that
  enumerates two or more routes — is real and deferred, with its build
  condition recorded in `docs/resident-instructions.md`.
- **The `docket` skill** fires when the queue is worked. The fork also
  happens in design rounds that never touch the queue, which is where the
  owner has been supplying it by hand.
- **A path scope** cannot reach a reply, which no read precedes. Settled for
  this whole file by `PL-WWDT`.

**Cost.** +2348 resident characters, and nothing was cut to pay for it. The
reason is recorded in `docs/resident-instructions.md` § "What stays resident,
and on what argument": the carrier being replaced is the owner's keyboard,
not a resident rule, so there is nothing superseded to retire. Two candidate
cuts were examined and both fail the rewrite test.

**Asked for 2026-09-21 (project owner); the form is the session's own and is
not yet ratified.** What the owner asked for was the outcome — the philosophy
reaching a session without worsening instruction rot — and named no mechanism,
so the forcing-question form, the `expert-review.md` placement and the
five-year phrasing being demoted to a tie-breaker are all the session's
recommendation. They were landed rather than put as a question because
`CLAUDE.md` § "The queue, and how the project owner works" requires a behavior
change to take effect in the session that asks for it, and because the edit is
one file reverted by one edit. Chosen over a fourth resident block in
`CLAUDE.md` and over a new item field with a check behind it. **If the owner
reads the sharpening as a change of meaning rather than a rendering of it, the
paragraph to rewrite is the last one**, which is where their own words sit.
