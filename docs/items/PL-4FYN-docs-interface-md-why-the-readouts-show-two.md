---
id: PL-4FYN
title: docs/INTERFACE.md § 'Why the readouts show two decimals' quotes differences from the independent solution measured on 2026-09-06 at the retired 0.1 s step (1.6e-12 and 5.2e-12 percentage points), which no test asserts; state the reason from the test's limits instead
status: done
feature: floating-point-domain
milestone: v0.6.21
touches: docs/INTERFACE.md
added: 2026-11-22
closed: 2026-11-22
pr: 2243
verify: ! grep -qF 'one two-billionth' docs/INTERFACE.md
---

**Problem.** docs/INTERFACE.md § 'Why the readouts show two decimals' quotes differences from the independent solution measured on 2026-09-06 at the retired 0.1 s step (1.6e-12 and 5.2e-12 percentage points), which no test asserts; state the reason from the test's limits instead

**Found by** the session that closed `PL-TV7Q` (measured figures in the reference test's comments), 2026-11-22. That item removed the unasserted figures from § "Comparing two readouts" only, as its title said. The section above it still says the simulator's results "differed from an independently computed solution by at most $`1.6\times10^{-12}`$ percentage points ... and by $`5.2\times10^{-12}`$ over an hour", dated 2026-09-06, when the step was 0.1 s. No test asserts either figure, and the step has changed since.

**Done when.** The section states its reason from the limits the independent-solution test enforces ($`4\times10^{-13}`$ and $`10^{-12}`$ as a fraction, so $`4\times10^{-11}`$ and $`10^{-10}`$ percentage points), or points at `docs/VERIFICATION.md` § "Independent-solution test", and quotes no dated measurement.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`, in the same pull request as `PL-TV7Q`. The opening paragraph of § "Why the readouts show two decimals" now takes its claim from the limits that `docs/VERIFICATION.md` § "Independent-solution test" enforces: $`4\times10^{-11}`$ percentage points over the five runs and $`10^{-10}`$ over the held hour, which are $`4\times10^{-13}`$ and $`10^{-12}`$ as a fraction. The larger is one hundred-millionth of the last displayed digit, 0.01 percentage points. The dated 2026-09-06 figures are gone. The conclusion that a third decimal would not be numerical noise still holds, because the limits leave it eight orders of magnitude clear.

Files checked: `docs/INTERFACE.md`, `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md` and `README.md`, by `grep -n "two-billionth\|1\.6\\\\times10^{-12}\|5\.2\\\\times10^{-12}"`. None printed.

**Review fix 2026-11-22**, after two blind review passes on #2243. The sentence on the hour now names what the test checks: one reference point (5% delivered, 4 L/min of fresh gas, the reference adult's default ventilation and cardiac output) at 60 s, 600 s and 3600 s (`test_the_shipped_step_reaches_the_pinned_reference_horizons`). The 4e-11 sentence now says it applies to the runs the test covers.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: a measured rounding figure standing in for, or copied beside, the bound it should be checked against. That head is still open, so this is not a re-entry; it was found by `PL-TV7Q`, which is under the same head.
