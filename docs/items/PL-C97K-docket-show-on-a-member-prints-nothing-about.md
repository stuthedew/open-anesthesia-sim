---
id: PL-C97K
title: docket show on a member prints nothing about the head whose root-cause-of names it, so a session opening a member cannot see it is explained by a generator
priority: P2
effort: S
status: ready
classes: defect
feature: generator-heads
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
verify: grep -q 'def test_show_names_the_generator_that_explains_a_member' subprojects/docket/tests/test_cli.py
---

**Problem.** docket show on a member prints nothing about the head whose root-cause-of names it, so a session opening a member cannot see it is explained by a generator

**Where.** `bin/docket show <id>` prints the item's own front matter and
brief. The head that explains it is recorded on the head alone:
`root-cause-of:` in `subprojects/docket/src/docket/model.py` is read by
`subprojects/docket/src/docket/plan.py` for ranking and by
`subprojects/docket/src/docket/checks.py` for validity, and nothing prints the
reverse edge. Observed 2026-09-19 on `PL-8LDF`, a member of `PL-4FBP`: `show`
says nothing about the head.

**Why it matters.** A session that reaches a member by name - the way the
project owner usually starts one - works it as an ordinary item while a
generator above it is still being decided, which is the one-at-a-time
patching the field exists to stop. The head's decision can re-scope or drop
the member, and the session cannot see that from the member.

**Done when.** `bin/docket show <id>` on an item that some head's
`root-cause-of:` names prints that head, with its title and status, and a
test under `subprojects/docket/tests/` covers it.
