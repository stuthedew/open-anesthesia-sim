---
id: PL-FSXD
title: The wash-in plot gives no ratio for an inspired concentration that the Circuit readout shows as 0.01%, the value the interface document names as the limit
priority: P2
effort: S
status: done
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/formatting.py, docs/INTERFACE.md, tests/unit/test_wash_in.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-27
pr: 2335
filed-pr: 2294
payoff: the Circuit readout and the F_A/F_I plot agree about which inspired values a ratio is drawn from
tests: tests/unit/test_wash_in.py::test_each_inspired_value_the_readout_shows_gives_a_ratio_always_or_never, tests/unit/test_wash_in.py::test_the_denominator_floor_is_where_the_readout_first_shows_one_step
---

**Problem.** `read_wash_in` in `src/anesthesia_sim/app/wash_in.py` gives no ratio while the inspired fraction is below 1e-4, and `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" calls that 0.01% limit "the smallest step of the concentration display". But `format_percent` in `src/anesthesia_sim/app/formatting.py` rounds to 0.01 percentage points and shows `<0.01%` only for a value that rounds to 0.00%. An inspired fraction from 5e-5 up to 1e-4 is therefore shown as "0.01%" in the Circuit readout (checked 2026-11-23: 5e-5, 7e-5 and 9.9e-5 all give "0.01%", and 4e-5 gives "<0.01%"). In that band the readout shows the very value the document names as the limit, while the caption beside the plot says "Not defined: the inspired concentration is too low to divide by." At another moment the same "0.01%" reading, from a fraction of 1e-4 or more, gives a drawn ratio. A washout passes through the band, and in a low-flow washout it can stay there for minutes.

Both blind review passes of `PL-P3ZL` found it on 2026-11-23. It is older than `PL-P3ZL`: the caption before that change said that no agent had reached the circuit, beside the same "0.01%".

**What to do.** Make the readout and the plot agree about which inspired concentrations the ratio is formed from. Research how a monitor or a display standard aligns a limit with a rounded readout, and record the sources here. Candidates are to test the limit against the value as the readout rounds it, to raise the limit to where the readout shows 0.02%, or to keep the limit and have the caption state it. Each changes when a user sees a ratio, so if the research does not settle it, put the choice to the project owner with a recommendation.

**Why it matters.** In a washout the readout says 0.01% while the plot says the inspired concentration is too low to divide by, and at another moment the same 0.01% gives a drawn ratio. A user cannot tell from the screen why one reading gives a ratio and the other does not.

**Done when.** A test shows that whenever the Circuit readout shows a given inspired value, the plot either always or never forms a ratio from it, and `docs/INTERFACE.md` states the limit in the readout's terms. The research and its sources are recorded here.

**Generator check.** A one-off: a limit in raw units compared with a value shown rounded, older than `PL-P3ZL`. `PL-GJ1W` covers the family of rounded results compared exactly in core, not a display limit.

**Research, 2026-11-27.** The question was how a limit is compared with a value that is shown rounded. The established answer, in conformance testing, is to round the value to the limit's last decimal place first and then compare it.

1. United States Pharmacopeia General Notices 7.20, "Rounding Rules": "When rounding is required, consider only one digit in the decimal place to the right of the last place in the limit expression," with the digit 5 or above rounding up, and rounding only after the final calculation. Read in full in Burgess C, "Rounding results for comparison with specification", *Pharm Technol* 2013;37(4), which quotes the rule, fetched directly (https://www.pharmtech.com/view/rounding-results-comparison-specification). The USP PDF itself (jira.hl7.org attachment) refused a direct fetch with 403, and the web fetch reached only §7.10 verbatim, so §7.20 is cited through Burgess.
2. ASTM E29's rounding method: "the test result is rounded to the place of decimals given in specification limits," and it passes if that rounded value is within the limits. The article also describes the absolute method, used for mechanical dimensions, and says the specification chooses which applies. Fortini P, Carson J, ASTM Standardization News, Nov/Dec 2023 (https://www.astm.org/news/absolute-rounding-conformity-specification-nd23), full text read through the web fetch tool; a direct fetch was refused with 403.
3. EDQM, Annex 1 to OMCL guideline PA/PH/OMCL(21)01R1 (https://www.edqm.eu/en/d/1582127): conformance is assessed by comparing the reportable value, rounded appropriately, to the limits, and rounding to decimal places is recommended. Read through the web fetch tool.
4. No patient-monitor manual or display standard found states whether an alarm limit is compared with the shown or the unrounded value. The GE B20 manual's alarm page (manualslib, printed p. 41) has no such rule. A MedDeviceGuide blog post was reported to say that alarms use the unrounded value, but that part was only a summary of the page, not its text, and is not relied on.

**Decision, 2026-11-27.** The first candidate: the limit is tested against the value as the readout rounds it. Rule 1 already stated its intent in the readout's terms ("the smallest inspired concentration that the interface itself reports"), and the conformance practice above compares a rounded value with the limit. The second candidate, raising the limit to 0.015%, would also satisfy the done-when test, but it keeps the limit in raw units beside a rounded readout, the shape that made this defect. It would also refuse a ratio for every fraction shown as `0.01%`, a reading that the readout presents as a number. The third candidate does not meet the done-when test. What a user sees change: in a washout, an inspired value shown as `0.01%` now gives the elimination caption or a drawn ratio rather than "too low to divide by", and the caption says "too low to divide by" only beside `<0.01%` or `0.00%`.

`WASH_IN_DENOMINATOR_FLOOR_FRACTION` is now found at import by a bisection over adjacent doubles, asking `formatting.reaches_concentration_display_resolution`, the readout's own rounding. It comes out at exactly 5e-5, the double whose percent, 0.005000000000000001, formats as `0.01`. A comparison with that constant keeps the per-second chart code to one float comparison, and the new test pins it to the readout from both sides.

**Regression test against the code before the fix.** `git stash push src/ && uv run pytest -q tests/unit/test_wash_in.py -k "always_or_never or first_shows"` failed both tests: `assert {'0.01%': {False, True}} == {}` and `assert '0.01%' == '<0.01%'`.

**Docs checked, 2026-11-27.** `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" (condition 1 and its note for developers) and § "Displayed precision" (the sentence on the wash-in limit), both reworded; `docs/MODEL.md` § on the F_A/F_I plot and its Known limitations, still true; `docs/VERIFICATION.md`, `docs/PARAMETERS.md`, `docs/ARCHITECTURE.md`, `docs/mutation-testing.md` and `README.md`, which state no value for the limit; the `tools/doc_check.py candidates` lines for `wash_in.py`, `test_wash_in.py` and `test_dashboard_frame.py`, still true.
