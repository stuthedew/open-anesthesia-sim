---
id: PL-MTHC
title: A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main
status: untriaged
added: 2026-09-27
---

**Problem.** A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main

**Evidence, 2026-09-27.** `0207afd7` recovered `PL-8ZGY`'s file onto
`claude/cool-meitner-pjnueb` from `claude/pl-w40l-kidkwe` while `#1199` was
still open there, so two branches each held a copy. `9d71a82c` corrected the
copy on `#1199`'s branch, with the owner's agreement; `#1199` merged as
`30820c98`; `82f71f2a` resolved the add/add conflict that followed by keeping
the other branch's copy whole; and `#1210` (`887fd223`) then put the
uncorrected brief on `main`. Every check passed throughout. Add/add conflicts
on item files recur - `PL-KBFN`, `PL-8KPD` and `PL-MQH0` each work around one -
so the triage that takes this asks whether one mechanism explains them.
Restored on `claude/pl-8zgy-restore-brief`.
