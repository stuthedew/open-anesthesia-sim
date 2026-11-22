---
id: PL-45B4
title: docs/machine-survey.md says neither ISO standard was read, while docs/MODEL.md quotes ISO 5360:2016 Table 2 and its footnote
priority: P3
effort: S
status: ready
classes: docs
feature: anesthesia-machine
touches: docs/machine-survey.md
added: 2026-11-11
payoff: A reader checking the agent colours against ISO 5360 can find how the standard was read, instead of a survey that says it never was.
---

**Problem.** docs/machine-survey.md says neither ISO standard was read, while docs/MODEL.md quotes ISO 5360:2016 Table 2 and its footnote

Found by `PL-KZ60` on 2026-11-11.

`docs/machine-survey.md` § "Sources" says of ISO 80601-2-13:2022 and ISO 5360:2016: "Neither standard was read, and the route to both was a web search". `docs/MODEL.md`, in the paragraph on the agent selector's colour, quotes ISO 5360:2016 Table 2 ("Dimensions and colours of agent-specific bottle collars and connectors") and its footnote b, and refers to the standard's Scope. So somebody read ISO 5360 after the survey was written, and the survey's entry no longer tells a reader where that reading is recorded.

**Checked 2026-11-22**, at `d4e8200c`. The mismatch is still there. `docs/machine-survey.md` § "Sources" still says "**Neither standard was read, and the route to both was a web search**". The quotation of ISO 5360:2016 Table 2, its footnotes b and c and its Scope now sits in `docs/INTERFACE.md`, in the paragraph on the agent selector's colour, because #2109 (`PL-CTXZ`) moved it there from `docs/MODEL.md` on 2026-11-13. Both texts were already present at the freeze: `git show 0947408:docs/machine-survey.md` holds "Neither was read", and `git show 0947408:docs/MODEL.md` holds the footnote c quotation "Munsell colour is the original". The quotation first appears at this clone's history horizon, so the shallow clone cannot show who read the standard or how.

**Why it matters.** A reader who checks the agent colours against their source finds the survey saying that nobody read the standard, while the interface specification quotes its table word for word. They cannot tell whether the quotation came from the standard itself or from a secondary source, so they cannot judge how far to trust the colour each agent is drawn in. No displayed value changes.

**Done when.** The survey's ISO 5360 entry points to the reading that `docs/INTERFACE.md` relies on, with its route and how much of the standard was read, or says why it cannot. The item that first quoted Table 2 is the place to look for the route. Nothing in the survey rests on what either standard requires, so no other claim in it changes.

**Generator check.** A one-off. The misread fact is which sources the project has read, and at what depth. `PL-KZ60` (checking each survey claim against how far its source was read) already swept that fact for the survey, and no head's `misread:` line states it.
