---
id: PL-JX2T
title: Decide what to do with origin/Review_articles: one unattributed commit ahead of main that no guard can see
priority: P2
effort: S
status: done
classes: docs
feature: provenance
touches: docs/references/README.md, docs/MODEL.md, README.md, .gitattributes
added: 2026-09-04
closed: 2026-09-04
pr: 298
verify: python3 tools/doc_check.py check && test -f docs/references/schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf
---

**Problem.** `origin/Review_articles` held one commit `main` did not — `556d454
Added review articles on math models`, from before the `claude/` branch
convention. Its name carried no item id, its subject led with none, and it had
never merged, so `docket flight`, `show`, `next`, `concurrent` and the digest
all read it as nobody's work. It was the exact shape `PL-CP74` is about,
sitting on the remote.

**Decision (project owner, 2026-09-04).** Keep the PDFs as references, move them
somewhere appropriate, merge, delete the branch.

**What landed.** `docs/references/`, holding both documents under sortable
`author-year-title` names and a `README.md` that carries the full citation for
each — the part that survives if the files ever have to be removed.

- Baker AB, Farmery AD. Inert gas transport in blood and tissues. *Compr
  Physiol*. 2011 Apr;1(2):569–92. DOI `10.1002/cphy.c100011`, PMID 23737195.
  Confirmed against PubMed; the branch filename credited only Baker, and the
  file's own XMP carries Wiley's legacy DOI `10.1002/j.2040-4603.2011.tb00337.x`
  for the same article.
- Schüttler J, Schwilden H, eds. *Modern Anesthetics*. Handbook of Experimental
  Pharmacology vol. 182. Springer; 2008. DOI `10.1007/978-3-540-74806-9`. The
  whole 497-page volume.

Content was moved rather than `git merge`d. The branch's own commit message said
*"Not intended for branch to be merged as is"*, and merging would have put both
blobs in the history at repository-root paths as well as at their real ones. One
copy of each blob, at the path it belongs at; `556d454` is named here and in the
references README so the provenance survives the branch's deletion.

**Three things found while doing it.**

`.gitattributes` did not exist, and git's per-file text heuristic had stored the
Baker PDF *as text* — 6068 lines of mojibake in the diff. The bytes survived
the round trip intact (`%%EOF` and `startxref` verified, byte counts unchanged),
so nothing was corrupted, but a future line-ending normalization would have
broken the xref offsets. `*.pdf binary` is now declared.

Both files are publisher-copyright works. The repository is private today, which
is what makes holding them ordinary personal use — and it is why the references
README states plainly that they must come out *before* any change to repository
visibility, and that taking them out means a `git filter-repo` pass and a
force-push rather than a delete commit.

They cost 6.7 MB of history that every container clone pays: the session-start
digest hook runs `git fetch --unshallow` once per container, measured at 3.4 s
for a `.git` going 8.8 MB to 11 MB, and this roughly doubles that. Accepted
rather than mitigated — Git LFS would be new infrastructure for two files.

**Where the owner's note pointed.** The branch commit added: *"lots of relevant
stuff in article on anesthesia considerations for down the road plans like
implementing IV and anesthetic depth"*. Both are already on the map —
`ROADMAP.md` "Planned milestones" items 13 (IV pharmacokinetic and effect-site
models) and 14 (a modular hypnosis/eBIS effect model) — so this is sourcing
material for those, not new scope, and the references README says so.

**Done when.** The branch is merged behind an item, deleted, or explicitly kept
with that decision recorded here. Done: content landed under `docs/references/`,
branch deleted.
