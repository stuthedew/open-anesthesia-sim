---
id: PL-JX0Z
title: Check whether trace-against-trace 3:1 is stricter than SC 1.4.11 requires, since it is the premise PL-GVXP's palette search rests on
priority: P2
effort: S
status: done
classes: docs, ux
feature: presentation-safety
touches: .claude/rules/ui-color.md, docs/MODEL.md
added: 2026-09-07
closed: 2026-09-07
pr: 433
verify: python3 tools/rules_paths_check.py && python3 -c "import pathlib,sys; q='little overlap with other lines they do not need to contrast with each other'; sys.exit(0 if all(q in ' '.join(pathlib.Path(f).read_text().split()) for f in ('.claude/rules/ui-color.md','docs/MODEL.md')) else 1)"
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

**Answered 2026-09-07 at the source.** The project owner supplied the W3C
Understanding document for SC 1.4.11 as a PDF, after the five routes recorded
above were each refused by the egress proxy.

**The secondary source was accurate, and the answer has a condition on it that
changes the conclusion.** The Understanding document's line-graph example
(Figure 38) says, in terms:

> The lines should have 3:1 contrast against their background, but as there is
> little overlap with other lines they do not need to contrast with each other
> or the graduated lines.

Its "Graphical Objects" section makes *"each line in a graph"* a graphical
object in its own right, and adds that *"Gestalt principles such as the 'law of
continuity' can be used to ignore minor overlaps with other graphical objects
or colors"*.

So SC 1.4.11 does **not** require trace-against-trace 3:1 — but both carve-outs
are conditioned on an absence of overlap, and **this chart does not have it.**
Six compartment traces start together at zero, converge toward equilibrium, and
cross through wash-in and washout; the overlap is the lesson rather than an
accident, and it is neither "little" nor "minor". The exemption that would
excuse pairwise separation is one this chart does not qualify for.

**Which makes the bar better founded than it was, not weaker.** It stands as a
deliberate exceedance whose justification is now the standard's own condition
rather than an assertion about what the standard demands.

**Two of the three citing places were already correct, and this is worth
recording because the item assumed otherwise.**

- `docs/MODEL.md` § "Color contrast, and the standard this interface is held to"
  already listed pairwise separation under the bars held *above* AA, and already
  said "SC 1.4.11 only asks 3:1 against the *background*". It gains the
  quotation and the overlap condition, which strengthen an argument that was
  already sound.
- `tools/contrast_check.py` was already right in code: `below_trace_floor`
  measures each trace against `PANEL` and nothing else, and the pairwise matrix
  is reported without failing anything. The tool enforces exactly what the
  criterion requires.
- `.claude/rules/ui-color.md` judgment 3 was the loose one. It read "Both are
  below SC 1.4.11's 3:1", which states the pairwise figures against the
  criterion as though the criterion asked for them. Corrected, with the
  condition and the quotation, and with an explicit instruction not to relax the
  bar by citing the criterion nor defend it by misquoting it.

**Not a defect in `PL-GVXP`, as this item predicted.** Every figure it measured
is measured correctly, the palette search was declined for a reason that still
holds, and line style beats hue for a dichromat under either reading.

**The PDF is not added to `docs/references/`.** The canonical URL is public and
stable — <https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html> —
so a citation resolves for any reader who is not inside a session container,
and the directory exists for documents a reader cannot otherwise reach.
