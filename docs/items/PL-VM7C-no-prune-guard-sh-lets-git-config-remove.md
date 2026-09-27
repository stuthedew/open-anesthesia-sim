---
id: PL-VM7C
title: no-prune-guard.sh lets git config --remove-section fetch and --rename-section fetch past, though either drops a local fetch.prune = false and a global true then prunes on the next plain fetch, as the refused --unset fetch.prune does
priority: P2
effort: S
status: done
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-27
pr: 1150
payoff: a session's git config --remove-section or --rename-section on the fetch section or a remote's is refused before it drops a local prune override or writes a prune or mirror setting, so no later plain fetch or push deletes the refs the guard keeps
verify: grep -q 'def test_a_config_section_write_is_refused' tests/unit/test_no_prune_guard.py
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

**Triaged 2026-09-27: inside the promise, as recommended.** `--remove-section`
and `--rename-section` write every setting of the section they name, so on a
section holding a prune or mirror setting each is "a prune or mirror setting
written by `config`", the header's own words, spelled by section. `PL-61FT`'s
bound files a spelling found by probing only where it is inside a promise, and
the prune guard's promise is the one drawn wide, because what it guards cannot
be undone: every documented spelling, "whether or not anybody has written it".

**Measured 2026-09-27, and wider than filed.** git 2.43.0, in scratch clones of
a scratch remote holding `main` and `other`, with the global config a scratch
file (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`). Piped to the hook as
payloads, every section spelling below was admitted and `git config --unset
fetch.prune` refused.

- The brief's two reproduce. With a global `fetch.prune = true` and a local
  `false`, `git config --remove-section fetch`, `git config --rename-section
  fetch kept` and `git config -f .git/config --remove-section fetch` each let
  the next plain `git fetch origin` delete `origin/other`.
- A section renamed *into* a guarded one writes the setting there, from a
  section the guard never reads. After `git config foo.prune true`, `git config
  --rename-section foo fetch` or `foo remote.origin`, both admitted today, the
  next plain fetch pruned with no global setting at all; renamed onto a
  `remote.origin.prune = false`, the moved `true` lands after it and wins.
  After `git config foo.mirror true` and `git config --rename-section foo
  remote.origin`, a plain `git push origin` from a clone holding only `main`
  deleted `other` on the remote: `PL-M2NV`'s outcome, by another road.
- The two the brief left unmeasured drop the override with the remote. After
  `--remove-section remote.origin` or `--rename-section remote.origin
  remote.kept`, a plain `git fetch origin` fails, having no remote to read, and
  once `git remote add origin` puts it back the next fetch prunes under the
  global `true`.
- A section name reaches only the section it names. `--remove-section remote`
  answers "no such section" and leaves `[remote "origin"]` whole; so do
  `FETCH` and `remote.ORIGIN` against the lower-case sections `git config`
  writes, and a hand-written `[Fetch]` is removed by `--remove-section Fetch`
  and not by `fetch`, so git matches the name as the file spells it.

So the fix reads a section action's names, and refuses one where either names
a section holding a guarded setting: `fetch` or `remote.<name>` for the prune
settings, `remote.<name>` for the mirror one, in either place of a rename.

**Why it matters.** The guard refuses the spelling that names a prune or mirror
setting and admits the one that names its section. So a session clearing a
`[fetch]` or `[remote "origin"]` section with `config` removes the local
`false` the named spelling is refused for removing, and the next plain fetch
deletes whatever a global `true` reaches, a stranded item's only copy among
them; and a rename into `remote.origin` reaches a mirror push, which deletes
other sessions' branches on the remote and cannot be taken back. No session is
recorded writing any of these. The promise holds them anyway, since what the
guard stops cannot be undone once it has run.

**Done when.** `git config --remove-section` or `--rename-section` naming `fetch`
or a `remote.<name>` section, in either place of a rename, is refused as `git
config --unset fetch.prune` is, pinned by
`test_a_config_section_write_is_refused`; a section action naming neither
still passes; and the hook's header says a section written whole is a write of
every setting it holds.

**Generator check.** An instance of `PL-61FT`'s fact, what a shell command does
when run, filed 2026-09-26 after that head closed the same day, and inside the
prune guard's promise, which the head's bound files as an item on purpose: the
bound stops a probed spelling *outside* a promise from becoming work, so this
is not evidence it failed. Recorded here and not in that head's
`root-cause-of:`, as `PL-8BR0` and `PL-FTDB` record theirs.
