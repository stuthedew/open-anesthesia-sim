---
id: PL-1DP1
title: fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)
status: untriaged
added: 2026-10-11
---

**Problem.** fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)
