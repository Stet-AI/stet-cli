# Dataset Build (Heavy)

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

Use this when the quick onboarding path is insufficient — need 50+ tasks,
complex CI, Docker debug loops, or multi-batch scaling.

```
pre-screen ──► understand + draft ──► iterate to green ──► scale + audit
     │                │                      │                    │
   VIABLE?        CI miner              ≥80% gold?          target count?
   └─ no: stop    ecosystem             └─ no: debug loop    └─ no: expand
                   docs reader           (up to 5×)           (batch discover)
```

## Pipeline Overview

```
discover (fetch change requests -> prefilter -> LLM scoring -> manifest)
  -> build (snapshots -> gold/F2P tests -> task dirs)
    -> select (gold replay valid launchable slice)
    -> harbor run -> validate
```

`discover` is cheap (no Docker). `build` is expensive (Docker containers by
default; `stet suite build --harbor-backend worktree --repo <path>` runs
base-fail/gold-pass verification in local git worktrees instead, no Docker
daemon needed, but requires a local repo with every task base commit).
The worktree backend uses Stet-owned `GOCACHE` and `TMPDIR` roots for each
task/command; it deliberately preserves an existing `GOMODCACHE` so it does
not redownload modules per task. Do not redirect `GOMODCACHE` per evaluation
cycle unless that isolation is explicitly required and the duplicate-download
cost is acceptable.
For Bazel tasks, selector queries keep writable output state isolated per task
while reusing Stet-owned Bazelisk and repository-download caches for the same
environment cohort during that build command. By default those caches live in
an ephemeral per-command root that command cleanup retires (unless
`--worktree-keep` protects it). Point `build.bazel_cache_root` /
`--bazel-cache-root` at a durable operator-owned directory to reuse the same
Bazelisk and `repository_cache` across suite build / regenerate-f2p runs; Stet
does not GC or delete that operator-supplied root.
For explicit `--base/--head` or fresh manifest builds, the default
`--source-mode auto` selects `reference` when the local worktree route proves
all reference prerequisites; rev-range builds stay portable until their
candidates are resolved. Every fallback is recorded in `build-summary.json`.
`--source-mode reference` keeps only
patches, task metadata, and verified local Git-authority
receipts in each task; it writes no task tarball, bundle, Docker collateral, or
snapshot. One shared shallow authority retains the complete selected base trees
but excludes unrelated history, so a large selected tree still needs equivalent
authority storage plus active verification worktrees.
Manifest and rev-range tasks share one authority while retaining exact per-task
commit/tree identity. This alpha path requires the worktree backend, L2 verification,
deterministic non-Bazel tests, `--llm-install-config=false`, and a non-empty
test patch. It is local and not Docker-portable. Reference manifest builds may
use `--retry-rejected`; direct rev-range retry remains outside the reference
path and must use a portable manifest workflow. Docker, Bazel, non-L2, and
generated install-config routes automatically stay portable; explicit
`--source-mode reference` remains fail-closed when they are incompatible.

For a repository disk budget, configure `build.storage_admission.mode: enforce`
with a positive `budget_bytes`. Stet decides before it creates or restarts the
dataset root, charges the logical union of `.stet`, registered external roots,
and the prospective output root, and records requested, backend-capped, and
effective validation workers in `storage-admission.json`. It can reduce
worktree concurrency only after the exact Git authority for the selected bases
has already been published and verified. For a first enforced reference build,
prepare only its selected base trees first:

```bash
stet suite bootstrap-authority --repo <repo> --base <base-sha> --max-authority-bytes <bytes> --json
```

The command verifies and stages one immutable exact-tree authority, refuses to
publish it when its logical bytes exceed the supplied cap, and emits its opaque
authority ID. It does not build a dataset or run tests. The cap applies before
authority publication; Git's temporary fetch/repack allocation and Docker
runtime storage remain separate physical risks. Without this bootstrap,
enforced `auto` falls portable when an authority is absent, while explicit
reference refuses before output creation. Enforcement is conservative logical/free-space admission, not a
physical-byte claim: portable source history and Docker/BuildKit runtime peaks
remain unknown, so portable builds refuse until those exposures have exact
bounds. Use `shadow` to inspect those receipts without blocking.
An enabled artifact-budget policy may compact or archive eligible completed
evidence as its separate, reviewed pre-build reconciliation step. A storage
admission refusal guarantees that Stet has not created or restarted the new
dataset output root or created a new Git authority.
`suite select` is the bridge from historically merged / selected task
candidates to a launchable rules slice: it oversamples built task dirs, runs
gold replay preflight, drops replay-invalid or unchecked tasks, and writes a
derived `stet.suite.yaml` with only gold replay valid `selection.task_ids`.
Bazel F2P selector receipts retain only query-proven positive labels; repo-relative patterns such as `src/...` are replaced before base/gold proof runs. When that focused proof succeeds and P2P would otherwise only fall back to the original broad command, P2P reuses its existing gold trial while the receipt retains the original broad command identity.
PR/MR-backed flows keep the `prs` source vocabulary for compatibility. GitHub
PRs use `gh`; GitLab MRs use `glab`. When an enterprise remote is ambiguous
such as `code.company.com`, pass `--change-provider github|gitlab` and, if
`origin` is not the right remote, `--change-remote <remote-or-url>`; use
`--source commits` when PR/MR provider access is unavailable.

## Resumability

The task .md IS the state. On resume, read it to determine current phase:

| .md contains | Resume from |
|---|---|
| Nothing / just frontmatter | Phase 0 |
| `## Pre-screen` filled | Phase 1 |
| `## Config Draft` with Harbor Dockerfile + harness manifest | Phase 2 |
| `## Iteration Log` with gold_pass >= 80% | Phase 3 |
| `## Build Log` with cumulative count >= target | Done — run audit checks |

## Phase 0: Pre-screen

Fast reject before investing time.

Checks:
1. **Change-request depth**: >= 500 merged PRs/MRs
2. **Recent activity**: change requests merged in last 6 months
3. **License**: Permissive (MIT, Apache 2.0, BSD)
4. **Test suite exists**: `tests/`, `test/`, `__tests__/`, `*_test.go`
5. **CI exists**: test-related GitHub Actions, GitLab CI, or equivalent CI
6. **CI is green**: inspect the provider's CI status; for GitHub,
   `gh run list --repo {owner}/{repo} --limit 5`
7. **Runnable test stack**: CI exposes deterministic test commands that can be
   reproduced in a Harbor Dockerfile. Stet is not limited to a fixed language
   list, but opaque, hosted-only, or unreproducible stacks may need harness work
   before they are viable.

Run a discover probe to measure pipeline yield:

```bash
# Narrow probe
stet suite discover --repo owner/repo --rev-range main~100..main --limit 50 \
  --min-complexity 3 --json --output $SCRATCH/prescreen-manifest.yaml

# Widen if 0 PASS
stet suite discover --repo owner/repo --rev-range main~500..main --limit 200 \
  --min-complexity 3 --json --output $SCRATCH/prescreen-manifest-wide.yaml

# Deep scan if still 0 PASS
stet suite discover --repo owner/repo --source commits --rev-range main~2000..main \
  --limit 500 --target-pass 5 --min-complexity 2 --json \
  --output $SCRATCH/prescreen-manifest-deep.yaml
```

Yield interpretation:
- >= 5% yield: VIABLE
- 1-4% on deep only: MARGINAL
- 0% on all probes: NOT VIABLE

**CHECKPOINT: Report verdict to user. Proceed to Phase 1 on approval.**

## Phase 1: Understand + Draft

Goal: produce a working `.stet/harbor.Dockerfile` plus
`.stet/stet.harness.yaml` by mining the repo's own CI and build files.

Launch 3 parallel subagents:

1. **CI Miner**: Read `.github/workflows/*.yml`, `.gitlab-ci.yml`, or
   equivalent CI config. Extract install steps, test commands, runtime
   versions, env vars, services, conditional logic.
2. **Ecosystem Analyzer**: Read package manager and build-system configs.
   Extract language/runtime constraints, package manager, dependency groups,
   workspace structure, native deps, and repo-level test runners.
3. **Docs Reader**: Read README, CONTRIBUTING, DEVELOPMENT docs. Extract
   setup instructions, test commands, gotchas, system deps.

Synthesize into:
- `.stet/harbor.Dockerfile` — repo-specific Harbor environment
- `.stet/stet.harness.yaml` — points `environment.dockerfile` at that file
- `stet init --test "<repo test cmd>"` — persist the canonical test command

**The test command must run the repo's actual test suite, not a smoke test.**
Priority: CI workflow > Makefile target > package.json script > README.
For monorepos or build-system-driven repos, preserve CI's runner and repo-level
flags, then prefer a broad positive target pattern that covers the changed area
and can be narrowed or kept broad by Stet. Avoid package-local commands, shard
wrappers, negative target filters, or leaf package-manager commands unless CI
shows that they are the real repo-level verifier.

Proactive gotcha handling:

| Issue | Prevention |
|---|---|
| Missing system tools | Install them in the Harbor Dockerfile |
| Wrong runtime or build tool version | Pin to CI matrix or repo config in the Dockerfile |
| Package manager or build-system network flakes | Add retry config and dependency prewarming in the Dockerfile |
| Repo expects setup steps before tests | Encode them in the Dockerfile, keep `stet init --test` focused on test execution |
| Monorepo command drift | Use CI's repo-level runner command; do not infer setup from unrelated leaf package files |

Harbor task exports default to runtime internet enabled. Keep package downloads
and equivalent dependency prewarming in the Dockerfile or install config anyway
so runtime execution does not depend on live setup fetches. Use the dependency
surface the selected test runner actually uses; for example, do not add
npm/pnpm/yarn installs just because a monorepo contains `package.json` when CI's
verifier is owned by another build system. When install steps are baked into the
exported Dockerfile, Stet renders verifier commands without replaying
`pre_install` / `install` at runtime. Use `env.allow_internet: false` in a
specific `task.yaml`, or `--harbor-disable-network` for an offline-only run,
only when the actual agent and verifier phases must run without network.
Cursor-backed Harbor exports also bake Cursor Agent into the task image, so
agent phases do not depend on runtime installer access. Model-backed solve
phases may need provider API access. Cursor-backed candidate runs inject
temporary CLI policy and hooks as a best-effort tool deterrent, then fail closed
in reports when the Harbor task explicitly disables network, for example via
`--harbor-disable-network`, and agent logs show WebFetch/WebSearch or shell
network-command use; do not treat `allow_internet = true` on those runs as
permission to move dependency setup or verifier installs back into runtime.
Even when network stays enabled, candidate guards deny obvious target-answer
routes such as public PR/commit pages, raw target-repo source, provider web
fetch/search surfaces, GitHub API answer endpoints, and target upstream git
history fetch/show/apply paths. Candidate-visible denials are intentionally
generic; use the operator artifacts for precise route and validity diagnostics.
Some provider CLIs still expose harness-looking launch details such as `/app`,
sandbox/trust flags, or headless execution modes; treat those as residual
eval-awareness risk until the provider wrappers support less revealing launch
metadata.
`--harbor-disable-network` runs tasks with `network_mode=none` (no DNS or
egress) and is rejected for model-backed agents, which cannot reach their
provider API offline; it is valid only for offline agents (oracle, nop).

The active Harbor export cache automatically converges to its 5 GiB ceiling and
reconciles toward 4 GiB using deterministic least-recently-used entries, except
for locked, in-flight, malformed, or unaccountable protected bytes. An
oversized new export is still delivered but bypasses retention; maintenance is
best effort and does not fail the requested export.

For Go tasks, build bakes the toolchain at the recipe's `runtime_version` and
freezes it (`GOTOOLCHAIN=local`) so the offline run never auto-downloads a
toolchain. A `go.mod`/`go.work` `toolchain goX.Y.Z` directive higher than
`runtime_version` now fails the build instead of silently fetching — raise
`runtime_version` to that patch level (a bare `1.25` resolves to `go1.25.0`).
Recognized standard worktree probes use authoritative runtime records
(including Bazel `Build label`) so wrapper banners and diagnostics cannot
satisfy strict version pins; custom probes retain legacy parsing.

Minimal harness contract:

```yaml
version: 1
schema: stet.harness/v1
runner:
  harbor_cmd:
    - harbor
environment:
  dockerfile: .stet/harbor.Dockerfile
```

If Harbor needs larger pods, keep the same Dockerfile and add Harbor resource
overrides under `runner.harbor_args`:

```yaml
runner:
  harbor_cmd:
    - harbor
  harbor_args:
    - --override-memory-mb
    - "8192"
    - --override-cpus
    - "2"
```

Use this for `ENOMEM` / OOMKilled failures during agent setup, including
Claude Code installation. Prefer `8192` MB first, then `16384` MB if the
install still OOMs. For compare-backed Claude Code runs, also lower
`--harbor-concurrency` to `2` when Stet reports
`harbor_claude_code_concurrent_setup_cache_skew`; Docker layer cache reuse can
make the second arm start installer-heavy containers more synchronously than
the first.

Suite-backed rules runs automatically apply `.stet/stet.harness.yaml` when it
exists. Use `eval.harness` in `stet.suite.yaml` only for a non-default harness
manifest (scalar path or `manifest:` object). Do not add `runner:` to
`.stet/stet.yaml`; runner settings live in `stet.harness/v1`.

**CHECKPOINT: Show the drafted Harbor Dockerfile, harness manifest, and test command with CI references. Proceed on approval.**

## Phase 2: Iterate to Green

Goal: >= 80% gold pass rate on a smoke batch.

```bash
stet init --repo /path/to/local/repo --yes --ai-provider <codex|claude|gemini|cursor> --test "<repo test cmd>"

stet suite discover --repo owner/repo --rev-range main~30..main --limit 10 \
  --output $MANIFEST_DIR/manifest.yaml

stet suite build --repo /path/to/local/repo --manifest $MANIFEST_DIR/manifest.yaml \
  --out $OUT --workers 2 --require-f2p=false
```

Portable builds publish one immutable repository source pack per unique base
commit under the dataset, then give each task a small receipt instead of a
task-local archive and history bundle. Tasks that share a base share those
bytes, including rejected tasks; Harbor materializes private compatibility
copies only while it runs.
Eligible Harbor tasks also share one labeled source-base image for the same
pack/platform recipe; each task keeps its post-source Dockerfile instructions.
Custom pre-source copies, behavior-mutated inputs, and command overrides fall
back to the legacy per-task image path rather than changing execution semantics.

For an older portable dataset that still has duplicate task-local
`repo.tar.gz` and `repo.bundle` files, preview a verified conversion first:
`stet artifacts sources migrate --dataset <dataset> --json`. It selects only
byte-identical, bundle-verified base commit/tree groups, leaves ambiguous files
protected, and reports logical reduction separately from unknown physical
reclaim. Apply only with its exact returned `--plan-id --apply`. The paired
`stet artifacts sources restore` preview/apply path recreates the exact legacy
files and prior receipt if a rollback is needed.

The source pack contains the tracked base tree, excluding Git metadata and
untracked files, and sanitizes escaping symlinks. New portable packs recursively
include exact locally available pinned submodule commit contents, subject to the
same escaping-symlink sanitization, without fetching; missing pinned objects fail
closed. Reference/Git-authority builds with gitlinks remain unsupported until
that authority carries recursive closure. Fresh builds automatically bypass
legacy snapshot cache generations without deleting them. Rebuild pre-fix packs,
including packs reused by a resumed build, because their receipts cannot prove
that closure.
The default cap is 500 MiB (524288000 bytes). For a larger monorepo, set
`build.max_snapshot_bytes` in `.stet/stet.yaml` or pass
`--max-snapshot-bytes N`; the flag wins over config. Any positive int64 value is
accepted, but raising the cap is operator-owned and can materially increase
disk use, extraction cost, and runtime. After changing the cap, rerun with
`--restart` or choose a fresh output directory so an existing build summary is
not reused.

On a Bazel repo, the fail-to-pass selector runs a `bazel query` per task in an
isolated output base, so each query pays a cold Bazel startup even when the same
query is about a second in a warm workspace. A query that exceeds the timeout
fails the task closed at `stage: selector` with
`runtime_classification: timeout` and is not retried. The default timeout is
10m. On `stet suite build`, raise it with `build.bazel_query_timeout` in
`.stet/stet.yaml` or `--bazel-query-timeout`, and the flag wins over config.
`stet dataset regenerate-f2p` takes the same `--bazel-query-timeout` flag but
reads no config file. Values must be positive Go durations, such as `20m`.

Cold Bazel startups also re-download external repos into the selector's
`repository_cache`. By default that cache is ephemeral per command, so a timed-
out first task never warms later runs. Set `build.bazel_cache_root` in
`.stet/stet.yaml` or `--bazel-cache-root` to a durable operator-owned directory
so Bazelisk and repository downloads persist across suite build /
regenerate-f2p invocations; the flag wins over config.
`stet dataset regenerate-f2p` accepts the same `--bazel-cache-root` flag but
reads no config file. Stet creates the directory if missing and never deletes
or GC-reaps an operator-supplied root. Unset keeps today's ephemeral
MkdirTemp root. This knob is applied on the worktree backend only; the Docker
harbor path does not share a selector repository cache today.

Keep the output root operator-controlled for the full build. Stet rejects a
symlinked output root and unsafe physical ancestry, and serializes concurrent
Stet builds on the resolved physical root, but is not an OS security boundary
against another process able to replace that root.

For manifest-backed builds, Stet freezes the exact input manifest and every
PASS-task patch before planning, then retains a sanitized authority copy under
the dataset. Reuse, resume, and rejected-task retry fail closed when the caller
manifest or retained authority no longer matches. Use `--restart` only when
intentionally replacing that dataset, or choose a fresh output directory.

The shadow `storage-admission.json` preview models logical exposure, not
physical allocation or reclaim. For portable builds it applies the snapshot
cap and Git-history proxy per unique source base. Base/head cardinality is
exact; manifest builds use parsed base identities; rev-range estimates remain
an upper bound until discovery resolves the slice. Docker/BuildKit, install
caches, and cross-filesystem copies remain explicitly unknown.

`--llm-install-config` defaults on (see the test_cmd-relevance note below), so
build needs a model client. Like `discover`, it resolves one from
`--ai-cmd`, `build.ai_cmd`, or `ai.default_provider` with a provider installed —
no explicit `--ai-cmd` needed once a provider is configured. Pass
`--llm-install-config=false` to build without one (lower-fidelity broad verifiers).
Without a recipe or LLM, the default install_config now infers `language` from the
test runner (e.g. `cargo`->rust, `pytest`->python) so runtime env (Rust's
`CARGO_NET_OFFLINE`) injects; Go stays `unknown` (relies on the go-runner sniff,
since the default carries no concrete Go toolchain version).

For a repo that ships a vetted recipe, prefer `--install-config <path>` (or
`build.install_config` in `.stet/stet.yaml`): it consumes the deterministic
recipe directly — a `.sh` that emits install_config JSON (run locally on the
host), or a static `.json` — bypasses LLM generation (no model client needed even
with `--llm-install-config` left on), and derives the allowlist from the recipe's
own commands so forms like `env PATH=… cargo test` and toolchain installers are
auto-allowed. A toolchain preflight then fails loud
(`toolchain preflight: rust test runner "cargo" is not installed …`) before any
fan-out/materialization for a non-base toolchain (Rust) the recipe doesn't
install, instead of a downstream "gold tests did not run". `stet init` on a Rust
repo scaffolds rustup/cargo into `.stet/harbor.Dockerfile` so `cargo test` runs unedited.

For Python repos that use `uv`, prefer the direct verifier command when one
exists, for example `uv run --frozen --no-sync coverage run -m pytest ...` or
`uv run --frozen pytest ...`. If CI needs a multi-step shell wrapper such as
`bash .stet/ci-test.sh`, pass it as the explicit configured `--test` command or
use a vetted `--install-config` recipe; do not ask the LLM install-config path to
invent an opaque wrapper.
When a generated install_config command invokes `uv` directly from `/app`, Stet
makes `uv` available before running the baked install layer. Generated install
and test commands cannot use `cd`, `&&`, or other shell chains; subdirectory-only
projects should fail closed under synthesis unless you route through a vetted
explicit recipe or operator path supported elsewhere. Init-generated uv starters
use an unpinned bootstrap; other Dockerfiles may receive Stet's default uv
bootstrap unless they already carry the `# stet-uv-toolchain` marker. If an
opaque wrapper hides the `uv` invocation, make `.stet/harbor.Dockerfile`
explicit about the required `uv` version before rerunning build.

For less common ecosystems, preserve the real CI verifier as an explicit
configured `--test` command instead of editing Stet's built-in allowlist. Stet
trusts operator-provided test commands exactly after shell-safety checks; the
built-in allowlist mainly constrains model-generated install/test commands.

### Fail closed when a repo is not buildable

`--llm-install-config` synthesis fails closed instead of fabricating a
non-working runner. When the repo needs a private registry, missing
credentials, or a setup the model cannot determine, the task is skipped loudly
under the distinct `install_config_unbuildable` reason (separate from
`install_config_failed`) with the model's stated reason in `build-summary.json`
— it does not emit an empty-install config that "succeeds" while proving zero
F2P tasks. The fix is to supply a deterministic `--install-config` recipe or
repair the environment (Dockerfile toolchain/credentials), then rebuild. For
inferred (Stet-generated) test commands, the synthesized verifier is rewritten
to an observable, cache-disabled, discovery-verified form (e.g. pytest gains
`-p no:cacheprovider`, a leading `--collect-only -q` discovery gate, and
`-v --color=no`); cache-disable and discovery have F2P-correctness value, the
verbose/no-color flags only aid log debuggability. Operator-supplied `--test`
commands are preserved verbatim and never rewritten.

For the interactive onboarding of an arbitrary repo, dispatch a subagent that
runs the agentic build-and-test loop, then feed its vetted result through the
trusted `--install-config` path rather than relying on one-shot synthesis. The
subagent's contract: confirm the project builds and tests from the repo root
(`/app`) — the runner executes install and the test command there and cannot
`cd` into a subdirectory, so a subdirectory-only project must fail closed rather
than onboard a recipe whose install lands in the wrong place; install
lockfile-aware (`npm ci`, `pip install -r`, `go mod download`, `cargo fetch`);
record only the
commands it actually ran successfully (no speculative or replaced steps); emit
an observable, discovery-verified test command that keeps the narrow selector;
and **fail closed — emit nothing if it cannot build**. It writes a vetted
`install_config.json`, which you then build with `--install-config <path>`.

Debug loop (up to 5 attempts). Ordered by frequency:

| Failure pattern | Classification | Fix |
|---|---|---|
| `command not found: make/cmake/gcc` | missing_binary | Add `apt-get install -y {binary}` to `.stet/harbor.Dockerfile` |
| `No such file: python3.X` / `node: not found` | wrong_runtime | Change runtime/toolchain in `.stet/harbor.Dockerfile` |
| `Timeout` / `exceeded time limit` | timeout | Keep the same test command; fix setup/runtime in the Dockerfile first |
| `ModuleNotFoundError` / `Cannot find module` | import_error | Add the missing dependency install to `.stet/harbor.Dockerfile` |
| `ConnectionError` / `fetch failed` | network_flake | Add retry config / package manager setup to the Dockerfile |
| `ENOENT` from setup hacks on old commits | path_drift | Simplify the Dockerfile; avoid commit-fragile file mutations when possible |
| vitest/jest per-test timeout | test_config | Prefer durable repo/env setup; patch configs only if CI already does something similar |
| `ENOMEM` / OOM killed / exit 137 | resource_limit | Increase Harbor pod memory if possible; if Docker Desktop cannot raise limits, reduce `--workers`, `--harbor-concurrency`, or `--command-workers`; inspect `docker events` to distinguish OOM from external SIGKILL |
| Docker daemon/network errors | infra_error | Check daemon health, stale containers, and stale networks; if no run is active, prune stopped containers and unused networks, then retry with lower effective concurrency |
| Lockfile version mismatch | lockfile_drift | Pin package manager version in `.stet/harbor.Dockerfile` |

`--llm-install-config` is **on by default** (it generates the install recipe and
may narrow generated verifiers, both of which lift dataset quality), so
`suite build` / `scenario generate` require `--ai-cmd` unless you pass
`--llm-install-config=false` to opt out (not recommended; you get lower-fidelity
broad verifiers).

After >= 80% gold pass, verify test_cmd relevance: pick a task with test
patch, confirm test_cmd runs those files. Under `--llm-install-config`, build
attempts runner-neutral selector evidence for generated whole-suite verifiers.
Explicit `--test` or config-provided test commands remain the task commands
unless the repo declares a `test_selector` config. During strict F2P proof,
Stet may derive flags-preserving Bazel label candidates when `bazel query` (or
Bazelisk) resolves a package pattern to actual test-rule labels and proves their
direct srcs, Rust crate srcs, direct data source files, or buildfiles cover
required test-patch directories. Large-package reverse-dependency recovery
first query-proves every changed source label; a missing or ambiguous source
abstains before any reverse-dependency query. Recursive patterns
are never recorded as strict F2P identities. An actual label is accepted only after the same dynamic
base-fail/gold-pass check as other targeted candidates. When Bazel candidate
derivation abstains (query pattern failure, the >16-label bound, or no
covering target), the build keeps the original broad command and reruns
base+gold for it under the same multi-run flake policy, accepting only on a
broad base-fail/gold-pass — recorded as `proof_strength: abstained_kept_broad`
with `fallback: keep_broad`. It never falls back to a partial or first-N label
subset. Infrastructure failures (disk/extraction errors, missing toolchain
binaries, selector crashes) classify as `executor_runtime_error`, skip the task
instead of minting a fallback proof, and are never recorded as `f2p_failed`.
If a base verifier fails before an intended changed test executes—for example,
zero-test import, collection, or generated-fixture setup failure—Stet records
`verifier_pretest_failure` and abstains instead of minting dynamic F2P.
Generated whole-suite verifiers may also narrow after
deterministic filesystem package/path/file proof for supported path runners.
Each task's existing
`build_logs/test_selection.json` path now carries `schema:
test_selection/v2`, stable reason codes, runner/target metadata, proof source
and strength, selected targets, covered paths, fallback, setup blocker class
when known, and a legacy v1 projection. Unsupported, ambiguous, malformed,
stale, or missing evidence keeps the broad command with `left_broad` or
`abstained`; selector coverage is corpus evidence, not model-quality evidence.
`proof_strength: selector_command_unverified` (reason `f2p_proposal_differential_unattested`)
is reserved for a base-fail/gold-pass result on a non-extractor-derived
command that lacks an attested named-test differential (>=1 named test
parsed as passing at gold and failing/absent at base from `go test -json` or
TAP output) — an exit-code-only differential alone never mints
`proven_dynamic_f2p` in that case. The headless setup agent's accepted oracle
proposal path is the built-in selection mode that binds a proposal-derived
command to this prover, so an accepted proposal without an attested
differential is what surfaces this value.

When the test command has no function-level extractor (an unrecognized runner)
and no accepted proposal binding, Stet still attempts a coarse file-level
recovery: it appends each changed test file from `test.patch` (added-line
hunks, deduped and capped) as a trailing positional argument and runs the same
base-fail/gold-pass loop. A successful proof is real F2P evidence but stamps
`proof_strength: narrowing_unverified` with `broadness: broad` and
`strictness_status: narrowing_unverified` — the runner may have ignored the
file argument and executed the whole suite, so file-level blast radius is not
claimed. If that rung also finds no proof, the abstain error names the
unrecognized command and the routes forward (enable the setup agent / oracle
proposal path, or a fixed manifest with `test_selector.fallback=keep_broad`).

Repos may declare a lower-trust selector input surface in `.stet/stet.yaml`:

```yaml
test_selector:
  runner: bazel
  selector_command: .stet/select-tests --changed-files-json <path>
  fallback: keep_broad
```

Stet records digest/provenance/trust state for this config. It does not treat
arbitrary selector-command output as proof unless Stet can normalize and
cross-check it.

### `test_selection` override (workspace layouts the auto ladder can't infer)

When the zero-config candidate ladder abstains on a custom layout (monorepos,
nx/turbo, bespoke runners, non-standard roots), declare a `test_selection` block
in `.stet/stet.harness.yaml` to supply the missing layout knowledge:

```yaml
test_selection:
  command_template: "npx vitest run {file_rel_project}{name}"
  path_strip_prefix: frontend        # optional, when no project matches
  projects:
    - glob: packages/*               # most-specific match wins
      cwd: packages/zod              # optional: run from this dir
      project_flag: "--project zod"  # optional: rendered as {project_flag}
```

Placeholders: `{file}` (repo-relative test path), `{file_rel_project}` (`{file}`
with the matched project's glob-dir or `path_strip_prefix` stripped), `{name}`
(quoted name filter rendered as ` -t '^name$'`, vitest/jest style; empty for
file targets), `{project_flag}`. Package-based runners (cargo/go/maven/gradle/
dotnet) select by package not file path, so use `{project_flag}`/`cwd` and omit
`{name}` for those.

Override candidates are tried **ahead of** the auto ladder but are still
proof-gated by the same base-fail/gold-pass run: a wrong block (unsafe path,
unknown placeholder, or a changed test file that matches none of the declared
`projects` globs) **fails the build loudly** — never a silent `repo_tests_only`
or a falsely-included cell. When `projects` is set, every changed test file must
match a glob; use `command_template` alone (no `projects`) for blanket coverage
of mixed layouts. The winning rung is recorded as `config-function#N` /
`config-file#N` in `DynamicProof.Rung`.

`stet init` pre-fills a **commented** suggestion when it detects a workspace
(pnpm / npm / nx / turbo / lerna / Cargo / go.work / Maven / Gradle / .NET);
review, adapt, and uncomment it. `stet dataset regenerate-f2p` operates on a
built dataset with no source repo, so it ignores the override and re-proves via
the auto ladder only. It runs directly on exported corpora: it resolves node PM
script aliases (`pnpm`/`yarn`/`npm test` -> the `vitest`/`jest` runner in
`package.json` scripts.test), splits a multi-step `test_cmd` (last entry is the
narrowed test command, earlier entries run as preamble first), and synthesizes
`solution.sh` when a task omits it. The gold pass-to-pass suite stays the broad
original command whenever an alias is resolved or a preamble exists.

**CHECKPOINT: Report iteration results. Proceed to scale on approval.**

To find a launchable rules slice from a built dataset without manually splicing
replacements:

```bash
stet suite select --suite-manifest .stet/rules/stet.suite.yaml \
  --target-valid 5 --oversample 4 --out .stet/rules/replay-valid \
  --change-manifest .stet/rules/stet.change.yaml --json
```

If the receipt is low-yield, treat it as historical replay attrition, not proof
that the merged change request failed tests. Follow the receipt's dominant invalidity
categories before widening the range or accepting a smaller exploratory slice.

## Docker Desktop Capacity Budget

Before scaling Docker-heavy build batches, check for stale state:

```bash
docker ps
docker system df
docker network ls
```

If no Stet/Harbor run is active and Docker has stale stopped containers,
Harbor task images, or unused per-run networks, inspect with Stet first:

```bash
stet harbor cleanup
```

Apply only the confirmed Stet-owned plan with `stet harbor cleanup --apply`.
Add `--prune-buildkit` only when broad Docker BuildKit cache cleanup is
acceptable. Do not delete `.stet` run roots or `~/.cache/stet` evidence
artifacts.

To discover where Stet is using disk, run `stet artifacts doctor` instead of
raw `du`; it reports per-root pressure plus, with `--global-caches`/`--docker`,
shared cache and Docker objects:

```bash
stet artifacts doctor --repo . --roots .stet,.tmp --global-caches --docker --json
```

Doctor inventories published reference-mode Git authorities as fully protected
storage with observed task reference counts. Compact cannot remove them yet;
`no_observed_reference` is diagnostic and is not deletion permission.
Doctor also emits a read-only lifecycle plan for managed roots, including the
valid `hot|compacted|archived|retired` state (or protected `unknown` for an
invalid/ambiguous receipt), local/restore-required/unavailable
capabilities, evidence consequences, and a metadata-bound preview ID. It does
not hash all artifact contents and is not mutation authority. Treat pins and
leases as separate safety constraints. An `unknown` exclusive physical reclaim
estimate is informational and never promises freed filesystem blocks.

Successful compare/run completions now auto-drop their regeneratable scratch
(`.harbor-dataset/` and `.smoke/`) while preserving evidence; set
`STET_KEEP_SCRATCH=1` to keep it for debugging. To reclaim a backlog, prefer the
native compact engine over manual `rm` so retention contracts and seals are
honored. Scope it to one root or the whole repo, and always preview first:

For a configured filesystem archive backend, `stet artifacts archive --repo .
--root <completed-root> --backend <id> --json` previews moving only raw replay
trajectories while keeping canonical reports, decisions, provenance, compact
patches, validation evidence, source packs, and Git authorities local. Apply
only with the returned current `--plan-id` plus `--apply`; restore uses the same
preview/review/apply flow. Physical reclaim remains `unknown`, so do not present
same-filesystem archival as disk-budget relief.

To prevent buildup, opt in with `stet artifacts policy --repo . --max-bytes N
--high-watermark-bytes N --low-watermark-bytes N` plus age and batch limits.
Admission and successful completion run one bounded pass. Stet compacts first
and archives only through a configured, validated backend; it never retires
automatically. `stet artifacts reconcile --repo . --json` reports logical
local reduction separately from unknown physical reclaim. New admission is
refused if the bounded pass still exceeds the hard budget.

Before considering retirement, refresh the stable-ID dependency graph with
`stet artifacts reachability --repo . --json`. Use expiring `stet artifacts
lease` records for active consumers; leases and pins are independent. `stet
artifacts retire --repo . --root <root> --json` persists a content-bound review
plan. Apply only with its exact `--approve PLAN_ID`; the command immediately
rechecks mutable safety inputs and exact deletion targets. Minimal local
reports, decisions, provenance, compact patches, and shared stores remain.
Receipt-only retirement is off by default and requires policy opt-in plus
explicit `--receipt-only --approve-receipt-only`; replay, repair, and regrade
then become unavailable and require a rerun.

```bash
# One root: status, preview, then reclaim (default --level all = compact bounded
# patches AND evict scratch; --level scratch|patch narrows).
stet artifacts status --root <root>
stet artifacts compact --root <root> --dry-run
stet artifacts compact --root <root>

# Repo-wide: dry-run by default; apply explicitly with an age guard.
stet artifacts compact --repo . --dry-run --json
stet artifacts compact --repo . --apply --older-than 14d

# Also include stale Docker/Harbor daemon resources in the same JSON envelope.
stet artifacts compact --root <root> --include-docker --dry-run
```

Add `--include-datasets` only when you also want to remove verified built
dataset directories, `--include-caches` to prune superseded out-of-repo
Harbor export caches, and `--include-docker` to also report/apply stale
Docker/Harbor daemon resources in the same JSON envelope (same safety gate as
`stet harbor cleanup`: refuses to remove anything if any Stet-owned Docker
resource is active anywhere; never prunes BuildKit cache without
`stet harbor cleanup --prune-buildkit`). Compact preserves
`patch_retention.v1.json` contracts and writes a `cleanup.v1.json` seal, but
never removes trajectories, APFS snapshots, or whole run roots.
`stet harbor cleanup` remains the dedicated Docker/Harbor surface; reclaim
refuses an active or partial root unless `--force`, and is always a no-op on a
pinned root (`stet artifacts pin`).

When Docker Desktop cannot allocate more memory, tune concurrency instead of
raising resource limits. Start with `--workers 2` for dataset builds. For eval
runs, budget effective concurrency explicitly:

- harness phase: `model-workers * harbor-concurrency`
- validation phase: `workers * command-workers`

Keep validation pressure around 5 or lower when Docker networking is strained.
For Claude Code compare/rules runs, prefer `--harbor-concurrency 2`; for Codex
runs, raise one axis at a time and watch `docker stats` / `docker events`.

## Phase 3: Scale + Audit

Discover in large batches using non-overlapping rev-ranges. Discover is cheap
(no Docker) — launch parallel discover batches on different ranges.

```bash
# Parallel discover
stet suite discover --rev-range main~200..main --limit 200 --output manifest-batch1.yaml
stet suite discover --rev-range main~400..main~200 --limit 200 --output manifest-batch2.yaml

# Sequential build (Docker is the bottleneck)
stet suite build --manifest manifest-batch1.yaml --out $OUT --workers 2 ...
stet suite build --manifest manifest-batch2.yaml --out $OUT --workers 2 ...
```

Course correction:

| Signal | Action |
|---|---|
| Repeated package-download flake | Harden the Harbor Dockerfile with retries / mirrors |
| Gold pass < 50% | Toolchain drift — fix config or stop |
| Discover pass < 15% | Diminishing returns |
| Docker errors | Kill zombies, reduce workers |

Stop expanding if 3 consecutive batches yield < 5 new tasks.

Every rejected candidate leaves `rejected/<taskID>/rejection.json` (task ID,
skip reason, error, timestamp, attempt) plus its preserved verifier logs, so a
rejection is always auditable after the fact. To re-verify eligible rejections
in place without redoing accepted work, rerun with `--retry-rejected`
(manifest mode only, mutually exclusive with `--restart`): it reuses accepted
task dirs byte-for-byte, retries only `f2p_failed` / `gold_validation_failed` /
`executor_runtime_error` classes, appends each retry under `attempts/<n>/`
without deleting prior receipts, and refuses a retry if the on-disk patch no
longer matches the manifest's recorded checksum. Build verification reruns
default to 2 attempts (`--flake-reruns N` to override); a divergent outcome
across attempts is rejected, never silently accepted.

For `--source-mode reference`, retry is still manifest-only: it reopens the
recorded immutable git authority and refuses altered patches, task identity, or
authority evidence before touching rejected evidence. It never recreates a
portable snapshot or rediscovers a rev-range.

Inline audit at target count:
1. Empty test patches -> flag for removal
2. Lockfile/CI-only artifacts -> flag
3. Patch size: reject < 80 lines or > 1500 lines
4. Non-test file ratio: flag > 80% test files
5. Spot-check ai_task quality

Update `apex/tasks/agent_docs/datasets.md` with the finalized recipe.

## Prompt shape (`--prompt-shape`)

`stet suite build` defaults to `--prompt-shape self-contained-natural`, which
emits the `ai_task` (imperative goal-first prose) verbatim. The manifest path
(`stet suite discover`) carries `ai_task` from discover-time enrichment. For
`--rev-range` and `--base/--head` paths, build generates `ai_task` after patch
split by calling the configured `--ai-cmd` against the split gold patch plus
PR/MR or commit context; the resulting provenance records `selected_source:
ai_task_generated` (vs `ai_task` for manifest-carried). Without `--ai-cmd`
under the default shape, rev-range tasks are skipped with reason
`ai_task_generation_unavailable` and base/head builds fail with the same
reason (single-task; no partial dataset is produced). If the AI call or the
parse of its output fails, the reason is `ai_task_generation_failed`. Pass
`--prompt-shape legacy` to opt out of natural-shape generation entirely.
Explicit `--prompt-shape self-contained-natural` keeps the existing hard
failure (`prompt_shape_requires_ai_task`) when `ai_task` cannot be produced.
Every task records the decision under `meta.prompt_provenance` in `task.yaml`,
and `build-summary.json` reports `prompt_shape_fallbacks`,
`prompt_shape_explicit_failures`, plus the two `ai_task_generation_*`
counters. For materialized tasks with selector evidence, `build-summary.json`
also includes a separate `test_selector` rollup with selector status,
reason-code, proof-strength, runner, target-kind, fallback, and legacy-v1
counts.

## Common Next Steps

Each phase checkpoint recommends one concrete next step:

- `approve`: proceed to next phase after reviewing checkpoint results
- `rerun`: retry the current phase after a config or toolchain fix
- `stop`: halt the pipeline at the current phase

## Harbor Dockerfile Starting Points

`stet init` generated Dockerfiles now install a real Go/Node+pnpm/Rust/Bazel
toolchain automatically, so you don't hand-add one for those languages; uv
repos still get an unpinned uv bootstrap. Use these as reference or as manual
starting points for a custom Dockerfile. Keep the actual repo test command in
`stet init --test`.

### Python (uv)
```dockerfile
FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624
RUN apt-get update -qq && apt-get install -y -qq git make curl && rm -rf /var/lib/apt/lists/*
# install Python/uv version that matches CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN uv sync --frozen --all-packages
```

### Node / pnpm
```dockerfile
FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624
RUN apt-get update -qq && apt-get install -y -qq git curl && rm -rf /var/lib/apt/lists/*
# install Node + pnpm versions that match CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN pnpm install --frozen-lockfile
```

### Go
```dockerfile
FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624
RUN apt-get update -qq && apt-get install -y -qq git curl build-essential && rm -rf /var/lib/apt/lists/*
# install Go version that matches CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN go mod download
```

### TypeScript (pnpm)
```dockerfile
FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624
RUN apt-get update -qq && apt-get install -y -qq git curl && rm -rf /var/lib/apt/lists/*
# install Node + package-manager versions that match CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN pnpm install --frozen-lockfile --prefer-offline
```

### TypeScript (npm)
```dockerfile
FROM ghcr.io/laude-institute/t-bench/ubuntu-24-04:20250624
RUN apt-get update -qq && apt-get install -y -qq git curl && rm -rf /var/lib/apt/lists/*
# install Node version that matches CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN npm ci
```
