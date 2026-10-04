---
id: PL-LBQY
title: A bare float written straight onto a non-frozen compartment field (circuit.fresh_gas_flow_l_min = 1000.0) is caught only at the next equation_settings(), so for one tick the snapshot and the readouts carry an unchecked value and SimulationSnapshot's typed fields carry no runtime check of their own; decide whether a __setattr__ guard or frozen compartments moves the check to the write, or record the one-tick window as accepted (found reviewing #1350)
status: untriaged
added: 2026-10-04
---

**Problem.** A bare float written straight onto a non-frozen compartment field (circuit.fresh_gas_flow_l_min = 1000.0) is caught only at the next equation_settings(), so for one tick the snapshot and the readouts carry an unchecked value and SimulationSnapshot's typed fields carry no runtime check of their own; decide whether a __setattr__ guard or frozen compartments moves the check to the write, or record the one-tick window as accepted (found reviewing #1350)
