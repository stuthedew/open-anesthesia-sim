---
id: PL-8W1W
title: SimulationState.step_count and simulation_step_s can be assigned after construction without any check - state.step_count = 5 stores a bare int, and = -3 after a step makes elapsed_s raise - the shape PL-LBQY records for the compartments' flows, on the run's own state; nothing in src writes either outside advance and reset; decide it with PL-LBQY: a __setattr__ guard, read-only fields, or the window recorded as accepted (found reviewing #1354)
status: untriaged
added: 2026-10-04
---

**Problem.** SimulationState.step_count and simulation_step_s can be assigned after construction without any check - state.step_count = 5 stores a bare int, and = -3 after a step makes elapsed_s raise - the shape PL-LBQY records for the compartments' flows, on the run's own state; nothing in src writes either outside advance and reset; decide it with PL-LBQY: a __setattr__ guard, read-only fields, or the window recorded as accepted (found reviewing #1354)
