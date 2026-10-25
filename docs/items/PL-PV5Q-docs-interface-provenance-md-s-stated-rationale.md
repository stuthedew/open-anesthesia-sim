---
id: PL-PV5Q
title: docs/interface-provenance.md's stated-rationale section rests on search-engine summaries because every blender.org host and web.archive.org are egress-blocked, so a session that can reach the HIG and Developer Docs should re-read it against the pages themselves
priority: P3
effort: M
status: done
classes: docs
feature: interface-areas
milestone: v0.6.8
touches: docs/interface-provenance.md, ROADMAP.md
added: 2026-09-16
closed: 2026-10-25
pr: 1818
verify: grep -qF 'read against the primary pages rather than search summaries' docs/interface-provenance.md && python3 tools/doc_check.py check
---

**Problem.** docs/interface-provenance.md's stated-rationale section rests on search-engine summaries because every blender.org host and web.archive.org are egress-blocked, so a session that can reach the HIG and Developer Docs should re-read it against the pages themselves

**Reachable now, measured 2026-09-26 (`PL-M701`).** The premise above no
longer holds for `blender.org`: `docs.blender.org`, `developer.blender.org`,
`www.blender.org`, `archive.blender.org` and `projects.blender.org` each
answered 200 at CONNECT through the proxy, and the project owner has
`blender.org` and `*.blender.org` on the environment's allowed domains.
`web.archive.org` was still refused. So any session can do this now; probe
again before starting, since the owner edits that list.

**Why it matters.** `docs/interface-provenance.md` is the document a session
building the layout is told to read first, and its stated-rationale section is
the half that says *why* Blender's designers made each choice - which is exactly
the half a search summary paraphrases rather than quotes. This project's own
source hierarchy refuses a secondary summary as the authority for a value;
adopting a rationale as precedent is the same act one register over. What is at
risk is not a clinical number but a design decision taken on a misread of why
the precedent exists - and four decided properties of the area model already
cite this section.

**Done when.** Each claim in the stated-rationale section is checked against the
Blender Manual and Developer Docs pages themselves and is confirmed, corrected
or withdrawn; the section records that it was read against the primary pages
rather than search summaries, with the date; and any claim still unreachable is
marked as resting on a summary rather than left indistinguishable from the rest.

**Outcome, 2026-10-25.** Every claim in the section was read at its primary
page, and § "Pages read on 2026-10-25" lists the pages. All five `blender.org`
hosts answered at CONNECT on the day. `projects.blender.org` serves its HTML
only to a JavaScript client, so task T91536 and its commit were read through
that forge's API. The re-read corrected three claims. Non-Modal is about
consistent input, not about not blocking. The main region does have a
definition: it is the one region always visible. And no page calls the
toolbar's tools "gizmo-driven". Two claims are now marked unconfirmed: that the
interface renamed the screen "layout", and that a temporary window adds a
hidden screen. Three findings were strengthened. Blender names the mode-error
hazard, through Raskin in Reynish's 2008 paper, but still has no doctrine for
keeping the mode visible. Blender's own 2025 tablet post says a single-area
design departs from non-overlap. And Pin Scene is an opt-in exception to the
2.8 workshop's rule that the scene belongs to the window. The section's main
finding held: Blender's reason for non-overlap is visibility and efficiency,
not information integrity.
