---
id: PL-VM7C
title: no-prune-guard.sh lets git config --remove-section fetch and --rename-section fetch past, though either drops a local fetch.prune = false and a global true then prunes on the next plain fetch, as the refused --unset fetch.prune does
status: untriaged
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
added: 2026-09-26
---

**Problem.** no-prune-guard.sh lets git config --remove-section fetch and --rename-section fetch past, though either drops a local fetch.prune = false and a global true then prunes on the next plain fetch, as the refused --unset fetch.prune does

**Found 2026-09-26 while working `PL-YFT4`**, listing the actions `git config
-h` documents on git 2.43.0 to learn which ones write. Measured in a scratch
clone of a scratch remote holding `main` and `other`, with `other` deleted on
the remote, the global config setting `fetch.prune = true` and the clone's
own config overriding it with `fetch.prune = false`: after `git config
--remove-section fetch` or `git config --rename-section fetch kept`, a plain
`git fetch origin` deleted `refs/remotes/origin/other`; with neither, it kept
it. `git config --unset fetch.prune` does the same and is refused, because
it names the setting; the two section spellings name only `fetch`, which the
`config` reading's setting pattern never matches, so both pass today.
Unmeasured: `--remove-section remote.origin` and `--rename-section` of a
remote's section, which drop `remote.<name>.prune` and `remote.<name>.mirror`
with the remote itself.

**Inside the promise or a known gap is the triager's call.** The header
promises "a prune or mirror setting written by `config`", and a section write
removes one; but it deletes no ref itself and prunes only where a config file
the hook never reads has turned pruning on, which is the reasoning the header
already applies to `--prune-tags`. Recommendation (marked): inside, as an
item rather than a `KNOWN_GAPS` row, since the refused `--unset fetch.prune`
is the same write spelled by name. It is a member of `PL-61FT`'s head: the
guard reads the setting from its name, and a section write never spells it.
