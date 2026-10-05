---
id: PL-0R4M
title: Every reader of git's own records runs git through subprocess.run(text=True), whose universal-newline decoding turns a raw carriage return in a commit subject into a newline before any split, so a subject holding one still reads as two lines
priority: P3
effort: M
status: ready
classes: defect
feature: line-ends
touches: subprojects/docket/src/docket/lines.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/verify.py, tools, .claude/hooks/stop_hook_patch.py, tests/unit, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage
added: 2026-10-05
payoff: A commit subject, body or -z path holding a raw carriage return is read as the one record git wrote, and a new git reader cannot turn text-mode decoding on without saying why
verify: grep -q 'def test_a_subject_holding_a_carriage_return_is_read_as_one_subject' subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_subject_holding_a_carriage_return_is_read_as_one_subject' tests/unit/test_branch_id_check.py && grep -q 'def test_no_subprocess_call_turns_text_mode_on_outside_its_exemptions' tests/unit/test_line_splits.py
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

**Reproduced again at triage, 2026-10-05**, through the module's own runner:
in a repository holding that commit, `vcs._run_git(["log", "--format=%s"],
root)` returns `'PL-AAAA one\nPL-BBBB two\n'` (git 2.43.0, Python 3.11.15).
Text mode is on whenever `text=`, `universal_newlines=`, `encoding=` or
`errors=` is passed, and `Popen._translate_newlines` then replaces `\r\n` and
`\r` after decoding, so a runner passing `encoding="utf-8"` alone, as two in
`tools/` do, translates too.

**Design** (decided at triage; the route the project owner's start prompt gave,
with the third kind below settled here). Three kinds of git output, by whether
a carriage return in them is the file's or git's:

- **Git's own records** - hashes, subjects, bodies, trailers, ref names, `-z`
  path listings, config values - are decoded as written, in the encoding text
  mode used and with no line end translated. Only these can carry a raw `\r`
  outside file content: git C-quotes a control character in any path it prints
  without `-z`, and `git check-ref-format` refuses one in a ref name.
- **A blob** read through `git show <rev>:<path>` or `cat-file` keeps the
  translation, as `read_text` does and as `vcs`'s batch reader already copies.
- **A patch** keeps it too: its `+` and `-` lines are file lines, and
  `verify`'s removed-assertion audit pairs them with blob lines decoded the
  same way, while the paths in its headers are C-quoted.

So `docket.lines` holds the two decodings, `record_text` and `file_text`; every
git runner reads bytes and decodes records with the first, and a read of a blob
or a patch passes through the second where it is made. A `subprocess` call in
`tools/`, `subprojects/docket/src/docket/` or `.claude/hooks/` that turns text
mode on is refused by `tests/unit/test_line_splits.py` unless it is listed
there with its reason, which a runner of a configured shell command is.
Inventory, 2026-10-05: 23 git runners and 196 call sites across the three
trees, of which the blob and patch reads are the minority.

**Generator check.** A member of `PL-4YVK`, filed while that head is open:
where one line ends in git's output, the fact its `misread:` names. The
splitting half closed in `#1364`; this is the decoding half, the one mechanism
still handing the head members.

**Done when.** A subject holding a raw `\r` is read as one subject by
`vcs`'s log readers and by `tools/branch_id_check.py`, with a real-repository
test; a blob holding `\r\n` still reads as `read_text` reads its file; and a
`subprocess` call that turns text mode on in those three trees fails
`tests/unit/test_line_splits.py` unless it is listed there with its reason.
