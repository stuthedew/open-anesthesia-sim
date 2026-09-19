---
id: PL-28HG
title: GitRunner._drop marks a root permanently unbatchable, so one transient cat-file fault costs every later blob in the command a separate git show process
priority: P3
effort: S
status: needs-decision
classes: perf, session-cost
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_git_runner.py
added: 2026-09-19
---

**Problem.** GitRunner._drop marks a root permanently unbatchable, so one transient cat-file fault costs every later blob in the command a separate git show process

**Found while fixing `PL-MM7F`** (the memo storing a failed git call), which is
the same shape one layer over: a single transient fault recorded for the rest of
the command instead of being retried.

`_drop` in `subprojects/docket/src/docket/vcs.py` adds the root to
`_unbatchable` before closing the dead process, and `_process` returns `None`
for any root in that set. So every path that drops a batch - an `OSError`
writing to stdin, an empty header, a header this cannot split into three
fields, an unreadable body - disables `git cat-file --batch` for that root for
the remainder of the command.

**Why it matters.** It costs processes and never correctness, which is exactly
why it is filed rather than fixed alongside `PL-MM7F`: the fallback is `git
show` through `_run_git`, the process the batch replaced, giving the same
answer. Measured on this repository 2026-09-19, one `bin/docket digest
--profile` folded 21 blobs into the batch out of 110 processes, so a fault on
the first blob turns a 110-process digest into roughly 131. Bounded and modest.
The two defects look alike and only one of them can mislead a reader, so
keeping them apart is the point.

**Decision needed.** Whether the permanence is right at all, and it is a real
question rather than an oversight to reverse. Retrying a genuinely broken
`cat-file` once per blob would be worse than the current behaviour, so anything
here has to separate a transient hiccup from a repository the batch cannot
serve. Three candidates: leave it as it stands and record why; retry once on
the first drop only; or retry whenever the previous drop was more than N blobs
ago. Do not simply remove the `_unbatchable.add`.

**Done when** the question above is answered in this file, and - if the answer
is to change the behaviour - a test drives one drop against a root whose batch
then works and asserts the process count.
