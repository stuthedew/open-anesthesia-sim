---
id: PL-BDNB
title: core/'s closed forms name the partial-pressure-equivalent fraction with bare _fraction locals, and integrated_circuit_fraction_s keeps the stutter PL-9SH6 removed from the accessor
priority: P3
effort: S
status: done
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/core
added: 2026-09-13
closed: 2026-09-14
verify: uv run pytest tests/unit/test_circuit.py && grep -q 'integrated_inspired_partial_pressure_fraction_s' src/anesthesia_sim/core/circuit.py
---

**Problem.** core/'s closed forms name the partial-pressure-equivalent fraction with bare _fraction locals, and integrated_circuit_fraction_s keeps the stutter PL-9SH6 removed from the accessor

`PL-9SH6` gave every *accessor* one name for the dimensionless
partial-pressure-equivalent fraction and deliberately stopped there. The local
variables inside the closed forms were not in its table and still carry short
names for the same quantity:

| Where | Local | What it holds |
| --- | --- | --- |
| `core/circuit.py:247-252` | `initial_fraction`, `delivered_fraction`, `next_fraction` | `inspired_`/`delivered_partial_pressure_fraction` |
| `core/circuit.py:259` | `integrated_circuit_fraction_s` | the inspired fraction integrated over the step, L·s/L |
| `core/tissue.py:194-196` | `initial_fraction`, `next_fraction` | `partial_pressure_fraction` |
| `core/blood.py:125-128` | `initial_fraction`, `next_fraction` | `partial_pressure_fraction` |
| `core/governing_equations.py:283` | `delivered_fraction` | `settings.delivered_partial_pressure_fraction` |

**Most of these are defensible and this item is not really about them.** A
local bound one line below the accessor it reads, inside a five-line closed
form, is not the translation step `.claude/rules/core-domain.md` objects to —
the full name is in the reader's eye. `delivered_fraction` in
`governing_equations.py` is the weakest of them, since it is bound at line 283
and last read at line 331, which is far enough that the reader no longer has
the accessor in view.

**`integrated_circuit_fraction_s` is the one worth deciding.** It carries
*both* defects `PL-9SH6` was written to remove. It is a short name for the
partial-pressure-equivalent fraction, and `circuit_` stutters on a
`BreathingCircuit` method exactly as `circuit_concentration_fraction` did —
which is the name that rename replaced with `inspired_`. It is also not simply
a fraction: it is the fraction integrated over the step, so its unit is
seconds, which is what the `_s` suffix says and what makes
`integrated_inspired_partial_pressure_fraction_s` the faithful form. Whether
that is an improvement at 44 characters is the judgment this item asks for.

**Why a tool will not catch it.** `tools/core_vocabulary_check.py`
(`PL-FZ6T`) matches whole identifiers against `RETIRED_NAMES`, so none of
these is a retired name and none is reported. That is correct rather than a
gap: whether a name is the one a reader who knows the domain would guess is
the judgment that file explicitly refuses to script.

**Found.** `PL-FZ6T`, building the retired-name rule, 2026-09-13. Scanning
`core/` for every identifier containing `_fraction` turned these up beside the
names the rule was written for.

**Not `PL-6KNM`.** That one is about `require_concentration_fraction`,
`concentration.py` and the `Fraction` `NewType` — the *representation* layer,
one question with three parts. These are locals inside the equations and can
be decided separately.
**Why it matters.** One of the five entries above is worth a decision and the
brief says which. `integrated_circuit_fraction_s` carries both defects
`PL-9SH6` was written to remove - a short name for the
partial-pressure-equivalent fraction, and a `circuit_` stutter on a
`BreathingCircuit` method - and it is the one identifier in the closed forms
that a reader who knows the domain would not guess, which is the bar
`.claude/rules/core-domain.md` sets. The risk this item carries is the opposite
one: that it becomes a five-site rename buying nothing, since a local bound two
lines below the accessor it reads is not a translation step.

**Done when.** A decision is recorded on `integrated_circuit_fraction_s` alone -
renamed to the faithful form, or kept with the reason written where a reader of
the closed form can see it - and the defensible locals are named as deliberately
left, so this is not re-raised. The decision should also say something about
`delivered_fraction` in `core/governing_equations.py`, which the brief marks as
the weakest of them: bound at line 283 and last read at line 331, far enough
that the accessor is no longer in the reader's eye.

**Decision needed.** Is `integrated_circuit_fraction_s` renamed to the faithful `integrated_inspired_partial_pressure_fraction_s`, at 44 characters, or kept with its reason written beside it?

**Decided 2026-09-14: `integrated_circuit_fraction_s` is renamed; the other
four locals are deliberately left, and the reasons are written where each is
read.**

**Renamed to `integrated_inspired_partial_pressure_fraction_s`.** It carried
both defects `PL-9SH6` was written to remove — a short name for the
partial-pressure-equivalent fraction, and a `circuit_` stutter on a
`BreathingCircuit` member — and it is the integral of
`inspired_partial_pressure_fraction` exactly, so the faithful name is the one
the project's own convention generates. Forty-six characters is the cost;
`.claude/rules/core-domain.md`'s test is whether a reader who knows the domain
would guess the name, and `integrated_circuit_fraction_s` fails it twice over
while a length does not. A comment at the binding states what the quantity is
($`\int F_I \mathrm{d}t`$, hence the seconds) and that the short locals above
it are left on purpose, so this is not re-raised.

**`initial_fraction`, `delivered_fraction`, `next_fraction`,
`fraction_remaining` in `circuit.py`, `tissue.py` and `blood.py` stay.** Each is
bound one line below the accessor it reads, inside a closed form short enough
that the full name is still in the reader's eye. That is not the translation
step the rule objects to.

**`delivered_fraction` in `core/governing_equations.py` stays, and the brief
was right that it needed an argument rather than the same sentence.** Bound at
line 283 and last read at line 331 — but every matrix row that reads it sits
directly under a comment writing the equation in the specification's own
symbols (`dM_delivered/dt = V_F * F_D`), so the reader has $`F_D`$ in view *at
the row* rather than carrying the binding down the module. Its neighbours
(`fresh_gas_l_s`, `ventilation_l_s`, `blood_gas`) are short for the same
reason, and the full `delivered_partial_pressure_fraction` would wrap the two
rows that read it — which is the case `.claude/rules/core-domain.md` settles
the other way: where a naming choice makes the model harder to see, the model
wins. The reasoning is now a comment at the binding.
