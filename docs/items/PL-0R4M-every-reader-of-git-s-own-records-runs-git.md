---
id: PL-0R4M
title: Every reader of git's own records runs git through subprocess.run(text=True), whose universal-newline decoding turns a raw carriage return in a commit subject into a newline before any split, so a subject holding one still reads as two lines
status: untriaged
feature: line-ends
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/verify.py, tools, .claude/hooks/stop_hook_patch.py, tests/unit, subprojects/docket/tests
added: 2026-10-05
---

**Problem.** Every reader of git's own records runs git through subprocess.run(text=True), whose universal-newline decoding turns a raw carriage return in a commit subject into a newline before any split, so a subject holding one still reads as two lines

**Found 2026-10-05 by `PL-4YVK`**, after its readers stopped splitting with
`splitlines()`. Reproduced on git 2.43.0 and Python 3.11: a commit made with
`-m "$(printf 'PL-AAAA one\rPL-BBBB two')"` keeps the raw `\r` (`git log
--format=%s` read as bytes prints `b'PL-AAAA one\rPL-BBBB two\n'`), and the
same call through `subprocess.run(..., text=True)` returns
`'PL-AAAA one\nPL-BBBB two\n'`. Text mode applies universal newlines
(https://docs.python.org/3/library/subprocess.html#frequently-used-arguments),
so the record is cut before `split_lines` sees it, and the second half opens
with an id that leads nothing. Ref names cannot hold a `\r`
(`git check-ref-format` refuses control characters); subjects, bodies and
`-z` path listings can.

**Why it matters.** `vcs._run_git` and every tool's own runner read git this
way, so each new reader inherits it; `PL-4YVK`'s generator stays `live` on it.

**Design question, not yet a repair.** A blob read through `git show
<rev>:<path>` wants the translation, as `read_text` does and as `vcs`'s batch
reader copies on purpose; git's own records (`log`, `for-each-ref`, `-z`
listings) do not. So the fix separates the two - bytes decoded without
translation for records - rather than turning text mode off everywhere.

**Done when.** A subject holding a raw `\r` is read as one subject by
`vcs`'s log readers and by `tools/branch_id_check.py`, with a real-repository
test, and new git readers cannot pick text-mode decoding for records silently.
