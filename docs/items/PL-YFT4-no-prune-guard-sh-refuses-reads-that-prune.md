---
id: PL-YFT4
title: no-prune-guard.sh refuses reads that prune nothing: git config --get fetch.prune, since its config shape matches the setting's name in any config call; git remote prune -n, a dry run; and git log -S fetch -p or git log --grep pull -p, since a command word is matched anywhere in the call
priority: P3
effort: S
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: reading the prune setting, a remote-prune dry run and a git log search that mentions fetch or pull pass the guard instead of costing a session a call and an untrue reason
verify: grep -q 'def test_a_read_that_prunes_nothing_is_admitted' tests/unit/test_no_prune_guard.py
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

**Why it matters.** Each refusal costs a session a call and a reason that is
not true, since it says the command prunes, and `git log -S` with `-p` is an
ordinary investigation. Reproduced as filed on `origin/main` (`6efd8c41`)
at triage, 2026-09-26: all four refused.

**Done when.** `git config --get fetch.prune`, `git remote prune -n origin`,
`git log -S fetch -p` and `git log --grep pull -p` pass the guard, while
`git config fetch.prune true`, `git remote prune origin` and `git fetch
--prune` stay refused, pinned in `tests/unit/test_no_prune_guard.py`. Whether
`git submodule foreach git fetch --prune` stays refused is the fix's to settle
and record.

**Since `PL-M2NV` (2026-09-26)** a second `config` shape sits in
`PUSH_SHAPES`, reading `remote.<name>.mirror` as the first reads a prune
setting, so `git config --get remote.origin.mirror` is refused for the same
first cause, and the fix to that cause is owed on both.

**Generator check.** A member of `PL-61FT` (the Bash guards read what a
command does from its spelling): filed by `PL-R17X`'s close, whose `pull`
shape brought the `git log --grep pull -p` refusal. Owed under any bound
`PL-61FT` sets, since these are canonical reads refused, so it is left ready.

**Met 2026-09-26 in ordinary work.** The project owner reported at 20:23 UTC,
relayed to the `PL-61FT` design thread, that the no-prune guard blocked a
read-only `git config --get fetch.prune` in ordinary work. That is the first
of the four spellings above, and the first spelling of any `PL-61FT` member
met rather than probed - within the hour of the bound being recorded, and by
the owner's own hand. Under that bound a known gap met in ordinary work is
worked as a defect at its own rank, so this item stays `ready` for that
spelling, and the hold the design round asked for on it is lifted by the
round's own rule rather than by a change to it. The other three spellings -
`git remote prune -n origin`, `git log -S fetch -p`, `git log --grep pull -p`
- are still met by nobody.

**Done when, re-scoped 2026-09-26.** A `git config` invoked only to read a
setting - `--get`, `--get-all`, `--get-regexp`, `--list` and `-l`, and their
kin - passes the guard whatever setting it names, `git config --get
fetch.prune` and `git config --get remote.origin.mirror` among them, while
`git config fetch.prune true` and every write of a prune or mirror setting
stays refused, pinned in `tests/unit/test_no_prune_guard.py`. The three
unmet spellings above are recorded as `KNOWN_GAPS` rows there under
`PL-61FT`'s build, or closed in the same change where that costs no reading
of their own; the four-spelling "Done when" above is superseded for them.
