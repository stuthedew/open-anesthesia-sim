---
id: PL-FTP5
title: Record the Blender study protocol and the interface model's design provenance in a durable doc, so a session building the layout knows which Blender sources it may read, what it may carry across, and what the project attributes - the rule currently exists only as a paragraph inside ROADMAP item 34
status: untriaged
touches: README.md, docs/
added: 2026-09-16
---

**Problem.** Record the Blender study protocol and the interface model's design provenance in a durable doc, so a session building the layout knows which Blender sources it may read, what it may carry across, and what the project attributes - the rule currently exists only as a paragraph inside ROADMAP item 34

**Why it matters.** The project owner asked on 2026-09-16 whether there is a
good-faith way to study Blender's architecture for inspiration. The answer is
yes, and it has enough moving parts that a session meeting the question cold
will either re-derive it (a full research round) or guess. It currently lives
only as one paragraph inside ROADMAP item 34, which a session reads only if it
happens to be scoping item 34.

Four things the record should carry:

1. **Reading is not one of the GPL's restricted acts.** GPLv2 § 0: "Activities
   other than copying, distribution and modification are not covered by this
   License; they are outside its scope." Studying Blender's source is
   unrestricted; what is restricted is copying, modifying, translating (§ 2
   names translation explicitly) and distributing.
2. **Architecture sits mostly on the unprotectable side, but not entirely.**
   17 U.S.C. § 102(b) excludes "any idea, procedure, process, system, method of
   operation, concept, principle, or discovery", while *Computer Associates
   Int'l v. Altai*, 982 F.2d 693 (2d Cir. 1992) holds that non-literal
   structure can be protected and gives the abstraction-filtration-comparison
   test for deciding which. Practical consequence: the higher the abstraction
   at which a concept is carried across, the safer — "tiled non-overlapping
   panes, each hosting a swappable view kind, saved as named workspaces" is a
   method of operation; a transliterated `bScreen`/`ScrArea`/`ARegion` struct
   graph is structure.
3. **The prose sources are both better and more encumbered.** Developer Docs
   and HIG carry the rationale; both are CC-BY-SA 4.0 (share-alike), so
   paraphrase and cite, never paste. See `PL-P5QX`.
4. **What the project attributes.** A README or docs line saying the
   workspace/area/editor model is modeled on Blender's, studied from its
   published design documentation. Not legally required for ideas; it is this
   project's own provenance standard, and it is the answer to the spirit
   question rather than the letter one. Blender's own Copyright Rules handbook
   draws the same line in the other direction — it bars copyrighted elements
   from other software while encouraging designs that build on Blender's own
   design history.

**Done when.** The protocol and the attribution exist somewhere a session
building the layout will actually read, and ROADMAP item 34 points at it rather
than restating it.

**Scope note.** This is a provenance/docs item, not a licensing opinion, and it
is not a scoping round for item 34.
