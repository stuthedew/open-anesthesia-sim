---
id: PL-FBKK
title: After an agent change, a price form that was already open in the agent cost View still has the earlier agent selected
priority: P2
effort: S
status: done
classes: defect, ux
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/qt_agent_price.py, tests/integration/test_agent_cost_view.py
deferred-from: v0.7.0 - a new problem: the price form came in with PL-1P15 (#1939, 7baae320, 2026-11-02), work building v0.7.0 after the freeze; not safety or science, and no price or cost the View shows changes
added: 2026-11-11
closed: 2026-11-22
pr: 2226
payoff: after an agent change, the open price form shows the agent the learner is now running, unless they picked one by hand
tests: tests/integration/test_agent_cost_view.py::test_an_open_price_form_follows_the_run_s_agent_until_the_reader_picks_one, tests/integration/test_agent_cost_view.py::test_an_agent_the_reader_picked_in_the_price_form_stays_through_an_agent_change, tests/integration/test_agent_cost_view.py::test_a_price_the_reader_is_typing_stays_with_its_agent_through_an_agent_change, tests/integration/test_agent_cost_view.py::test_a_refused_price_stays_beside_the_agent_it_was_refused_for_through_an_agent_change
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

**Documentation checked on 2026-11-22**, each passage that names a changed module, for a statement the change made untrue: `docs/ARCHITECTURE.md`, `docs/INTERFACE.md`, `docs/interface-provenance.md`, `ROADMAP.md` and `.claude/rules/ui-areas.md`. None needed a change.

**Blind review, 2026-11-22, and what changed.** The review found two faults in the first build, where only a hand pick stopped the selector following. A refusal shown for sevoflurane stayed on screen after the follow moved the form to desflurane, so it read as desflurane's refusal. A bottle price the reader had typed, without pressing Set price, was replaced by the new agent's stored price without a word. The selector now follows the run's agent until the reader uses the form at all: picks an agent, types in a field, edits the date or presses Set price. This keeps triage's rule for an untouched form and extends "picked by hand" to every use, because each of these is the reader working on the agent the form names. No price or cost changes, so it is not put to the owner. Two tests fail before the change with `assert 'desflurane' == 'sevoflurane'`: `test_a_price_the_reader_is_typing_stays_with_its_agent_through_an_agent_change` and `test_a_refused_price_stays_beside_the_agent_it_was_refused_for_through_an_agent_change`.
