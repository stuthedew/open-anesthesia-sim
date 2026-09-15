---
id: PL-548V
title: citing-sources.md tells a session to clone the private reference corpus with no destination and no ignore rule, so running it from the repository root leaves a nested git repo in the working tree
priority: P3
effort: S
status: ready
classes: docs, infra
touches: .claude/rules/citing-sources.md, .gitignore
added: 2026-09-15
not-delegable: proving it means cloning the private corpus from a session holding add_repo access and reading git status afterwards, which no check in this repository can do; the rule's own text is the only artifact, and whether it names a usable destination is a judgement rather than a match
---

**Problem.** citing-sources.md tells a session to clone the private reference corpus with no destination and no ignore rule, so running it from the repository root leaves a nested git repo in the working tree

**Where.** `.claude/rules/citing-sources.md:88-89`:

> Attach it with `add_repo` (owner `stuthedew`, repo
> `open-anesthesia-sim-references`, access `read`), then `git clone --depth 1
> https://github.com/stuthedew/open-anesthesia-sim-references`.

**The clone names no destination**, so it lands in the current working
directory - the repository root, for a session that has not `cd`ed elsewhere -
as `open-anesthesia-sim-references/`, a nested git repository that nothing
tracks and, until `PL-DLR3`, nothing ignored either.

**Two costs, and the second is not cosmetic.** The directory reads as untracked
in `git status` while a session decides what its own diff contains. And `git
add` on it records a gitlink rather than files: mode `160000` pointing at a
commit this repository has no `.gitmodules` entry for, so a clone of this
repository gets an unresolvable reference. Reproduced in a scratch repository
2026-09-15; git warns, but the warning is easy to miss inside a `git add -A`.

**Recommended fix, for the project owner to accept or replace.** Name a
destination outside the working tree in the rule itself - the session scratchpad
is the natural one, since the corpus is read and discarded within a session and
nothing in the repository should ever hold it. That removes the hazard rather
than hiding it. Keep an ignore rule as well for anyone who clones into the root
anyway: the two are not exclusive, and the same pairing was the answer for the
subproject lockfile in `PL-8PT6`.

**Note the asymmetry with `PL-DLR3`.** That item ignores the directories the
project owner already has, including `oas-mirror/`. This one is about the
instruction that keeps producing new ones, under whatever name the session
happens to use - an ignore rule written against today's names does not cover
tomorrow's clone.

**Why it matters.** The hazard outlives the fix that looks like it. `PL-DLR3`
ignores `oas-mirror/`, the directory the project owner already had, and that
closes today's instance and no other: the rule here produces a *new* directory
under whatever name the next session picks, so an ignore list written against
today's names never catches up. It is also the one instruction in this
repository that tells a session to create a nested git repository, which is the
failure with teeth - `git add` on one records a gitlink (mode `160000`) against
no `.gitmodules` entry, so a clone gets an unresolvable reference rather than
files, and git's warning is easy to miss inside a `git add -A`.

Low priority because it is rare rather than harmless: it fires only when a
session reaches a terminal source and attaches the corpus, which has happened
twice since `PL-XJ5P` opened it on 2026-09-13.

**Done when.** The rule names an explicit clone destination, and following it
verbatim from the repository root leaves `git status` clean.
