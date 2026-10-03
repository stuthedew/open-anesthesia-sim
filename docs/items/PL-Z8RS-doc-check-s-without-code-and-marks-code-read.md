---
id: PL-Z8RS
title: doc_check's _without_code and _marks_code read code spans a line at a time, so on a line a wrapped span closes, its closing run pairs with the next span's opening run and the prose between reads as code: a TeX delimiter there goes unchecked, and a word there is listed as code
status: untriaged
added: 2026-10-03
---

**Problem.** doc_check's _without_code and _marks_code read code spans a line at a time, so on a line a wrapped span closes, its closing run pairs with the next span's opening run and the prose between reads as code: a TeX delimiter there goes unchecked, and a word there is listed as code

**Found 2026-10-03** by `PL-9L39`, which moved both readers onto `docket.release.CODE_SPAN_RE` and left them reading one line at a time, as they read before. Against the document-level reading, `_marks_code` still misreads 1,061 of 133,251 words on the lines of `doc_check`'s documents that hold a backtick, most of them on a line a wrapped span closes. `_without_code` misreads the same lines, and there the miss is silent: a `\(` in the prose between the closing run and the next span is blanked, so the math check never reads it. `doc_check._code_spans` already reads a document's spans whole, so the likely fix maps its spans onto lines for both readers, with `_without_code` blanking math spans first as it does now. `docket new` matched this to `PL-Q9LK` on its title: a different fact, a workflow's shell script, read a line at a time by the same tool.
