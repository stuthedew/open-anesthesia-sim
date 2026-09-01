---
id: PL-1TPM
title: docket next ranks work the current milestone excludes, with no sign that it does
priority: P2
effort: S
status: done
classes: defect, infra
feature: planning-cadence
milestone: v0.2.8
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_plan.py
added: 2026-08-30
closed: 2026-08-30
commit: 1c75693
pr: 92
verify: uv run pytest subprojects/docket/tests -k "next and scope"
---

**Problem.** `docket next` ranks on priority, feature progress and in-flight
status. It does not read the roadmap, so it cannot know that the current step
excludes an item. Run today, its second and third suggestions are PL-F52R
(draw the MAC-awake reference band) and PL-NV9W (label the alveolar readout
end-tidal-equivalent) — and PL-F52R is inside v0.4.0's Required scope, which
`ROADMAP.md`'s "Explicitly out of scope for v0.3.0" excludes from the release
now being built.

Six items are in this position: PL-DHV7, PL-VM40, PL-F52R, PL-ZRSP, PL-R3KB
and PL-011 are all v0.4.0 scope, several are `P1`, and `docket next` presents
them as ready work with no qualification.

**Why it matters.** `docket wave` already computes the answer — it prints
`Beat  clear the gate` and lists the gate's open entries — but the two commands
do not talk, so the tool that ranks is blind to the tool that decides. A
session that follows the skill exactly reads `wave` first and is fine. A
session that runs `next` alone, or a reader skimming its output, is handed
milestone-blocked work as the second-best thing to do. That is the failure the
`Beat` line exists to prevent, reintroduced one command over.

It is also the case `PL-019F` describes from the other side: that item fixes
`CLAUDE.md`'s rule to answer at roadmap-step altitude, so the *session* asks
the right question. This item makes the *tool* stop offering the wrong answer.
Neither substitutes for the other, and this one is the cheaper guard because it
does not depend on an instruction being followed.

**Where.** `subprojects/docket/src/docket/plan.py` (the ranking);
`subprojects/docket/src/docket/roadmap.py` already parses the milestone
sections and the frozen gate list that would supply the exclusion.

**Approach.** Keep it on the decidable side. `roadmap.py` can already read
which milestone section an item id appears in; the current step is what `wave`
computes. So `next` can mark — not hide — an item whose id appears in a
milestone section later than the current step: one suffix on the line, in the
shape `next` already uses for `strongest model`. Marking rather than filtering
matters, because "is this really out of scope?" is a judgment and the prose
that answers it is not parseable; a suppressed item would be a verdict the
tool cannot support, while a marked one is a fact it can.

Do not attempt to infer scope from anything but an explicit id in a milestone
section. An item that is out of scope for a reason stated only in prose stays
unmarked, and that limitation belongs in `subprojects/docket/README.md`
alongside the concurrency one, which is honest in the same way.

**Found.** While testing what a from-scratch session would answer to "what
should we work on next" (2026-08-30). The top suggestion was right and
well-reasoned; the two beneath it were not startable.

**Done when.** `docket next` marks a suggestion whose id appears in a milestone
section the current step has not reached, the marking is derived from ids
rather than prose, and `subprojects/docket/README.md` records what the marking
cannot see.
