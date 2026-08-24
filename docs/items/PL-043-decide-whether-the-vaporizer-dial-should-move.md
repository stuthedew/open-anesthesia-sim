---
id: PL-043
title: Decide whether the vaporizer dial should move in real increments
priority: P2
effort: S
status: needs-decision
classes: ux, feature
touches: docs/MODEL.md, src/anesthesia_sim/app/simulation_view.py
added: 2026-08-24
---

**Problem.** `_delivered_concentration_slider` has no `divisions`, so the
delivered-agent setting is continuous over 0 to the agent's dial maximum. A
user can set 4.37% sevoflurane. Real variable-bypass vaporizers are dialed in
discrete increments — commonly 0.2% over the low range and larger above it —
and the Tec 6 desflurane vaporizer is dialed in 1% steps over most of its
range. PL-040 fixed how the setting is *displayed* (0.01 percentage points,
matching the modeled concentrations it produces); it did not touch what the
control can be set to.
**Why it matters.** The delivered concentration is the one number in this
interface a user maps directly onto a physical action at a real machine, so a
control that offers positions no vaporizer has teaches a dial that does not
exist. Against that: the continuous control is a better instrument for
exploring the model's response, which is the simulator's actual purpose, and
quantizing it would make some of the model's behavior unreachable.
**Where.** `app/simulation_view.py` (`_delivered_concentration_slider` and
`_handle_delivered_concentration_change`), the agent data files if the
increment becomes a cited per-agent parameter, `docs/MODEL.md` § "Runtime
controls".
**Decision needed.** Leave the control continuous and say so; quantize it to
per-agent cited increments; or quantize with an explicit fine-adjust escape.
An increment adopted per agent is a device-capability parameter and needs the
same citation discipline as `max_delivered_concentration_percent`.
**Done when.** The choice and its reasoning are recorded, and `docs/MODEL.md`
§ "Runtime controls" states what the delivered-concentration control offers.
