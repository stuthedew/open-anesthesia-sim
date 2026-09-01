---
id: PL-4MHK
title: pyproject.toml's description is vaguer than the project's own framing and omits the educational-only qualifier
status: untriaged
touches: pyproject.toml
added: 2026-09-01
---

**Problem.** `[project] description` in `pyproject.toml` reads "Open-source
anesthesia simulation project". It says nothing about what is modeled
(volatile-agent uptake and distribution, three agents, one reference adult),
and — unlike `README.md` and the in-app framing — it carries no
educational-only qualifier.

**Why it matters.** It is a displayed statement about a clinically-flavored
tool that travels further than the file it lives in: it is the package
summary surfaced by `uv pip show`, by any wheel built from this tree, and by
PyPI if the project is ever published there. "Anesthesia simulation project"
read cold implies a broader and more clinical scope than the model has.
Presentation correctness is part of the safety standard, so the summary a
package carries should match the one `README.md` opens with rather than
being a looser paraphrase of it.

**Where.** `pyproject.toml`, `[project] description`. The wording it should
agree with is `README.md`'s opening paragraph and the GitHub repository
"About" description, which the project owner set on 2026-09-01.

**Done when.** The `description` field names volatile-agent uptake and
distribution and states the educational-only limit, and reads consistently
with `README.md`'s opening and the repository's GitHub description. Consider
whether `tools/doc_check.py` can decide the agreement rather than leaving it
to a reader; if it cannot, say so in the item rather than adding a check that
guesses.
