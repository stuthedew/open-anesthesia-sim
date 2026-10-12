---
id: PL-QNHZ
title: verify.changed_paths and vcs.working_paths each list the checkout's uncommitted paths, by status --porcelain and by diff HEAD plus ls-files, and a staged edit whose working copy is restored to HEAD is listed by one only - PL-8HSX measured it and kept the pair
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: docket answers which paths a checkout changed by one reading
verify: grep -q 'def test_a_staged_edit_restored_in_the_working_copy_is_listed' subprojects/docket/tests/test_vcs.py
---

**Problem.** verify.changed_paths and vcs.working_paths each list the checkout's uncommitted paths, by status --porcelain and by diff HEAD plus ls-files, and a staged edit whose working copy is restored to HEAD is listed by one only - PL-8HSX measured it and kept the pair

- `verify.changed_paths` reads `status --porcelain -z`; `vcs.working_paths` reads `diff --name-only HEAD` and `ls-files --others`. On a staged edit whose working copy was restored to HEAD (porcelain `MM`), verify lists it and working_paths does not. `PL-8HSX` (done) measured this case and kept both readers.
- `tools/doc_check._changed_paths` is a third, diffing two-dot against the working tree; `PL-X229` (ready) holds that half.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** One function lists a checkout's changed paths for both, and a test pins the `MM` case.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
