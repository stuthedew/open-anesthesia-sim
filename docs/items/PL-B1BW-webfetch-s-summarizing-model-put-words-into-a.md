---
id: PL-B1BW
title: WebFetch's summarizing model put words into a documentation quote: asked on 2026-10-01 for code.claude.com's settings reference verbatim, it returned a bullet saying env refuses every CLAUDE_CODE_ and ANTHROPIC_ variable, which the page's own markdown does not carry, so a quotation recorded in an item should be read from the page's .md with curl, not through WebFetch
priority: P2
effort: S
status: done
classes: defect
milestone: v0.5.21
touches: .claude/hooks/webfetch-quote-note.sh, .claude/settings.json, tests/unit/test_webfetch_quote_note.py, docs/ARCHITECTURE.md, .claude/rules/citing-sources.md, docket.toml
added: 2026-10-01
closed: 2026-10-01
pr: 1254
payoff: a WebFetch result arrives marked as a model's answer, with the curl route to the page's own words beside it, so a quotation it invented does not reach an item or a reply as the documentation's
verify: uv run pytest tests/unit/test_webfetch_quote_note.py && ! grep -qF 'and the page itself for an allowed one' .claude/rules/citing-sources.md
---

**Problem.** WebFetch's summarizing model put words into a documentation quote: asked on 2026-10-01 for code.claude.com's settings reference verbatim, it returned a bullet saying env refuses every CLAUDE_CODE_ and ANTHROPIC_ variable, which the page's own markdown does not carry, so a quotation recorded in an item should be read from the page's .md with curl, not through WebFetch

**Measured 2026-10-01, while closing `PL-9DYK`.** At 00:37Z a session asked
WebFetch to "Quote verbatim the full entry for the `env` settings key" from
https://code.claude.com/docs/en/settings-reference. The answer opened "Claude
Code refuses to set these variables from `env` and skips them silently", and
one bullet read "Variables whose names start with `CLAUDE_CODE_` or
`ANTHROPIC_`, which are reserved for Claude Code's own configuration". The
page's markdown, fetched with `curl` that minute and again at 01:40Z, carries
neither sentence. Its § "Variables Claude Code ignores in `env`" names
particular variables (`CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, the
operating-system directory variables, the telemetry exporters) and says Claude
Code "drops each one, apart from a few values that turn telemetry off, and logs
a warning you can see with `claude --debug`". The invented prefix rule would
have explained away the measurement that session was recording, an unset
`CLAUDE_CODE_SUBAGENT_MODEL` (`PL-KLN5`); reading the `.md` is what caught it.

**It is documented behaviour.** WebFetch "runs the prompt against the content
using a small, fast model. For most fetches, Claude receives that model's
answer, not the raw page", and "Large pages are truncated to a fixed character
limit before processing" (https://code.claude.com/docs/en/tools-reference,
§ "WebFetch tool behavior", read from the page's markdown 2026-10-01). The
tool's own description says it "answers `prompt` against it using a small fast
model". The session had both and misread them: an answer to a request for
verbatim text looks like verbatim text.

**Why it matters.** This project writes its working rules on quotations of
Claude Code's documentation: 27 item files and eight standing documents cited
code.claude.com on 2026-10-01. A sentence the page does not carry, recorded as
its words, is obeyed by every later session and checked by nothing, and the
owner reads a quotation as the reference that lets them verify a claim.

**Built: a `PostToolUse` hook on WebFetch,
`.claude/hooks/webfetch-quote-note.sh`.** Every successful result arrives with
a fixed note: it is a model's answer, use it for leads, and read a quotation,
an exact value or a claim of absence from the page itself with `curl`, adding
`.md` where the site serves Markdown. A hook rather than a clause because the
rule is needed the moment a result is in hand, which no read precedes, and a
quotation can reach a reply before any file a path-scoped rule loads on; the
hook's header carries the case. Two routes were weighed and not taken. Resident
prose would cost every session for a rule needed only after a fetch. A
quote-checking script would need the network, so it could not run in
`make check`, and `curl` with `grep -F` already does the comparison: the
benefit was unclear, so no.

`.claude/rules/citing-sources.md` said WebFetch returns "the page itself for an
allowed one", which the documentation above contradicts; it now says what the
result is and sends quotations to `curl`. `docs/ARCHITECTURE.md`'s wired-hooks
count is ten.

**Not done here: the quotations already recorded.** Which of the live
documents' quotations came through WebFetch is unrecorded, and checking them
against their pages is its own item, `PL-124X`.

**Done when.** A WebFetch result carries the note, pinned by
`tests/unit/test_webfetch_quote_note.py` (wiring by exact tool name, valid
output under a page-sized payload), and `.claude/rules/citing-sources.md` no
longer says WebFetch returns the page.

**Generator check.** An external behaviour nothing modelled, what a WebFetch
result is: a model's answer rather than the page. No head's `misread:` states
it, and the four other items naming WebFetch are about egress refusals; a
one-off.
