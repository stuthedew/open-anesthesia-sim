---
id: PL-R7C4
title: src/anesthesia_sim/app/qt_widgets.py and tools/contrast_check.py say SC 1.4.11's inactive-component exception was never read at the source, but PL-JX0Z records the project owner supplying W3C's Understanding document for SC 1.4.11 on 2026-09-07; check whether that text carries the exception and correct both if it does
status: untriaged
added: 2026-10-06
---

**Problem.** src/anesthesia_sim/app/qt_widgets.py and tools/contrast_check.py say SC 1.4.11's inactive-component exception was never read at the source, but PL-JX0Z records the project owner supplying W3C's Understanding document for SC 1.4.11 on 2026-09-07; check whether that text carries the exception and correct both if it does

**Found 2026-10-06** while closing `PL-CLW5`, which dated both sentences'
`w3.org` refusal (refused again at the CONNECT that day) and changed nothing
else in them. `PL-JX0Z`'s 2026-09-07 answer quotes the Understanding
document's Figure 38 from the PDF the project owner supplied; whether that
document also states SC 1.4.11's inactive-component exception, which both
sentences say nobody here has read, was not checked. If it does, the claim
both sentences rest on is wrong, and so is the reason they give for keeping
the transport button's edge at `MUTED` in both states.
