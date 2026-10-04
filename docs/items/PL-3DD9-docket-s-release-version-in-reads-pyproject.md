---
id: PL-3DD9
title: docket's release.version_in reads pyproject.toml's version with a one-line pattern, so a TOML multi-line string reads as no version and tag_release declines for the wrong reason; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's release.version_in reads pyproject.toml's version with a one-line pattern, so a TOML multi-line string reads as no version and tag_release declines for the wrong reason; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `version = """\n0.5.22"""` reads '' where `tomllib` gives '0.5.22', and `tag_release` then declines with "declares no version" (by reading). Latent and implausible: `pyproject.toml` line 3 is one line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
