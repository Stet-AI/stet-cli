# Onboarding

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

Use this when the user wants to set up a new repo for Stet evals, build a
dataset, or get a starter task slice. For heavy dataset builds (50+ tasks,
Docker debug loops), see [dataset-build](dataset-build.md).

```
read CI ──► init ──► discover ──► build ──► receipt
                                              │
                                ┌─────────────┼─────────────┐
                                ▼             ▼             ▼
                            smoke       approve       rules
```

## When To Use

- "Onboard this repo for evals"
- "Set up Stet on this repo"
- "Build a dataset from this repo"
- First time on a repo with no `.stet/stet.yaml`
- User wants a reusable task slice before running probes or comparisons

## Driver-Agent Contract

For generic prompts such as "set up Stet in this repo" or "get an initial
AGENTS.md signal", the driver agent owns the setup loop. Do not require the
operator to understand task corpus construction, rev ranges, config-diff versus
rules, or selector internals before Stet can do useful work.

- Treat the dataset as the primary onboarding deliverable. The first AGENTS.md
  signal is downstream of a high-quality starter dataset, not a substitute for
  it.
- For normal onboarding, aim for a meaningful starter dataset: roughly 10-20
  build-ready tasks with subsystem and difficulty coverage. A 1-3 task run is a
  smoke or no-spend triage, not onboarding. For first AGENTS.md/CLAUDE.md
  signal, fewer than 10 retained ready tasks means setup is incomplete. Keep
  widening, shifting, or repairing setup until the receipt supports that
  quality bar or names a concrete blocker.
- Diversity is part of dataset quality. Prefer tasks that touch different
  packages, subsystems, feature areas, and test surfaces. If the ready tasks all
  cluster in one package or workflow, keep mining an additional range or report
  the slice as low-confidence instead of calling it representative.
- Leave discovery quality lanes on by default. Use `--skip-quality-lanes` only
  when the operator explicitly asks for a no-spend corpus preflight, and label
  the result as preflight rather than a high-quality dataset.
- For automated first AGENTS.md/CLAUDE.md onboarding, run
  `stet init --repo . --yes --ai-provider <provider> --quality recommended --test ...`
  by default (`--ai-provider` is now required non-interactively; see below).
  Switch to `standard`, `custom`, or no-quality only when the operator
  explicitly asks for that; non-instruction generic setup can still ask when
  the right quality setting is genuinely ambiguous.
- If provider auth or hosted PR metadata is unavailable, `--source commits` is
  a fallback source, not a smaller bar. Keep the same onboarding-scale budget
  (`--limit 200 --target-pass 25` as the starting point) and do not add
  `--skip-quality-lanes` unless the operator explicitly asked for preflight.
- Infer the first starter slice from CI, repo history, and recent product work.
  Ask the operator about product-area weighting only when they request a
  reusable production dataset or the inferred slice would be misleading.
- Before task building, choose the narrowest credible bounded verifier from CI
  and pass it explicitly with `--test` to the init/build flow. Read CI first;
  examples such as
  `bazel test //...`, an unfiltered `pytest`, `go test ./...`, or a
  workspace-wide script are broad, not bounded. If only a broad verifier is
  available, stop before build and propose bounded alternatives; do not broaden
  verification merely to increase yield. Record verifier scope and skipped
  scope in the receipt. Validate one representative task when possible, then
  expand only when the bounded slice needs more coverage.
- If discovery, build, probe, or config-diff returns zero ready tasks, or fewer
  than 10 retained ready tasks for AGENTS.md/CLAUDE.md, continue setup: follow
  `next_command`, widen or shift `--rev-range`, use `--allow-no-test-changes`
  for repo-level test projects, repair install or Docker setup, or switch to a
  known dataset. Stop only at a concrete blocker; do not launch a
  config-diff/probe workaround and call it onboarding evidence.
- After the dataset has at least 10 retained ready tasks, use manifest-backed
  rules for the first AGENTS.md/CLAUDE.md signal. Use probe/config-diff only as
  an explicit throwaway prefilter on that retained slice, not as the setup
  substitute.
- If `stet context` reports `run_instruction_rules`, create the AGENTS.md or
  CLAUDE.md `stet.change.yaml` and `stet.suite.yaml` over the retained dataset,
  then run `stet manifest resolve` and `stet eval rules plan`; do not reinterpret
  that recommendation as a config-diff step.
- Before launching the first AGENTS.md/CLAUDE.md rules run, inspect the plan JSON
  grader profile. Unless the operator explicitly chose `standard`, `custom`, or
  `--no-quality`, `graders.quality_profile.effective_graders` should include the
  full recommended quality set: `clarity`, `simplicity`, `coherence`,
  `intentionality`, `robustness`, `instruction_adherence`, `scope_discipline`,
  and `diff_minimality`. If a pinned `.stet/stet.yaml` or change manifest narrows
  that set, repair the onboarding config to `recommended` or ask before honoring
  the narrower pin; do not silently treat a discipline-only plan as the default
  first-run signal.
- A newly added AGENTS.md/CLAUDE.md is still a normal rules case: Stet treats
  the baseline instruction file as empty and the working tree file as the
  candidate. If rules cannot resolve the instruction path, check the candidate
  path, CLI version, and dataset setup before considering an explicit
  before/after config-diff prefilter.
- Ask before auth setup, private dependency access, meaningful spend,
  lifecycle mutation, destructive recovery, or locking a reusable dataset.

## Quick Path

For most repos, the quick path is enough:

```bash
# 1. Infer the starter dataset target
#    For generic setup, sample merged PRs/commits and choose a representative
#    first slice yourself. Ask about product areas, PR types, paths, and
#    difficulty mix only when the operator needs a reusable production slice.

# 2. Resolve test setup from CI evidence
#    Read GitHub Actions, GitLab CI, or equivalent repo CI config, then
#    Makefile, package.json scripts, README.
#    Pick the narrowest credible bounded verifier from CI. CI is ground truth,
#    not README. If only a repo-wide verifier exists, stop before build and
#    propose bounded alternatives.

# 3. Author the Harbor environment
#    Write .stet/harbor.Dockerfile for this repo and reference it from
#    .stet/stet.harness.yaml under environment.dockerfile.

# 4. If Claude is the selected provider, set up host auth first
#    Run `claude setup-token`, store the printed token in
#    ~/.config/stet/claude-oauth-token with 0600 permissions, and do not export
#    it globally. Stet fails before launching Claude runs if auth is missing.

# 5. Persist config
#    For automated first AGENTS.md/CLAUDE.md onboarding, default to recommended
#    quality graders. Use standard/custom/no-quality only when explicitly
#    requested; generic non-instruction setup may clarify ambiguous grader
#    settings.
stet init --repo . --yes --ai-provider <codex|claude|gemini|cursor> --quality recommended --test "<bounded verifier>"

# 6. Mine candidate pool
stet suite discover --repo . --rev-range main~200..main --limit 200 --target-pass 25
#    GitHub PR source uses `gh`; GitLab MR source uses `glab`.
#    For ambiguous enterprise hosts, add `--change-provider github|gitlab`;
#    use `--source commits` when provider auth/tooling is unavailable.
#    With --source commits, keep the same --limit/--target-pass budget; do not
#    shrink to a 3-task smoke for normal onboarding.
#    Do not use --skip-quality-lanes for ordinary onboarding; it is only for an
#    explicit no-spend corpus preflight.
#    On short/shallow histories where main~200 predates the first commit, discover
#    auto-clamps to all reachable history (prints a NOTE) instead of erroring.

# 7. Build dataset
stet suite build --repo . --manifest .stet/discover-manifest.yaml --test "<bounded verifier>" --workers 2
#    Requires Docker by default. Add --harbor-backend worktree to verify
#    base-fail/gold-pass in local git worktrees from --repo instead — no
#    Docker daemon needed; the built dataset is still Docker-portable.
#    Build is complete only when the dataset root has build-summary.json.
#    During onboarding, if task directories exist but build-summary.json is
#    missing, treat the dataset as partial/interrupted setup output. Rerun
#    `suite build --restart` or use a fresh --out; do not create a rules suite
#    from those directories.

# 8. Validate setup with one cheap local replay/test smoke when available
#    Confirm at least one representative task can execute in Docker before
#    treating the starter slice as ready. This is setup validation, not a model
#    smoke, probe, or rules eval.

# 9. Read receipt and propose starter slice
# Build writes build-summary.json and onboarding_receipt.v1.json to the dataset root.
# If build_ready is zero, fewer than 10 for AGENTS.md/CLAUDE.md, or lifecycle
# is setup_required, report the setup blocker and repair plan. Do not proceed
# to AGENTS.md/CLAUDE.md signal.
```

Task-selection rules:
- Dataset selection is product work, not a mechanical newest-PR slice.
- For a generic first setup, infer the first useful slice and call out the
  assumption. Interview the operator before locking a reusable production slice:
  important product areas, PR types, paths, exclusions, and desired
  easy/medium/hard mix.
- Use read-only subagents when available to sample merged PRs/commits and map
  where representative work lies in the repo. If subagents are unavailable, do
  the same bounded history sampling yourself and say so.
- Prefer a slice with real workflow relevance, strong test signal, path or
  subsystem coverage, and mixed task difficulty. Do not hide coverage gaps.
- Track the path/subsystem distribution while selecting tasks. A set of passing
  tasks that all exercise one package is skewed; add adjacent ranges or older
  product-work windows until the starter slice covers multiple important repo
  areas, or explicitly report the skew as a confidence limit.
- For normal onboarding, do not stop at 3 PASS tasks. Discover enough candidate
  work to plausibly build 10-20 ready tasks; use smaller numbers only for an
  explicitly requested smoke/preflight and label the confidence accordingly.
- Quality lanes are part of dataset quality. Do not pass `--skip-quality-lanes`
  in ordinary onboarding; if spend is not approved, stop with a preflight
  receipt instead of calling the slice ready.
- If discover/build/status reports zero PASS tasks, `zero_ready_recent_slice`,
  or `no_eval_ready_tasks`, treat it as a slice-selection problem first. Do not
  call the repo unevaluable until you have tried one wider or better-targeted
  slice, or reported why the repo history is mostly docs, release metadata,
  submodule bumps, generated files, or another weak-signal pattern.

Too-few task recovery:
- Read the status or partial receipt first. Use `failure_class`, reject reasons,
  and `next_command` rather than guessing from pass rate alone.
- Widen or shift the slice before giving up: `main~50..main` -> `main~200..main`
  -> `main~500..main`, or choose an older range that contains product work.
- Use `--source commits` when PR provider auth/tooling is unavailable, and add
  `--limit`/`--target-pass` so Stet can keep searching until it finds enough.
  For normal onboarding, `--target-pass 25 --limit 200` is a better starting
  point than tiny smoke values; widen from there when build-ready yield is low.
- For either PR or commit discovery, `--target-pass` bounds PASS yield while
  `--limit` remains the maximum source-search budget.
- If the repo uses broad repo-level tests but commits rarely edit tests, rerun
  discover with `--allow-no-test-changes`.
- If discover's dropoff is dominated by LLM-gate reasons (`no_hard_signal`,
  `mechanical`, `low_complexity`, `boilerplate`, ...), widening `--rev-range` and
  `--allow-no-test-changes` will not help, and `--min-complexity` only affects
  gate-PASS complexity (it cannot clear `no_hard_signal`). Treat the repo as
  low-yield for behavioral evals: pick a repo with richer behavioral PR history
  or author tasks manually.
- If the repo is a docs/release wrapper or implementation lives in a submodule
  or sibling repo, say that concretely and continue setup in the actual
  implementation repo/root when it is unambiguous and the AGENTS.md/CLAUDE.md
  treatment is present/effective there or intentionally mirrored there. Carry
  the same onboarding bar there. Ask when the correct implementation root is
  ambiguous, private access/auth is needed, the instruction surface exists only
  in the wrapper, or the operator must provide a known dataset/root.
- If a downstream `probe --file` has no eval-ready tasks, return to onboarding:
  widen or shift `--rev-range`, use `--allow-no-test-changes` when appropriate,
  or repair the dataset. This is not evidence about the config change.
- If AGENTS.md/CLAUDE.md `probe --file` or `config-diff` reports a tiny
  retained slice, such as `AGENTS.md/CLAUDE.md config-diff selected N task(s)`,
  return to onboarding and expand or repair the dataset. Do not narrow with
  `--task-id` to get a one-task instruction read.
- If `stet eval rules plan` reports `instruction_dataset_incomplete`, rerun
  `stet suite build --restart` against the intended dataset, or build to a fresh
  `--out` and update the suite after that output has `build-summary.json`. A
  sibling output like `.stet/dataset-serial` is ignored unless the suite
  manifest points `eval.dataset` and `selection.task_ids` at that completed
  dataset.

Test-setup rules:
- The agent owns test-command selection. `stet init` writes config; it does not
  replace repo reading and judgment.
- Priority order: CI workflow steps (highest trust) > Makefile/justfile targets
  > package.json scripts > README (lowest trust).
- Avoid placeholder commands (`echo`, `true`, lint-only, build-only).
- For monorepos or build-system-driven repos, preserve the real CI runner and
  repo-level flags, then narrow verification to a credible package, directory,
  project, or target. Do not substitute a package-manager install or test
  command merely because a leaf package file exists. If narrowing is impossible,
  stop before build and ask for approval to use the repo-wide verifier.
- `stet init` writes `.stet/stet.harness.yaml` and `.stet/harbor.Dockerfile`
  when they are missing. Treat the generated harness as starter setup only. It
  does not choose or pin repo runtime versions. Read CI plus repo runtime files
  (`go.work`, `go.mod`, `rust-toolchain`, `.python-version`, `.node-version`,
  `.bazelversion`, package manager config) and edit the Dockerfile to install
  the selected toolchain before building.
- The Harbor Dockerfile should include the dependencies the real tests need:
  language runtimes, package managers, system packages, service clients, build
  tools, and repo-specific setup visible in CI.
- Before calling the starter slice ready, run the smallest local replay or test
  smoke that proves at least one representative task executes in Docker. If it
  cannot run, report the blocker instead of upgrading confidence.
- If the repo rarely co-locates test edits with code changes, use
  `stet suite discover --allow-no-test-changes ...` to admit repo-tests-only
  tasks.

Quality onboarding rules:
- Interactive `stet init` now recommends enabling the `craft` and `discipline`
  bundles. Accepting that prompt writes the repo
  `quality` selection into `.stet/stet.yaml`.
- For automated first AGENTS.md/CLAUDE.md onboarding, pass
  `--quality recommended` with `stet init --yes`. This is the driver-agent
  default, not a CLI implicit default. Use `standard`, `custom` after
  inspecting `stet graders --repo <path> --json`, or no-quality only when the
  operator explicitly asks for that. For non-instruction generic setup, ask
  only when the quality setting is actually ambiguous.
- Non-interactive `stet init` (`--yes`, or any run without a TTY) now requires
  an explicit `--ai-provider <codex|claude|gemini|cursor>` whenever a runnable
  provider is detected. It no longer auto-selects one from PATH; it fails fast
  and writes no config when the flag is omitted, so choose the provider that
  will run the graders. Interactive runs still prompt.
- The configured quality panel now surfaces in `stet eval rules plan` and runs
  during the eval even when the suite pins a grader evaluator model; a pinned
  evaluator no longer silently drops the craft/discipline graders, so the plan's
  grader list reflects the full panel that will actually run.
- `stet init --ai-provider claude` requires usable Claude auth. Prefer running
  `claude setup-token` and storing the printed token in
  `~/.config/stet/claude-oauth-token` with `0600` permissions; Stet reads that
  file and forwards `CLAUDE_CODE_OAUTH_TOKEN` only to Stet-managed Claude runs.
  Do not put the token in shell profiles, repo `.env` files, or committed
  config. For one-off automation, use command-scoped env:
  `CLAUDE_CODE_OAUTH_TOKEN=<token> stet ...`. Stet also accepts Claude
  credential JSON or Anthropic API/auth token env vars. Stet does not read
  Claude credentials from the macOS Keychain by default.
- `stet init --yes` stays low-friction and does not enable quality bundles by
  default. Silent auto-init paths outside first AGENTS.md/CLAUDE.md onboarding
  should keep bundle selection empty until an operator opts in; pass
  `--quality recommended` for the first instruction-surface signal, or
  `--quality standard` when they explicitly decline recommended graders.
- Do not launch the first smoke, probe, or eval run while the repo has no
  `quality:` block, `--grader`, or explicit operator decline. If the operator
  has not explicitly declined recommended graders for first AGENTS.md/CLAUDE.md
  onboarding, run init with `--quality recommended` before the run or pass
  equivalent explicit graders where the command supports them.

## Onboarding Receipt

Build writes `onboarding_receipt.v1.json` to the dataset root with:

- `candidate_pool`: total, passed, build_ready, build_skipped, skip_reasons
- `task_selection`: frozen `TaskSelectionRecord` with requested/realized IDs
- `task_rationale`: per-task selected/rejected with reasons
- `test_setup`: commands and source
- `test_selector`: selector status, reason-code, proof-strength, runner,
  target-kind, fallback, and legacy-v1 counts when selection was attempted
- `confidence`: `high`/`medium`/`low` with reasons
- `lifecycle`: `journey_kind: "onboard"`, `decision_grade: "exploratory"`

If `candidate_pool.build_ready` is zero, or fewer than 10 for first
AGENTS.md/CLAUDE.md signal, the lifecycle phase is `setup_required` and the
next action is setup/install-config repair, not starter-slice approval. A
`install_config_unbuildable` skip reason means LLM synthesis failed closed
(unbuildable repo, reason in `build-summary.json`); supply a deterministic
`--install-config` recipe or fix the Dockerfile environment — see
[dataset-build](dataset-build.md).

If `warnings[].code` includes `test_relevance_mismatch`, do not treat a
Docker-only retry or wider rev range as sufficient. The selected task paths are
not covered by the configured tests. Update `.stet/stet.yaml`/`stet init
--test` to exercise those paths, choose a matching repo/root, or mine a slice
covered by the current tests, then rerun discover/build before AGENTS.md rules.
If `infra_contaminated` is also present, repair Docker/containerd too; both
blockers must be cleared before the retained dataset is usable.

Keep selector yield distinct from dataset confidence: it describes verifier
target proof for the corpus, not model quality, F2P validity, gold replay,
flake status, ambiguity, or representativeness.

## Reporting

```text
STET :: DATASET

answer      starter slice ready
confidence  medium
step        onboard -> rules
funnel      240 scanned -> 32 passed discover -> 15 build-ready
dropoff     208 rejected before build
            top: no_test_changes 96, llm_gate_fail 64, oversize 22
build       15 materialized, 4 skipped
            top: unsafe_external_symlink 3
coverage    workflow, validation, model routing, tracing, docs/runtime
why         Breadth is good enough for a first repo signal, while the coverage
            gaps stay visible for later dataset expansion.
recommend   launch the first manifest-backed AGENTS.md rules signal
command     stet eval rules --change-manifest stet.change.yaml --json
other       run an explicit smoke/preflight only when the operator asks for a
            cheaper lower-confidence calibration read; stop with dataset receipt only
```

## Proposal Rules

- Recommend a variable-size starter slice, not a fixed `N`.
- Prefer tasks with strong test signal and plausible medium difficulty.
- Avoid trivially small, obviously huge, duplicate-looking, or weak-signal
  tasks.
- Keep light subsystem/path coverage and a reasonable easy/medium/hard mix.
- Include `confidence`, the funnel, what was excluded, and coverage gaps.
- Show at most 5 representative tasks, then `+N more`.

## Common Next Steps

- `approve`: accept the proposed starter slice; slice is locked for the first
  retained-slice signal.
- `rules`: approve and launch the first manifest-backed AGENTS.md/CLAUDE.md
  signal over the retained starter slice.
- `prefilter`: only when the operator explicitly asks for a throwaway
  lower-confidence read over the same retained slice.
- `smoke`: only when the operator explicitly asks for lower-confidence
  model/harness calibration; label it preflight, not the AGENTS.md signal.

## Escalation Handoff

After onboarding, the next AGENTS.md/CLAUDE.md step is **rules** over the
retained starter slice. Probe/config-diff are explicit prefilters only and
inherit the onboarding receipt's `task_selection` contract.

For benchmark-first model or harness workflows, a finished probe can become a
baseline:

```
onboard -> probe -> baseline freeze -> compare -> gate -> promote
```

Do not use that path for first AGENTS.md/CLAUDE.md onboarding. Instruction
surfaces use rules after the retained starter slice; probe/config-diff remain
explicit prefilters only. Onboarding produces `exploratory`-grade evidence;
gate requires `gateable`-grade evidence from the matching rules or benchmark
workflow.
