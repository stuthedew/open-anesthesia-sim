---
id: PL-9L39
title: Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it
priority: P3
effort: S
status: ready
classes: defect
feature: read-facts-through-docket
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a double-backtick span reads the same in every checker, so a brief quoting a backtick cannot pass one check and trip another
verify: ! grep -qF '_CODE_SPAN = re.compile' subprojects/docket/src/docket/checks.py && ! grep -qF 'CODE_SPAN_RE = re.compile' tools/doc_check.py
---

**Problem.** Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:367` (`CODE_SPAN_RE`) and `:662` (`BACKTICK_RUN_RE`); `subprojects/docket/src/docket/checks.py:2953` (`_CODE_SPAN`, beside an import of the real one); `subprojects/docket/src/docket/verify.py:199`. Whether each reader wants a CommonMark span or a looser backticked token is the first question for whoever works it.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
