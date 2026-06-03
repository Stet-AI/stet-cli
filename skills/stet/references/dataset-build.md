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

`discover` is cheap (no Docker). `build` is expensive (Docker containers).
`suite select` is the bridge from historically merged / selected task
candidates to a launchable rules slice: it oversamples built task dirs, runs
gold replay preflight, drops replay-invalid or unchecked tasks, and writes a
derived `stet.suite.yaml` with only gold replay valid `selection.task_ids`.
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
7. **Language supported**: Python, TypeScript/JavaScript, or Go

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
2. **Ecosystem Analyzer**: Read package manager configs. Extract language,
   package manager, dependency groups, workspace structure, native deps.
3. **Docs Reader**: Read README, CONTRIBUTING, DEVELOPMENT docs. Extract
   setup instructions, test commands, gotchas, system deps.

Synthesize into:
- `.stet/harbor.Dockerfile` — repo-specific Harbor environment
- `.stet/stet.harness.yaml` — points `environment.dockerfile` at that file
- `stet init --test "<repo test cmd>"` — persist the canonical test command

**The test command must run the repo's actual test suite, not a smoke test.**
Priority: CI workflow > Makefile target > package.json script > README.

Proactive gotcha handling:

| Issue | Prevention |
|---|---|
| Missing system tools | Install them in the Harbor Dockerfile |
| Wrong Node/Python version | Pin to CI matrix version in the Dockerfile |
| Package manager network flakes | Add retry config in the Dockerfile |
| Repo expects setup steps before tests | Encode them in the Dockerfile, keep `stet init --test` focused on test execution |

Harbor task exports run agent solve and verifier test phases without live setup
fetches by default. Keep package downloads, `go mod download`, `cargo fetch`,
and equivalent dependency prewarming in the Dockerfile or install config so the
runtime can execute from cached dependencies. When install steps are baked into
the exported Dockerfile, Stet renders verifier commands without replaying
`pre_install` / `install` at runtime. Use `env.allow_internet: true` in a
specific `task.yaml` only for tasks whose actual tests legitimately require
live internet. Cursor-backed Harbor exports also bake Cursor Agent into the task
image, so agent phases do not depend on runtime installer access. Model-backed
solve phases may need provider API access. Cursor-backed candidate runs inject
temporary CLI policy and hooks as a best-effort tool deterrent, then fail closed
in reports when agent logs show WebFetch/WebSearch or shell network-command
contamination; do not treat `allow_internet = true` on those runs as permission
to move dependency setup or verifier installs back into runtime.

For Go tasks, build bakes the toolchain at the recipe's `runtime_version` and
freezes it (`GOTOOLCHAIN=local`) so the offline run never auto-downloads a
toolchain. A `go.mod`/`go.work` `toolchain goX.Y.Z` directive higher than
`runtime_version` now fails the build instead of silently fetching — raise
`runtime_version` to that patch level (a bare `1.25` resolves to `go1.25.0`).

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
stet init --repo /path/to/local/repo --yes --test "<repo test cmd>"

stet suite discover --repo owner/repo --rev-range main~30..main --limit 10 \
  --output $MANIFEST_DIR/manifest.yaml

stet suite build --repo /path/to/local/repo --manifest $MANIFEST_DIR/manifest.yaml \
  --out $OUT --workers 2 --require-f2p=false
```

`--llm-install-config` defaults on (see the test_cmd-relevance note below), so
build needs a model client. Like `discover`, it resolves one from
`--ai-cmd`, `build.ai_cmd`, or `ai.default_provider` with a provider installed —
no explicit `--ai-cmd` needed once a provider is configured. Pass
`--llm-install-config=false` to build without one (lower-fidelity broad verifiers).

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
narrows verifiers, both of which lift dataset quality), so `suite build` /
`scenario generate` require `--ai-cmd` unless you pass `--llm-install-config=false`
to opt out (not recommended; you get lower-fidelity broad verifiers).

After >= 80% gold pass, verify test_cmd relevance: pick a task with test
patch, confirm test_cmd runs those files. Under `--llm-install-config`, build
auto-narrows a single broad whole-suite verifier (e.g. `go test ./...`, bare
`pytest`, `pnpm test`) to the test packages/files covering the change and
fail-closes to the broad command otherwise; each task's
`build_logs/test_selection.json` records the outcome (`narrowed` / `left_broad`
/ `abstained`).

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

For completed Stet roots that are using disk because of retained raw patches,
run `stet artifacts status --root <root>` before manual deletion, then
`stet artifacts compact --root <root>` when bounded patch metadata is enough.
This preserves `patch_retention.v1.json` contracts but does not remove
datasets, repo bundles, trajectories, Docker cache, APFS snapshots, or whole
run roots.

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

Inline audit at target count:
1. Empty test patches -> flag for removal
2. Lockfile/CI-only artifacts -> flag
3. Patch size: reject < 80 lines or > 1500 lines
4. Non-test file ratio: flag > 80% test files
5. Spot-check ai_task quality

Update `agent_docs/datasets.md` with the finalized recipe.

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
counters.

## Common Next Steps

Each phase checkpoint recommends one concrete next step:

- `approve`: proceed to next phase after reviewing checkpoint results
- `rerun`: retry the current phase after a config or toolchain fix
- `stop`: halt the pipeline at the current phase

## Harbor Dockerfile Starting Points

Use these as starting points; pin versions from CI and keep the actual repo
test command in `stet init --test`.

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
# install Node + corepack/pnpm versions that match CI here
WORKDIR /app
ADD repo.tar.gz /app
RUN corepack enable && corepack prepare pnpm@latest --activate
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
