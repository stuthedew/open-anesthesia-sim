---
id: PL-9L39
title: Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it
status: untriaged
feature: read-facts-through-docket
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py
added: 2026-10-01
---

**Problem.** Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:367` (`CODE_SPAN_RE`) and `:662` (`BACKTICK_RUN_RE`); `subprojects/docket/src/docket/checks.py:2953` (`_CODE_SPAN`, beside an import of the real one); `subprojects/docket/src/docket/verify.py:199`. Whether each reader wants a CommonMark span or a looser backticked token is the first question for whoever works it.
