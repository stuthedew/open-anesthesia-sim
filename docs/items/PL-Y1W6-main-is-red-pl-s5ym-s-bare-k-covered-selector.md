---
id: PL-Y1W6
title: main is red: PL-S5YM's bare -k covered selector now matches a braced-citation test #593 added, so docket check --verify errors on every tree containing #593
status: untriaged
added: 2026-09-15
---

**Problem.** main is red: PL-S5YM's bare -k covered selector now matches a braced-citation test #593 added, so docket check --verify errors on every tree containing #593

**`main` is red now**, at `7ba6108e` (the `#593` merge, `PL-MXSL` + `PL-F933`).
Run `#1985` failed with exactly one error and nothing else:

```text
PL-S5YM is open but its `verify:` command already passes (1 of 147 checked).
Either the work landed and the item was never closed - close it - or the
command does not discriminate and proves nothing
```

As the digest puts it, no pull request will show this: `quality.yml` fires on
`pull_request` and on `push` to `main`, and the push run is the only one that
ran against a tree containing `#593`.

**Mechanism.** `PL-S5YM` carries `verify: uv run pytest
tests/unit/test_doc_check.py -k covered`, written 2026-08-30 - a bare `-k`, the
shape the `docket` skill's "Watch it fail for the right reason, and never a
bare `-k`" section exists to refuse. `#593` added
`test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered` to that
file. `-k` matches substrings, so the stale selector now matches it, one test
is selected, it passes, and `docket check --verify` errors.

Reproduced 2026-09-15 in a detached worktree at `origin/main`:

```text
collected 235 items / 234 deselected / 1 selected
1 passed, 234 deselected in 0.31s          # exit 0
```

On a tree without `#593` the same command exits 5 - selects nothing - which
`docket check` reports separately and does not error on. That is the whole
difference, and it is why `#594`, `#595` and `#596` are all green: every one of
them forked before `#593`.

**Why it compounds.** `CLAUDE.md`'s third friction test - something upstream of
every other command. `docket check` gates `make check` and CI, so every branch
cut from `main` from now on inherits this error, red before its first commit.
The three open pull requests are green only by the accident of when they
forked; each goes red the moment it takes the base in.

**The fix is one line, in `PL-S5YM`'s front matter**, and it is the second of
the two dispositions `docket check` names: the command does not discriminate.
Replace the bare selector with the paired shape the skill prescribes -
something that runs and passes today, paired with a `grep` for what the work
adds:

```text
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_file_outside_a_childless_directory_still_fails' tests/unit/test_doc_check.py
```

That exits 1 before the work (the code an ordinary failing test gives), the
pytest half proves the file's suite healthy, and the `grep` names the exact
test `PL-S5YM` owes.

**A second finding, which changes what `PL-S5YM` owes.** Its brief says of the
covered-directory branch: "None is exercised by `tests/unit/test_doc_check.py`".
That is false, and was false when it was written -
`test_childless_directory_covers_its_whole_subtree` has existed at
`tests/unit/test_doc_check.py:208` since `PL-032`, and asserts the positive
direction ("a file beneath a childless directory needs no line"). What is
genuinely missing is the negative direction, which `PL-S5YM`'s own **Approach**
section asks for: "a file outside it still fails". So the item is half done and
its brief overstates the gap. Correct the brief in the same pass, and let the
`grep` name the negative-direction test rather than a general one.

**Not this branch's to fix.** Found while closing `PL-7XTS` on
`claude/lucid-planck-jkyod9`, whose declared `touches` is
`.claude/skills/docket/SKILL.md`. Putting the repair on `#595` would widen a
green pull request past its commission and discard its passing run, and this
session's harness binds it to that one branch. So it is filed rather than
fixed.
