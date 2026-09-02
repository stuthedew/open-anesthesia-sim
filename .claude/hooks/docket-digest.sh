#!/usr/bin/env bash
# SessionStart hook: emit a short digest of the docket into session context, so
# a session knows where its branch stands, that the queue exists, what is at
# the top of it, what is already in flight on a branch, and whether anything is
# waiting to be triaged - all without reading the store. The digest is
# deliberately a few lines: this text is resent on every turn of the session.
#
# `docket branch` runs first because it is what fetches, and both it and the
# digest's stranded-item line need refs a container does not hold: it clones
# one branch, so an item committed on a branch that never merged is invisible
# to it. The fetch used to sit in this file and run *after* the digest, so that
# line was computed from the previous session's refs while the comment above it
# claimed otherwise.
#
# Neither line is bash any more, and the branch check is the reason. It was
# fifty lines here, which is the only place it could run: at session start,
# once, on a condition that develops *during* a session - another session
# merges, and a discussion that is about to become implementation is sitting on
# a base that moved. A rule that can only run at session start cannot answer
# that, so it moved into `vcs.py`, where `bin/docket branch` asks it again at
# any moment.
#
# Fails silently if python3, git, the remote or the store is missing, so a
# checkout without any of them still starts cleanly.
set -uo pipefail

command -v python3 >/dev/null 2>&1 || exit 0

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
[ -x "$root/bin/docket" ] || exit 0
[ -d "$root/docs/items" ] || exit 0

# Deepen a shallow checkout once, before anything below reads a ref (PL-K2ZK).
#
# A container clones shallow, and `branches_in_flight` cannot find a merge base
# for a ref whose history was truncated - so it declines to answer, correctly,
# and goes on declining in every session for the life of that container. The
# answer it declines to give is one a single fetch makes available: measured
# 2026-09-02, 3.4 s for 52 commits to 542 and `.git` 8.8 MB to 11 MB, after
# which the decline is gone.
#
# Three properties matter and are held by tests rather than by this comment.
# It is guarded on the checkout actually being shallow, so it runs once per
# container and is a no-op every session after. It is bounded by `timeout`
# where that exists, so a hanging remote costs a session start seconds rather
# than holding it open. And it fails silently: no network, no remote, or no
# git leaves the checkout exactly as shallow as it was, and the deepen-me line
# `docket branch` prints is then still the remedy a person is given.
#
# `--unshallow` rather than a bounded `--deepen` because this repository is
# small enough to make the whole history the cheaper thing to reason about. If
# that stops being true, `--deepen=100` is the same guard with a bound.
if command -v git >/dev/null 2>&1 &&
  [ "$(git -C "$root" rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
  bound=""
  command -v timeout >/dev/null 2>&1 && bound="timeout 60"
  # Unquoted on purpose: empty when `timeout` is absent, two words when not.
  # shellcheck disable=SC2086
  $bound git -C "$root" fetch --quiet --unshallow origin >/dev/null 2>&1 || true
fi

# `--brief` because the digest below prints what is in flight, and printing it
# twice in text that is resent on every turn is the one cost this file is
# careful about.
"$root/bin/docket" branch --brief 2>/dev/null || true

"$root/bin/docket" digest 2>/dev/null || true
