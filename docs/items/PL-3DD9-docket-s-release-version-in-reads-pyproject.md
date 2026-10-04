---
id: PL-3DD9
title: docket's release.version_in reads pyproject.toml's version with a one-line pattern, so a TOML multi-line string reads as no version and tag_release declines for the wrong reason; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py, tools/tag_release.py, tools/doc_check.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a version file docket cannot read is reported as unreadable rather than as declaring no version, and a bump is never written to a line the reader does not read
verify: grep -qF '"project version, ' tests/unit/test_doc_check.py
---

**Problem.** docket's release.version_in reads pyproject.toml's version with a one-line pattern, so a TOML multi-line string reads as no version and tag_release declines for the wrong reason; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `version = """\n0.5.22"""` reads '' where `tomllib` gives '0.5.22', and `tag_release` then declines with "declares no version" (by reading). Latent and implausible: `pyproject.toml` line 3 is one line.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, `version_in('[project]\nname = "x"\nversion = """\n0.5.22"""\n')` returns `''` where `tomllib` reads `'0.5.22'`, and `prepare_bump`'s `VERSION_RE` finds no field to bump in the same text.

**Why it matters.** Latent and implausible here, since `pyproject.toml` writes its version on one line. What it buys is that `tag_release`, `released_on_base` and the tag check say why they could not name a version, rather than reporting a file they could not read as one declaring none, and that a bump is never written to a line the reader does not read.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `version_in` reads `[project]`'s `version` with `tomllib` (PEP 621) and raises on text that is not TOML; each caller reading another ref's copy declines by name on that; `prepare_bump` reads its write back and refuses a bump its one-line pattern could not make; `project version, ...` cases in `CONTINUED_STATEMENTS` pin it.
