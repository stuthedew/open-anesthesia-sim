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

# The dead ends, immediately after the queue state and before the exception
# line below. Placed here because it answers a different question from
# everything above it: the digest says what is *open*, this says what has
# already been *closed off*, and a session that reads the first without the
# second proposes a refuted approach and has to be talked out of it in a reply.
#
# It prints the entry lines only, never `docs/dead-ends.md`'s preamble, which
# is instructions for adding an entry rather than for reading one - the split
# is what keeps the always-loaded half small, and `tools/dead_ends.py check`
# holds the emitted half to 30 entries and 4,000 bytes. That cap exists because
# this text is resent on every turn: measured on an agent benchmark, add-all
# memory curation reached 13.04% accuracy against strict selection's 38.86%
# (Xu et al., ACL 2026), and on identical questions a focused ~300-token prompt
# beat a ~113,000-token one by 30-60 points across 18 models (Chroma, 2025-07).
#
# Bare `python3` like `main_ci_status.py` below, and silent on every way it can
# fail - no file, no interpreter - so a checkout without it starts as it did
# before. `PL-NB35`.
python3 "$root/tools/dead_ends.py" emit 2>/dev/null || true

# Last, and usually silent. The whole-store `verify:` replay runs only on push
# to `main` (`PL-SDHR`: a pull request cannot have changed whether some *other*
# item's work merged, and replaying the store on every branch costs more than
# it buys), so when that replay fails it fails on a run no pull request shows.
# `main` was red across three consecutive merges with every session believing
# the tree was clean (`PL-0ZGK`).
#
# This reads that verdict and prints a line only when it is a failure - nothing
# when `main` is green, and nothing when the read itself fails, so an offline
# container starts exactly as it did before. It is deliberately not `bin/docket
# digest`'s job: `docket` answers from a bare checkout without a network and
# knows nothing about GitHub, and it should stay that way.
#
# Placed after the digest rather than before it because it is the exception
# line: on a normal session start it contributes nothing at all, and on a bad
# one it is the last thing read before the conversation.
python3 "$root/tools/main_ci_status.py" 2>/dev/null || true

# Beside the line above, and the same exception shape one step further out:
# that one reports a `main` whose checks went red, this a `main` whose history
# lost its reasoning. This repository's squash commit message *is* the pull
# request body, and 187 of 683 squash commits landed without one - 763,224
# characters that survive only on GitHub (`PL-843V`).
#
# Here rather than in `make check`, which was where it first went, for a reason
# about *when a session may act* rather than about cost. The remedy is a
# network fetch and a commit of files outside the current item's declared
# `touches`, which `CLAUDE.md`'s fix-now rule forbids inline and its
# housekeeping rule says must be filed first and worked under its own id. A
# `make check` advisory therefore fires at the one moment a session is not
# allowed to do anything about it, and an advisory nobody can act on trains a
# reader to skim the region a real one appears in. Session start is before an
# item is picked, which is when filing or starting one is exactly the right
# move. It is also the only place the answer is fresh: this reads `origin/main`
# and does no fetch of its own, and `bin/docket branch` above has just done one.
#
# One line, and silent when every loss is already recorded under
# `docs/pr-bodies/`. Detection reads `git log` and one directory listing, so
# unlike its neighbour it touches no network at all.
python3 "$root/tools/pr_body_check.py" 2>/dev/null || true
