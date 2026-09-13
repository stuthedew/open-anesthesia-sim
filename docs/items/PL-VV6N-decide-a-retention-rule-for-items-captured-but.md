---
id: PL-VV6N
title: Decide a retention rule for items captured but never worked
status: needs-decision
added: 2026-09-13
---

**Problem.** The capture rule files every finding, and nothing ever expires.
The question is whether the queue needs a forcing function that closes items
nobody will work.

**Decision needed.** Adopt an expiry/closure rule, or decide explicitly that
capture is unbounded and the open-backlog ratio is managed some other way.

**What the measurements say — an age-based rule is mis-calibrated today.**
Measured 2026-09-13: no item in this store has ever taken more than 14 days to
reach terminal, 58.7% close the same day they are filed, and the oldest open P3
is 20 days old. An age threshold in months would fire on nothing. The
never-worked-drop rate is 46 of 91 drops = 5.7% of all items ever created, so
capture noise is low.

**But the ratio is off professional norms.** Measured against live trackers via
the GitHub API, same day: microsoft/vscode 18,386 open of 253,380 filed (7.3%),
kubernetes/kubernetes 1,854 of 49,655 (3.7%), home-assistant/core 2,651 of
73,994 (3.6%). This store is 238 open of 814 filed = 29%. Those projects get
there by closing aggressively rather than by working everything: vscode has
49,403 issues closed as "not planned" (19.5% of all filings), and of its 2024
cohort 42.2% were closed not-planned against 9.0% still open. This store has
dropped 91 of 814 = 11.2%.

**The professional forcing functions are threshold-based, not age-based.**
VS Code's documented policy closes a `Backlog Candidates` feature request that
has not gathered 20 up-votes within 60 days. home-assistant/core auto-closes
after 90 days inactive plus a 7-day warning. Reinertsen's W7 is "The Principle
of WIP Purging: when WIP is high, purge low value projects" — deletion, not
better prioritisation.

**Counter-evidence, which is real.** Stale-bot adoption across 20 large OSS
projects cleared PR backlog but was followed by a considerable decrease in
active contributors (Wessel et al., TOSEM 2023). probot/stale is archived and
VS Code's own bespoke triage automation was archived 2025-11-14 — the tooling
is itself abandoned at a high rate. And on a solo project with no contributors
to lose, the offsetting cost is different: Masicampo & Baumeister (JPSP
2011;101(4):667-83) found unfulfilled goals cause intrusive thoughts and degrade
unrelated task performance, and that a specific written plan eliminates the
effect — which is an argument that capture is doing real cognitive work.

**Open question the data cannot settle.** 27% of the open set (64 items) is
`needs-decision` — owner-blocked, not worker-blocked. A retention rule aimed at
P3 would not touch these, and they may be the larger share of the problem.
