---
id: PL-4L6Z
title: Verify the model by making it compute a predictable event: recover a stored parameter from a simulated measurement, as Lerou and Booij recover alveolar volume by simulated helium dilution
priority: P2
effort: M
status: done
classes: test
feature: model-spec-accuracy
touches: tests/reference/, docs/MODEL.md
added: 2026-09-06
closed: 2026-10-25
pr: 1819
payoff: The shipped model must now recover its stored alveolar and tissue volumes from simulated measurements, so an equation the specification states wrongly but that conserves agent fails a test.
verify: grep -rq 'def test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value' tests/reference/ && grep -rq 'def test_an_alveolar_volume_recovered_by_closed_circuit_dilution_matches_the_stored_value' tests/reference/ && grep -q '### Parameter-recovery test' docs/MODEL.md
---

**Problem.** This project's verification rests on comparing the shipped step
against an oracle integrator and on mass-balance tolerances. Lerou and Booij
(Br J Anaesth 2001;86:12-28, read at full-text depth 2026-09-06) use a third
device this project has no instance of, and they name what it is for:
verification is "to ascertain its internal mathematical consistency, the
numerical accuracy of the computer processor and, **especially, the freedom
from designer-induced errors**". Their device is to make the model compute an
event whose answer is already known - they simulate the closed-circuit helium
dilution measurement of alveolar volume and check that the model recovers the
alveolar volume it was configured with.

That is a different class of test from an oracle comparison. An oracle checks
that the integrator solves the equations that were written; this checks that
the equations that were written are the ones intended, by running the model
through a procedure whose outcome is fixed by a stored parameter rather than by
the solver. A sign error, a swapped compartment or a units slip that an oracle
reproduces faithfully - because the oracle integrates the same wrong equations -
shows up here as a measurement that comes back wrong.

**Why it matters.** It is the one verification device that catches
designer-induced error rather than numerical error, which is the failure mode
`docs/MODEL.md`'s safety-critical standard is least protected against today:
every existing check would pass on a model that solves the wrong system
correctly. It is also cheap - it needs no new physics, only a scripted
procedure and an assertion.

Candidate procedures, in order of how little new machinery each needs:

1. **Recover a tissue volume from a washin.** Drive a compartment to a known
   fraction of equilibrium and recover its volume from the integrated uptake
   and the partition coefficient. Uses only what the model already exposes.
2. **Recover the alveolar volume** by an inert-tracer dilution, which is
   Lerou and Booij's own case, though it needs a second gas the model does not
   yet carry - see `PL-L2F2`, which is about exactly that gap.
3. **Recover cardiac output** from the Fick relation across a compartment at
   steady state.

**Where.** `tests/reference/`, alongside the existing oracle gate;
`docs/MODEL.md` - "Required tests", which is where the invariant would be
stated. `PL-8LDF` (tie MODEL.md's required invariants to named tests) and
`PL-GZP6` (two required tests are not implemented) are the neighbouring work,
and this would be a third entry rather than a replacement for either.

**Done when.** At least one procedure of this shape runs in the suite, asserts
recovery of a stored parameter to a stated tolerance, and is named in
`docs/MODEL.md` as a verification test distinct from the oracle comparison,
with a sentence saying what class of error it catches that the oracle does not.

**Classed `test` rather than `science`, and it can be overruled.** Nothing in
the model is known to be wrong, and this adds a verification device rather than
correcting a value or a claim - so by the reading `PL-B1WW` was triaged under,
it is a test-quality question and the band stays P2. The counter-argument is
real and is the brief's own: the class of error it catches is invisible to
every check the project has, so a designer-induced error would reach a reader
with all gates green. If that is the weight to give it, the class becomes
`science` and `docket check` moves it to P1.

The `verify:` command names candidate 1 - recovering a tissue volume from a
washin - because it needs no new physics; candidates 2 and 3 would want the
command re-pointed before the work rather than after. Run 2026-09-06 before the
work: exit 1 in 87 s, with `tests/reference/` passing (the whole suite was
green in the same session's `make check`, 1995 passed) and the test absent.

**Re-confirmed 2026-10-25.** The brief still held against the tree. No test
recovered a stored parameter, and `docs/MODEL.md` § "Required tests" named no
such test. One premise had changed. Candidate 2 no longer needs a second gas,
because the supported ranges now reach zero fresh gas flow and zero cardiac
output (`core/supported_ranges.py`). With the circuit closed and the blood flow
stopped, the agent behaves as an insoluble tracer, which is the role helium
plays in Lerou and Booij's measurement.

**Done 2026-10-25.** `tests/reference/test_parameter_recovery.py` runs two
procedures for each of the three agents. The first is Lerou and Booij's
closed-circuit dilution, which recovers the stored alveolar volume from
$`V_A = V_C(F_1-F_2)/F_2`$. The second is candidate 1, which recovers each
tissue group's stored volume from its Fick-principle uptake through the
opening wash-in. Measured residuals are 6.1e-13 relative for the dilution and
7.9e-11 for the washin, against bounds of 1e-11 and 1e-9. Both are stated in
the module. The six cases take about 3 s together. `docs/MODEL.md` §
"Parameter-recovery test" names both tests. It says which class of error they
catch that the oracle and the mass-balance test do not: an equation this
document states wrongly in a way that still conserves agent.

That claim was checked by putting four errors into the shipped code in turn,
in a scratch script outside the suite. Three conserve agent: a tissue capacity
formed as $`V_i\lambda_{i:b}`$ with its rate formed to match, muscle and fat
with their flow fractions swapped, and every flow left in litres per minute.
The washin test failed on each, and the agent accounting raised on none. The
fourth, a tissue rate formed with the tissue:gas coefficient while the
capacity stayed right, does not conserve agent, and the agent accounting
refused it before the test's assertion was reached. So the brief's "swapped
compartment" and "units slip" examples hold. An error that loses or creates
agent is the mass-balance test's to catch rather than this one's. A sign error
was not tried.

Candidate 3, cardiac output from the Fick relation, was not built. It would
need the alveolar balance's rate of change, and it checks the same two
exchange terms that the two tests above already check.

Lerou and Booij's citation was confirmed through PubMed on 2026-10-25 (PMID
11575385, doi:10.1093/bja/86.1.12), read at the abstract. The private
reference corpus does not hold the paper. The brief's quotation about
"designer-induced errors" comes from the 2026-09-06 full-text reading and
was not re-read.
