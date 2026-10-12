---
id: PL-S9JK
title: Tools run git through their own runners beside vcs._run_git and disagree on whether a non-zero exit is an answer, on non-UTF-8 output and on timeouts - branch_id_check, pr_body_check, left_behind_check, pr_title_check, generator_check, verify, doc_check and contrast_check's decode - and verify._blobs and vcs.GitRunner._blob read a cat-file header two ways
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, tools/branch_id_check.py, tools/pr_body_check.py, tools/left_behind_check.py, tools/pr_title_check.py, tools/generator_check.py, tools/doc_check.py, tools/contrast_check.py, tests/unit/test_branch_id_check.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: git's exit status, output and silence mean one thing to every reader
verify: grep -q 'def test_a_missing_blob_is_an_answer_as_vcs_reads_it' tests/unit/test_branch_id_check.py
---

**Problem.** Tools run git through their own runners beside vcs._run_git and disagree on whether a non-zero exit is an answer, on non-UTF-8 output and on timeouts - branch_id_check, pr_body_check, left_behind_check, pr_title_check, generator_check, verify, doc_check and contrast_check's decode - and verify._blobs and vcs.GitRunner._blob read a cat-file header two ways

- Whether git answered: `vcs._run_git`, `verify._git`, `doc_check._git_output`, `branch_id_check._git` (whose docstring claims `_run_git`'s rule), `pr_body_check._git`, `left_behind_check._stdout`, `pr_title_check._git` and an inline read in `generator_check`. On `git show HEAD:no/such/file` `_run_git` reads an answer and `branch_id_check._git` none; pr_body_check and left_behind_check return `""` for every failure. On non-UTF-8 stdout verify and doc_check raise `GitUnanswered` and pr_title_check and generator_check `UnicodeDecodeError`; past 1,800 s verify gives up and doc_check waits. `PL-0T5X` aligned doc_check by copying.
- Decoding: `tools/contrast_check.py` decodes UTF-8 and translates `\r` itself beside `lines.file_text`, which decodes by the locale; they part under a non-UTF-8 locale.
- A `cat-file --batch` header: `verify._blobs` beside `vcs.GitRunner._blob`. On `<spec> ambiguous` verify reads no file there, and vcs reads an unreadable shape and drops the batch for that root.
- The default branch: `doc_check._baseline` loops over `DEFAULT_BRANCHES` itself beside `vcs.default_base`; where the read of `origin/main` times out and a local `main` exists, vcs marks it unresolved and doc_check measures against it unmarked.
- `ls-remote` output: `vcs.remote_heads` beside `left_behind_check.read_remote`; they agree.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** The tools and verify run git through `vcs`'s runner (or one shared runner), the cat-file header is read once, and a test pins `git show HEAD:no/such/file` in `branch_id_check`. `PL-JTCQ` holds the readers without `-z`.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
