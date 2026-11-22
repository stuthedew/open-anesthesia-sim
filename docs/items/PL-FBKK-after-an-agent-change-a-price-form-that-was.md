---
id: PL-FBKK
title: After an agent change, a price form that was already open in the agent cost View still has the earlier agent selected
priority: P2
effort: S
status: ready
classes: defect, ux
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/qt_agent_price.py, tests/integration/test_agent_cost_view.py
deferred-from: v0.7.0 - a new problem: the price form came in with PL-1P15 (#1939, 7baae320, 2026-11-02), work building v0.7.0 after the freeze; not safety or science, and no price or cost the View shows changes
added: 2026-11-11
payoff: after an agent change, the open price form shows the agent the learner is now running, unless they picked one by hand
---

**Problem.** After an agent change, a price form that was already open in the agent cost View still has the earlier agent selected

**Found on 2026-11-11 by the builder of `PL-RF2S`'s second pull request, and
not fixed there.** `PriceEntry.show_prices` (`app/qt_agent_price.py`) moves the
agent selector to the first displayed run's agent only until an agent has been
chosen once (`_agent_chosen`). After that the selector stays where it is. So
with the form open on sevoflurane, a change of the run's agent to desflurane
leaves the form on sevoflurane, on a drawn frame as well as on a halt. The
builder checked this with a script and wrote no test.

**This may be intended.** The selector is the reader's own choice of which
agent to price, and the form names that agent beside its fields. Triage
decides whether the form should follow the run's agent when the reader has not
picked one by hand. `PL-RF2S`'s second pull request fixed the case next to it:
a form first opened after an agent change that no frame drew named the agent
that the run no longer holds.

**Checked 2026-11-22.** `PriceEntry.show_prices` in `app/qt_agent_price.py` still moves the selector to the first displayed run's agent only while `_agent_chosen` is false. It sets `_agent_chosen` on that first move as well as on a pick by hand (`_handle_agent_pick`). So after its first fill the form never follows the run's agent again, whether or not the reader ever picked one. Its docstring calls the run's agent the one "the selector starts on". The form came in with `PL-1P15` (#1939, 2026-11-02), after the freeze.

**Why it matters.** A learner who changes the run's agent and then types a price into the open form sets the earlier agent's price, while the View's cost is for the new agent. The form names its agent beside its fields, so the price goes where the form says. But the learner did not choose the agent the selector shows, and the price they meant for the new agent is not set.

**Decided at triage, 2026-11-22.** The form follows the run's agent until the reader picks an agent by hand, and keeps a hand pick after that. A selector the reader never touched should not stay on a run's earlier agent, because that is stale state of the kind the interface avoids elsewhere. A hand pick is the reader's own choice, so it stays. No price or cost changes under either rule, so this is not put to the owner.

**Done when.** After an agent change, an open price form in which the reader has not picked an agent shows the run's new agent. A form in which the reader picked an agent by hand keeps that pick. A test shows both.

**Generator check.** The fact misread is which widgets state a run's current state, and that each is restated on every path that changes it. The open head `PL-RF2S` states that fact. The selector takes the run's agent at the form's first fill and is not restated on an agent change. The head is open, so this is not a re-entry.
