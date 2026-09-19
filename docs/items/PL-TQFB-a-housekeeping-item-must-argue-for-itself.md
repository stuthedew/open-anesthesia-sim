---
id: PL-TQFB
title: A housekeeping item must argue for itself: docket check demands Problem, Why it matters and Done when at any status past untriaged, so 22 triage-pass items carry 1,127 lines of which 12 repeat the same rationale and only 2 carry a finding
priority: P3
effort: S
status: needs-decision
classes: infra, docs
touches: subprojects/docket/src/docket/checks.py, .claude/skills/docket/SKILL.md, CLAUDE.md
added: 2026-09-19
---

**Problem.** A housekeeping item must argue for itself: docket check demands Problem, Why it matters and Done when at any status past untriaged, so 22 triage-pass items carry 1,127 lines of which 12 repeat the same rationale and only 2 carry a finding

**Where it comes from.** The project owner, 2026-09-19, on watching `PL-CSV0`
be filed: "Why does triage create a PL? That seems pointless to me... open a PL
saying we are triaging because it's bad to not be triaged seems pointless and
wasteful. Isn't that self evident?"

**The id is not the waste, and two mechanisms say so.** Neither is
bookkeeping, and both fail closed:

1. `tools/branch_id_check.py` refuses a branch in the `claude/*` namespace that
   is ahead of the default base and carries no `PL-` id in its name or at the
   front of any commit subject. Every session branch in this project is
   harness-generated `claude/*`, so an unfiled housekeeping pass is a branch
   that fails `make check` and CI outright.
2. A triage pass's diff is confined to `docs/items/`, which
   `branches_in_flight` deliberately refuses to read as work - otherwise every
   capture commit would take startable items out of `bin/docket next`
   (`PL-X3WZ`). The only thing that raises the in-flight mark for such a pass
   is an item whose own `touches` never leaves `docs/items/`, which
   `branches_in_flight` reads off the item rather than off the commit
   (`PL-7790`). No item, no mark. `PL-N1JK` is what that costs: two triage
   passes on one item on 2026-09-06, invisible to each other however carefully
   each fetched, and the merge discarded one of two identical answers.

**The brief is the waste, and here is the count.** `docket check` requires
`**Problem.**`, `**Why it matters.**` and `**Done when.**` at any status past
`untriaged`, so every housekeeping pass writes an argument for why the
housekeeping was worth doing. Measured over the store on 2026-09-19:

```
items titled "Triage ..."                                    22
their combined length                             1,127 lines  (~51 each)
repeating the same rationale
  ("invisible to bin/docket next", "a second queue nobody reads")  12 of 22
carrying any finding beyond the pass itself                    2 of 22
```

Twenty of twenty-two carry nothing a later session needs. The rationale they
restate is already written once, resident, in `CLAUDE.md`'s housekeeping rule -
so the requirement is making each pass re-derive a sentence every session has
already loaded.

**What would make this proposal wrong**, per
`.claude/rules/expert-review.md`: if the briefs being suppressed carried real
content. They do not, at 2 of 22 - and both survivors stay legal under every
option below, since each would *permit* a short brief rather than forbid a long
one. `PL-CSV0`'s own brief is one of the two, carrying three premises checked
against the tree, and it is the shape worth protecting.

**Decision needed.** Which of three, and they are not equivalent:

1. **Exempt the shape from the three-section requirement** - a `housekeeping`
   class, or a `docket new --housekeeping` flag, that `checks.py` reads to skip
   `**Why it matters.**` and `**Done when.**`. The item keeps its id, its
   `touches` and its `verify:`, and both mechanisms above keep working. Roughly
   one branch in `checks.py` and one line in the skill. Takes a pass's item
   from ~50 lines to ~5.
2. **Point the requirement at a standing rationale** - accept a brief that
   cites `CLAUDE.md`'s housekeeping rule instead of restating it. Same saving,
   one more indirection, and it leaves the sections present but empty of
   argument, which is the shape `PL-D188` already reports as an item with no
   brief.
3. **Drop the item entirely** - widen `branch_id_check`'s release exemption to
   cover a `Triage: ...` subject, and let housekeeping carry no id. This is the
   full-strength version of the question as asked. It gives up the in-flight
   mark, which is the half that is load-bearing, and reopens `PL-N1JK`.

Route 1 is the recommendation: it removes the cost the owner identified and
keeps the two properties that are not what they were objecting to.

**Why it matters.** At 22 items and counting, this is a recurring tax on the
one kind of work the project does most often, and it is paid at the worst
moment - a housekeeping pass is short, and the brief can be the larger half of
it. It also teaches the wrong thing: a session that has written "an untriaged
item is invisible to `bin/docket next`" for the twelfth time is a session
learning that briefs are a formality, which is the habit that produces a thin
brief on an item where the brief was the point.

**Done when.** A housekeeping pass can file its item without arguing for the
category, the two mechanisms above still see it, and the existing 22 are left
alone - rewriting closed items would spend more than the rule saves.
