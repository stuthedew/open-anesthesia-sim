---
id: PL-NW76
title: Turn the 150,000-token session cap from a stopping rule into a starting budget
priority: P2
effort: S
status: done
classes: session-cost
verify: grep -qF 'check that budget before starting an item' CLAUDE.md && grep -qF 'externalize before handing off' CLAUDE.md && grep -qF 'at about 150,000 tokens' CLAUDE.md && python3 tools/doc_check.py check
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-16
closed: 2026-09-16
pr: 624
---

**Problem.** `PL-H253` capped session length at about 150,000 tokens and made
it a *stopping* rule — read `get_session` "at a natural break rather than
continuously", then hand off. A stopping rule fails in two ways at once, and
both were visible on the day it landed.

It overshoots by construction. The overshoot is bounded by the gap between
natural breaks, not by the cap, so the number cannot be held however willing
the session is. `PL-H253` records its own author at **176,689 tokens** when
they finally read it — 18% over, on the session that wrote the rule.

And it cuts across work in progress. Stopping on reaching a number means the
number arrives mid-item, and whatever is not on disk at that moment is gone.

**Why it matters.** The handoff toll is real but bounded, and the two halves
behave differently. Measured 2026-09-16: resident set 53,630 characters
(~13.4k tokens), session digest 3,242 characters (~800 tokens), plus the
harness prompt — roughly 20–25k tokens to bring a session back to zero, about
17% of the cap. That is cheap for item work, which this project externalizes
well: the item file, leading-id commits, `bin/docket flight`,
`docs/WORKING_NOTES.md`, the start digest. It is expensive for a design round,
whose product is the reasoning chain and which nothing writes down until
someone decides to.

**On the number itself, which this item does not change.** `PL-H253`'s first
three steps hold — resident share is 2.5–5.6%, so trimming is not the lever;
total length is; observed sessions ran 263k–519k. The fourth does not follow:
150,000 is about a third of what was observed rather than a measured knee, and
it sits at 15% of the 1,000,000-token window (`get_session`, `max_tokens`,
confirmed live).

The conservative figure survives anyway, on a better argument than the one
recorded. The benchmarks putting effective capacity at 60–70% of nominal
measure *retrieval*; this project stakes correctness on *instruction
adherence*, and LongGenBench and LIFBench both find adherence degrading with
length independently of retrieval skill — a model strong at long-input
retrieval still loses prompt adherence over length, worst on complex
multi-constraint instruction sets. A 768-line resident set is that case. So the
cap is defended here rather than re-derived, and no re-measurement is proposed:
the fix below is robust to whether 150,000 is the right figure, because
checking a budget before the spend is correct at 150k, 300k or 600k.

**Done when.** The rule in `CLAUDE.md` § "Session and tool-use efficiency"
reads as a budget checked *before starting an item* rather than a limit hit
while working — if the next item will not fit, hand off instead of starting —
with `externalize before handing off` as the fallback for an item that ran long
or a design round holding its reasoning in the conversation.
`docs/resident-instructions.md` records the reshape against the moment it now
governs. Project owner approved 2026-09-16.
