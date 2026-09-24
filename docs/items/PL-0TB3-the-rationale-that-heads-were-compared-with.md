---
id: PL-0TB3
title: The rationale that heads were compared with nothing, so one record got a head per reader, is written out in five docstrings and the docket README; the apparatus standard names restated prose as bloat
priority: P3
effort: S
status: ready
classes: docs
feature: generator-identification
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md
added: 2026-09-24
payoff: the reason heads carry a misread: line is kept true in one place instead of six
verify: ! grep -rqF --include=*.py 'one head at a time' subprojects/docket/src/docket && ! grep -rqF --include=*.py 'head per reader' subprojects/docket/src/docket
---

**Problem.** The rationale that heads were compared with nothing, so one record got a head per reader, is written out in five docstrings and the docket README; the apparatus standard names restated prose as bloat

**Premise re-checked at triage, 2026-09-24.** The rationale that triage
compared each new item with one head at a time, so one record got a head per
reader, is written out at six sites, about 48 lines between them:

- `Item.misread`'s comment in `model.py`
- `overlaps` in `plan.py`
- `format_clusters` in `render.py`
- `_check_misread` in `checks.py`
- `cmd_generators` in `cli.py`
- `subprojects/docket/README.md` § "What the front matter is, exactly", whose
  paragraph nearly repeats `model.py`'s word for word

`grep -rn 'one head at a time'` and `'head per reader'` between them find all
five source copies. The sentence in `.claude/rules/apparatus-standard.md`
names "prose restating what a command already prints" as bloat, which is one
step from prose restating prose. The case for the cut is the duplication
itself.

**Why it matters.** Each copy is a sentence the next change to the mechanism
has to find and keep true. A stale copy in one docstring is the drift
`.claude/rules/citation-drift.md` says gets found one file at a time and filed
as an item.

**Done when.** The rationale is stated once, in the README section above. Each
source site keeps at most a clause pointing there or naming `PL-5MYR`, and no
source file under `subprojects/docket/src/docket/` restates it.

**Generator check.** A one-off. It was written by one session, `PL-5MYR`'s, at
each function that session touched, and no head's `misread:` states a fact
this misreads. The closed-head paragraph written three times by the same
commit is the same shape. That is noted here, and not added to this item's
scope.
