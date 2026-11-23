---
id: PL-JMMB
title: Every Projects thread appends its no-guard-hooks paragraph to the end of PL-CR81, so two open pull requests conflict on that file whenever both threads record one: on 2026-11-22 #2205 met the conflict three times in 40 minutes
priority: P3
effort: S
status: dropped
classes: defect
feature: projects-trial
touches: docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md, .claude/skills/docket/modes/coordinator.md
added: 2026-11-22
closed: 2026-11-23
reason: the premise is gone: #2207 (PL-4J4H, 2026-11-22) changed coordinator.md so a thread with no guard hooks files a new item instead of appending to PL-CR81, and no paragraph has been appended since
---

**Problem.** Every Projects thread appends its no-guard-hooks paragraph to the end of PL-CR81, so two open pull requests conflict on that file whenever both threads record one: on 2026-11-22 #2205 met the conflict three times in 40 minutes

**Found 2026-11-22.** Each thread that starts without the repository's guard
hooks records one dated paragraph at the end of `PL-CR81`, as
`.claude/skills/docket/modes/coordinator.md` asks. Four threads did so on
2026-11-22, and the pull request for the feature registry had to resolve a
merge conflict in that file three times, each time a paragraph from another
thread landed first. The paragraphs also repeat one finding, since the cause
has not changed since the 2026-11-14 paragraph. A fix could count the
instances in one line, or record each in a file per thread.

**Generator check.** A one-off: a rule that asked every thread to append to one file, since replaced.
