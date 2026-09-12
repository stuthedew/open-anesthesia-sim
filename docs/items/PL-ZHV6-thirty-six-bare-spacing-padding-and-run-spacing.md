---
id: PL-ZHV6
title: Thirty-six bare spacing, padding and run_spacing literals remain in simulation_view.py because naming them one by one would produce value-named constants; they need a designed spacing scale, which is the interface pass's work
status: dropped
added: 2026-09-08
closed: 2026-09-12
reason: Absorbed by PL-L9RD. This item's own statement of the problem is that the thirty-six literals need a designed spacing scale rather than one-by-one naming, and that this is the interface pass's work; PL-L9RD is that pass and names spacing rhythm among the decisions it makes once. The literals are in app/simulation_view.py, which PL-25KS replaces, so naming them now would be work done twice on a file being deleted.
---

**Problem.** Thirty-six bare spacing, padding and run_spacing literals remain in simulation_view.py because naming them one by one would produce value-named constants; they need a designed spacing scale, which is the interface pass's work
