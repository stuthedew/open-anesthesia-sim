---
id: PL-2P9L
title: Triage the 21 untriaged items standing in the queue on 2026-09-19
priority: P2
effort: S
status: done
classes: infra
touches: docs/items, ROADMAP.md
added: 2026-09-19
closed: 2026-09-19
pr: 710
verify: ! grep -l '^status: untriaged' docs/items/PL-0QRP-*.md docs/items/PL-245B-*.md docs/items/PL-28HG-*.md docs/items/PL-2DTK-*.md docs/items/PL-2P9L-*.md docs/items/PL-4FD2-*.md docs/items/PL-4HKS-*.md docs/items/PL-BX1C-*.md docs/items/PL-CNJH-*.md docs/items/PL-CWD4-*.md docs/items/PL-D1NT-*.md docs/items/PL-DK8Y-*.md docs/items/PL-JF5Z-*.md docs/items/PL-QMC0-*.md docs/items/PL-R77L-*.md docs/items/PL-SZJ2-*.md docs/items/PL-WVJ0-*.md docs/items/PL-Y5JX-*.md docs/items/PL-YS9F-*.md docs/items/PL-ZPDM-*.md
---

**Problem.** Triage the 21 untriaged items standing in the queue on 2026-09-19

**Why it matters.** An untriaged item is invisible to `bin/docket next`, which
ranks on `priority`, and absent from `bin/docket gate`, which counts debt by
`classes` and `status`. Twenty-one of them is a second queue nobody reads -
`docket.toml`'s `untriaged_stale_days = 14` is the standing judgment that this
state is a defect rather than a backlog. All twenty-one were captured on
2026-09-19, so none is stale yet; the number is what makes the pass worth a
commit of its own.

**Filed before the work, not after.** `CLAUDE.md`'s housekeeping rule: every
in-flight guard this project has matches a `PL-` id, so a triage pass carrying
none reads as nobody's work to `flight`, `show`, `next` and `concurrent` alike,
and keeps reading that way after the commit has landed.

**Done when.** Every item this pass took carries `priority`, `effort`, `classes`
and `touches`, sits at a status past `untriaged`, and satisfies `bin/docket
check`; and the items left untriaged are the ones another session is demonstrably
holding, named in the reply with the branch or session that holds them.

**The pass owed the gate a disposition, and that is why `ROADMAP.md` is in
`touches`.** Classing an item is what makes it debt, so triaging seventeen of
the nineteen into `defect`, `perf` or `needs-decision` turned them into open
debt that v0.5.0's frozen gate said nothing about, and
`tools/doc_check.py`'s disposition advisory failed `make check` on exactly
those seventeen ids. Verified against `origin/main`'s copy of `docs/items/`
first: clean there, so the failure was this pass's own and not inherited. They
are declined into the existing `### Declined to Gate 2 …` subsection - the
checker reads only the first one after the gate heading, so a second would have
orphaned the 66 dispositions already there - and `check_gate_reentries` fired on
none of them, so none qualifies on presence.
