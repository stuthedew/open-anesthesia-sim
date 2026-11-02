---
id: PL-476M
title: docs/MODEL.md, the three agent files' sources notes and .claude/rules/sources-and-docstrings.md call the stored tissue:gas coefficients Yasuda, Targ and Eger's measurements 'as Gas Man rounded them', but isoflurane fat 70.0 against 64.2 and desflurane fat 13.0 against 12.0 are not roundings; seven of the nine cells differ, all within one SD
priority: P2
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: docs/MODEL.md, src/anesthesia_sim/data/agents/, .claude/rules/sources-and-docstrings.md
added: 2026-10-25
closed: 2026-11-02
pr: 1940
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

**Closed 2026-11-02.** The three agent files' `sources` notes, `docs/MODEL.md`
and `.claude/rules/sources-and-docstrings.md` now call the stored tissue:gas
coefficients Gas Man's figures for Yasuda, Targ and Eger's measurements, each
within one standard deviation. Measured against Table 1 on 2026-11-02, two of
the nine match the mean exactly (desflurane vessel-rich, sevoflurane fat). Two
more are the mean rounded to the stored precision (isoflurane vessel-rich
2.09 to 2.1, sevoflurane muscle 2.38 to 2.4). The other five are not
roundings, from −4.3% (sevoflurane vessel-rich) to +9.0% (isoflurane fat).
The notes' count, "three of the nine reproduce them", now says four, two
exactly and two as roundings. Blind review found that count and one more
stale sentence in the same notes: storing Yasuda's figures "would also end the
property … that all three agents carry one identical rounding". That sentence
was false twice over. The stored values are not one uniform rounding, and
storing Yasuda's own figures would keep the one-study property that
`docs/MODEL.md` § "v0.2.0: isoflurane and desflurane" relies on. It is
removed, which leaves the notes' reasons for declining the same as the Declined paragraph in `docs/MODEL.md`.

**No version moves.** No stored value changed, only the `sources` notes. The
data files' `schema_version` describes the file's shape, which did not change,
and the parameter set has no version of its own apart from the release.
