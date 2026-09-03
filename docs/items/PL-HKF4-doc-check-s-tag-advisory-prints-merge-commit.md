---
id: PL-HKF4
title: doc_check's tag advisory prints `<merge commit>`, which a shell reads as redirection, so pasting it fails with "no such file or directory: merge" instead of tagging
status: untriaged
added: 2026-09-03
---

**Problem.** `tools/doc_check.py:1273` prints the tag command as

    git tag -a v0.3.1 <merge commit> -m "v0.3.1"

A shell does not read `<merge commit>` as a placeholder. `<merge` is input
redirection from a file named `merge` and `commit>` is output redirection to a
file named `commit`, so pasting the line verbatim never reaches `git` at all —
zsh answers `no such file or directory: merge`, which names neither git, nor
the tag, nor the thing that is actually missing.

**Why it matters.** The advisory fires at exactly the moment somebody is
copying it, once per release, and the release cannot be finished until the tag
lands: `bin/docket release` refuses to cut the next one while the previous is
untagged. Observed 2026-09-03 on the v0.3.1 cut — the project owner pasted the
line and got the error, which cost a round trip to diagnose. The failure is
also maximally unhelpful for the one thing it is trying to teach: the reader
learns that a file called `merge` is missing.

`.claude/skills/docket/SKILL.md` already says "Never ask the owner to 'tag
vX.Y.Z'. Paste the commands, filled in", so the standard is written down and
the tooling does not meet it.

**Where.** Two callers print the same string, and they are *not* the same case:

- `tools/doc_check.py:1273` — fires **after** the merge has landed. That is
  what the advisory means: the version is on the default branch and carries no
  tag. So the commit is resolvable here, and printing a placeholder is a
  missed answer rather than a formatting choice.
- `subprojects/docket/src/docket/cli.py:635` — fires at `release` time,
  **before** the merge exists. It genuinely cannot know the SHA, so a
  placeholder is correct; it just must not be one a shell mangles.
- `.claude/skills/docket/SKILL.md:607` — the worked example a session copies.
  Same shape, and worth fixing for consistency, though a session is told to
  fill it in.

**Approach.** Two changes, and the second is the cheap half:

1. In `doc_check.py`, resolve the commit rather than naming it. The merge
   commit is the newest commit on the default branch whose `pyproject.toml`
   holds the untagged version and whose parent does not — `git log
   origin/<default> -1 -S'version = "<v>"' -- pyproject.toml` is one way, and
   the existing release-train reader already knows the version and the default
   branch. Print the real SHA. Fall back to the placeholder form below when it
   cannot be resolved (shallow checkout, no remote), rather than guessing.
2. Change the placeholder itself, everywhere it survives, to something a shell
   cannot read as redirection. `git tag -a v0.3.1 MERGE_COMMIT -m "v0.3.1"`
   with a line above saying what `MERGE_COMMIT` is, fails as
   `fatal: Failed to resolve 'MERGE_COMMIT'` — which names the problem.

**Found.** Cutting v0.3.1 (2026-09-03), when the project owner hit the error.

**Done when.** `tools/doc_check.py`'s advisory prints the resolved merge commit
where one can be found, no printed command in `tools/` or
`subprojects/docket/` contains a `<...>` placeholder a shell reads as
redirection, and a test covers both the resolved and the unresolvable case.
