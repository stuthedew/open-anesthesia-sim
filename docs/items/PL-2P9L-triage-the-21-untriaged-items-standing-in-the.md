---
id: PL-2P9L
title: Triage the 21 untriaged items standing in the queue on 2026-09-19
priority: P2
effort: S
status: done
classes: infra
milestone: v0.4.29
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Seventeen from the 2026-09-19 triage pass** (`PL-2P9L`). Twenty-one items were untriaged that morning, and every one of them had been captured that same day. Classing an item is what makes it debt, so these arrive at this gate together and are declined together: `PL-245B`, `PL-28HG`, `PL-2DTK`, `PL-4FD2`, `PL-4HKS`, `PL-BX1C`, `PL-CNJH`, `PL-CWD4`, `PL-D1NT`, `PL-DK8Y`, `PL-QMC0`, `PL-R77L`, `PL-SZJ2`, `PL-WVJ0`, `PL-Y5JX`, `PL-YS9F` and `PL-ZPDM`. One of them, `PL-QMC0`, closed in `#708` hours later. It is left named here rather than removed, because this subsection records the disposition taken. An entry that was declined and then fixed anyway is still an entry that was declined. `PL-0VFF` is the open item for the fact that nothing here distinguishes the two. The three facts that the first thirty rest on apply to all seventeen. They were captured after the 2026-09-06 freeze. They are `P2` or `P3` and neither `safety` nor `science`. They sit wholly in the workflow lane: every `touches` path they declare is inside `docket.toml`'s `workflow_paths`, so none can affect a reader of the simulator.

> **The arithmetic above has reversed since it was written, and it now argues the same way harder.** The paragraphs at the head of this subsection defer on the ground that this gate "is not draining". Today it stands at 168 cleared of 175, with four entries left that it can clear. That premise is stale, but the conclusion it supported is not. Admitting these seventeen would take the clearable remainder from four to twenty-one. It would also move a milestone that is one beat from starting back behind five times the work it currently waits on. A gate one step from opening is the point at which "The gate is a snapshot, not a moving target" does the most work, not the least. The temptation to fold in the day's findings is strongest exactly when the list is nearly empty. Any of the seventeen whose *problem* predates the freeze belongs on the list rather than here. `check_gate_reentries` decides that, not this paragraph.
