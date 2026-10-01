#!/usr/bin/env bash
# PostToolUse hook on WebFetch: attach to every result a note that it is a
# small model's answer about the page, not the page, so nothing in it is
# recorded as the page's words (`PL-B1BW`).
#
# **The failure.** On 2026-10-01 a session asked WebFetch to "Quote verbatim"
# code.claude.com's settings-reference entry for `env`, and was handed a list
# headed "Claude Code refuses to set these variables from `env` and skips them
# silently", one bullet reading "Variables whose names start with
# `CLAUDE_CODE_` or `ANTHROPIC_`, which are reserved for Claude Code's own
# configuration". The page's markdown carries neither sentence: its section
# names particular variables, and says Claude Code drops each one and logs a
# warning. The invented rule would have explained away the very measurement
# that session was recording (`PL-KLN5`); it was caught only because the
# session then read the page's `.md` with curl.
#
# **It is documented behaviour, not a fault.** WebFetch "runs the prompt
# against the content using a small, fast model. For most fetches, Claude
# receives that model's answer, not the raw page", and "Large pages are
# truncated to a fixed character limit before processing"
# (https://code.claude.com/docs/en/tools-reference, § "WebFetch tool
# behavior", read from the page's markdown 2026-10-01). The tool's own
# description says it too, and the session misread it anyway: an answer to a
# request for verbatim text looks like verbatim text.
#
# **Why a hook and not a clause.** The rule is needed the moment a result is
# in hand, which no read precedes, and a quotation can reach a reply before it
# reaches any file a path-scoped rule would load on. A `PostToolUse` hook's
# `additionalContext` is "added to Claude's context alongside the tool result"
# (https://code.claude.com/docs/en/hooks, § "PostToolUse decision control",
# read 2026-10-01), so the note arrives with every result, in a subagent as in
# the main session, and the resident set does not grow to carry it.
#
# **It decides nothing.** Every result gets the same note. Whether a session
# will quote from one is judgment, and guessing it from the prompt would miss
# the case that matters: a quotation lifted from an answer to a question that
# never asked for one. A failed fetch is `PostToolUseFailure`, and gets
# nothing.
#
# The note is fixed text, so it needs neither python3 nor the store. The
# payload carries the whole result, so it is read and discarded rather than
# left in a pipe nobody drains.
set -uo pipefail

cat >/dev/null

cat <<'JSON'
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "This WebFetch result is a small model's answer about the page, not the page: WebFetch is lossy by design and truncates a large page before that model reads it (https://code.claude.com/docs/en/tools-reference, § \"WebFetch tool behavior\"), and on 2026-10-01 it put a sentence into a documentation quote that the page does not carry (`PL-B1BW`). Use it for leads. Before you record or report a quotation, an exact value, or that the page does not say something, read the page itself with curl - adding `.md` to the URL where the site serves Markdown, as code.claude.com does - and take the words and the § heading from that."}}
JSON
