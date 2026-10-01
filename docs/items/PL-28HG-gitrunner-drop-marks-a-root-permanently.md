---
id: PL-28HG
title: GitRunner._drop marks a root permanently unbatchable, so one transient cat-file fault costs every later blob in the command a separate git show process
priority: P3
effort: S
status: done
classes: perf, session-cost
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_git_runner.py
added: 2026-09-19
closed: 2026-10-01
pr: 1266
verify: uv run pytest subprojects/docket/tests/test_git_runner.py && grep -q 'Decision, 2026-10-01: leave the permanence' docs/items/PL-28HG-gitrunner-drop-marks-a-root-permanently.md && grep -q 'PL-28HG' subprojects/docket/src/docket/vcs.py
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

## Decision, 2026-10-01: leave the permanence as it stands

Taken by the session working the item, on the owner's 2026-10-01 request to
work the session-cost items; its blast radius is one internal structure, so it
is a session's call rather than the owner's (rule 14).

**What would make this wrong.** A retry is worth building only if drops happen
in normal use *and* a fresh `cat-file --batch` on the same root would then
serve. Retry-once costs one extra process plus one failed blob per command
where the fault is persistent, and saves about 20 where it is transient, so it
breaks even at roughly one transient drop per twenty persistent ones - but both
sides multiply a drop rate, and the build and upkeep (a counter beside
`_unbatchable`, a test, the docstring) is paid whatever that rate is.

**The count.** With `_drop` and `_blob` instrumented and nothing else changed,
15 runs of `bin/docket digest --no-fetch` and one each of `flight`, `next` and
`stranded` on this repository dropped the batch **0 times in 638 blob reads**.
The one drop this repository has ever had on record was deterministic, not
transient: the `missing` header before `PL-0J9K`'s parser read it, pinned by
`test_a_missing_blob_does_not_cost_the_batch_for_the_rest_of_the_command`. A
retry there would have dropped again on the next absent blob.

**Why the permanence is the right default, not merely a cheap one.** Every path
into `_drop` is one of two kinds. A header or body this parser cannot read is a
protocol shape, and it recurs on the same root, so a retry spends a process to
learn the same thing. A write or read failing is the child having died, and
within one command of a second or two that is an environment killing processes
(memory pressure, a signal, a git that cannot run), which a fresh child
inherits. Neither kind is the transient hiccup a retry pays for, and the
fallback is `git show`, the process the batch replaced, with the same answer.
The ceiling stays where the brief measured it: one fault on the first blob
turns about 110 processes into about 131, and costs no correctness.

**What would reopen it.** A drop seen in normal use. `--profile` already shows
one without new instrumentation: its "the blob batch folded N" line falls short
of the `show` row's reads, and `show` starts spawning processes. One such
observation not traceable to a deterministic header shape is the evidence for
retry-once on the first drop, the cheaper of the two retry candidates.
