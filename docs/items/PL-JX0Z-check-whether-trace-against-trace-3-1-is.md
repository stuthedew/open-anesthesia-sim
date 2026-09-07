---
id: PL-JX0Z
title: Check whether trace-against-trace 3:1 is stricter than SC 1.4.11 requires, since it is the premise PL-GVXP's palette search rests on
status: untriaged
added: 2026-09-07
---

**Problem.** This project holds every pair of chart traces to 3:1 against *each
other*. `.claude/rules/ui-color.md` judgment 3 states it as arithmetic — six
traces cannot exceed $`21^{1/5}\approx1.84`$ pairwise, below SC 1.4.11's 3:1 —
and `docs/MODEL.md` § "The six compartment traces" rests its whole design on
the trace-against-trace matrix, whose worst pair is 1.01:1. `PL-GVXP` ran and
declined a palette search on that basis, and `tools/contrast_check.py` carries
a `TRACE_FLOOR` enforcing it.

A secondary source states that SC 1.4.11 asks a line graph's lines to clear
3:1 against the **background**, and that where they do not overlap they need
not contrast with **each other**. If that is what the standard says, this
project's bar is stricter than AA requires.

**Why it matters, and why it is not simply "we are being safe".** Two
directions, and they point opposite ways.

- If the bar is over-strict for the single-run chart, then `KNOWN_SHORTFALLS`
  is tracking a shortfall that is not one, `PL-W8DQ` is holding a slider track
  to a floor it need not meet, and a palette search that was declined as
  impossible may have been declined against the wrong requirement.
- If the bar is right, nothing changes and the reasoning is confirmed — which
  is worth having written down, because three items now cite the arithmetic as
  settled.

The stricter reading is clearly correct in at least one place regardless:
`PL-HLD5`'s branch comparison deliberately draws two curves of the same
compartment adjacent and at similar values, so those *do* overlap, and the
"where they do not overlap" carve-out does not reach them.

**Not a defect in `PL-GVXP`.** Everything that item measured is measured
correctly, and line style as the separating channel is right under either
reading — six dash patterns beat six hues for a dichromat whatever the
contrast bar says. What is in question is only whether the *palette* was held
to a requirement the standard does not impose.

**Where.** `.claude/rules/ui-color.md` judgment 3; `docs/MODEL.md` § "The six
compartment traces"; `tools/contrast_check.py` (`TRACE_FLOOR`,
`KNOWN_SHORTFALLS`).

**The route is the obstacle, and it is the known one.** The primary source is
W3C's Understanding document for SC 1.4.11. `w3.org`, `dequeuniversity.com`,
`digitala11y.com`, `wcag.com` and `accessibility.build` were each tried on
2026-09-07 and each returned `EGRESS_BLOCKED` from the proxy, so the claim
above is a search summary read at one remove and is explicitly *not* a finding.
`PL-XJ5P` carries the general gap. Reading this needs a route the session
container does not have — the project owner opening the page, most simply.

**Done when.** The Understanding document has been read at the source, and
either the trace-against-trace bar is restated with its actual justification
(a project decision to exceed AA, which is a legitimate answer and should say
so), or it is relaxed to what the standard requires and the three citing
places are corrected together.

**Found 2026-09-07** while recommending the channel assignment for `PL-HLD5`.
