---
id: PL-4FYN
title: docs/INTERFACE.md § 'Why the readouts show two decimals' quotes differences from the independent solution measured on 2026-09-06 at the retired 0.1 s step (1.6e-12 and 5.2e-12 percentage points), which no test asserts; state the reason from the test's limits instead
status: untriaged
feature: floating-point-domain
touches: docs/INTERFACE.md
added: 2026-11-22
---

**Problem.** docs/INTERFACE.md § 'Why the readouts show two decimals' quotes differences from the independent solution measured on 2026-09-06 at the retired 0.1 s step (1.6e-12 and 5.2e-12 percentage points), which no test asserts; state the reason from the test's limits instead

**Found by** the session that closed `PL-TV7Q` (measured figures in the reference test's comments), 2026-11-22. That item removed the unasserted figures from § "Comparing two readouts" only, as its title said. The section above it still says the simulator's results "differed from an independently computed solution by at most $`1.6\times10^{-12}`$ percentage points ... and by $`5.2\times10^{-12}`$ over an hour", dated 2026-09-06, when the step was 0.1 s. No test asserts either figure, and the step has changed since.

**Done when.** The section states its reason from the limits the independent-solution test enforces ($`4\times10^{-13}`$ and $`10^{-12}`$ as a fraction, so $`4\times10^{-11}`$ and $`10^{-10}`$ percentage points), or points at `docs/VERIFICATION.md` § "Independent-solution test", and quotes no dated measurement.
