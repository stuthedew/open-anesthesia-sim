---
id: PL-YTDN
title: Rename the nine item files whose slug no longer matches their title, now that docket check names them
status: untriaged
added: 2026-09-13
---

**Problem.** Rename the nine item files whose slug no longer matches their title, now that docket check names them

Measured 2026-09-13, on the tree that closed `PL-3833`: nine of 810 item
files carry a slug their title no longer generates — `PL-0VFF`, `PL-5N7T`,
`PL-6194`, `PL-68XK`, `PL-DZFJ`, `PL-K9HV`, `PL-TTMF`, `PL-XQRK`, `PL-ZX12`.
`bin/docket check` now names all nine on one advisory line; this item is the
pass that discharges it.

**Why it is a separate item.** `PL-3833` deliberately stopped at reporting.
Its own 2026-09-08 addendum records why: a rename arriving as a side effect
of an unrelated command made `PL-36R4` a rename-against-edit conflict for
whoever merged second, so the safe split is to report the drift and leave the
rename to a session that has checked who else holds the file. Four of the
nine (`PL-0VFF`, `PL-6194`, `PL-DZFJ`, `PL-ZX12`) are open Gate 1 entries, so
this wants a moment when no gate session is running.

**Done when.** The nine files are renamed with `git mv` to the name
`docket.store.filename_for` writes, the advisory is silent, and `make check`
passes. Worth asking at that point whether the check should be promoted from
an advisory to an error, which is only safe once the count is zero.
