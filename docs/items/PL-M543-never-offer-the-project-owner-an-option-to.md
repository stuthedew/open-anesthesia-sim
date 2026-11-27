---
id: PL-M543
title: Never offer the project owner an option to build something that rests on a paper read only as an abstract, even as an option not recommended
priority: P2
effort: S
status: done
classes: docs
feature: provenance
touches: CLAUDE.md
added: 2026-11-27
closed: 2026-11-27
pr: 2338
payoff: the owner is never offered an option to build something resting on a paper nobody read in full
verify: grep -qF 'Offer no option to build something that rests on it either' CLAUDE.md
---

**Problem.** Never offer the project owner an option to build something that rests on a paper read only as an abstract, even as an option not recommended

**Why it matters.** The project owner, 2026-11-27, in the v0.8.0 scoping
thread: "You shouldn't suggest implementing something based on abstracts". A
scope card had offered adding the spread of ventilation-perfusion ratios as a
second option. One of its two supporting papers had been read only as an
abstract. `CLAUDE.md` already says to rest no recommendation on an abstract
alone. Offering an option is itself a suggestion to build it, so the rule has
to cover every option put in front of the owner.

**Done when.** `CLAUDE.md` § "Proactive expert review and domain best
practices" says that no option to build something may rest on a paper read only
as an abstract, recommended or not.

**Generator check.** None: filed from the project owner's correction in the v0.8.0 scoping thread, not by a finding.
