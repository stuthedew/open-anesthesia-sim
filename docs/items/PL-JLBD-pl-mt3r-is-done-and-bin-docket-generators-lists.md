---
id: PL-JLBD
title: PL-MT3R is done and bin/docket generators lists it drained, yet its front matter still carries generator: live and docket check is silent, so the field and the register disagree about one head while the pause rule reads only open items
status: untriaged
added: 2026-10-01
---

**Problem.** PL-MT3R is done and bin/docket generators lists it drained, yet its front matter still carries generator: live and docket check is silent, so the field and the register disagree about one head while the pause rule reads only open items

**Recorded alternative, from the 2026-10-01 survey.** Either the close-out writes `generator: spent - <why>` on a drained head, or `docket check` refuses `generator: live` on a closed item; which is the triage question. Found 2026-10-01 while measuring whether the generator pause still binds: it does not, since no open item carries the field.
