---
id: PL-CFWP
title: docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** docket's verify.is_suppression_line reads one diff line at a time, so a pytest.mark.skip split by a backslash or a bracket continuation is not counted as an added suppression; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `@pytest.mark.\` over `    skip(reason='flaky')`, and `@(pytest.mark` over `  .skip(...))`, both valid to `ast.parse`, read [False, False]; one line reads True, so the audit prints "no suppression added: none". `is_assertion_line`'s docstring names its continuation misses; this one's does not. Latent.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
