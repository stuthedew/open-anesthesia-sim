---
id: PL-PV5Q
title: docs/interface-provenance.md's stated-rationale section rests on search-engine summaries because every blender.org host and web.archive.org are egress-blocked, so a session that can reach the HIG and Developer Docs should re-read it against the pages themselves
priority: P3
effort: M
status: ready
classes: docs
feature: interface-areas
touches: docs/interface-provenance.md
added: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'read against the primary pages rather than search summaries' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md's stated-rationale section rests on search-engine summaries because every blender.org host and web.archive.org are egress-blocked, so a session that can reach the HIG and Developer Docs should re-read it against the pages themselves

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
