# Dataset Factory admission

Use the Factory before any model run when the request needs a source-bound
task corpus. It does not infer a corpus from archive contents or historical
outcomes.

Run the no-spend source boundary with a sealed request and immutable archive:

```text
stet suite factory universe \
  --request <sealed-request.json> \
  --authority-root <root> \
  --source-id <id> \
  --source-path <relative-source.tar> \
  --source-digest <sha256:...> \
  --json
```

The source archive needs one `candidate_source_manifest/v1` that declares
`candidate_blind=true`, lists ordered exhaustive include/exclude decisions,
and binds each included candidate's base/head and solution/test patch digests
to files inside that archive. The source reference binds the enclosing archive
digest.

`needs_action` with `candidate_source_manifest` means the archive cannot supply
a lawful candidate universe. `manifest_valid_unadmitted` with
`prospective_universe_ledger` means the manifest is valid but still is not a
corpus, selection, qualification result, calibration result, or evaluation
authorization. Follow the typed next action; do not widen, substitute sources,
or treat unavailable authority as zero. Seal that ledger only with the exact
admission receipt and source references:

```text
stet suite factory universe seal \
  --request <sealed-request.json> --authority-root <root> \
  --source-id <id> --source-path <relative-source.tar> \
  --source-digest <sha256:...> \
  --admission-id <id> --admission-path <relative-admission.json> \
  --admission-digest <sha256:...> --json
```

This writes membership only. A shortfall remains a typed unavailable action;
it never becomes a selection or corpus claim.

Before qualification, use `stet suite factory universe readiness` with the
same sealed request, source, admission, and ledger references. It never turns
patches or commit text into task instructions, setup, test evidence, or a
corpus. If an archive lacks a complete candidate-bound task-materialization
manifest, it returns `candidate_task_materialization_manifest` as one typed
new-request action: adding an embedded source-bound manifest changes the
source digest and cannot repair the old request in place.

`stet suite factory universe materialization-plan` records the source-only
facts available for every included candidate (base/head, patch identities,
optional commit name, and declared command candidates). They remain unverified
and do not become instructions, setup, qualification, calibration, selection,
or a corpus. It returns a typed new-request action for the embedded
task-materialization manifest.
