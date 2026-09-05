# Declared clean-extraction compatibility fixtures

These fixtures remove two workspace-layout assumptions exposed by the first R17
clean extraction. They do not change the frozen source or evidence.

- `source/formal/` and `source/tools/` are byte-identical packaging mirrors of
  `source/paper-repo/formal/` and `source/paper-repo/tools/`. Seven legacy
  full-suite tests locate both the formal model and its Alloy/Java runtime by
  walking ancestors of `source/implementation`; the canonical R12 formal
  command continues to use the copies under `source/paper-repo/`.
- `git-metadata/` is a small deterministic synthetic Git metadata fixture whose
  only committed file is top-level `SOURCE_MANIFEST_SHA256.txt`. Five legacy
  benchmark tests require `git status` or `git rev-parse` even though R13
  deliberately excludes the live repositories' `.git` directories. E10 sets
  `GIT_DIR` to this fixture and `GIT_WORK_TREE` to the extracted package root.

The synthetic fixture is test compatibility metadata, not the source identity
and not the “final commit.” The authoritative identity remains
`source_manifest.json` with SHA-256 shown in the committed marker file. The R17
release manifest covers both mirrors and the fixture exactly.
