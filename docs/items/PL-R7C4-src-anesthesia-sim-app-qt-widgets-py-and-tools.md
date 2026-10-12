---
id: PL-R7C4
title: src/anesthesia_sim/app/qt_widgets.py and tools/contrast_check.py say SC 1.4.11's inactive-component exception was never read at the source, but PL-JX0Z records the project owner supplying W3C's Understanding document for SC 1.4.11 on 2026-09-07; check whether that text carries the exception and correct both if it does
priority: P3
effort: S
status: ready
classes: docs
touches: src/anesthesia_sim/app/stylesheets.py, tools/contrast_check.py
added: 2026-10-06
payoff: the reason given for the transport button's disabled-state edge rests on what WCAG actually says, read at W3C's source, rather than on its never having been read
verify: ! grep -qF 'inactive-component wording has never' src/anesthesia_sim/app/stylesheets.py && ! grep -qF 'was **not** read at the source' tools/contrast_check.py && ! grep -qF 'check_disabled_states_are_the_style_s' src/anesthesia_sim/app/stylesheets.py
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

**Re-confirmed 2026-10-11:** `www.w3.org` is still refused at the CONNECT (403).
The W3C's own source repository answers through GitHub:
`https://raw.githubusercontent.com/w3c/wcag/main/understanding/21/non-text-contrast.html`
returned 200, which is a route to the same document `PL-JX0Z` never had. The
supplied PDF was not added to the repository (`PL-JX0Z`), so it cannot be
re-read here.

**Why it matters.** Both sentences give a reason for a design choice - the
transport button's edge staying `MUTED` in both states - that rests on a claim
about the source. If the Understanding document states the inactive-component
exception, the claim is wrong. The choice may well survive, since meeting 3:1
outright needs no exception, but its stated reason would not.

**Generator check.** An instance of `PL-CLW5`'s fact (whether a host answers is
a dated probe, not a standing fact), filed in the commit that closed that head;
a one-off follow-up, since the sentence is dated and what remains is reading the
source.

**Done when.** The Understanding document for SC 1.4.11 has been read at the
W3C's source, and both sentences say, dated and with that URL, what it states
about inactive components; if it states the exception, the reason given for the
`MUTED` edge is restated so it does not rest on the exception being unread.

**Also in the same docstring, found 2026-10-11 by the triage pass:**
`transport_button_stylesheet`'s docstring (now in `app/stylesheets.py`) names
`check_disabled_states_are_the_style_s`, since renamed
`check_authored_disabled_colours_are_measured` in `tools/contrast_check.py`.
The rewrite above corrects it in passing.

**Moved, 2026-10-12.** `PL-Y4YX` moved `transport_button_stylesheet`, with
this docstring verbatim, from `app/qt_widgets.py` into `app/stylesheets.py`,
so `touches:` and `verify:` now name that file; read at the old path, the
command would have passed with none of this work done. Both sentences and the
stale check name are as the brief describes, one file over.
