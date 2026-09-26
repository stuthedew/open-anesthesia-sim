---
id: PL-QFCR
title: arming.TOOLING and GATE write this repository's layout into the docket package, which reads every other path it depends on from docket.toml
status: untriaged
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/config.py, docket.toml
added: 2026-09-25
---

**Problem.** arming.TOOLING and GATE write this repository's layout into the docket package, which reads every other path it depends on from docket.toml

**Found** building `PL-K6B2`, whose `touches` reach neither `config.py` nor `docket.toml`, so the tooling's path went in as a module constant beside `claims.CUTOVER_MARKER`, the one precedent. `config.py` says of `notes_file` that the package "keeps no notion of any particular repository's layout"; `CUTOVER_MARKER` goes when `PL-CH3Z` lands, and these two stay. A `docket.toml` field is a new field, which the generator pause holds.
