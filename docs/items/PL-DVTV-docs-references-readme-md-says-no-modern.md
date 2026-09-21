---
id: PL-DVTV
title: docs/references/README.md says no Modern Anesthetics chapter has been read at full text, but Meyer et al. was read on 2026-09-19 and is now cited in docs/MODEL.md
priority: P3
effort: S
status: ready
classes: docs
feature: circuit-boundary-docs
touches: docs/references/README.md
added: 2026-09-20
payoff: a session checking the provenance of docs/MODEL.md's new Meyer citation finds the reading recorded, instead of a standing refusal that would read it as unsourced
verify: grep -q 'PL-WJNS' docs/references/README.md
---

**Problem.** docs/references/README.md says no Modern Anesthetics chapter has been read at full text, but Meyer et al. was read on 2026-09-19 and is now cited in docs/MODEL.md

 — found while closing `PL-WJNS`, which added the first citation of that
chapter to `docs/MODEL.md`.

`docs/references/README.md` § "Schüttler & Schwilden 2008 — *Modern
Anesthetics*" ends: *"**No chapter has been read at full text**, so nothing
here may yet be cited for a value."* That was written 2026-09-15 and was true
then. On 2026-09-19 the machine survey read Meyer et al.'s chapter (pp.
451–470) at full text from the private reference corpus and recorded the route
and depth in `docs/machine-survey.md` § "Sources"; `PL-WJNS` has now quoted it
in `docs/MODEL.md` § "Breathing circuit" for the Zeus's surplus gas valve.

**Why it matters.** The sentence is a standing refusal, and it now refuses a
reading that has happened. A session checking the provenance of the new
`docs/MODEL.md` citation reads it and concludes the citation is unsourced —
which is the opposite of the truth, and exactly the failure the extraction-note
rule in `.claude/rules/citing-sources.md` exists to prevent. The reading is
recorded, just not in the file that says where readings are recorded.

**Where.** `docs/references/README.md` § "Schüttler & Schwilden 2008", closing
paragraph; the four-chapter list above it, where Meyer et al. is the fourth
entry.

**Done when.** The entry records that Meyer et al.'s chapter has been read at
full text, with the date and the route, and the blanket sentence is narrowed to
the chapters that genuinely have not been read.
