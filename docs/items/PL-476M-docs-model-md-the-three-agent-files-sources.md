---
id: PL-476M
title: docs/MODEL.md, the three agent files' sources notes and .claude/rules/sources-and-docstrings.md call the stored tissue:gas coefficients Yasuda, Targ and Eger's measurements 'as Gas Man rounded them', but isoflurane fat 70.0 against 64.2 and desflurane fat 13.0 against 12.0 are not roundings; seven of the nine cells differ, all within one SD
status: untriaged
feature: stale-source-claims
added: 2026-10-25
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
