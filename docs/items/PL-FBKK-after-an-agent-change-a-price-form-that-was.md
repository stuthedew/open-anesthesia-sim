---
id: PL-FBKK
title: After an agent change, a price form that was already open in the agent cost View still has the earlier agent selected
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-11
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
