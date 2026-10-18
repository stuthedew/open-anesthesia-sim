# The YAML Test Suite's in-domain cases

`cases.json` holds the 254 cases of the YAML Test Suite that a front matter
could hold. `subprojects/docket/tests/test_frontmatter_suite.py` reads it. The
suite is maintained by the YAML project (https://github.com/yaml/yaml-test-suite).
This copy comes from its npm repackaging, `yaml-test-suite` 0.1.0
(https://www.npmjs.com/package/yaml-test-suite), because GitHub's archive
download answered 403 in the container where it was taken (`PL-P6LL`). The
tarball's SHA-256 was
`0f39975dd3410d889837a0ed530008707b009a74ea4450d0be1ff53e2c6e3f32`. `LICENSE`
carries both MIT notices.

The package holds 402 cases. 148 of them contain a line that opens with `---`,
`...` or `%`, which no front matter can contain, so they were left out. Of the
254 kept, 51 are cases YAML must refuse.

Each entry keeps the case's `id` (the suite's test id, a slash, and the case's
index within that test), its `name`, its `yaml`, and `fail`. A case YAML must
read also keeps `json`, the value the suite expects, as JSON text. That text is
`null` where the suite gives none, and it holds several values where the case
holds several documents.

To take it again, run `npm pack yaml-test-suite@0.1.0` in an empty directory
and unpack the tarball there. Then read each `data/*.js` module after its
`export default` as JSON, and keep each case whose `yaml` holds no line opening
with `---`, `...` or `%`.
