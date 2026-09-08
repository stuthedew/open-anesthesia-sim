---
id: PL-5CGK
title: chart_downsampling.py cites M4 but implements AM4, and the difference is a determinism guarantee
priority: P2
effort: S
status: dropped
classes: docs
feature: provenance
touches: src/anesthesia_sim/app/chart_downsampling.py, docs/references/README.md
added: 2026-09-04
verify: python3 tools/doc_check.py check && grep -q 'AM4' src/anesthesia_sim/app/chart_downsampling.py
closed: 2026-09-05
reason: Superseded by PL-8LXM, which deletes app/chart_downsampling.py, its tests and the M4 paper together with every citation of them. The gap this item records between what the module cites and what it computes is real, and it is preserved in PL-8LXM's brief as part of why that removal is of good work rather than of bad.
---

**Problem.** `app/chart_downsampling.py` states that it "implements **M4** as
published — Jugel U, Jerzak Z, Hackenbroich G, Markl V, ... 2014". That is
accurate about *what it selects* — Definition 2's four extremum tuples — and
incomplete about *how it computes them*. The paper's own formulation (its § 5,
Value Preserving Aggregation) scans the series twice and joins the aggregated
extreme back against the input to recover which tuple produced it. This
implementation does neither: `M4Aggregate` carries the sample *index*
alongside the extreme value, so one pass produces the tuple and its position
together.

That shape has a name and a citation. Kohn A, Moritz D, Neumann T, "DashQL —
Complete Analysis Workflows with SQL", arXiv:2306.03714 (the PDF's metadata
marks it a VGTC special-issue paper for TVCG), § 3.6.1, proposes it as
**AM4** — supplied by the project owner 2026-09-04, read at § 3.6.1 and § 5.
Their Figure 8 computes `min(x), arg_min(y,x), max(x), arg_max(y,x), min(y),
arg_min(x,y), max(y), arg_max(x,y)` per bin, which is `M4Aggregate`'s eight
quantities exactly.

**Why it matters.** Two reasons, and the second is the one with teeth.

*Provenance.* `PL-D9WD` argued that naming the algorithm is what makes the
chart auditable — "the chart implements M4 (Jugel et al. 2014)" can be checked
against a paper on disk, where "something M4-like" cannot. The same argument
applies one level down: a reader comparing this module against Jugel et al.'s
§ 5 will find a query with a join and a `DISTINCT` that this code does not
have, and nothing tells them the difference is deliberate and named.

*A guarantee the citation does not carry.* DashQL § 3.6.1 states that
`arg_min(a, b)` "selects an **arbitrary** attribute for a where b is
minimal". For a one-shot query that is harmless. Here it would be a defect:
`PL-Q197`'s fix is that a completed bucket chooses the same sample on every
frame, so an arbitrary tie-break would let drawn points move between frames
and re-patch the client — the exact failure that saturated the Flutter
process. This implementation resolves ties deterministically to the earliest
position (`_scan` compares with a strict `<` and `>`, `merge_m4_aggregates`
keeps the earlier on a tie), which is *stronger* than AM4 requires and is
currently written down nowhere.

That matters beyond documentation. `PL-011` (bound the controller's
concentration history) is the item most likely to consider moving this into a
store, and DuckDB — which DashQL names as providing `arg_min` — would satisfy
AM4 while silently dropping the tie-break guarantee.

**Whether this data is DashQL's pathological case, measured rather than
assumed (2026-09-04).** Their example for the original formulation is
`f(x) = 42`, a constant function, whose join "will then emit the entire input
relation". Run against the real model at a 0.1 s step, counting what that join
would emit against M4's promised four tuples per bucket:

| Run | Repeated values | Join emits | We draw |
| --- | ---: | ---: | ---: |
| Wash-in at 2%, 20 min | 0.0% | 1.0x | 188 |
| Two hours at 2% | 0.0% | 1.0x | 282 |
| Vaporizer never opened, 20 min | 100% | 32.4x | 188 |

So it is the *idle* run that is pathological, and only that one: with the
vaporizer closed every compartment sits at exactly 0.0 and the join returns
the whole relation. Any run with agent flowing has **no** ties at all — zero
across 12 000 and 72 000 samples on all six traces, comfortably inside the
"under one percent" both papers assume. An earlier draft of this item claimed
compartments go bit-identical at equilibrium; they do not, at two hours the
exponential approach still moves the last bits, and that claim is withdrawn.

None of it reaches this implementation, and for a structural reason rather
than a favourable-data one: no join means ties cannot multiply the output, so
188 points are drawn in the plateau case and 188 in the wash-in case. It
matters only for a future formulation that reconstructs a tuple by matching
on its value.

**Where.**

1. `src/anesthesia_sim/app/chart_downsampling.py` — the module docstring's
   algorithm section, and a sentence on the tie-break beside
   `merge_m4_aggregates` or `M4Aggregate`.
2. `docs/references/README.md` — a DashQL entry, if the PDF is filed. **Check
   its arXiv licence first**: that directory's README makes licence a per-file
   question and records that the M4 paper may stay only because VLDB publishes
   it CC BY-NC-ND. Do not assume an arXiv posting carries a redistributable
   licence.
3. `docs/MODEL.md` — its interface-boundary section names M4 as the selection
   the chart uses. That statement stays true and needs no change; the
   computation shape is a code concern, not a specification one.

**Done when.** The module names AM4 as what its aggregate shape is, with the
citation; the deterministic tie-break is stated as a requirement of this
application rather than left as an implementation accident; and the reference
entry exists or the licence check is recorded as the reason it does not.

**Closed against `PL-8LXM` on 2026-09-08.** The module that cited M4 while
implementing AM4 is deleted, so the provenance gap this item described has no
subject. The distinction it established is worth keeping findable, and it is:
Kohn A, Moritz D, Neumann T, "DashQL - Complete Analysis Workflows with SQL",
arXiv:2306.03714 § 3.6.1 names **AM4** for the one-pass form that carries the
sample index alongside the extreme value, which is what the deleted
`M4Aggregate` computed.
