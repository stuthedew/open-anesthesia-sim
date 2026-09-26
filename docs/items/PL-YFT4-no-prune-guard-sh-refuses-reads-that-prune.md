---
id: PL-YFT4
title: no-prune-guard.sh refuses reads that prune nothing: git config --get fetch.prune, since its config shape matches the setting's name in any config call; git remote prune -n, a dry run; and git log -S fetch -p or git log --grep pull -p, since a command word is matched anywhere in the call
status: untriaged
added: 2026-09-26
---

**Problem.** no-prune-guard.sh refuses reads that prune nothing: git config --get fetch.prune, since its config shape matches the setting's name in any config call; git remote prune -n, a dry run; and git log -S fetch -p or git log --grep pull -p, since a command word is matched anywhere in the call

**Found 2026-09-26 while working `PL-R17X`**, piping each as a hook payload:
`git config --get fetch.prune`, `git remote prune -n origin`, `git log -S
fetch -p` and `git log --grep pull -p` are all refused. The first reads the
setting; the second is `--dry-run`, and on git 2.43.0 against a scratch remote
it deleted nothing; the last two are a pickaxe and a message search, with
patches. Three causes: the `config` shape matches a prune setting's name in any
`git config` call, read or write; `remote prune` is refused whatever flag
follows it; and each shape looks for its command word anywhere after `git`
rather than where git reads the command name. The last is also why `git
submodule foreach git fetch --prune` is refused, which a fix anchoring the
shapes would give up. `git log -S fetch -p` predates `PL-R17X`; `git log
--grep pull -p` came with it, since `PL-R17X` added the `pull` shape. A
refusal here costs a session one call and a misleading reason, not a ref.

**Not a recurrence of `PL-R17X`**, though filing matched it there on the shared
path: `PL-R17X` is about spellings that prune and pass, this one about
spellings that prune nothing and are refused, from three causes of their own.
