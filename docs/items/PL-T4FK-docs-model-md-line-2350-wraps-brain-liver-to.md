---
id: PL-T4FK
title: docs/MODEL.md line 2350 wraps '+ brain + liver' to the margin, so CommonMark renders it as a bullet reading 'brain + liver is 3,820 of 6,480 ml/min - 59.0%', which gives the kidney + heart + brain + liver sum to two organs (the wrapped-marker shape PL-DSMK fixed in ROADMAP.md)
priority: P1
effort: S
status: ready
classes: docs, science
feature: prose-renders-as-written
touches: docs/MODEL.md
added: 2026-10-04
payoff: the rendered specification gives the 59.0% share of cardiac output to the four organs it belongs to, so the finding it supports reads as stated
verify: ! grep -qE '^ *\+ (heart|brain|liver) ' docs/MODEL.md
---

**Problem.** docs/MODEL.md line 2350 wraps '+ brain + liver' to the margin, so CommonMark renders it as a bullet reading 'brain + liver is 3,820 of 6,480 ml/min - 59.0%', which gives the kidney + heart + brain + liver sum to two organs (the wrapped-marker shape PL-DSMK fixed in ROADMAP.md)

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`uv run --no-project --with markdown-it-py==4.2.0 markdown-it docs/MODEL.md | grep -A2 'kidney + heart</p>'`
prints the paragraph closing on "On Mapleson's own rows, kidney + heart", then
`<ul>` and `<li>brain + liver is 3,820 of 6,480 ml/min — <strong>59.0%</strong> —`.
The CLI renders with `MarkdownIt()`, whose default is the `commonmark` preset,
and the list item runs to the end of the paragraph, taking in the 63.0%
comparison and the bold conclusion after it. It is the only line in the file
that opens with a plus and a space; the two that open `+0.38` and `+1.59` are
signed numbers, not list markers.

**Why it matters.** `docs/MODEL.md` is the authoritative specification of the
model, and a clinician reading it rendered, as GitHub shows it, is told in a
bullet that brain and liver take 59.0% of cardiac output, where the figure is
the four-organ sum on Mapleson's rows. The paragraph is the negative finding
that the model's perfusion fractions have no identified origin, and that
figure is its evidence, so a reader either learns a wrong physiological share
or, knowing the real ones, stops trusting the argument it carries.

**Done when.** The paragraph opening "And the negative finding, which is the
one that matters" in `docs/MODEL.md` § "Source hierarchy: what may be cited as
the authority for a value" renders as one paragraph, its four-organ sum
rewrapped so that no line opens with one of the sum's plus signs, and the
`markdown-it` command above prints no `<li>` after "kidney + heart".

**Classed `science`** (triage, 2026-10-04). The rendered authoritative
specification states a wrong share of cardiac output, which is a scientific
statement misread rather than a formatting nicety; nothing computed or
displayed depends on it, which is why it is not `safety`. Captured after
v0.6.0's freeze, it joins the gate's product lane under the `science`
exception.
