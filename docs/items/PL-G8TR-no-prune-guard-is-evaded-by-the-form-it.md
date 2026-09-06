---
id: PL-G8TR
status: untriaged
added: 2026-09-06
title: no-prune-guard is evaded by the form it recommends - git branch -dr driven from a generated list is a prune
touches: .claude/hooks/no-prune-guard.sh
---

**Problem.** `.claude/hooks/no-prune-guard.sh` refuses four shapes, all of
them `git fetch --prune`, `git remote prune`, `git remote update --prune`
and the config forms. It does not match `git branch -dr`, deliberately: that
is the safe remedy the guard's own message prints, on the reasoning that
deleting **one** ref **by name** is a considered act.

Run on 2026-09-06:

```sh
git for-each-ref --format='%(refname:short)' refs/remotes/origin | sed 's#^origin/##' \
  | grep -vxFf <(git ls-remote --heads origin | sed 's#.*refs/heads/##') \
  | xargs -r -I{} git branch -dr origin/{}
```

That is a prune. It computes exactly the set `--prune` computes and deletes
all of it - in the one form the guard whitelists, and with a name supplied for
each, so every property the guard relies on is satisfied while the property it
cares about is not. What made the safe form safe was **quantity and
deliberation**, not the flag; the guard tests the flag.

**Why it matters.** The guard is not advice, it is the project's answer to
`PL-HKF4` coming within one prune of losing an item that existed on no other
ref. Its value is entirely in stopping a session to ask "is any of this the
only copy?" - and a pipeline reaches the same end state with no such stop. It
was harmless this time only because the two refs it removed belonged to
branches whose pull requests had merged (#385, #384), which was checked by
hand before running it; the command cannot check that itself, and nothing
required the check.

**What is not the fix.** Refusing `git branch -dr` outright would break the
remedy the guard recommends and the `stranded` recovery recipe that depends
on it. The distinguishing property is that the ref names are *generated* rather
than typed - piped in, or more than one or two in a single call.

**Where.** `.claude/hooks/no-prune-guard.sh`, the `PATTERNS` list; the
recovery recipe in `.claude/skills/docket/SKILL.md` that prints
`git branch -dr`; `PL-JK0M` for why the prohibition moved into the hook.

**Done when.** A `git branch -d`/`-D` with `-r` whose ref names arrive
from a pipe, or which names several refs at once, is refused with the same
message as `--prune` - while a single named ref typed by a session still
passes, so the documented remedy keeps working.
