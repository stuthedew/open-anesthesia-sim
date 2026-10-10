---
id: PL-L4X3
title: docket status, show and next answer a gate entry's placement from roadmap.Scope, which carries no Wave.unread, so an id on a gate entry the list walker declines by name - carried on from the margin - is reported placed by no section at exit 0, where wave, picks, check and the digest each name the decline; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket status, show and next answer a gate entry's placement from roadmap.Scope, which carries no Wave.unread, so an id on a gate entry the list walker declines by name - carried on from the margin - is reported placed by no section at exit 0, where wave, picks, check and the digest each name the decline; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's render, plan and claims modules.
`plan.placement_line` (for `docket show`'s plan line), `plan._placed` (for
`docket next`'s reasons) and `plan.placement_mark` with
`render.format_status` and `render._plan_header` (for `docket status`) answer
from `roadmap.Scope`, which has no field for `Wave.unread`. When
`list_entry_lines` declines a gate entry carried on from the margin - a lazy
continuation line (CommonMark 0.31.2 § 5.2) - the entry ends before that line,
and any id on it drops out of `Scope.current` and `Scope.later`.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, on docket's picks test fixture with one gate entry carried on from the
margin, against markdown-it-py 4.2.0 and cmark-gfm 0.29, which read one list
item naming both ids:

```text
- PL-B2B2 and
PL-Z9Z9 (S) entry PL-B2B2
```

`docket wave` exits 1 naming the line; `docket status` exits 0 listing the
second id unmarked (placed by no section, per its legend); `docket show` exits
0 with a plan line saying no section places it; `docket next` exits 0 with the
same reason. Nothing on any of the three says a list went unread. Latent:
`wave` over `ROADMAP.md` reads every entry whole today, and `doc_check` fails
the form under `make check`; a session that runs the three on an edited
roadmap before `make check` is told a wrong placement.

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-GMR6`'s fix left, whose brief says
the
decline reached check, wave and the digest and stopped there; its fix reached
picks.

**Done when.** `status`, `show` and `next` name the plan's unread entries as
`wave` and `picks` do and exit 1 where any went unread; a test pins each.
