---
id: PL-KD98
title: bin/docket wave reports 'implement' for a milestone whose Required scope is complete, because the beat reads only the frozen gate list and never the scope's item ids
status: untriaged
added: 2026-09-05
---
**Problem.** `bin/docket wave` chose `IMPLEMENT` for v0.4.0 while twelve of the
milestone's thirteen `Required scope` entries were `done`, and the digest
turned that into an assertion: `No release to offer: the roadmap gives 0.4.0
to "the teachable case", which is unfinished`. The project owner asked for the
cut anyway and was right.

**Why it happens.** `_shipping_the_gate()` in
`subprojects/docket/src/docket/roadmap.py` decides the beat from the *frozen
gate list* and the step's version order alone. A milestone recording both a
gate and a scope of its own falls to the `else` branch and is `IMPLEMENT` by
construction, whatever its scope's real state — the docstring says so
deliberately: "its gate clears so that its scope can be implemented, which is
the cadence's ordinary case".

**Why it matters.** The declining is correct; the *wording* is not.
`.claude/skills/docket/SKILL.md` already tells a session that `wave` "computes
and decides nothing", so a session that reads the skill adds the judgment. But
the digest prints `No release to offer` in every session, ahead of the skill
being loaded, and phrases a non-answer as a verdict. A session that trusts it
declines a release that is due.

**Where.** `subprojects/docket/src/docket/roadmap.py` (`_shipping_the_gate`,
`wave`), `subprojects/docket/src/docket/render.py:1058` (the digest line).

**Two candidate fixes, and the choice is the design work.** Parse `PL-` ids out
of the `Required scope` subsection the way the gate list is parsed, and report
the scope's own split (`12 of 13 scope entries closed`) — the same shape the
gate already gets — leaving the beat to say `implement` with the count beside
it. Or leave the computation alone and soften the digest's assertion to a
declining one, which costs nothing and fixes the misreading without teaching
the tool to read prose it was deliberately kept out of. Prefer the second
unless the first turns out cheap: `Required scope` is prose with ids in it,
and a parser over it is the judgment half `CLAUDE.md` says not to script.

**Done when.** A session standing on a milestone whose Required scope is
complete is not told there is no release to offer.
