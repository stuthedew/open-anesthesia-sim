---
id: PL-T4FK
title: docs/MODEL.md line 2350 wraps '+ brain + liver' to the margin, so CommonMark renders it as a bullet reading 'brain + liver is 3,820 of 6,480 ml/min - 59.0%', which gives the kidney + heart + brain + liver sum to two organs (the wrapped-marker shape PL-DSMK fixed in ROADMAP.md)
priority: P1
effort: S
status: done
classes: docs, science
feature: prose-renders-as-written
touches: docs/MODEL.md
added: 2026-10-04
closed: 2026-10-05
pr: 1367
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

**Fixed 2026-10-05.** The paragraph is rewrapped at the file's 80 columns with
the four-organ sum held on one line, so the line that opened `+ brain + liver`
(line 2374 by then, ten commits after filing) now opens
`kidney + heart + brain + liver is 3,820 of 6,480 ml/min`. No word changed:
`git diff --word-diff` shows none. Rendered whole with the command above
before and after, the file differs in one place only - the `<ul><li>` holding
"brain + liver is 3,820 ..." is gone, and its text closes the paragraph it
belongs to, ahead of the unchanged `<p>` opening "Two of the three
coincidences". The `verify:` grep passes.

The sum is kept whole rather than broken after `kidney +`, which would also
have rendered correctly, so that the source reads the four organs together as
the page does. A later rewrap can still split it; finding that is `PL-LNNL`'s
check. Until then, a scan for a list marker opening a line whose predecessor
ends mid-sentence - a non-blank, unindented prose line without closing
punctuation - finds this line before the fix and nothing in `docs/MODEL.md`
or `README.md` after it. It is a heuristic and not
the check `PL-LNNL` asks for: it reads the source rather than a CommonMark
parse, and it passes over a marker after a line ending a sentence.
