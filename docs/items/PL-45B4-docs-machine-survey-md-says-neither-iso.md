---
id: PL-45B4
title: docs/machine-survey.md says neither ISO standard was read, while docs/MODEL.md quotes ISO 5360:2016 Table 2 and its footnote
status: untriaged
touches: docs/machine-survey.md
added: 2026-11-11
---

**Problem.** docs/machine-survey.md says neither ISO standard was read, while docs/MODEL.md quotes ISO 5360:2016 Table 2 and its footnote

Found by `PL-KZ60` on 2026-11-11.

`docs/machine-survey.md` § "Sources" says of ISO 80601-2-13:2022 and ISO 5360:2016: "Neither standard was read, and the route to both was a web search". `docs/MODEL.md`, in the paragraph on the agent selector's colour, quotes ISO 5360:2016 Table 2 ("Dimensions and colours of agent-specific bottle collars and connectors") and its footnote b, and refers to the standard's Scope. So somebody read ISO 5360 after the survey was written, and the survey's entry no longer tells a reader where that reading is recorded.

**Done when.** The survey's ISO 5360 entry points to the reading `docs/MODEL.md` relies on, with its route and depth, or says why it does not. Find the route first with `git log -S "Table 2" -- docs/MODEL.md` and the item that added it. Nothing in the survey rests on what either standard requires, so no claim changes.
