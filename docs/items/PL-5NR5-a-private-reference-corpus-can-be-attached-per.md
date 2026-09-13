---
id: PL-5NR5
title: A private reference corpus can be attached per session with add_repo, which is the fourth candidate PL-XJ5P does not list: owner-supplied full texts re-uploaded into every session that needs them
priority: P2
effort: S
status: blocked
blocked-by: PL-XJ5P
classes: docs, infra
feature: provenance
touches: docs/references/README.md
added: 2026-09-13
---

**Problem.** Owner-supplied full texts reach a session only by being uploaded
into that session's chat. Nothing carries them to the next one, so a source
already read is re-provided by hand each time it is needed. Reported by the
project owner, 2026-09-13: both papers supplied to the session working
`PL-V6M0`, `PL-XJ5P`, `PL-RFLN` and `PL-1XPX` (the P1 needs-decision set) had
been provided in an earlier session and had to be provided again.

**Why it matters.** `PL-XJ5P` (citing-sources says there is always a route, but
a pre-abstract subscription paper has none) measured seven sources in the
terminal case and found the whole remaining provenance chain for the reference
patient's eleven parameters is made of it. Its "Decision needed" lists three
candidates. None of them is storage: the middle one — an owner-supplied extract
read without the repository holding the scan — has been exercised twice, and
both times the reading survived only as prose in the item, not as a document a
later session could re-open. So the per-session upload is the current
mechanism rather than a gap in it, and it scales with sessions rather than with
sources.

**A fourth candidate, verified against the documentation 2026-09-13.** A
private GitHub repository can be attached to a running session and cloned, with
no credential inside the sandbox:

- `add_repo` puts a repository in the session's scope mid-session, and the
  GitHub proxy then authenticates the clone. Per
  https://code.claude.com/docs/en/cloud-environments § "GitHub proxy", the
  git client inside the VM "uses a scoped credential, which the proxy verifies
  and swaps for your actual GitHub token", and GitHub traffic bypasses the
  environment's network allowlist entirely, so the **Trusted** level needs no
  change.
- The repository must be one the Claude GitHub App is installed on; private
  repositories are supported on that condition
  (https://code.claude.com/docs/en/claude-code-on-the-web § "GitHub
  authentication options").

**Why the cheaper-looking route was rejected.** A setup script writing the
corpus to disk would be snapshotted and reused by every later session — the
environment cache "keeps what the setup script writes to disk" — which would
make the corpus free rather than one call per session. It cannot reach the
repository, though: "GitHub API and release-asset requests reach only
repositories attached to the session, so a setup script that downloads release
assets from an unattached repository gets a 403", and the setup script runs
before any attachment exists. Closing that gap needs a personal access token in
an environment variable, and the same page warns that "anyone who uses the
environment can read the values" — the token would be readable by every command
in the sandbox. Naming it `GH_TOKEN` would additionally displace the proxy for
all GitHub traffic, since a token set there "passes through to the container
unchanged". One tool call per session buys the corpus without a secret; that is
the trade this item recommends taking.

**Relationship to the redistribution rule.** `docs/references/README.md` used
to say that "this repository is private, which is what makes that ordinary
personal use rather than redistribution". A separate private repository
restores that premise for the material `PL-SHG5` removed, without reopening it
for the public one. Nothing proposed here puts a publisher-copyright file back
into this repository.

**Decision needed.** Whether to stand up a private companion repository for
owner-supplied full texts, and whether that becomes a fourth candidate in
`PL-XJ5P`'s decision or is settled separately. `PL-Z3V5` is the half that
decides how much this is needed: with reading written back as extracted facts,
the corpus is consulted once per source rather than once per session.

## Verified end to end, 2026-09-13

The project owner created `stuthedew/open-anesthesia-sim-references` (private)
the same day. Both halves of the route were then exercised from a running
session rather than read about:

- `add_repo` attached it mid-session and reported `"status":"appended"`, with
  the session holding two repositories. The system prompt's Repository Scope
  list still showed only the original one, which is expected — the attachment
  widens GitHub scope without rewriting that text.
- `git clone --depth 1` over HTTPS succeeded with **no credential anywhere in
  the sandbox** and no change to the environment's network level, which stayed
  **Trusted**. The clone landed at `/home/user/open-anesthesia-sim-references`
  and reported `warning: You appear to have cloned an empty repository`, the
  repository having no commits yet.

So the cost of the corpus is one `add_repo` call plus one shallow clone, paid
by a session only when it actually needs a source. Nothing is required of the
environment configuration, and no personal access token exists to leak or
rotate.

**Two constraints found while verifying, both actionable.**

- **File size.** GitHub warns at 50 MiB and hard-blocks at 100 MiB for a normal
  git object, but a file added through the browser uploader is capped at 25 MB
  ([Repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits),
  [About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github);
  `docs.github.com` is blocked by this environment's egress proxy, so both were
  read through search rather than fetched). A 497-page scanned volume will
  exceed the browser cap, so the large items have to arrive by command line.
  Git LFS is the documented route above 100 MiB and is not recommended here
  until a file actually needs it — it adds a credential path through the proxy
  that the plain clone above does not have.
- **The corpus must not carry a `CLAUDE.md`.** `register_repo_root` loads an
  attached repository's `CLAUDE.md`, skills and plugins into the session. A
  storage repository that carried one would inject resident context into every
  session that attached it, for no benefit. It was deliberately not registered
  here.

**Where the durable pointer belongs, and why this item did not write it.** A
cold session has no way to learn the corpus exists. The right home is
`docs/references/README.md`, which already indexes sources and whose
"Redistribution" section is what closed the old route. That file is in
`PL-XJ5P`'s `touches` and `PL-XJ5P` is in flight, so editing it from here would
collide; the pointer is left for that item to write alongside its own decision.

## Corpus populated and indexed, 2026-09-13

Four papers were added by the project owner and are now named, indexed and
pushed. Citations verified against PubMed the same day; two of the four are
sources `PL-XJ5P` had measured as having no reachable route at all:

- Mapleson WW. *J Appl Physiol* 1963;18:197–204. PMID 13932730,
  DOI 10.1152/jappl.1963.18.1.197. On `PL-XJ5P`'s terminal list; `PL-6Q8N`'s
  primary lineage for the reference adult.
- Smith NT, Zwart A, Beneken JEW. *Anesthesiology* 1972;37(1):47–58.
  PMID 5050101, DOI 10.1097/00000542-197207000-00008. On `PL-XJ5P`'s terminal
  list via `PL-8SDL`. A scan with no text layer, so it needs page-image reading.
  PubMed's stored title misspells "distribution" as "disribution".
- Yasuda N, et al. *Anesth Analg* 1991;72(3):316–24. PMID 1994760,
  DOI 10.1213/00000539-199103000-00007.
- Nickalls RWD, Mapleson WW. *Br J Anaesth* 2003;91(2):170–4. PMID 12878613,
  DOI 10.1093/bja/aeg132.

**The corpus paid for itself on arrival.**
`tests/reference/test_published_wash_in_and_elimination.py` already uses
Yasuda's five-minute elimination vectors — sevoflurane 0.157 ± 0.020,
isoflurane 0.223 ± 0.024, n = 7 — as reference values, and until now cited them
with no holdable source behind them. The same file records the model at +3.79 SD
and +4.15 SD against those two, which is the discrepancy family `PL-RFLN` is
trying to settle for desflurane. `PL-RFLN` is in flight and did not have this
paper when it started.

**Correction to this item's earlier reasoning about the setup script.** The
setup script cannot fetch the corpus, which stands. But it is exactly the right
place for the *reader*: `poppler-utils` is **not** in the base image, and
without it every PDF read fails with `pdftoppm is not installed`. Installing it
costs an `apt-get update` plus install in every session that skips it, and the
environment cache "keeps what the setup script writes to disk", so one line in
the setup script pays it once per snapshot instead:

```bash
apt-get update -qq && apt-get install -y -qq poppler-utils || true
```

`|| true` because a failed install must not stop the session from starting.
`pdftotext -layout FILE -` is then far cheaper than page-image rendering and
works for every holding except the Smith 1972 scan.

**Done when.** `docs/references/README.md` names the private corpus: the
repository it lives in, the `add_repo`-then-clone route, and the
`poppler-utils` prerequisite the base image does not carry — so a session that
has never read this item can reach a held source. The corpus itself is already
standing and verified, which is why nothing here is about building it.

**Blocked on `PL-XJ5P`** (citing-sources says there is always a route, but a
pre-abstract subscription paper has none), which holds `docs/references/README.md`
in flight and whose own "Done when" already requires that file to say what now
stands where owner-supplied full texts used to. That sentence and this one are
the same sentence, so this item closes with `PL-XJ5P` rather than beside it.
Working it separately would mean two sessions resolving one paragraph.
