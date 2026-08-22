# v0.0.2 idealized breathing-circuit wash-in

## Purpose

This milestone replaces the dimensionless demonstration curve with one
analytically solvable physical subsystem: a constant-volume, perfectly mixed
breathing circuit supplied by constant fresh gas flow.

It does not model a patient, ventilation, rebreathing chemistry, uptake,
metabolism, anesthetic potency, or clinical behavior.

## State and inputs

- `circuit_concentration_fraction` is the current agent fraction in the circuit.
- `delivered_concentration_fraction` is the fresh-gas agent fraction.
- `fresh_gas_flow_l_min` is fresh gas flow in liters per minute.
- `circuit_volume_l` is the constant mixed-circuit volume in liters.
- `elapsed_s` and `simulation_step_s` are measured in seconds.

Concentration fractions are stored from 0 through 1. The UI converts them to
percent only for display and input.

## Governing equation

For equal inflow and outflow from a perfectly mixed constant-volume circuit:

    dF_circuit/dt = (FGF / V) * (F_delivered - F_circuit)

Because flow is entered in liters per minute and simulation time is seconds:

    time_constant_s = 60 * circuit_volume_l / fresh_gas_flow_l_min

For constant inputs over one simulation step, the exact update is:

    F_next = F_delivered
             + (F_current - F_delivered) * exp(-step_s / time_constant_s)

At zero fresh gas flow, the time constant is infinite and concentration does
not change.

## Required invariants

- Circuit volume is positive and finite.
- Fresh gas flow is nonnegative and finite.
- Concentration fractions remain between 0 and 1.
- Positive flow moves circuit concentration monotonically toward the delivered
  concentration without overshoot.
- One large step and many smaller steps give the same result for constant inputs.
- Reset clears elapsed time and circuit concentration but preserves settings.

## Known limitations

This is an idealized validation model, not a complete anesthesia circuit. It
assumes instantaneous perfect mixing, constant volume, equal inflow and outflow,
constant settings during each step, and no patient connection or uptake.