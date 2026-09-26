---
id: PL-L8VP
title: doc_check reads make targets inside fenced code blocks, so a shell comment '# make sure the virtualenv' or make's own 'No rule to make target' output fails make check; fences contribute 5 real mentions of 112
priority: P3
effort: S
status: done
classes: defect
feature: exact-gates
milestone: v0.5.12
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1086
payoff: a shell comment or pasted make output in a fenced block passes make check, instead of being reworded to satisfy a check that read it as a command
verify: grep -q 'def test_a_fenced_shell_comment_saying_make_sure_names_no_target' tests/unit/test_doc_check.py && grep -q 'def test_make_error_output_in_a_fence_names_no_target' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads make targets inside fenced code blocks, so a shell comment '# make sure the virtualenv' or make's own 'No rule to make target' output fails make check; fences contribute 5 real mentions of 112

Reproduced both. 107 make targets are checked in code spans, all real; 5 in fences, all real. Scanning fences buys 5 checked mentions and brings two false-refusal classes.

Re-confirmed 2026-09-25 against 46954a81: `check_make_targets` on one scratch document holding two fences errored on `make sure` for the comment `# make sure the virtualenv exists` and on `make target` for make's own `make: *** No rule to make target 'foo'.  Stop.` - `_make_mentions` runs `MAKE_MENTION_RE` over every line of every fenced block. Of the two fixes below, only reading lines that begin with `make ` keeps `test_a_target_named_in_a_fenced_block_is_read` true; not scanning fences deletes that assertion, which the close-out's removed-assertion audit refuses, so prefer the first-word rule.

**Generator check.** The fact misread is whether a fenced line makes the `make <target>` claim, recognised by the words `make X` anywhere on the line - `PL-GPJ7`'s `misread:`, and a member of it correctly. Already recorded as a recurrence on `PL-YSMV`, the same check family's earlier false refusal.

**Why it matters.** Same class as PL-YSMV: a gate refusing correct content.

**Done when.** Fenced blocks are not scanned for make targets, or only lines that begin with `make `; a test holds both reproductions through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Built 2026-09-26, as step 2 of `PL-GPJ7`'s split.** `FENCED_MAKE_RE` reads a fenced line only where `make` is its first word, the fix this brief preferred, so `test_a_target_named_in_a_fenced_block_is_read` holds unchanged and both reproductions pass. Of the 5 fenced mentions in the documents, 2 open their line and are still read. The other 3 name `check` from mid-line - two in the package map's tree comments in `docs/ARCHITECTURE.md`, one after `set -o pipefail;` in `docs/worker.md` - and are no longer read; 109 code-span mentions of targets still are, `make check` many times among them.
