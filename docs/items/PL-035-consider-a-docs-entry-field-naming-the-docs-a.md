---
id: PL-035
title: Consider a `**Docs.**` entry field naming the docs a task will touch
priority: P2
effort: S
status: needs-decision
classes: docs, infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, tools/doc_check.py
added: 2026-08-24
---

**Problem.** Close-out has to work out which documents a change could have
invalidated after the change is written. The session that captured the item
often already knew — it just had nowhere in the entry format to say so.
**Why it matters.** `tools/doc_check.py candidates` narrows the sweep from a
diff, but it only finds documents that already name something the diff
touched. A document that *should* mention a new feature and does not is
exactly what it cannot see, and is a failure mode that has happened here.
**Where.** `docs/PUNCH_LIST.md` (entry format), `tools/punch_list.py`
(`_check_entry`), `.claude/skills/punch-list/SKILL.md` (capture mode).
**Decision needed.** Whether an optional field earns its cost. Against: an
optional field that is usually omitted is noise, and a wrong guess at
capture time may be worse than no guess. For: it is free to write when the
capturing session already knows, and close-out reads it for nothing. Decide
also whether the checker should validate that the named paths exist, which
`doc_check.py`'s resolver already does for prose.
**Done when.** The field is either in the format spec and validated, or the
decision not to add it is recorded in "Archive" with its reason.
