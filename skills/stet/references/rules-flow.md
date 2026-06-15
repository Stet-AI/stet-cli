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
- `eval rules plan`: preflight tasks, arms, graders, frozen-baseline reuse, cost confidence, missing pricing/cost data, and cheaper alternatives without launching compare evidence. It persists an `eval_rules_plan.v1.json` receipt with replay-validity identity that a matching launch can reuse. It is not free: plan runs the Harbor `oracle`-agent gold-replay validation containers to populate `replay_validity` and runs the LLM-grader preflight, so under contention it routinely takes 8–10+ minutes. A future `--quick-plan` that skips replay validation does not exist yet; when an operator needs a sub-minute readiness check, reach for `stet manifest resolve` instead. The next command, `stet eval rules` without `--plan`, is the charged launch. The plan output's `task_selection_adequacy.verdict` is informational; values such as `insufficient_history` describe historical sample size for confidence calibration and do not block launch.
- `eval rules`: launch the bounded rules-backed run
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
staging, grader preflight, harness resolve, frozen-baseline load, rev-range buildability) are
surfaced separately as a top-level `launch_error` field on the
`eval_rules_runtime.v1.json` artifact, on `eval status --change-manifest --json`
when launch is blocked, and on `eval report --change-manifest --json`
(where `decision.reasons` and `decision.next_action` are also overridden so
the receipt names the launch failure). The skill wrapper preflight
(`eval rules skill --plan --json`) emits the same struct via the
`evalRulesSkillPreflightFailureV1` envelope on stdout. The shape is
`{phase, message, target, code, remediation, occurred_at}`; `phase` is one of
`resolve_baseline_context`, `resolve_candidate_context`, `stage_skills_root`,
`grader_preflight`, `harness_resolve`, `frozen_baseline_load`, or
`rev_range_buildability`.
`launch_error` and `last_error` can coexist when the launcher fails after a
partial runtime already saw per-task crashes. Read `launch_error` first when
`stet eval rules` exits before any per-task arm runs; the per-task agent
crash path is `last_error`.

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

`--ai-cmd` is a launch-only override for `stet eval rules`; use an absolute
script path when launching from scratch directories. `eval.grader_ai_model_id`
in `stet.suite.yaml` supplies the independent evaluator for LLM-backed graders
so the model under test does not grade its own work. Stet defaults to
provider-native schema output through the matching local CLI; set
`eval.grader_runtime: shell_text` with `eval.grader_ai_cmd` only when forcing
the legacy shell-text evaluator. `--grader-ai-model-id` is the matching CLI
override, and `plan` / charged launch refuse pre-flight when neither the suite
nor the CLI supplies an evaluator and the resolved grader set includes any
LLM-backed grader.

For Cursor-backed model-under-test runs, use `Composer 2.5` / `composer-2.5`
and `agent.name: cursor`; do not use `composer-2.5-fast` unless the fast tier is
the explicit treatment. Keep graders independent with `--grader-ai-model-id`;
add `--grader-ai-cmd` only for legacy shell-text grading. A local `agent login`
session is enough; Stet bridges the host Cursor OAuth credential into Harbor
without requiring `CURSOR_API_KEY`.

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

For optimization loops, add `--plan-task-slices --iteration-count N
--checkpoint-count N --holdout-count N --seed <seed> --change-manifest
<stet.change.yaml>`. This writes `iteration.suite.yaml`,
`checkpoint.suite.yaml`, `holdout.suite.yaml`, and `task_slice_plan.v1.json`,
then wires the suites into `change.rules`. `checkpoint` is the validation lane;
there is no separate public `screening` lane. The planner receipt explains
selection strategy, fallback signals, exclusions, and holdout contamination, but
it does not replace replay-validity checks.

Put stable variance controls in the suite manifest under `eval:`:
`task_order_seed`, `workers`, `model_workers`, `harbor_concurrency`, and
`harness_cli_cache`. `stet eval rules` accepts matching CLI flags for temporary
overrides; CLI values take precedence over suite YAML. `stet eval rules skill`
also accepts `--task-order-seed` and writes it into its synthesized iteration
suite; omit the flag for fresh per-run randomness.

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
`stet.yaml` `quality:` config, or the recommended default (`discipline` bundle +
`intentionality`) when no quality config exists. This ensures decision-grade
evidence on the first run without requiring post-hoc `regrade-graders`.

The rules-default profile bundles **7 graders total**: the coding-quality trio
(`equivalence`, `code_review`, `footprint_risk`) plus 4 quality graders — the
`discipline` bundle (`clarity`, `simplicity`, `coherence`) and `intentionality`.
If the repo pins a `quality:` profile in `.stet/stet.yaml` (e.g.,
`craft+discipline`), the rules-default seven are REPLACED by the pinned set
(typically 10–11 graders, adding `robustness`, `instruction_adherence`,
`scope_discipline`, `diff_minimality`, and the craft graders) — see
`quality_profile.source` in plan output to confirm which path resolved.
This is distinct from the **leaderboard** profile used for model-comparison
runs, which bundles the full **8 craft + discipline graders** (`clarity`,
`simplicity`, `coherence`, `intentionality`, `robustness`,
`instruction_adherence`, `scope_discipline`, `diff_minimality`). Operators
moving between the rules and leaderboard flows should expect that difference;
neither profile is a strict superset of the other and they grade different
surfaces.

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

The default quality bundle is LLM-backed (the `discipline` bundle covers
`instruction_adherence`, `scope_discipline`, `diff_minimality`, and the
recommended default adds `intentionality` alongside it), so
`eval.grader_ai_model_id` must be set in `stet.suite.yaml` (or supplied as
`--grader-ai-model-id`) for any non-skill treatment that auto-bundles them.
`stet eval rules plan` and `stet eval rules` both refuse pre-flight when those
evaluator fields are missing and any LLM-backed grader is bundled. Worked
stanza:

    eval:
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
  dataset: ./dataset
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
  dataset: ./dataset
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

Suite manifest paths: `eval.dataset:` (and other path fields) is resolved
relative to the suite manifest's own directory; the resolver walks up to the
nearest `.stet` ancestor to anchor relative paths. The schema does not support
`${repo}` interpolation. For fixtures, leave the suite manifest in place
rather than copying it, and reference it via
`--suite-manifest /absolute/path/to/fixture/stet.suite.yaml`; copying detaches
the manifest from its repo-anchored baseDir and breaks relative paths.

Selection precedence: when `eval.dataset` points at a pre-built dataset, plan
and `eval rules` take task IDs from that dataset and `selection.mode: rev_range`
(plus `selection.rev_range`) is harmlessly ignored. `selection.mode: rev_range`
only takes effect when no `eval.dataset` is set, in which case Stet uses the
rev range to discover tasks fresh. To narrow a pre-built dataset to a specific
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
  dataset: ./dataset
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
  dataset: ./dataset
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
