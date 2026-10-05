---
id: PL-SWD1
title: fraction_from_percent and percent_from_fraction take the other type silently - percent_from_fraction(Percent(0.5)) is a Percent of 50.0 and fraction_from_percent(Fraction(0.5)) a Fraction of 0.005 - because the arithmetic runs first and the constructor's swapped-type check sees a plain float; refuse a Percent where a Fraction is handed in and the reverse, as the constructors do, before converting (found reviewing PL-LLMN)
status: untriaged
feature: parse-dont-validate
added: 2026-10-05
---

**Problem.** fraction_from_percent and percent_from_fraction take the other type silently - percent_from_fraction(Percent(0.5)) is a Percent of 50.0 and fraction_from_percent(Fraction(0.5)) a Fraction of 0.005 - because the arithmetic runs first and the constructor's swapped-type check sees a plain float; refuse a Percent where a Fraction is handed in and the reverse, as the constructors do, before converting (found reviewing PL-LLMN)
