---
id: PL-674D
title: '`docket release` bumps pyproject.toml but leaves uv.lock stale, breaking make check'
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: Makefile, .claude/skills/docket/SKILL.md
added: 2026-08-25
---

**Problem.** `docket release` writes the new version into `pyproject.toml` and
stops. `uv.lock` records the project's own version too, so the very next
command a release runs — `make check`, whose first step is `uv sync --locked`
— fails with "The lockfile at `uv.lock` needs to be updated, but `--locked`
was provided".

**Why it matters.** The failure lands between "the release is written" and
"the release is verified", which is the worst place for it: the tree is
half-updated, `make check` is red, and the reason has nothing to do with the
release's content. A session that has not seen it before will read a red
`make check` as its own doing.

It has now happened twice, on both releases since the tool gained the command.
`5e9a8f6` ("Release v0.2.3") and `3ed704a` ("Release v0.2.4") each carry a
one-line `uv.lock` version bump alongside the `pyproject.toml` one — the
manual `uv lock` being run by hand. The session that cut v0.2.4 was working in
a tree whose own history documented the trap and hit it anyway.

**Where.** `Makefile`, `.claude/skills/docket/SKILL.md` (release mode).

**Decided.** Put the sequencing in the `Makefile`, where the toolchain already
lives: a `release` target that runs `bin/docket release`, then `uv lock`, then
`make check`, with the docket skill's release mode invoking `make release`
instead of `bin/docket release`.

Why this over the three options originally listed:

- **Not "teach `bump_version` to rewrite the lockfile".** Beyond the
  generality cost, a lockfile is a generated artifact and hand-editing
  generated artifacts is a liability. Rewriting the version string happens to
  match what `uv lock` produces today; nothing guarantees it keeps doing so,
  and if uv ever covers that field with an integrity hash the failure mode
  changes from a loud `--locked` error into a lockfile that passes checks
  while misdescribing the tree.
- **Not "print a follow-up command".** Still manual, and manual is what failed
  twice.
- **Not "document the step in the skill"** as the item's stated default. That
  option was never actually implemented — `uv lock`, `uv.lock` and `lockfile`
  appear nowhere in the skill or `subprojects/docket/README.md` — and it is
  the weakest of the three. `CLAUDE.md` decides this case directly: build when
  the work recurs and the answer is deterministic. A release-time lockfile
  bump recurs at every release and has no judgment in it.

`docket` is left untouched, so it stays standard-library-only and
package-manager-agnostic: no lockfile format knowledge, no `subprocess`, no
new configuration key. The `Makefile` already holds `uv sync --locked --dev`,
so `uv lock` sits beside the toolchain fact it belongs to.

**Accepted cost.** `bin/docket release` remains a footgun if invoked directly.
This works because the documented entry point changes, not because the tool
became safe. The alternative — a `post_version_command` key in `docket.toml`
that `docket release` executes — would make the tool itself safe for any
caller, at the price of giving `docket` a command-execution surface it does
not have. Deliberately not taken.

**Rejected route worth recording:** having `bin/docket check` detect a stale
lockfile cannot help, because `make check` runs `sync` first, so `uv sync
--locked` fails before `bin/docket check` is reached.

**No `verify:` command.** Proving this fixed means cutting a release, so there
is nothing a check can run beforehand; it is confirmed at the next release.
That leaves the item non-delegable by derivation, which is the honest status
rather than an oversight.

**Done when.** Cutting a release through the documented entry point leaves
`make check` passing with no manual step, and the skill's release mode names
that entry point.
