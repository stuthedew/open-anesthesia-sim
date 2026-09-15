---
id: PL-RFGY
title: .gitignore ignores .vscode/ while .vscode/settings.json is tracked, so extensions.json and launch.json cannot be added without git add -f
priority: P3
effort: S
status: done
classes: defect
touches: .gitignore, .vscode/extensions.json
added: 2026-09-15
closed: 2026-09-15
pr: 589
verify: python3 tools/doc_check.py check && ! git check-ignore -q --no-index .vscode/extensions.json && git check-ignore -q --no-index .vscode/ipch/x
---

**Problem.** .gitignore ignores .vscode/ while .vscode/settings.json is tracked, so extensions.json and launch.json cannot be added without git add -f

**Measured, 2026-09-15.** `git ls-files | git check-ignore --stdin --no-index
--verbose` over the whole tree returns exactly one line:

    .gitignore:60:.vscode/	.vscode/settings.json

That is the only tracked file this repository's own ignore rules claim to
exclude. It survives because a path already in the index is not re-tested
against `.gitignore` — which is also why the same command *without*
`--no-index` returns nothing, and why the state has gone unnoticed since the
bootstrap commit (`be48070b`) added both the file and the rule.

**Why it matters.** The rule is not describing what the repository does. The
tracked `settings.json` sets `editor.formatOnSave` and names
`charliermarsh.ruff` as the Python formatter, so it is deliberately shared
project configuration, not editor noise — but the companion files that make
that configuration work are silently unaddable:

    .vscode/extensions.json   .gitignore:60:.vscode/
    .vscode/launch.json       .gitignore:60:.vscode/

A session that writes `.vscode/extensions.json` to recommend the very
extension `settings.json` requires, runs `git add -A`, and commits, produces a
commit that does not contain it and says nothing. That is the failure shape
this repository already treats as serious elsewhere — `PL-8PT6` and `PL-1YDK`
are the same class in the other direction, a generated file no rule covered.

**The fix, from the published template rather than invented.**
`github/gitignore`'s `Global/VisualStudioCode.gitignore`
(https://github.com/github/gitignore/blob/main/Global/VisualStudioCode.gitignore,
read 2026-09-15) is the established form and states the pattern exactly:
ignore the directory's contents, then re-admit the shared files by name.

    .vscode/*
    !.vscode/settings.json
    !.vscode/tasks.json
    !.vscode/launch.json
    !.vscode/extensions.json
    !.vscode/*.code-snippets
    !*.code-workspace

Note `.vscode/*` rather than `.vscode/`: a negation cannot re-admit a file
whose *parent directory* is excluded, because git does not descend into an
excluded directory to evaluate it. `.vscode/` excludes the directory and every
negation under it is dead; `.vscode/*` excludes the entries, which is what
makes the exceptions reachable. Anyone editing this block has to know that or
they will reintroduce the bug while appearing to fix it.

**Done when.** `git ls-files | git check-ignore --stdin --no-index` prints
nothing, and `git check-ignore -q --no-index .vscode/extensions.json` exits
non-zero while the same on `.vscode/ipch/x` exits zero.

**Read that command without `--verbose`.** With `-v` it prints the last
pattern that *matched*, negations included, so the fixed state prints

    .gitignore:73:!.vscode/settings.json	.vscode/settings.json

which is the exception doing its job and reads exactly like the failure above
it. Only the non-verbose form lists ignored paths, and only its exit code (1
for none) is the verdict.

**Not done here.** Whether `.vscode/extensions.json` should actually be
written is a separate decision, left to the project owner; this item only stops
the repository from silently discarding it.
