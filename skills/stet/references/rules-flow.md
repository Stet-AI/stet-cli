# Rules Flow

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

```
context/reuse check -> manifest resolve -> eval rules plan -> eval rules -> status -> report
                                                               |          |
                                                            wait     promote / inspect / stop
                                                               |
                                                         repair compare
```

Use this for manifest-backed change control.

This is the right path when the operator wants a formal rollout decision from
`stet.change.yaml` and `stet.suite.yaml`, not just a repo-local directional
read.

For AGENTS.md, CLAUDE.md, shared skill, or harness-policy optimization, this is
also the required path for any candidate the agent intends to keep, recommend,
baseline, promote, or describe as improving shared behavior. A prior
`config-diff` can be cited only as a directional prefilter; it does not replace
the rules run or prove custom `agents_*` grader coverage.

Route within rules:

| Need | Stay or jump |
|---|---|
| Ordinary rollout manifest | Stay here. |
| AGENTS.md / CLAUDE.md manifest examples and overlay details | Stay here; see "A/B Testing AGENTS.md or CLAUDE.md". |
| Shared skill A/B, revision, or wrapper run | Jump to [rules-skill-loop](rules-skill-loop.md). |
| Active status or stuckness | Jump to [status-checkin](status-checkin.md). |
| Incomplete compare recovery | Stay here for `eval rules repair`; use [status-checkin](status-checkin.md) for active health. |
| Baseline freshness and reuse | Stay here for rules-specific freshness; keep root baseline rules in mind. |

## Flow

```bash
stet manifest resolve --change-manifest .stet/rules/stet.change.yaml
stet eval rules plan --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml --json
stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml
stet eval status --change-manifest .stet/rules/stet.change.yaml --json
stet eval rules repair --change-manifest .stet/rules/stet.change.yaml --json
stet eval report --change-manifest .stet/rules/stet.change.yaml --json
```

Roles:
- `context/reuse check`: before any charged launch, run
  `stet context --repo <repo> --json` unless you are already anchored on a
  specific active run or completed report. Prefer an exact frozen baseline from
  context, or freeze a complete eligible baseline arm/root, when it preserves the
  task slice, Harness Surface, Search Space, grader coverage, and validity. A
  partial baseline arm is not reusable until it has required arm artifacts such
  as `manifest.json` plus `reports/summary.json`; a completed baseline from a
  different slice is not a matched baseline.
- `manifest resolve`: inspect normalized inputs before launch. Prints the canonical resolved change manifest as YAML (or JSON with `--json`); injected defaults (e.g. `context.baseline.source`, `context.candidate.source`, `policy.version`, `treatments[*].path`) are inlined silently — there is no separate validation verdict. On a malformed manifest, `manifest resolve` exits non-zero; without `--json` it emits a plain-text stderr line, and with `--json` it emits a structured `{"error": {"code", "message", "field"}}` envelope on stdout. A non-zero exit is the validation contract — treat it as "malformed manifest" and read `error.code` / `error.field` (or the stderr line) for the field-precise reason.
- `eval rules plan`: preflight tasks, arms, graders, frozen-baseline reuse, cost confidence, missing pricing/cost data, and cheaper alternatives without launching compare evidence. It persists an `eval_rules_plan.v1.json` receipt with replay-validity identity that a matching launch can reuse. It is not free: plan runs the Harbor `oracle`-agent gold-replay validation containers to populate `replay_validity` and runs the LLM-grader preflight, so under contention it routinely takes 8–10+ minutes. Replay validity uses matching proven dynamic F2P selector evidence from `build_logs/test_selection.json` when available, then `task.yaml` `validation.fail_to_pass_tests`, before falling back to broader `tests/test_outputs.py` commands. A future `--quick-plan` that skips replay validation does not exist yet; when an operator needs a sub-minute readiness check, reach for `stet manifest resolve` instead. The next command, `stet eval rules` without `--plan`, is the charged launch. The plan output's `task_selection_adequacy.verdict` is usually informational; values such as `insufficient_history` describe historical sample size for confidence calibration. Exception: AGENTS.md/CLAUDE.md rules runs below 10 selected retained tasks are blocked as `task_selection`; expand the onboarding dataset first instead of launching a tiny rules comparison. The plan receipt also carries an `interpretation` (`kind: preview`) block; narrate it to the user per the operator-contract interpretation rule — state the odds and tier-matched verb from `confidence`, offer `one_liner` verbatim, and never relay raw posture tokens.
- `eval rules`: launch the bounded rules-backed run. By default the compare projects Harbor test outcomes. Pass `--retest-tests` (or equivalently `--validate-arg "--retest-tests"`) on the main `stet eval rules` launch to run real validate-side tests on both arms instead of projecting; it applies symmetrically to baseline and candidate. The setting is persisted in the rules runtime artifact and re-applied automatically by `--relaunch-arm`, so a relaunch retests the same way the original launch did. Retest is opt-in only on the main launch (not the `checkpoint`/`holdout`/`skill` subcommands). When the fresh compare writes incomplete required grader coverage, launch makes one bounded in-place repair/regrade attempt before final reporting; use `eval rules repair` if coverage remains incomplete or the run is interrupted.
- `eval status`: explain the current phase or health
- `eval rules repair`: recover an incomplete rules compare from the persisted runtime; when the surface is replayable, it can resume a baseline-phase compare or rerun a missing/partial candidate arm while preserving completed evidence, then repair/regrade missing coverage. `eval rules resume` remains accepted for compatibility. Pass `--parse-retries N` to forward grader JSON parse-repair attempts during regrade recovery. Pass `--report-mode separate_axes|strict_publishable_pass` to pin the reporting mode when the baseline and candidate arms were produced by Stet binaries whose default drifted; baseline mode is used automatically otherwise.
- `grader_profile_mismatch`: repair/regrade blockers include expected and actual evaluator runtime, provider, command hash, and measuring-device digests so operators can distinguish real profile drift from reconstruction bugs.
- `eval report`: read the finished rollout decision

`eval status --change-manifest --json` reports three axes. `rules_runtime`
means metadata is `resolved`, `unresolved`, or `stale`; `arm_evidence` means
compare arm artifacts are `none`, `partial`, `running`, `complete`, or `failed`;
`compare_decision` means the decision is `reportable`, `missing_experiment`,
`inconsistent`, `active`, or `blocked_until_report`. `active` means the arms are
still running, so the report is legitimately not materialized yet — keep polling
rather than repairing. If arm evidence exists but
`experiment.json` is missing, the decision remains inspect-only. Repair with
`stet eval rules repair --change-manifest ... --json` when the launch exited or
stalled; use `--restart` only to discard evidence.

The same JSON also carries `phase_tree` plus
`trial_result_reportability`: `active_but_healthy`, `partial_artifacts_only`,
`ready_to_report`, `blocked_until_report`, or `final_report_available`.
Use `trial_result_reportability`, not `compare_decision`, as the heartbeat
authority for active/partial/ready/final Trial Result status.
Treat smoke summaries, trajectories, task details, and arm summaries as
liveness/partial evidence until reportability reaches `ready_to_report` or
`final_report_available`; do not infer keep/reject from those partial artifacts.

In `eval report --json`, `evidence_quality.factors[].signal=="compare_state"`
means the compare artifacts reached a coherent terminal state. Missing grader
coverage is reported separately as `grader_coverage`, and may still keep the
report inspect-only.

The envelope also carries a top-level `activity_state` of `running`, `stalled`,
or `exited` so a polled receipt can disambiguate "no evidence yet because still
running" from "no evidence yet because the run died." `activity_state` is
authoritative: an embedded `report.execution.status` of `inspect` is provisional
unless `activity_state == "exited"`. While `activity_state` is `running` or
`stalled`, treat any embedded `report` as in-flight scaffolding rather than a
terminal verdict, and re-poll instead of acting on it. Note that this top-level
field is distinct from the per-arm `run_status.activity_state` (values
`active`/`waiting_on_*`/`no_progress`), which describes one resolved arm's
internal phase rather than the launcher process as a whole.

When the agent harness records an exception on any per-task run (e.g. codex
crashing during `agent_setup`), `eval status` surfaces the most recent failure
in a top-level `last_error` field with `type`, `message`, `agent`, `task_id`,
`phase`, and `occurred_at`. The text renderer prints a `Last error:` line. Use
this to tell whether the agent itself or the Stet wiring is broken before
chasing downstream grader errors. The field is omitted on happy-path receipts.

Pre-arm launcher failures (baseline/candidate context resolution, skills-root
staging, grader preflight, harness resolve, frozen-baseline load, rev-range buildability, task selection) are
surfaced separately as a top-level `launch_error` field on the
`eval_rules_runtime.v1.json` artifact, on `eval status --change-manifest --json`
when launch is blocked, and on `eval report --change-manifest --json`
(where `decision.reasons` and `decision.next_action` are also overridden so
the receipt names the launch failure). The skill wrapper preflight
(`eval rules skill --plan --json`) emits the same struct via the
`evalRulesSkillPreflightFailureV1` envelope on stdout. The shape is
`{phase, message, target, code, remediation, occurred_at}`; `phase` is one of
`resolve_baseline_context`, `resolve_candidate_context`, `stage_skills_root`,
`grader_preflight`, `harness_resolve`, `frozen_baseline_load`,
`rev_range_buildability`, or `task_selection`.
`launch_error` and `last_error` can coexist when the launcher fails after a
partial runtime already saw per-task crashes. Read `launch_error` first when
`stet eval rules` exits before any per-task arm runs; the per-task agent
crash path is `last_error`.

For AGENTS.md/CLAUDE.md onboarding, `code=instruction_dataset_incomplete`
means the suite points at task directories without a dataset
`build-summary.json` clean-build marker. Do not interpret the directory count
as retained evidence. Rerun `stet suite build --restart`, or build to a fresh
`--out`; then update the suite only after `eval.dataset` points at the
completed dataset root.

The `code` field disambiguates structurally similar phases. Within
`resolve_baseline_context` / `resolve_candidate_context` you may see:

- `code=context_path_unresolved` — the requested AGENTS.md / CLAUDE.md /
  docs path does not exist at the configured baseline ref. Remediation
  points at the manifest path or the `context.baseline` pin.
- `code=default_branch_unresolved` — the repo's default branch could not
  be resolved (origin/HEAD not set, HEAD detached, or the same-named
  remote ref missing). `target=default_branch`. Remediation names the
  git-config fix (`git remote set-head origin -a`) or the
  `context.baseline.source` pin. Common in worktrees and freshly-cloned
  repos where origin/HEAD has not been set.
- `code=repo_not_a_git_repository` — the configured `repo:` path does
  not point at a git working tree. `target=repo`. Almost always a
  manifest-authoring bug: relative `repo:` values in `stet.suite.yaml`
  are resolved against the **`.stet` ancestor's parent (the repo root)**,
  not against the suite file's own directory. For a suite that lives at
  `<repo>/.stet/<somewhere>/stet.suite.yaml`, the canonical form is
  `repo: .`; writing `repo: ../../..` over-traverses out of the repo.
  Remediation points at the `repo:` field of the suite manifest.

Within `grader_preflight`, `target=grader_ai_cmd` and you may see
`code=grader_preflight_failed` for an unavailable or invalid evaluator command,
or `code=grader_ai_session_limited` when the evaluator reports quota, rate
limit, or session-limit exhaustion. Remediation points to waiting for reset or
choosing an available grader AI command/model, then rerunning `stet eval rules`.

Within `task_selection`, AGENTS.md/CLAUDE.md runs may emit
`code=instruction_dataset_too_small` when the retained dataset has fewer than
10 qualifying tasks. Qualifying means `proven_dynamic_f2p` selector proof
(`repo_tests_only` and tasks with no qualifying selector evidence are
excluded, fail-closed), then deduped by source commit and by a two-segment
touched-subsystem key so one PR or one area of the repo cannot be double- or
triple-counted; on corpora where the subsystem key collapses (a flat top-level
tests/ dir, a monorepo package root) a degenerate-signal guard skips subsystem
dedupe and falls back to commit-only dedupe, which the error message
discloses. Follow the remediation: expand or rebuild the onboarding dataset
with an onboarding-scale discover command such as
`stet suite discover --repo . --rev-range HEAD~200..HEAD --limit 200 --target-pass 25`,
keep quality lanes on, then rerun `stet eval rules` with a larger retained
slice that carries real F2P selector proof.

Do not treat that floor as a reason to switch to one-task `probe --file` or
`config-diff`. AGENTS.md/CLAUDE.md probe and config-diff reads use the same
onboarding floor: under 10 retained ready tasks is setup-incomplete, not an
instruction-surface signal.

`--ai-cmd` is a launch-only override for `stet eval rules`; use an absolute
script path when launching from scratch directories. The default evaluator and
LLM-backed graders resolve from `ai.default_provider` (or an auto-discovered
provider) and authenticate off that provider's local credential — for Claude,
stet's long-lived `setup-token` — so no wrapper command is needed; pass
`--ai-cmd` only to override the provider. `eval.grader_ai_model_id`
in `stet.suite.yaml` supplies the independent evaluator for LLM-backed graders
so the model under test does not grade its own work. Stet defaults to
provider-native schema output through the matching local CLI; set
`eval.grader_runtime: shell_text` with `eval.grader_ai_cmd` only when forcing
the legacy shell-text evaluator. `--grader-ai-model-id` is the matching CLI
override, and `plan` / charged launch refuse pre-flight when neither the suite
nor the CLI supplies an evaluator and the resolved grader set includes any
LLM-backed grader.

For agentic v2.alpha pointwise grading, set
`eval.grader_runtime: v2.alpha_rewardkit` or pass
`--grader-runtime v2.alpha_rewardkit`, and still provide
`eval.grader_ai_model_id` / `--grader-ai-model-id`. Stet rewrites the existing
candidate-blind `verification_contract.v1` as one flat 30–40-item binary rubric
covering every reporting dimension, then runs exactly one read-only agentic
judge session per task/arm. The judge sees only `{repo/, agent.patch,
verification_contract.v1.json}` and every yes/no verdict requires a valid
candidate-evidence line citation from `repo/` or `agent.patch`; a contract
citation may only supplement it. Stet also re-derives the staged contract's
bindings from the current task instruction, gold/test patches, base snapshot,
F2P/P2P names, and instruction surfaces; stale or cross-task contracts fail
closed. Tasks missing a staged `verification_contract.v1` fail closed as
unavailable; on `stet runs regrade-graders`, add
`--synthesize-verification-contracts` to synthesize missing candidate-blind
contracts (cached by task identity, so every arm of the same task reuses one
identical contract). Synthesis accepts Claude models only and uses a fresh
prompt-only, zero-tool Claude session with only process basics and Claude
authentication in its environment; default `--parse-retries 1` permits one semantic
repair after the initial synthesis response, while transport failures do not
retry. `--seeds` must remain `1`; malformed or partial **judge** output
is not repaired or retried. It cannot be combined with `eval.grader_ai_cmd`,
`--grader-ai-cmd`, `--grader-provider`, or a silent v1 fallback. Docker and
worktree backends are supported, but worktree evidence must carry current
decision-grade integrity for the selected task/base commit.

The existing alpha trace records the Claude judge's `total_cost_usd`, wall/API
duration, and turn count. Stet accepts only one successful, non-refusal Claude
JSON envelope with exact structured criterion output; missing cost telemetry,
malformed output, and error envelopes fail closed without a repair call.

The current direct alpha judge is a zero-subagent macOS Claude session with
only `Read`, `Grep`, and `Glob`; shell, write, delegation, and web tools are
technically denied. Its subprocess environment contains only `PATH`, `HOME`,
`TMPDIR`, and resolved Claude authentication; ambient proxy, routing, model,
runtime, and effort controls are excluded. Outbound provider transport remains
allowed, so the recorded profile does not claim provider-only networking. A
Cursor/Composer **grader** fails closed before invocation
because the installed headless Cursor CLI has no enforceable tool allowlist.
This does not prevent Cursor/Composer from being the independent model under
test when the grader is Claude.

For Cursor-backed model-under-test runs, use `Composer 2.5` / `composer-2.5`
and `agent.name: cursor`; do not use `composer-2.5-fast` unless the fast tier is
the explicit treatment. Keep graders independent with `--grader-ai-model-id`;
add `--grader-ai-cmd` only for legacy shell-text grading. A local `agent login`
session is enough; Stet bridges the host Cursor OAuth credential into Harbor
without requiring `CURSOR_API_KEY`.

If a Cursor-backed run records a zero-byte selected patch with
`agent_setup_failed`, `agent_bootstrap_failure`, or
`verifier_failed_before_patch_application`, the agent did not produce valid work.
Treat the run as a harness/bootstrap failure: fix Cursor auth/config or the
pre-patch verifier boundary and rerun, instead of regrading or interpreting
zero-pass metrics as model quality.

Cursor is not a provider-schema grader runtime: the `agent` CLI emits free text,
not schema-forced JSON, so Stet cannot infer a cursor grader provider. To grade
with a Cursor model in a cursor-only environment, force the shell-text bridge:
`--grader-runtime shell_text --grader-ai-model-id composer-2.5 --grader-ai-cmd
'agent --print --output-format text --mode ask --model composer-2.5 --trust
"$(cat)"'`. The wrapper must own Cursor auth (a local `agent login` session on
PATH is sufficient); Stet forwards only Claude evaluator credentials.

For Claude model-update selectors, `model:opus 4.8` is accepted as an alias for
canonical `claude-opus-4-8`. Cost estimates use the bundled pricing table in
`internal/h2h/pricing.v1.json`; if that metadata is missing for a future model,
the plan/report cost surface must say so instead of implying priced evidence.

To iterate on a high-signal slice from an existing dataset, pass repeatable
`--task-id <id>` to `eval rules plan` and `eval rules`, or put the stable slice
in the suite manifest as `selection.task_ids`. Task IDs must match ready task
directories in `eval.dataset`.

When you need Stet to find N launchable tasks instead of hand-picking
replacements, run `stet suite select --suite-manifest <stet.suite.yaml>
--target-valid N --out <dir>` first. It treats suite candidates as historically
merged / selected until gold replay proves them valid, writes a yield receipt,
and emits a derived suite manifest whose `selection.task_ids` are gold replay
valid / launchable.

For `agents_md` / `claude_md` change manifests, `suite select` also enforces
the 10-task instruction-surface floor before it prints a plan command. If the
receipt reports `instruction_dataset_too_small`, follow `next_actions` to
expand and rebuild the retained slice; do not run `eval rules plan` from that
underfloor suite.

For optimization loops, add `--plan-task-slices --iteration-count N
--checkpoint-count N --holdout-count N --seed <seed> --change-manifest
<stet.change.yaml>`. This writes `iteration.suite.yaml`,
`checkpoint.suite.yaml`, `holdout.suite.yaml`, and `task_slice_plan.v1.json`,
then wires the suites into `change.rules`. `checkpoint` is the validation lane;
there is no separate public `screening` lane. The planner receipt explains
selection strategy, fallback signals, exclusions, and holdout contamination, but
it does not replace replay-validity checks.

##### Build-proof reuse at selection (STET-622)

In a one-build → immediate-slice flow, `suite select` and a fresh dataset build
prove an overlapping fact (gold-pass). By default, when a candidate's
`build_logs/test_selection.json` carries a proven-dynamic-F2P proof whose
recorded task + environment identity still matches the task on disk, `suite
select` reuses that proof as the selection eligibility signal and **skips the
gold replay** for that candidate. This mirrors the STET-375 freshness-gate
shape: build records an identity (`build_identity` block: environment-group id +
task content hashes) at proof time, and selection recomputes + compares it at
use time.

- The skip is **freshness-gated, never blind**: if the recorded identity does
  not match (task content drift, env-group change, missing identity on a
  pre-STET-622 build), `suite select` falls back to a real gold replay. No
  candidate is ever selected on stale evidence.
- Each attempt in `suite_selection_receipt.v1.json` records
  `validation_source`: `reused_build_evidence` (proof reused, replay skipped) or
  `gold_replay` (fresh gold test ran). The receipt also carries roll-up
  `reused_build_evidence_count` and `replayed_count`.
- `--force-replay` forces a real gold replay for every candidate regardless of
  evidence freshness — the escape hatch when you want to re-validate the slice.
- Limitation: reuse applies only to `proven_dynamic_f2p` evidence (a recorded
  dynamic base-fail/gold-pass proof). Other proof strengths, legacy v1
  evidence, and pre-STET-622 builds (no `build_identity` block) replay as
  before. Use the same dataset-root path for `stet dataset build` and
  `suite select`; a different spelling (relative vs. absolute, symlinked root)
  leaves the recorded task identity unmatched and the candidate falls back to
  replay — safe, but defeats the optimization.

Put stable variance controls in the suite manifest under `eval:`:
`task_order_seed`, `workers`, `model_workers`, `harbor_concurrency`, and
`harness_cli_cache`. `stet eval rules` accepts matching CLI flags for temporary
overrides; CLI values take precedence over suite YAML. `stet eval rules skill`
also accepts `--task-order-seed` and writes it into its synthesized iteration
suite; omit the flag for fresh per-run randomness.

Harbor task-dependency caching is automatic: at image bake Stet injects a
build-time BuildKit cache mount for language download/package caches (Go modules,
Cargo registry/git, npm/pnpm/yarn, pip/uv) so repeated builds reuse downloaded
deps. There is no flag; set `STET_TASK_DEP_CACHE=off` to disable it. Reclaim the
shared cache with `stet harbor cleanup --prune-buildkit --apply`.

Harbor's Docker backend remains the default. Use `--harbor-backend worktree`
only when the operator explicitly wants local, Docker-free execution from a
local git commit. Keep `repo:` set in `stet.suite.yaml`, pass worktree controls
only as needed (`--worktree-keep`, `--worktree-install=false`,
`--worktree-allow-pre-install`, `--worktree-concurrency N`), and treat
Docker-only controls such as `--harbor-arg` and `--harness-cli-cache` as
unsupported on the worktree path. On worktree, Stet resolves the baseline
default branch from the local branch HEAD only when no `origin` remote is
configured. If `origin` exists but `origin/HEAD` and same-name `origin/<branch>`
are missing, Stet preserves `default_branch` so the strict plan/launch error
surfaces. To pin the baseline explicitly, set
`context.baseline.source: ref` and set `context.baseline.ref` to a commit or
branch in the change manifest. Worktree-backend evidence is inspect-only and
non-decision-grade by default on integrity grounds, so do not make rollout,
model, cost, or efficiency claims from unsandboxed worktree runs. A successful
Docker-free run is expected to read as inspect — it exits with code 21 (not 0)
and a transient `status=failed` line can appear even though the run completed,
so trust the report, not the exit code. Worktree runs also do not emit per-task
trajectory artifacts, so behavior, cost, and token telemetry are unavailable on
this path. Status/report remain the canonical decision readers; use per-task
`worktree_integrity.json` only when diagnosing worktree isolation,
source-mutation, or forbidden-artifact findings.

The Docker-free path also covers dataset build: `stet suite build
--harbor-backend worktree --repo <path>`, `stet dataset regenerate-f2p
--harbor-backend worktree --repo <path>`, and `stet eval rules skill
--harbor-backend worktree` run oracle base-fail/gold-pass verification in
detached git worktrees instead of Docker (`--worktree-keep`,
`--worktree-allow-pre-install`, `--worktree-install=false`,
`--worktree-concurrency N` configure it the same way as on the eval path); for
`eval rules skill`, one flag selection reaches both the internal build and the
delegated `eval rules` launch. `--repo` must be a local git repo containing
every task base commit. Built datasets stay fully portable regardless of
backend, so a later Docker run works unchanged. Worktree-built proofs
(`test_selection.json` `build_identity.runner_backend: worktree`) are not
reused as decision-grade evidence by `eval rules` task selection — a real
replay runs instead — and worktree-built/worktree-evaluated evidence remains
inspect-only for rollout or model claims.

`stet eval rules` accepts `--reasoning-effort low|medium|high|xhigh|max` to set
the reasoning level for both arms (default `high`); it is backend-agnostic and
applies to the worktree path too (e.g. run gpt-5.4 at `medium`). The CLI flag
overrides any `harness_settings.reasoning_effort` declared in the change
manifest.

`stet eval rules` is non-destructive by default when a matching rules runtime
already exists. It reuses completed evidence, auto-resumes candidate-phase
partial evidence when Stet can prove the replay is safe, and refuses to discard
partial arm evidence. Use `stet eval status --change-manifest ...` before any
recovery decision, then `stet eval rules repair --change-manifest ... --json`
when the active process has exited or status is stalled. Use `--restart` only
when intentionally discarding existing evidence and starting over.

Fresh rules runs use `--smoke-policy auto` by default: Stet runs one candidate
smoke only when the harness fingerprint needs proof, otherwise status/report
explain the reuse or skip in `smoke_preflight`. Use `--smoke-policy always` to
force smoke, or `--smoke-policy never` / legacy `--skip-smoke-preflight` for an
explicit override.

## Replay-Invalid Smoke

If smoke fails before `compare/experiment.json` with
`no_gold_pass_commands`, `all_commands_ignored_gold_failure_mode_unset`, or
`tests_unknown_all_commands_ignored_gold_failure_mode_unset`, the selected
slice is not gold-valid evidence yet. Do not treat that as model quality, a
rollout decision, or proof that current-checkout tests are broken.

First diagnose the verifier failure. Read `stet eval status
--change-manifest ... --json`, `stet eval report --change-manifest ... --json`,
the failed arm root, and per-task `validation.json` / `task_detail.json`
artifacts. Identify the task IDs, verifier commands, `gold_outcome`,
`gold_failure_mode`, `partial_score_reason`, and stdout/stderr hints. Explain
the likely cause before choosing an action: for example a path-sensitive test,
stale command, missing selector, container-only failure, archived dependency
drift, too-narrow slice, bad generated task, or another concrete replay issue.

Choose a bounded next action from that diagnosis. It may be a different task
slice, adjusted task selection, an already-known gold-valid test command, or an
inspect-only stop when no safe recovery is justified. Relaunch only after the
evidence input changes, or after you can explain why the same input is now
plausibly gold-valid. STET-340 tracks a product-supported gold-replay preflight;
until that exists, preserve inspect-only caveats and avoid rollout claims until
a gold-valid compare completes.

## Default Quality Graders

For non-skill treatments (AGENTS.md, CLAUDE.md, model_update, harness_bundle,
docs_glob), `eval rules` automatically includes the repo's quality graders from
`stet.yaml` `quality:` config, or the recommended default (`craft` +
`discipline`) when no quality config exists. This ensures decision-grade
evidence on the first run without requiring post-hoc `regrade-graders`.

The rules-default profile bundles **11 graders total**: the coding-quality trio
(`equivalence`, `code_review`, `footprint_risk`) plus the full **8 craft +
discipline quality graders** (`clarity`, `simplicity`, `coherence`,
`intentionality`, `robustness`, `instruction_adherence`, `scope_discipline`,
`diff_minimality`).
If the repo pins a `quality:` profile in `.stet/stet.yaml` (e.g.,
`discipline` only), the rules-default eleven are REPLACED by the pinned set —
see
`quality_profile.source` in plan output to confirm which path resolved.
This now matches the **leaderboard** quality bundle while keeping the
rules-specific coding-quality trio in front of it.

In plan and runtime output, `graders.grader_profile.source` records how the
profile was chosen: `derived` means it was inferred from defaults (the
recommended bundle plus any `stet.yaml` `quality:` config) because the change
manifest did not pin a profile, and `explicit` means `change.rules.grader_profile`
in the manifest set the graders, evaluator model, or command. Treat `derived`
as the normal first-run posture; `explicit` is the steady state once a repo
pins its grader contract. A third value, `legacy`, may appear on older
manifests that predate the explicit `grader_profile` contract — treat it as
"profile carried forward from a pre-contract manifest" and migrate to
`explicit` when the repo refreshes its rules manifests.

### Grader lifecycle pinning

`stet graders promote` pins the current binary's grader stack (embedded grader
bundle digest, judge prompt-template digest, reducer version) as the live
measuring device at `.stet/grader-profiles/live.v1.json`; promoting from a
dirty-tree build requires `--allow-dirty` and is recorded as
`operator_override`. Once a pin exists, `eval rules` measurement runs stamp
`graders.grader_profile.lifecycle` (plus `lifecycle_id`,
`grader_bundle_sha256`, `prompt_templates_digest`, `reducer_version`) in
runtime and report output: `live` (matches the pin), `candidate` or `scratch`
(explicit calibration opt-in via `STET_GRADER_PROFILE=<name>`; `scratch` when
the binary came from a dirty tree), `drifted` (stack changed, no opt-in), or
`unpinned` (no pin; behavior unchanged). A drifted stack refuses at measurement
launch — set `STET_GRADER_PROFILE=<name>` to run it as a calibration
candidate, or `stet graders promote` to accept the new stack as live.
Plan/status/read paths never refuse; they report the lifecycle instead. Any
non-`live` lifecycle is inspect-only, never decision-grade. `stet graders
status|show` compare the current binary against the pin. Limitation: only
`eval rules` measurement runs enforce and stamp lifecycle; `regrade` and
`batch-grade` re-grading paths do not yet.

The default quality bundle is LLM-backed (`craft` covers `clarity`,
`simplicity`, `coherence`, `intentionality`, and `robustness`; `discipline`
covers `instruction_adherence`, `scope_discipline`, and `diff_minimality`), so
`eval.grader_ai_model_id` must be set in `stet.suite.yaml` (or supplied as
`--grader-ai-model-id`) for any non-skill treatment that auto-bundles them.
`stet eval rules plan` and `stet eval rules` both refuse pre-flight when those
evaluator fields are missing and any LLM-backed grader is bundled. Worked
stanza:

    eval:
      grader_ai_model_id: claude-sonnet-4-6

RewardKit v2.alpha uses the same independent evaluator field plus its runtime:

    eval:
      grader_runtime: v2.alpha_rewardkit
      grader_ai_model_id: claude-sonnet-4-6

Pick an evaluator distinct from the candidate model so the grader is not
grading its own work. Pass `--no-quality` (or set `no_quality: true` on
`eval`) when you intentionally want to drop the auto-bundled craft and
discipline graders. Note that validation-backed runs still bundle
`equivalence` and `code_review` (both LLM-backed), so `--no-quality` alone
does not bypass the preflight; supplying the evaluator stanza is the
straightforward path.

Skill treatments (`skill_diff`) do not receive bundled quality graders; they use
the `skill_workbench` pack instead. See [rules-skill-loop](rules-skill-loop.md)
for skill A/B and skill revision details.

Missing expected quality graders produce an `inspect` verdict with a concrete
`regrade-graders` repair command.

## Skill And Shared-Skill Loops

Skill A/B, skill revisions, `stet eval rules skill`, and shared-skill loop
details live in [rules-skill-loop](rules-skill-loop.md). Keep this file focused
on generic manifest-backed rules rollout mechanics.

## Harness Bundle Guards

For harness-bundle guards, keep the public/private boundary straight:
- `stet.harness/v1` is still the minimal public input manifest.
- Claude Code hooks are represented as Claude settings, not as a Stet hook DSL. Put the customer-authored project settings file at `.claude/settings.json` and declare every repo-local hook script or hook directory in the harness manifest:
  ```yaml
  claude_code:
    settings_path: .claude/settings.json
    hook_files:
      - .claude/hooks/
  ```
  Stet resolves those files from the same baseline/candidate source as the harness manifest, rejects unsafe paths/symlinks/URLs and undeclared repo-local command files, stages them for `agent: claude-code`, and hashes the settings plus hook files and executable modes into `harness_surface`.
- The richer executed evidence lives below that boundary as `harness_surface` inside `rules_runtime.v1.json`, `stet eval report --change-manifest --json`, and `release.v1.json`. Harness-bundle runs use `kind: harness_bundle`; ordinary `agents_md` / `claude_md` runs use `kind: instruction_surface` unless the suite uses the repo default `.stet/stet.harness.yaml` or supplies `eval.harness`, which records `kind: runtime_harness`.
- Hook execution observability is currently conservative: `runner_runtime.v1.json` records the configured hook count, settings digest, hook file digests, executable modes, `execution_status: unobserved`, `failure_category: harness_hook_failure`, zero observed failures/timeouts unless stable telemetry is present, and `observability: session_log_only`. Do not claim hooks improved quality without a completed repo eval and a report showing both quality and runtime deltas.
- If the rules launch also declares `change.rules.search_space: ./stet.search_space.yaml`, the public `stet.search_space/v1` manifest stays requested-contract only while runtime and rules reports project the executed `search_space` object plus `search_space_path` and `search_space_digest` with `source=requested_manifest`. Without that manifest, rules runtime still emits `search_space` with `source=runtime_default` so the effective bounded context is always present. `release.v1.json` carries the same nested `search_space` object and tracks the digest under freshness.
- A rules launch may also declare `change.rules.candidate_identity` with `candidate_id`, `parent_id`, `decision_subject`, `primary_lever`, changed/logical surfaces, changed artifacts, and optional `compound.declared`. Runtime writes `candidate_identity` into `rules_runtime.v1.json`, rules reports, check-ins, plan output, and Trial Result context. `valid_one_lever_treatment` is decision-usable for the declared surface; `inspect_only_declared_compound_treatment` and `inspect_only_adjacent_surface_drift` are diagnostic; `invalid_search_space_violation` and `invalid_undeclared_compound_treatment` block rules launch before spend when a requested search space proves the identity invalid.
- `manifest resolve` does not emit `harness_surface`, `search_space`, staged manifest paths, or other runtime-only provenance.

## Receipt

```text
STET :: RULES REPORT

answer      safe
confidence  medium
phase       report
compare     candidate vs baseline
sample      32 tasks
delta       pass +1pp  equiv +5pp  cost -8%
driver      candidate improves equivalence and cost without failing guardrails
holdout     decision_grade
promotion   ready_to_promote
evidence    .stet/rules/stet.change.yaml
why         Promote is next only because the Trial Result links a clean holdout
            and reports promotion_status=ready_to_promote.
recommend   promote release state
command     stet promote --change-manifest .stet/rules/stet.change.yaml --reason "..."
other       inspect deeper evidence before rollout mutation; stop without changing rollout state
```

Release warning codes carried in receipts include `default_branch_fallback`:
surfaced when the change manifest does not pin an explicit baseline source and
the rules launcher fell back to the repo's default branch. It is informational,
not blocking; pin `context.baseline.source` explicitly in the change manifest
to silence it.

Common next steps:
- `promote`: `stet promote --change-manifest .stet/rules/stet.change.yaml --reason "..."`
- `promote override`: `stet promote --change-manifest .stet/rules/stet.change.yaml --reason "..." --allow-inspect` when trust remains `inspect` and the operator is intentionally overriding the gate
- `repair compare`: `stet eval rules repair --change-manifest .stet/rules/stet.change.yaml --json` when the persisted rules runtime exists but the canonical Trial Result is incomplete; use this for OOM/rate-limit interruptions before deleting the compare root, because repair reruns only missing/retryable arm tasks and can replay unchanged AGENTS.md/CLAUDE.md overlays from the change manifest. `resume` remains accepted as a compatibility alias. Repair cannot recover a terminal arm failure: when status/report emit a `repair` block with code `RULES_COMPARE_ARM_FAILED` or `RULES_ACTIVE_ARM_FAILED`, inspect the failed arm root, address the harness failure (auth, config, missing bundle, etc.), then relaunch instead of repairing
- `relaunch arm`: when one arm lost every cell's `agent.patch` to a transient single-arm wipeout (e.g. an HTTP 429 that left results+validation present but `agent_no_patch`/empty patches and no arm summary), plain `repair`/`resume` stays non-spending and emits an `arm_relaunch_required` blocker; rerun `stet eval rules resume --rules-root <dir> --relaunch-arm candidate` to relaunch only that arm's empty cells while reusing every good cell and the sibling arm byte-for-byte. Accepts a comma list and repeats (`--relaunch-arm candidate,baseline`) or `all`; it spends tokens. Prefer it over `--restart`, which discards everything
- `retry graders`: use the `repair-ai-coverage` or `regrade-graders` command emitted by report/status; add `--parse-retries N` for saved grader prompts that failed JSON/schema parsing, and keep the emitted `--grading-timeout` for timeout-gapped custom graders
- `restart`: `stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml --restart` only when the operator intentionally discards existing rules evidence for that change manifest

## Running Rules Check-In

When the rules flow is still running, use the same running/check-in contract as
plain `stet eval status`, but include the manifest path and current phase.

## A/B Testing AGENTS.md or CLAUDE.md

The rules flow is the preferred path for A/B testing AGENTS.md or CLAUDE.md.
It provides full provenance, release lifecycle integration, and writes the
treatment content directly to the container filesystem so the agent reads the
correct version from disk at runtime.

If the work is an iterative wording search, run cheap probes only to discard
obviously bad drafts. As soon as one draft becomes the current best candidate,
switch back to this rules flow before reporting that the draft is better or
ready for rollout.

### Change manifest

```yaml
version: 1
schema: stet.change/v1
name: test-agents-md-update
change:
  kind: rules
  rules:
    treatments:
      - kind: agents_md    # or claude_md
```

Context defaults: baseline reads from the default git branch (committed
version), candidate reads from the working tree (uncommitted edits). Override
with explicit `context.baseline` / `context.candidate` blocks if needed.
If AGENTS.md or CLAUDE.md is new in the candidate and absent at the baseline
ref, rules treats the baseline instruction file as empty; keep using this flow
instead of switching to config-diff.

### Suite manifest

```yaml
version: 1
schema: stet.suite/v1
repo: .
selection:
  mode: rev_range
  rev_range: main~5..main
  task_ids:            # optional targeted rerun slice
    - flux-pr-1234
    - flux-pr-5678
eval:
  dataset: .stet/dataset
  baseline_model: model:sonnet 4.6
  candidate_model: model:sonnet 4.6
  grader_ai_model_id: claude-sonnet-4-6
```

Dataset builds write `repo.repository_slug` into each task from the suite repo's
change-request remote. Ensure `origin`, or `--change-remote`, points at the
canonical hosted repo before materializing a dataset.

If `stet context` or a prior completed run gives you a compatible frozen
baseline, use it in the suite manifest before launching:

```yaml
eval:
  dataset: .stet/dataset
  baseline: .stet/baselines/my-capability.json
  candidate_model: model:sonnet 4.6
  grader_ai_model_id: claude-sonnet-4-6
```

Fresh `baseline_model` evidence is for first baselines, stale or invalid
baselines, incompatible task slices / harness surfaces / grader sets, or an
explicit release-gate need for new matched baseline evidence. Otherwise, the
frozen baseline is the token-saving default.

Use the same model for both arms when testing instructions, not the model.
Model fields are selectors, so use `model:<name or alias>` rather than a raw
model string.

Suite manifest paths: `eval.dataset:` (and other path fields) are resolved
against the manifest's base directory. For a suite that lives under a `.stet/`
directory — the recommended layout — that base is the repo root (the parent of
the nearest `.stet` ancestor), so a suite at `<repo>/.stet/rules/stet.suite.yaml`
uses `dataset: .stet/dataset` to point at `<repo>/.stet/dataset`. A suite that is
not under any `.stet` ancestor anchors relative paths at its own directory
instead, so keep suites under `.stet/` to get repo-root anchoring. The schema
does not support `${repo}` interpolation. For fixtures, leave the suite manifest
in place rather than copying it, and reference it via
`--suite-manifest /absolute/path/to/fixture/stet.suite.yaml`; copying detaches
the manifest from its repo-anchored baseDir and breaks relative paths.

Selection precedence: when `eval.dataset` points at a pre-built dataset, plan
and `eval rules` take task IDs from that dataset, so the `selection:` block may
be omitted entirely. If you do include a `selection:` block it must still be
valid — a present `mode` is still schema-checked (e.g. `rev_range` still
requires `selection.rev_range`) — but its `mode` does not change which tasks
run. `selection.mode: rev_range` only takes effect when no
`eval.dataset` is set, in which case Stet uses the rev range to discover tasks
fresh. To narrow a pre-built dataset to a specific
slice, use `selection.task_ids` (or repeated `--task-id` on plan/launch);
changing the rev range in a manifest that also sets `eval.dataset` will not
shift which tasks run.

`eval.grader_ai_model_id` is required for AGENTS.md / CLAUDE.md (and any other
non-skill) rollouts: rules launches auto-bundle the craft + discipline LLM
graders, and `stet eval rules plan` and the launch refuse pre-flight if the
evaluator model is missing. Pick a different model from the candidate so the
grader is not grading its own work. Pass `--no-quality` (or set
`no_quality: true` on `eval`) only when you intentionally want to drop the
auto-bundled graders.

When Harbor needs runtime settings such as larger pod memory, put them in the
repo's `.stet/stet.harness.yaml`; suite-backed rules runs apply that canonical
manifest automatically. Use `eval.harness` when the suite should point at a
different harness manifest:

```yaml
eval:
  dataset: .stet/dataset
  baseline_model: model:sonnet 4.6
  candidate_model: model:sonnet 4.6
  harness: .stet/high-memory.harness.yaml
```

Rules reports include each compare arm's effective runner settings when Stet
has them. If a Claude Code compare emits
`harbor_claude_code_concurrent_setup_cache_skew`, treat setup-only arm failures
as infrastructure risk first: Harbor `--force-build` still reuses Docker
layers, so the candidate arm may start installer-heavy containers more
synchronously than the baseline. Lower `--harbor-concurrency` to `2` and use
`runner.harbor_args` memory overrides before rerunning.

When evaluating Claude Code hooks, keep the hook files repo-relative and
customer-authored under `.claude/`. Stet stages `.claude/settings.json` and the
declared `hook_files` for Claude Code and invalidates cached evidence when any
declared hook file digest or executable mode changes. Hooks that intentionally
transform patches, validation inputs, or scoring artifacts are outside this
first-cut contract.

This applies the same runner config to both arms. It is runtime config, not the
candidate treatment. Use `change.rules.harness` only with a `harness_bundle`
treatment when the harness itself is the thing being evaluated. Do not add
`runner:` to `.stet/stet.yaml`.

When you already froze the baseline evidence with `stet baseline freeze`, replace
`baseline_model` with the benchmark baseline reference:

```yaml
eval:
  dataset: .stet/dataset
  baseline: .stet/baselines/my-capability.json
  candidate_model: model:sonnet 4.6
```

`eval.baseline` is mutually exclusive with `eval.baseline_model`. In this mode
`stet eval rules` materializes the frozen benchmark baseline, runs only the
candidate arm fresh, applies candidate-side treatments and overlays, records
`frozen_baseline` provenance, and skips baseline phases.

Prefer this mode for A/A repeats, candidate repairs/reruns, and iterative
candidate work whenever the frozen reference is still compatible. Treat a fresh
baseline arm as the explicit exception, not the default. When reuse is
incompatible, follow the freshness, slice, validity, and provenance next action
first; do not use fresh baseline spend to paper over a wrong slice, invalid
frame, or missing required coverage. Use `--force-fresh-baseline` only for a
compatible task slice where the operator intentionally needs fresh matched
baseline evidence against the current harness surface.

The same frozen-baseline reuse can also be declared in the change manifest, which
keeps the run reproducible from the manifest alone (no `--baseline` side-channel
flag needed):

```yaml
change:
  kind: rules
  rules:
    frozen_baseline:
      path: .stet/baselines/my-capability.json
    context:
      candidate:
        source: working_tree
    treatments:
      - kind: agents_md
```

`change.rules.frozen_baseline` is mutually exclusive with
`change.rules.context.baseline`, and conflicts with `suite.eval.baseline` at
lowering time. The CLI `--baseline` flag is still accepted for backcompat but
must resolve to the same absolute path as the manifest declaration; mismatched
values fail with a field-specific error.

#### Baseline freshness gate (STET-375)

A frozen benchmark baseline is a snapshot of grader scores against a specific
harness surface (AGENTS.md, CLAUDE.md, skills bundle). When the surrounding
harness changes between freeze time and replay time, the comparison is
measuring harness drift rather than the candidate change. To make that
visible:

- `stet baseline freeze` records the baseline-arm harness surface digest on
  the baseline via `--harness-surface-digest` / `--harness-surface-kind`. The
  digest lives on the rules runtime artifact that produced the run you are
  freezing. The artifact path is content-addressed (under
  `.stet/eval-rules/<hash>/rules_runtime.v1.json`), so discover it from the
  `evidence.rules_runtime_path` field of `stet eval report --json` rather
  than hand-rolling the directory layout. For example:

  ```bash
  CHANGE=.stet/rules/stet.change.yaml
  RUNTIME=$(stet eval report --change-manifest "$CHANGE" --json \
    | jq -r .evidence.rules_runtime_path)
  DIGEST=$(jq -er '.harness_surface.baseline_digest' "$RUNTIME") || {
    echo "error: $RUNTIME has no harness_surface.baseline_digest; rerun stet eval rules to produce a post-STET-375 runtime artifact before freezing" >&2
    exit 1
  }
  KIND=$(jq -er '.harness_surface.kind' "$RUNTIME")
  stet baseline freeze \
    --from "$(dirname "$RUNTIME")/compare/arms/baseline" \
    --name my-baseline \
    --harness-surface-digest "$DIGEST" \
    --harness-surface-kind   "$KIND"
  ```

  `--from` must point at the baseline arm root (`.../compare/arms/baseline`),
  not the compare root: `stet baseline freeze` resolves the benchmark baseline
  from a single arm's `manifest.json` + `reports/summary.json`. Pointing at the
  compare root would fall back to a snapshot freeze that silently drops the
  `--harness-surface-*` flags and leaves the gate at `cache_status=unknown`.

  The `jq -er` guard is load-bearing: with plain `jq -r`, a pre-STET-375
  runtime artifact (`baseline_digest: null`) yields the literal string
  `"null"`, which gets recorded as the digest and produces a nonsensical
  `stale_detected` reason on every subsequent run. `-e` makes `jq` exit
  non-zero on null so the freeze fails cleanly instead.

  Baselines frozen before this gate, or frozen without these flags, replay
  with `cache_status=unknown`.
- Each `stet eval rules` run with `--baseline` recomputes the current harness
  surface's baseline-arm digest, compares it to the recorded one, and labels
  the baseline arm's `cache_status` in `eval_report.v1.json`:
  - `hit` — digests match; frozen replay is sound
  - `stale_detected` — digests diverge; a `WARNING` is logged and a
    `Baseline cache_status` line appears in `stet eval status`
  - `unknown` — recorded or current digest unavailable
- The gate is soft: it never blocks the run. Before bypassing reuse, read
  `decision_receipt.baseline_freshness.next_action` or
  `evidence.baseline_freshness.next_action` from the report evidence; status may
  only expose the cache-status line unless it embeds the report/check-in payload.
  To break out of a confirmed stale-baseline loop on a compatible slice, pass
  `--force-fresh-baseline` to `stet eval rules`; the flag ignores the frozen
  snapshot and runs the baseline arm fresh against the current harness surface.

### Run

```bash
# Edit AGENTS.md or CLAUDE.md (don't commit yet)
# Add --baseline .stet/baselines/<name>.json when a valid frozen baseline exists.
stet eval rules \
  --change-manifest .stet/rules/stet.change.yaml \
  --suite-manifest .stet/rules/stet.suite.yaml
stet eval status --change-manifest .stet/rules/stet.change.yaml
stet eval report --change-manifest .stet/rules/stet.change.yaml --json
```

CLI `--baseline .stet/baselines/my-capability.json` may override the suite
baseline and takes precedence over `eval.baseline`, but it cannot be combined
with `--baseline-model`. If `stet eval rules plan` reports a reusable baseline
and no incompatibility, carry that baseline into launch instead of spending a
fresh baseline arm.

### How file overlays work

For `agents_md` and `claude_md` treatments, Stet stages file overlays outside
`/app`, installs them into the Harbor workspace, and avoids Jinja2 prompt
injection. For `skill_diff` treatments under `.agents/skills/...` or
`.claude/skills/...`, Stet stages the baseline/candidate content through the
repo-managed skills filesystem envelope so the agent sees a normal skill file.
Rules/compare launches also require the agent to load the staged `/skills/...`
copy before task work, and report/status evidence distinguishes activated
skill use from mounted-or-listed-only packaging evidence.
`docs_glob` remains prompt-template context for now because filesystem staging
would need explicit add/delete semantics when glob match sets differ by arm.

The same file overlay mechanism applies across all entry points:
- `stet eval rules` (manifest-backed)
- `stet eval config-diff` (when the file is AGENTS.md or CLAUDE.md)
- `stet eval compare --baseline-file/--candidate-file` (when `--logical-path`
  is AGENTS.md or CLAUDE.md)

Symlinks (e.g., `AGENTS.md -> CLAUDE.md`, or the reverse `CLAUDE.md -> AGENTS.md`
that many real repos use) are followed transparently during baseline/ref and
working-tree resolution; either direction is supported. Harbor stages overlay
content outside `/app`, then installs it through the existing symlink target
when the destination is a symlink, so the agent sees the convention file as a
symlink rather than a regular file copy. The installed overlay is committed
into the task image's treatment baseline, so captured agent patches should
contain only the agent's work, not the treatment overlay itself.

## Decision Semantics

Rules receipts should always explain:
- what happened
- why the result is `safe`, `not safe`, or `inconclusive`
- what the next keyed action does to rollout state
