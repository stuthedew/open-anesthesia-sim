---
id: PL-476M
title: docs/MODEL.md, the three agent files' sources notes and .claude/rules/sources-and-docstrings.md call the stored tissue:gas coefficients Yasuda, Targ and Eger's measurements 'as Gas Man rounded them', but isoflurane fat 70.0 against 64.2 and desflurane fat 13.0 against 12.0 are not roundings; seven of the nine cells differ, all within one SD
priority: P2
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: docs/MODEL.md, src/anesthesia_sim/data/agents/, .claude/rules/sources-and-docstrings.md
added: 2026-10-25
payoff: The provenance notes say what Gas Man did to Yasuda's tissue measurements, so a reader no longer takes a 9% difference for rounding.
verify: grep -rq "Gas Man's figures for Yasuda" src/anesthesia_sim/data/agents/isoflurane.json && grep -q "Gas Man's figures for Yasuda" .claude/rules/sources-and-docstrings.md
---

**Problem.** docs/MODEL.md, the three agent files' sources notes and .claude/rules/sources-and-docstrings.md call the stored tissue:gas coefficients Yasuda, Targ and Eger's measurements 'as Gas Man rounded them', but isoflurane fat 70.0 against 64.2 and desflurane fat 13.0 against 12.0 are not roundings; seven of the nine cells differ, all within one SD

**Found 2026-10-25** by blind review pass 2 of pull request 1819. That
branch fixed the one sentence it had added (§ "Parameter provenance", the
Baker cross-check), which now says "Gas Man's figures for Yasuda, Targ and
Eger's measurements". The older wording is elsewhere: `docs/MODEL.md`'s
"Declined" paragraph ("Gas Man's rounding of them"), the `sources` notes in
`src/anesthesia_sim/data/agents/*.json`, and
`.claude/rules/sources-and-docstrings.md`.

Measured from `docs/MODEL.md`'s v0.2.0 table: seven of the nine stored
values differ from Yasuda's means, by −4.3% (sevoflurane vessel-rich) to
+9.0% (isoflurane fat), and every one lies within 0.71 SD. Rounding to the
printed precision explains 2.38 to 2.4 and 2.09 to 2.1, but not 64.2 to 70.0,
12.0 to 13.0, 4.40 to 4.5 or 0.94 to 0.97. The right word is probably
"adjusted" or "Gas Man's figures for"; which one is a wording choice. Editing
a `sources` note changes a data file, so check whether the parameter set's
version must move with it.

**Why it matters.** "Rounded" tells a reader that the stored coefficient is
Yasuda's mean to the printed precision. For isoflurane fat it is 9% above the
mean, and § "Known limitations" now sizes the uncertainty from that
difference. A provenance note that understates the gap makes the stored value
look better measured than it is.

**Done when.** No live document or `sources` note calls the stored tissue:gas
coefficients Yasuda's measurements "as Gas Man rounded them" or "Gas Man's
rounding". Each says instead that they are Gas Man's figures for Yasuda's
measurements, within one standard deviation of each.

**Generator check.** Not a generator. One phrase was copied into several
documents when `PL-FN5F` recorded the adoption on 2026-09-13. Nothing keeps
producing new copies, and this item covers every copy the search found.
