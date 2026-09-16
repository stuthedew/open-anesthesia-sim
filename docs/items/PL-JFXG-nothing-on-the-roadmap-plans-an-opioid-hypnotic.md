---
id: PL-JFXG
title: Nothing on the roadmap plans an opioid/hypnotic interaction display, though CLAUDE.md's safety standard names interaction surfaces outright and the owner wants an isobologram widget predicting tolerance of laryngoscopy
priority: P3
effort: S
status: done
classes: planning, docs
touches: ROADMAP.md
added: 2026-09-15
closed: 2026-09-15
pr: 597
verify: python3 tools/doc_check.py check && grep -qF 'Add an opioid/hypnotic interaction display' ROADMAP.md
---

**Problem.** Nothing on the roadmap plans an opioid/hypnotic interaction display, though CLAUDE.md's safety standard names interaction surfaces outright and the owner wants an isobologram widget predicting tolerance of laryngoscopy

**Why it matters.** `CLAUDE.md`'s safety-critical standard names "interaction
surfaces" in its own list of examples, alongside effect-site concentrations and
MAC-equivalent values, so the project has already decided how such a display
would be held. What it has never done is plan one. The roadmap's IV and effect
arm - items 13 (IV PK/PD and effect site), 14 (hypnosis/eBIS) and 15
(nociceptive response) - gets as far as two single-drug effect models and stops
short of the interaction between them, which is the clinically interesting part
and the one the owner asked for on 2026-09-15: an isobologram predicting
tolerance of laryngoscopy from a propofol/opioid pair.

**Why it is not simply item 13 plus item 15.** A response-surface interaction
model is its own published model class with its own parameter set, its own
applicability domain and its own validation, and it is not derivable from two
single-drug models: synergy is the measured quantity. So it needs a versioned
parameter file, a provenance record and a source-hierarchy decision exactly as
each agent file has, and it cannot ride item 15's scope silently.

**What it would owe under the clinical-output standard**, all of which argues
for planning it rather than adding it to a widget list later: the endpoint it
is drawn for must be named on the display, because tolerance of laryngoscopy,
of intubation and of skin incision are different surfaces; the plotted point is
a *predicted* pair of effect-site concentrations and must not read as a
measurement; and the iso-effect contours carry population uncertainty that
a clean curve implies away.

**Done when.** `ROADMAP.md` carries a planned-milestone line for an
opioid/hypnotic interaction display, placed after the items it depends on and
stating that the interaction model is a distinct model class with its own
provenance, so scoping it does not start by assuming items 13 and 15 already
contain it.

**Closed 2026-09-15** as planned-milestone **item 37**, placed after items 13
(IV PK/PD and effect site) and 15 (nociceptive response). The line records the
three things that would otherwise be rediscovered at scoping time: that the
interaction model is a distinct model class whose measured quantity is the
synergy, so it owes its own parameter file and provenance rather than riding
item 15's scope; that the endpoint must be named on screen, laryngoscopy,
intubation and skin incision being different surfaces; and that the plotted
point is a predicted pair rather than a measurement, with the contours'
population uncertainty visible.

**No parameter set is named, deliberately.** Which published response surface
this project adopts is a source-hierarchy decision like every entry under
`src/anesthesia_sim/data/`, and none was verified against its source in the
session that filed this. Naming one here would be the memory-sourced constant
`.claude/rules/expert-review.md` refuses.
