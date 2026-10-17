---
id: PL-8JV2
title: A schema version is checked as a whole number from 1 in three places (Migration, _check_version, oldest_readable) and carried as a bare int everywhere else - kept_file_name(True) writes workspaces.vTrue.json and set_aside_file_name(when, -1) writes a double hyphen - so build it once as a SchemaVersion type in serialization._read_version and carry the type through migrations, the store's Loaded and UnsupportedSchemaVersion (found reviewing PL-SSQW)
status: untriaged
added: 2026-10-17
---

**Problem.** A schema version is checked as a whole number from 1 in three places (Migration, _check_version, oldest_readable) and carried as a bare int everywhere else - kept_file_name(True) writes workspaces.vTrue.json and set_aside_file_name(when, -1) writes a double hyphen - so build it once as a SchemaVersion type in serialization._read_version and carry the type through migrations, the store's Loaded and UnsupportedSchemaVersion (found reviewing PL-SSQW)
