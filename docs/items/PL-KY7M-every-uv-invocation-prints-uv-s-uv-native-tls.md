---
id: PL-KY7M
title: Every uv invocation prints uv's UV_NATIVE_TLS deprecation warning, 10 lines per make check run, because the remote container sets the variable uv renamed to UV_SYSTEM_CERTS
status: untriaged
feature: dev-tooling
touches: Makefile
added: 2026-09-12
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

**Why it is worth a line of Makefile.** `PL-V87X` measured this exact noise on
its way out: of the 7 warning lines in a `make check` run on 2026-09-02, six
were this one. It was left alone then as somebody else's variable. The suite
has grown since and so has the count, from 6 to 10. `PL-ZBJ0` carries the
general rule - an advisory that fires every run without changing a decision is
a defect in the advisory, because it costs attention forever and trains a
session to skim the output where a real finding also appears.

There is a second cost, which is not cosmetic. The warning says the variable
*will be removed*. On the release that removes it, the container's setting
stops applying silently: no error, no warning, just a uv that no longer loads
the platform certificate store. Translating the variable now is also the fix
for that.

**What uv 0.12.10 says.** `--native-tls` no longer appears in `uv sync --help`.
`--system-certs` does, documented as "Whether to load TLS certificates from the
platform's native certificate store", reading `UV_SYSTEM_CERTS`. Same
behaviour, new name.

**Proposed fix.** Translate the variable at the top of the `Makefile`, so every
recipe line inherits the new name and not the old one:

```make
# The Claude Code remote container exports UV_NATIVE_TLS, which uv renamed to
# UV_SYSTEM_CERTS and now warns about once per invocation - 10 lines a `make
# check`. Translate it rather than drop it: the setting is the container's
# intent, and uv will remove the old name.
ifdef UV_NATIVE_TLS
export UV_SYSTEM_CERTS := $(UV_NATIVE_TLS)
unexport UV_NATIVE_TLS
endif
```

Verified 2026-09-12 that GNU make does export the new name and does withhold
the inherited one from recipe lines: a probe target printed
`NATIVE=[<unset>] SYSTEM=[true]`. The `ifdef` makes the block inert on a
machine that never set the variable, so a local checkout is unaffected.

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

**Close-out owes both halves.** `grep` that the block landed, and a run that
proves TLS still works through the proxy - the `verify:` line above covers the
first and `make sync` completing covers the second, since a broken certificate
store fails the resolve rather than passing quietly.

**Nobody else holds this.** All 12 branch refs in the checkout were read on
2026-09-12: no branch, merged or in flight, touches `UV_NATIVE_TLS`,
`UV_SYSTEM_CERTS` or `native-tls`, and no item in the queue or stranded on a
branch names the deprecation.
