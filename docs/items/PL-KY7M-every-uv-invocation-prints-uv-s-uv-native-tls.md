---
id: PL-KY7M
title: Every uv invocation prints uv's UV_NATIVE_TLS deprecation warning, 10 lines per make check run, because the remote container sets the variable uv renamed to UV_SYSTEM_CERTS
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.14
touches: Makefile
added: 2026-09-12
closed: 2026-09-12
pr: 497
verify: UV_NATIVE_TLS=true make sync 2>&1 | grep -c UV_NATIVE_TLS | grep -qx 0
---

**Problem.** Every uv invocation in a remote container prints:

```text
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be
removed in a future release. Use `UV_SYSTEM_CERTS` instead.
```

`make -n check` spawns 10 of them (`uv sync`, `ruff format`, `ruff check`,
`mypy`, `pytest`, and the five `uv run python tools/*.py` checks), and each
prints the warning exactly once - measured 2026-09-12, one line per invocation
for both `uv sync --locked --dev` and a bare `uv run python -c pass`. So a
clean `make check` opens and closes on noise the run cannot act on, and the
two lines visible before the first real finding are the ones a reader has to
scroll past to reach it.

**The variable is not this repository's.** `grep -rn UV_NATIVE_TLS` over the
tree matches nothing but prose in `PL-V87X` (the isort/formatter warning item,
closed 2026-09-02). It is exported by the Claude Code remote container -
`UV_NATIVE_TLS=true` - alongside `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`,
`CURL_CA_BUNDLE` and three more, all pointing at the agent proxy's CA bundle
at `/root/.ccr/ca-bundle.crt`. Nothing in the repository asked for it and
nothing in the repository can stop the container setting it; what the
repository controls is the environment it hands to the tools it spawns.

**Why it matters, and why it is not only noise.** `PL-V87X` measured this exact
output on its way out: of the 7 warning lines in a `make check` run on
2026-09-02, six were this one. It was left alone then as somebody else's
variable. The suite has grown since and so has the count, from 6 to 10.
`PL-ZBJ0` carries the general rule - an advisory that fires every run without
changing a decision is a defect in the advisory, because it costs attention
forever and trains a session to skim the output where a real finding also
appears.

The second cost is not cosmetic at all. The warning says the variable *will be
removed*. On the release that removes it, the container's setting stops
applying silently: no error, no warning, just a uv that no longer loads the
platform certificate store. Translating the variable now is also the fix for
that, and it is why the block translates rather than simply dropping the name.

**What uv 0.12.10 says.** `--native-tls` no longer appears in `uv sync --help`.
`--system-certs` does, documented as "Whether to load TLS certificates from the
platform's native certificate store", reading `UV_SYSTEM_CERTS`. Same
behaviour, new name.

**Done when.** `make check` prints no `UV_NATIVE_TLS` line in a container that
sets the variable, and uv still resolves against the index through the agent
proxy.

**Fixed 2026-09-12.** The `Makefile` translates the variable once, above the
targets, so every recipe inherits the new name and not the old one:

```make
ifdef UV_NATIVE_TLS
export UV_SYSTEM_CERTS := $(UV_NATIVE_TLS)
unexport UV_NATIVE_TLS
endif
```

`ifdef` makes the block inert on a machine that never set the variable, so a
local checkout is unaffected. Measured after the edit: a green `make check` is
**102 lines carrying 0 warnings**, against 10 `UV_NATIVE_TLS` lines before it -
and against the 104 lines and 7 warnings `PL-V87X` measured on 2026-09-02, so
the suite's whole warning budget is now spent on warnings that mean something.
A scratch makefile including this one reports `NATIVE=[<unset>]
SYSTEM=[true]` for what a recipe inherits.

**Verified safe on the proxy.** A real index fetch
(`uv pip install --dry-run --no-cache --refresh 'packaging>=24'`) succeeds
three ways on 2026-09-12: with the inherited `UV_NATIVE_TLS` (and the warning),
with `UV_SYSTEM_CERTS=true` and the old name unset (no warning), and with
neither set. The third is the informative one - `SSL_CERT_FILE` already points
uv at the proxy bundle, so `UV_NATIVE_TLS` is belt-and-braces in this container
rather than load-bearing. Translating it is therefore the conservative move:
it preserves whatever the container meant by it, wherever that does matter,
and costs nothing where it does not.

**What it does not cover.** Only processes make spawns. A session that types
`uv run pytest tests/unit/test_x.py` directly still gets one warning line. That
is 1 line rather than 10, and there is no lever that reaches it:
`.claude/settings.json`'s `env` block can set a variable but not unset one, and
uv warns on the mere presence of the old name.

**The `verify:` command covers both halves,** and was watched failing before the
work: `UV_NATIVE_TLS=true make sync` counted 1 matching line before the edit and
0 after. `make sync` completing is the second half - a certificate store that
failed to load fails the resolve rather than passing quietly.

**Nobody else held it.** All 12 branch refs in the checkout were read on
2026-09-12: no branch, merged or in flight, touched `UV_NATIVE_TLS`,
`UV_SYSTEM_CERTS` or `native-tls`, and no item in the queue or stranded on a
branch named the deprecation. Four open items also declare `touches: Makefile`
(`PL-7J96`, `PL-8XPQ`, `PL-QV5Y`, `PL-LWMS`); none is in flight, and this is
the smaller change.
