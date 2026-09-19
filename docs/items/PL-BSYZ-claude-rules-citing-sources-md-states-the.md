---
id: PL-BSYZ
title: `.claude/rules/citing-sources.md` states the egress refusal as a standing fact measured 2026-09-04, so it will tell sessions not to retry doi.org and Crossref the moment the environment's network policy opens
priority: P2
effort: S
status: done
classes: defect
touches: .claude/rules/citing-sources.md
added: 2026-09-19
closed: 2026-09-19
pr: 728
verify: grep -qF 'the indexes opened and the publishers did not' .claude/rules/citing-sources.md
---

**Problem.** `.claude/rules/citing-sources.md` states the egress refusal as a standing fact measured 2026-09-04, so it will tell sessions not to retry doi.org and Crossref the moment the environment's network policy opens

**Where.** `.claude/rules/citing-sources.md`, which loads on
`docs/references/**`, `docs/MODEL.md` and `src/anesthesia_sim/data/**`. The
section carried this heading when the problem was found, and this item's work
replaced it — quoted in a fence because the rename is the item's own subject:

```text
## Direct HTTP to publishers and indexes is refused
```

**What it says now.** That the egress proxy rejects the tunnel itself, measured
2026-09-04 against `doi.org`, `api.crossref.org`, `api.openalex.org`,
`www.sciencedirect.com`, `link.springer.com`, `arxiv.org` and NCBI's own hosts;
and then, as instruction rather than observation, *"Do not retry, do not look
for a proxy around it, and do not treat it as the environment misbehaving."*
The section routes every literature question to the PubMed MCP server and the
private corpus on the strength of it.

**Why it will be wrong.** The measurement is a fact about an environment
setting, not about this project, and the project owner is actively trying to
change that setting - they reported on 2026-09-19 having set the network policy
to allow all domains. The instruction outlives the measurement: once egress
opens, a session that reads this rule will decline to fetch a DOI it could now
resolve, and will reach for a second-hand route instead. That is worse than the
current state, because the rule reads as settled rather than as dated, and
because `CLAUDE.md` requires consulting the source rather than memory - this
would block the better route while sounding like it was protecting it.

**Measured 2026-09-19, and the policy is not open yet**, which is why this is
filed rather than fixed. The gateway answers `403 Forbidden` to the CONNECT for
every host outside a GitHub-only allowlist: `api.github.com` 200,
`raw.githubusercontent.com` 301, `github.com` 400 (reached), against
`example.com`, `www.google.com`, `docs.github.com`, `help.github.com` and
`doi.org` all refused. A container provisioned fresh 16 minutes later, in the
same and only environment (`env_...bJnCq`, "Default"), measured identically -
so this is the environment's live policy rather than a stale container.

**Done when.** Either the policy is open and this section is rewritten to match
what is then reachable - keeping the dated measurement as history and moving
the "do not retry" instruction to whatever is genuinely still refused - or the
policy stays shut and the section gains the one sentence it is missing: that
this is an environment setting with a date on it, re-measurable in one command,
rather than a property of the project.

**How to re-measure**, from any session:

```sh
for h in doi.org api.crossref.org www.sciencedirect.com pubmed.ncbi.nlm.nih.gov; do
  printf '%-28s %s\n' "$h" \
    "$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "https://$h/" 2>&1 | tail -1)"
done
```

`000` is the CONNECT refused; anything else is the host reached. The proxy's own
log names the reason: `curl -sS "$HTTPS_PROXY/__agentproxy/status"`, field
`recentRelayFailures`.

**Found.** 2026-09-19, in `PL-0SCG`, when the project owner asked why
`help.github.com` was still blocked after they had opened the network policy.

**The access level is `Custom`, not `Full`** (project owner, 2026-09-19,
ratified, over `Full` - chosen because this repository is public, its copyright
exposure is not yet closed, and an allowlist is a record of what a session
could reach where `Full` is not). Verified against
`https://code.claude.com/docs/en/cloud-environments` the same day: the
**Network access** field takes four levels - `None`, `Trusted`
(the default), `Full` (any domain) and `Custom` (own allowlist, optionally
including the defaults) - set from the environment dialog at `claude.ai/code`.
There is no organization-level allowlist an admin can push over it.

**Measured before the change, 2026-09-19**, and matching the documented
`Trusted` list host for host - which is what establishes that the environment
was still on `Trusted` rather than on a custom list resembling it. Reachable:
`api.anthropic.com`, `docs.claude.com`, `code.claude.com`,
`platform.claude.com`, `claude.ai`, `github.com`, `api.github.com`,
`raw.githubusercontent.com`. Refused at the CONNECT: `doi.org`,
`docs.github.com`, `help.github.com`, `anthropic.com`, `console.anthropic.com`,
`support.claude.com`, `status.claude.com`, `example.com`, `creativecommons.org`,
`releases.astral.sh`.

**The allowlist adopted** covers the literature hosts this rule names, the
Anthropic hosts outside the default list, Blender (project owner, 2026-09-19 -
developer documentation and design reference for the interface work), plus
`docs.github.com` and `releases.astral.sh`. Blender and Anthropic are entered
as `*.` wildcards deliberately: the subdomains could not be confirmed from a
session that could not reach them, and a guessed hostname is the failure this
rule exists to prevent.

**So the rewrite has two halves, not one.** Re-measure with the command above
and correct what the section claims is refused; and keep the section, because
`Custom` means some hosts genuinely stay refused - the rule becomes a statement
about an allowlist with a date on it rather than about the environment being
closed.

**No check can replace the dated sentence, and that is structural rather than
a gap in the tooling.** The allowlist is a property of the *cloud environment*,
enforced at the egress gateway outside the session's sandbox; nothing in this
repository can read it, set it, or scope it per-repo. Verified 2026-09-19
against `code.claude.com/docs/en/cloud-environments`: environment selection is
a UI pick on the Desktop, mobile and web surfaces, and only
`remote.defaultEnvironmentId` - which binds `claude --cloud` alone - is
settable from a repository's `.claude/settings.json`. A committed setting that
bound the terminal and not the Desktop was considered and refused on those
grounds (project owner, 2026-09-19, ratified, over a second environment
selected per session): it is a guarantee that silently does not hold on the
surface this project actually uses.

So `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" does
not reach this one - the decidable part sits outside the tree. What the
rewrite owes instead is the honest shape: the date, the command that
re-measures, and no claim that survives the next environment edit.

## Done, 2026-09-19

**Step 1 first: the policy change was verified before anything was rewritten.**
Ten hosts, all answering with an HTTP status and none with `000`. Had any come
back refused, the brief's instruction was to stop and report rather than record
a half-open allowlist as open.

**Then the control probe, which is what shaped the rewrite.** Ten reachable
hosts would have supported "egress is open"; that claim is falsified by finding
anything still refused, so hosts *not* on the adopted list were probed too.
Four of six came back `000` — `example.com`, `www.google.com`, `www.nejm.org`
and `en.wikipedia.org` — and `www.w3.org`, `www.icrp.org`,
`journals.sagepub.com` and `epubs.siam.org` followed. So `Custom` is a genuine
allowlist and the section survives, exactly as the brief predicted.

The shape that emerged is sharper than "some hosts stay refused": **the indexes
opened and the publishers did not.** `doi.org`, Crossref, OpenAlex, PubMed,
arXiv, Springer's `link.` host and WorldCat all answer; NEJM, SIAM, Sage, W3C
and ICRP do not. That makes identifier and metadata verification a direct call
while leaving full text on the PubMed and corpus routes, which is why both
survive the rewrite rather than being retired.

**Two measurement artifacts were excluded from the evidence.** `pypi.org` and
`api.anthropic.com` answer, but both sit in the proxy's `noProxy` list and
bypass the gateway entirely, so neither says anything about the allowlist. The
rewrite says so, because reading one of them as proof that egress is open is
the obvious next error.

**The trap the rewrite exists to head off.** A refused host and a bot-blocking
publisher both put `403` on the screen: the gateway answers `curl: (56) CONNECT
tunnel failed, response 403` with `%{http_code}` `000`, while
`www.sciencedirect.com` — which is reachable — answers `HTTP/1.1 200 Connection
Established` and then `HTTP/2 403`. The old section's own evidence sentence
quoted the first string, so a session skimming for `403` would now misread a
reachable source as blocked. `WebFetch` disambiguates, returning a structured
`EGRESS_BLOCKED` for the first case and the page for the second; both were
verified.

**Kept as history, per the brief:** the 2026-09-04 `Trusted`-era measurement,
which is what explains why the PubMed MCP server and the private corpus were
adopted. Neither is obsolete; the publishers that made them necessary are still
refused.

**Corrected, per the brief:** the instruction "Do not retry, do not look for a
proxy around it" is gone, since it would now stop a session resolving a DOI it
can reach. What is kept is the half that is still true — a refusal licenses no
inference, and least of all a fall back to memory — plus an explicit refusal to
evade the gateway, which is a decision the project owner took rather than an
obstacle.

**A rider found and not fixed here:** `PL-5MT4`, a DOI in
`core/matrix_exponential.py` that does not resolve. Filed rather than fixed
because it is outside this item's `touches`.

**One anaphor this rewrite broke and repaired:** the PubMed section opened
"Verified the same day", which pointed at the 2026-09-04 measurement when it
was the nearest date above. It now names the date.
