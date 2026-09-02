---
id: PL-21GS
title: "Readout 4's zeros were measured on a blind instrument: stranded could not read the refs a shallow clone truncated"
status: untriaged
feature: planning-cadence
touches: docs/items/
added: 2026-09-02
---

**Problem.** `PL-SZ56`'s readout 4 is `bin/docket stranded`, and its t=0 value
and every interim reading up to 2026-09-02 were taken in a shallow container.
`stranded` is bounded by the refs the checkout holds — it says so itself, "a
branch not fetched here was not read, so this is bounded by what has been" —
and a shallow clone truncates some of them. The readings were therefore
`0 of what could be seen`, not `0`.

Landing `PL-K2ZK` made the difference visible within one session. Before the
deepening, `stranded` reported across **6** branch refs and found nothing;
after it, across **7**, and found `PL-8DJ7` on
`origin/claude/pl-prhn-bug-w4eq4j`.

**Why it matters, and what it does not change.** It does not change the
verdict. That branch had a commit 22 minutes old at the time of reading, and
readout 4's amended threshold excludes a branch with a commit in the last 48
hours precisely because a live session's branch is expected there. Readout 4
passes.

What it changes is how strongly the *earlier* zeros may be stated. They are
weaker evidence than the ones taken after `PL-K2ZK`, and a close-out that
reads five identical zeros as five identical measurements is overstating four
of them. This is the same class of defect readout 3 had — an instrument whose
answer was bounded by something the reading did not mention — found the same
day, and worth saying once rather than twice.

**Where.** A sentence in the close-out's readout 4, in
`docs/releases/v0.3.0.md`, or a stated confound in
`docs/items/PL-SZ56-assess-the-v0-3-0-loop-trial-against-its-pre.md`
alongside the two already recorded there.

**Not an amendment, and deliberately not filed as one.** `PL-SZ56`'s
threshold is unchanged and should stay unchanged: this narrows nothing and
relaxes nothing, it only says what the instrument could see when each reading
was taken. Recording it as a confound is the honest disposition; changing the
readout again, twice in one day, on a pre-registered assessment, is not.

**Done when.** The close-out states that readout 4's pre-`PL-K2ZK` readings
were bounded by the refs a shallow checkout held, names the 6-to-7 ref change
and `PL-8DJ7` as the worked example, and says the post-deepening readings are
the stronger ones.
