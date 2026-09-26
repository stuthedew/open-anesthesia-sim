---
id: PL-HK4J
title: The printed tag line can tag the wrong commit in a shallow clone: the oldest fetched commit reads as adding every file, so a cut older than the clone's depth resolves to that commit (release.tag_commands; cli._cut_seen_here and doc_check already refuse to name a cut there)
status: untriaged
feature: release-process
added: 2026-09-26
---

**Problem.** The printed tag line can tag the wrong commit in a shallow clone: the oldest fetched commit reads as adding every file, so a cut older than the clone's depth resolves to that commit (release.tag_commands; cli._cut_seen_here and doc_check already refuse to name a cut there)
