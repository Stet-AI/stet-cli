# Compare And Check-In

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

```
compare ──► report ──► complete?
                       ├─ yes, winner (release context) ──► gate / inspect / stop
                       ├─ yes, winner (baseline-first context) ──► refresh baseline / inspect / stop
                       ├─ yes, mixed ──► inspect / rerun / stop
                       └─ incomplete ──► repair / rerun / stop
```

Use this for pairwise compare, active run status, inspect handoff, and recovery
after partial results.

## Pairwise Compare

Use `compare` when the question is "baseline or candidate?" and the dataset or
compare-compatible roots already exist.

Before proposing a fresh compare, run:

```bash
stet context --repo /path/to/repo --json
```

If `artifact_reuse` is present, prefer the listed exact comparable roots or
frozen baselines before launching a new eval. If only near matches are
available, explain the task-slice or dataset drift explicitly so the operator can
decide whether fresh spend preserves enough decision value.

```bash
stet eval compare \
  --baseline /path/to/baseline-reference.json \
  --candidate-root /path/to/after \
  --out ./stet-compare \
  --json
```

Or with two explicit compare-compatible roots:

```bash
stet eval compare \
  --baseline-root /path/to/before \
  --candidate-root /path/to/after \
  --json
```

For an existing-root question with two or more arms where the answer is a
standing rather than "baseline or candidate?", use generic multi-arm compare:

```bash
stet eval compare \
  --multi-arm \
  --source-root /path/to/root-a \
  --source-root /path/to/root-b \
  --arm low=<selector-low> \
  --arm high=<selector-high> \
  --comparison-surface <harness-surface-key> \
  --denominator-policy publishable \
  --out ./stet-multi-arm \
  --json
```

Use `--denominator-policy include-contaminated` only when the operator
explicitly wants an exploratory full-denominator read. Report that validity and
denominator policy separately: contamination labels
(`agent_network_contamination`, `agent_answer_contamination`) are non-blocking
flags. Those cells keep their real `matrix_status` and count under
`publishable`, but they are not automatically clean; inspect the trace,
blocked-access events, and dataset overlap before making rollout-grade or public
claims, or exclude them by flag for a contamination-free denominator. Read
`decision_receipt.compare.multi_arm`, `multi_arm.standings`, and
`statistics.multi_arm` instead of reconstructing counts by hand. New multi-arm
reports include quality columns in `multi_arm.standings`; bind metric claims to
`statistics.multi_arm.metrics.<metric>.calibration.tier` and check each metric
standing's coverage counts before comparing arms.

Compare-only staging hardlinks immutable `runs/**` artifacts and copies mutable
metadata such as `reports/` and `validation/`. Put `--out` on the same
filesystem as reused roots; if hardlinks fail, compare fails instead of copying
large agent artifacts such as `agent.patch`. Staging excludes agent runtime
scratch (`agent/.tmp` and `agent/plugins` caches, reported as `compare:
excluded N agent scratch path(s) ...`) and, on failure, removes its partial arm
so you can retry the same `--out` without deleting `arms/` by hand.

Harbor patch capture should honor the task repo's `.gitignore` before Stet's
cache/build denylist runs. If ignored environment artifacts appear in
`agent.patch`, diagnose patch capture before judging model quality.

Or with two plain files that should be evaluated as one logical repo path:

```bash
stet eval compare \
  --dataset /path/to/dataset \
  --out ./stet-compare \
  --baseline-model "sonnet 4.6" \
  --candidate-model "sonnet 4.6" \
  --baseline-file /path/to/agents.before.md \
  --candidate-file /path/to/empty.md \
  --logical-path AGENTS.md \
  --grader equivalence \
  --grader code_review \
  --grader footprint_risk \
  --json
```

Report compare results with baseline/candidate/delta explicitly. The report now
includes metric narrative lines and a failure taxonomy for all recommendation
types (promote, hold, inspect), not just inspect.

`stet eval compare` also runs a paired bootstrap post-pass and attaches
`aggregate.<metric>.uncertainty` blocks (`baseline_ci`, `candidate_ci`,
`delta_ci`, `win_loss_tie`, `bootstrap`) for `tests_pass_rate`,
`leaderboard_eligible_pass_rate`, the derived `clean_pass_rate` (tests ∧
equivalence ∧ code review), equivalence/code-review/footprint grader metrics,
code-review rubric means, continuous encodings of the binary equivalence and
code-review graders, the derived `graded_equivalence` 0-4 `score_mean` metric
when both arms persist it, and custom grader metrics when paired values exist.
`graded_equivalence` is additive: arms without the persisted metric drop it and
compare byte-identically, so backfill older roots with
`stet runs regrade-graders --rederive-only` before expecting the row.
Tune with `--bootstrap-iterations N` (default 10000), `--bootstrap-seed N`
(default 1), `--ci-level F` (default 0.95); pass `--no-bootstrap` to skip the
pass. CIs are percentile-method, repo-stratified by per-task
`task_dataset_keys` when present, then task-id prefixes such as `zod/<task>`,
then the selection `dataset_key` fallback. The receipt prints an
`Uncertainty:` block with baseline/candidate/Δ ranges and direction-aware W/L/T
counts; older reports without these fields keep loading unchanged.

Alongside each `uncertainty` block, the same pass attaches an additive
`aggregate.<metric>.reduced_estimators` block computed on the same paired
deltas: `log_ratio` (geometric-mean candidate/baseline ratio + back-transformed
CI) for multiplicative metrics, `cuped` (covariate-adjusted delta with `theta`
and `covariate_source` — gold-patch size from `task_detail.json`, falling back
with a reason when absent), `wilcoxon` (signed-rank p + method), `robust_means`
(trimmed/Winsorized), and `mcnemar` (exact two-sided) for paired-binary metrics.
The block also carries standardized `effect_sizes` when estimable, such as
paired `cohens_dz` / `log_ratio_dz`, Wilcoxon rank-biserial, and McNemar
discordant effects; degenerate cases carry a reason instead of a fake zero.
Token/cost/duration get their own `aggregate.multiplicative_metrics.<name>`
entries whose headline is the geometric ratio (never a raw mean of arms). All
blocks are optional; reports without them load unchanged.

Compare reports also emit diagnostic `aggregate.cost_attribution` and
`behavior.cost_attribution` blocks. They include stable per-task driver keys,
paired driver deltas when behavior traces are available, unavailable-driver
reasons when traces or driver fields are missing, and top token-movement
contributors. This is attribution only: overlapping driver counts must not be
summed, and the block does not change
`decision_receipt.cost_evidence.evidence_class`.

The same pass also attaches a `calibration` tier label to each populated metric
entry, including fixed aggregate metrics, nested `multiplicative_metrics`, custom
graders, and binary-grader continuous encodings. Each label records paired delta
`median`/`p75`/`p90`, a `minimum detectable effect` (`mde`/`mde_unit`), the
small-n-appropriate interval (`delta_ci` + `ci_method` — a Beta-Binomial
credible interval for pass-rate metrics below the small-n threshold, the
log-ratio or percentile bootstrap otherwise), the backing estimator + `p_value`,
and a `tier` of `decision-grade` / `directional` / `noise-band`. The tier is
driven by graded/continuous metrics (Wilcoxon); binary metrics (tests /
equivalence / code-review pass) carry `low_power_binary` and are read as the
weakest layer at small n. `small_n: true` (default threshold 200, Bowyer 2025)
means the CI is not well-calibrated — do not read it as tight. A metric pinned
near-ceiling for both arms is flagged `saturated` and demoted to `noise-band`
unless its estimator is itself significant. New reports preserve raw `p_value`,
add BH-FDR `calibration.multiplicity.q_value`, and compute the visible tier from
the adjusted value unless an exact pre-registered primary metric is exempt. The
compare-level roll-up is
`aggregate.calibration`: it lists `decision_grade_metrics` /
`directional_metrics` / `noise_band_metrics`, and fails closed with a `reason`
and `next_action` when no metric had a paired subset. Treat a delta as
optimization signal only when its metric labels `decision-grade` (or consistently
`directional` across runs); never iterate on a `noise-band` movement.
The same information is projected by default into `statistics` in
`experiment.json`, `eval_report.v1.json`, and the sibling HTML report so readers
do not need to reconstruct the panel from raw aggregate fields.

When a compatible `grader_noise.v1.json` calibration artifact is present, the
default panel annotates graded deltas with `grader_noise` and marks movements
below the judge noise floor. Missing artifacts, legacy artifacts without
`grader_profile`, or profile mismatches fail closed as unknown or blocked rather
than applying a stale floor.

For subjective grader deltas, also read
`decision_receipt.graders.discrimination` (mirrored at
`decision_receipt.compare.grader_discrimination`). Missing, stale,
profile-incompatible, underpowered, invalid, or same-model-inapplicable
discrimination evidence keeps the compare inspect-only for promotion, hold /
rollback, and public superiority claims. Directional reads are still useful for
iteration, candidate ranking, and deciding where to spend the next eval budget;
do not discard them just because they are not rollout-grade.
When present, `decision_receipt.graders.reliability_policy` and status
`compare.grader_reliability_policy` summarize which required grader dimensions
are decision-grade, directional, blocked, or missing reliability evidence.
If `ready=0/N` or the policy is `BLOCKED`, do not treat subjective grader
movement as rollout-grade evidence by itself, even when per-dimension grader
scores are populated. When the policy reports directional graders, preserve that
signal in the check-in and use it to choose the next candidate, rubric repair,
or expanded task slice.
If `claim_readiness.claims[].readiness_state` is `abstained`,
`insufficient_evidence`, or `needs_review`, keep the claim blocked or
inspect-only until the named grader/evidence blocker is repaired. A
`directional` readiness state can support diagnosis, iteration, candidate
ranking, and follow-up eval selection; it is not calibrated enough to be the
sole basis for rollout-grade decisions.
If the compatible `grader_discrimination.v1.json` artifact lives outside the
compare root, pass `--grader-discrimination-artifact <path>` to the compare or
report command; Stet still fails closed on missing, unreadable, or
profile-incompatible artifacts.

When `delta_ci` is available, promotion is noise-aware: a candidate
point-estimate win only counts as promotion-strength when the favorable delta is
greater than `promote_noise_floor * (delta_ci.hi - delta_ci.lo)`. The default is
`0.5`; set it with suite `eval.promote_noise_floor` or direct
`--promote-noise-floor`. Missing CI keeps the legacy point-estimate behavior,
while CI-backed wins below the floor produce inspect/inconclusive rather than
promote.

Compare task selection is canonical and sorted, while harness dispatch is
shuffled by default with a generated seed recorded in arm manifests. For
dataset-backed compares, `--task-order-seed <seed>` overrides that seed for
deterministic replay while preserving the same sorted task set in
`task_selection` and reports.
Existing-root compares can use repeatable `--task-id` / `--task-pr` to
materialize a no-spend narrowed compare root; selected tasks must exist in both
arms, and persisted compare/report artifacts describe that narrowed slice.

```text
STET :: COMPARE

answer      safe
confidence  medium
step        compare -> gate
baseline    sonnet 4.6
candidate   codex 5.3
sample      24 tasks
delta       pass +0pp  equiv +7pp  review -2pp  footprint +0.15
failures    no_patch 0→3  infra 0→0  test_failure 2→1
driver      candidate wins on equivalence without introducing review regressions;
            3 candidate tasks produced no patch (inspect subtypes before
            calling this model behavior or setup failure)
evidence    .tmp/stet-compare
why         Gate is next because the candidate has a bounded win and this is
            where compare evidence becomes a release decision surface.
recommend   gate release state
command     stet eval workbench gate --from <compare-root>
other       inspect mixed or surprising task evidence first; stop without lifecycle change
```

When the compare is against a frozen baseline and the operator is running a
baseline-first improvement loop rather than a release rollout, change the
default next action:

```text
STET :: COMPARE

answer      winner
confidence  medium
step        compare -> baseline refresh
baseline    current frozen baseline
candidate   latest candidate
sample      9 tasks
delta       tests +50pp  equiv +50pp  review +0pp  footprint -0.01
driver      candidate beats the frozen baseline on the resolved comparison
            metrics and this workflow is baseline-first, not release-gated.

recommend   freeze candidate as current baseline
command     stet baseline freeze --from <winning-candidate-root> --name <baseline-id> --json
other       inspect remaining quality misses before another loop; stop without updating baseline
```

When this is the first completed model, reasoning, or harness-setting compare
for a repo, valid directional evidence can still be worth freezing. If one arm
clearly leads but the sample is too small for promotion, recommend baseline
capture as the default next step and keep the confidence label explicit:

```text
STET :: COMPARE

answer      directional winner
confidence  low
step        compare -> baseline capture
baseline    opus 4.6
candidate   opus 4.7
sample      3 tasks (directional only)
delta       tests +0pp  equiv +0.69  review +0.69  cost lower
driver      candidate leads across every requested quality dimension, but the
            sample is below the decision-grade threshold.

recommend   freeze 4.7 as directional baseline
command     stet baseline freeze --from <winning-candidate-root> --name <baseline-id> --json
other       rerun at full slice for promote-grade evidence; stop without baseline state
```

When the failure taxonomy shows `no_patch` or `infra` counts, surface them in the
`failures` and `driver` rows. Inspect `validation_failure.kind` subtypes before
interpreting the counts: `agent_no_patch`, `patch_capture_empty`,
`patch_capture_sanitized_empty`, and `unknown_no_patch` are task-level no-patch
outcomes, while `setup_failed_before_agent`, `agent_never_ran`, and
`verifier_failed_before_patch_application` are invalidating infra blockers. The
operator needs to know whether the delta is model/task signal or an artifact of
broken setup or verification.

Do not read `behavior_metrics.patch_calls: 0` (or `distinct_patched_files: 0`) as
patchless — those count formal patch-tool calls the trajectory parser observed,
not whether a diff exists. The canonical patch-presence signal is the
`behavior_metrics.patch_artifact` block (`present` / `size_bytes`), resolved from
the on-disk `agent.patch` and followed through stitched/retry runs to the
aggregate path. A task can show zero patch calls beside a present, nonzero patch
artifact. A Go `invalid toolchain … is a language version but not a toolchain
version` verifier failure is classified as `infra_toolchain`, not an ordinary
model failure.

The report text now includes for all recommendation types:
- A comparison table with baseline/candidate/delta columns
- A failure breakdown section (omitted when both arms are clean)
- Metric narrative lines showing `Label: X% -> Y% (state)` per signal
- Review mean lines now label the contributing population explicitly (`publishable` or `all validated`) and include per-arm `n=` counts when available.

Machine-readable default:
- Read persisted `<compare-root>/.stet/eval-report/eval_report.v1.json` first
  when it exists. Otherwise run `stet eval report --out <compare-root> --json`.
- Read `decision_receipt` as the canonical decision object.
- Do not read top-level `decision` or top-level `metrics`; those legacy fields
  are no longer present in the JSON report.
- For completed compares, the same object is also persisted at
  `<compare-root>/.stet/eval-report/eval_report.v1.json`.
- Read `trial_context` for task corpus, task selection, Harness Surface, Search
  Space, baseline/candidate refs, supporting evidence, freshness, and raw
  machine recommendation before opening sibling artifacts.
- Read the outer `lifecycle`, `validity`, `evidence_quality`, `arms`, and
  `quality` fields too. `decision_receipt` is the interpreted verdict; the
  outer fields tell you whether the evidence is replayable, trustworthy, and
  clearly tied to the expected baseline/candidate lineage.
- Use `decision_receipt.metrics`, `decision_receipt.tasks`, and
  `decision_receipt.compare` instead of reconstructing the answer from
  `experiment.json`, arm summaries, and per-task validation files.
- When present, read `decision_receipt.capability_read` before making a
  capability claim from targeted F2P: `precise_f2p_lower_bound` is the strict
  gold-function lower bound, `mechanically_clean` is the submitted patch
  compile/check read, and `recall_supported` includes mechanically clean
  valid-but-different behavioral recall labels. Supporting modes may include
  `equivalence`, `agent_test_replay`, and `adapted_reference_test`;
  adapted-reference-test support must carry an audited adapted test diff, not a
  silent application patch. Treat these as paired recall evidence, not as a
  replacement for the strict lower-bound headline. Per-cell labels are mirrored
  in
  `decision_receipt.tasks[*].{baseline,candidate}_behavioral_recall_label` and
  mechanical status in
  `decision_receipt.tasks[*].{baseline,candidate}_mechanical_cleanliness_status`.
  A `behavioral_recall_label` of `adaptation_inconclusive` is neither credited
  recall nor a confirmed failure: the strict gate failed but no discriminating
  test was executed (for example the adaptation model judged no reference-test
  patch was needed), so do not count it as a solve or as a true regression.
- After a recall-active run, read the terminal "Behavioral recall" panel (and
  its programmatic source `task_selection_adequacy.test_verdict_basis`). It
  renders the strict precise-gold-fn pass-rate as a high-precision lower bound
  versus the recall-supported rate (precise + `impl_divergent_equivalent`), with
  a `credited / inconclusive / non_solve` breakdown. Per-arm tallies live in
  `test_verdict_basis.arms[*]` (`precise_gold_fn_pass_label_cells`,
  `impl_divergent_equivalent_cells`, `adaptation_inconclusive_cells`,
  `non_solve_cells`) — use those, not the collapsed aggregate, for a compare or
  multi-arm read. The panel is intentionally silent on clean test-backed corpora
  (no impl-divergent or inconclusive cells), so its absence is not a defect.
- Treat cost deltas as decision-grade only when the cost metric row has
  `comparability.comparable: true`. If `cost_per_task` or `total_cost` says
  `delta_display: "incomparable"`, cite the raw costs only as audit data and
  do not count them as a candidate advantage.
- For cost comparability, read `comparability.reasons` and the baseline /
  candidate provenance maps. `cache_artifact_missing`,
  `smoke_reuse_cache_provenance_missing`, `legacy_pricing_used`,
  `pricing_mode_mixed`, and `pricing_provenance_mismatch` are distinct
  causes; the raw cost fields remain audit data when any of them blocks the
  delta.
- `decision_receipt.cost_evidence` rolls the per-metric cost/token verdicts
  into one class: `decision_grade` (back a cost claim), `directional` (read the
  delta as direction only — data present but provenance not comparable), or
  `incomplete` (token coverage missing — cost is diagnostic only). It fails
  closed to `directional`, lists the blocking `reasons`, and per arm separates
  `raw_total_agent_tokens` from `billable_cost_usd` and `uncached_input_tokens`
  and carries `cache_status` for frozen-baseline reuse. Read this single block
  instead of re-deriving comparability from each cost/token row.
- `claim_readiness` is the claim-grade summary. Read it before saying same
  quality, better model, cheaper, behavior-efficient, or cheap-first-policy
  evidence is ready. It separates `ready`, `directional`, and `blocked` by claim
  type, and its `grader_admissibility` block distinguishes requested coverage
  from comparison-effective grader math. Missing, asymmetric, unavailable, or
  provenance-mismatched decisive graders block public cost/quality claims even
  if tests and raw cost deltas look favorable.
- `decision_receipt.runtime_token_evidence` is the common surface for "did
  total runtime token usage move?" across run, compare, and A/A/B optimizer
  reads. Use `raw_total_agent_tokens` there, not prompt-surface file size; read
  `coverage` / `reasons` before treating the movement as decision-grade. Grader
  cost is separate and may be explicitly missing.
- Conditional economics and footprint rows use the Go report definition of
  clean pass: tests pass, equivalence is `equivalent`, and code review is
  `pass`.
- When bootstrap ran, `decision_receipt.metrics[*].uncertainty` may include
  `baseline_ci`, `candidate_ci`, `delta_ci`, `win_loss_tie`, and `bootstrap`.
  `decision_receipt.headline_uncertainty` repeats the headline metric's CI
  envelope for quick verdict reading; absence means bootstrap was skipped or no
  paired uncertainty was available.
- Check `decision_receipt.recommendation_policy.promote_noise_floor` when
  explaining a compare verdict; it records the resolved floor used to decide
  whether CI-backed point-estimate wins were promotion-strength.
- For LLM-as-a-judge provenance, read `evaluator_model` plus
  `evaluator_model_status` from
  `decision_receipt.tasks[*].{baseline,candidate}_graders.<grader_id>` for the
  exact per-task judge, and read aggregate model sets plus status from
  `decision_receipt.graders.run.<grader_id>.evaluator_models` or
  `decision_receipt.graders.compare.<grader_id>.{baseline,candidate}_evaluator_models`.
- Also read `decision_receipt.graders.profile_status` and `grader_profile`.
  Treat `mixed` or `missing_legacy` profile status as inspect-only evidence,
  even when aggregate grader scores are present.
- Read `decision_receipt.graders.discrimination` before using subjective grader
  deltas for model superiority, promotion, hold / rollback, or public claims.
  If its status/readiness/applicability is not decision-grade, follow its
  blockers and next action instead of treating the graded delta as decisive.
- When `quality` is present, use it to identify the enabled grader bundles,
  effective grader IDs, and recurring strengths/risks per dimension. Treat
  those recurring reasons as evidence for follow-up guidance rather than as
  auto-generated AGENTS.md edits.
- For compare review means, prefer the explicit metric rows ending in
  `_publishable` or `_all_validated`; read their `population`,
  `population_label`, `baseline_task_count`, and `candidate_task_count`
  fields before summarizing a winner. These are quality computed only on the
  gradable (patch-producing) subset — read them together with the separate
  `aggregate.patch_reliability` axis (`no_patch_rate`/`no_patch_count` per arm),
  so a clean-but-unreliable arm with many no-patch tasks is never credited as
  high quality. The two axes are distinct: quality-when-patched is not the same
  as reliability-of-producing-a-patch.
- Within `decision_receipt.compare`, prefer `failure_taxonomy`,
  `grader_coverage`, and `task_flips` before scraping per-task artifacts.
- If built-in grader outcomes are missing or unknown, `grader_coverage` lists
  the affected arm/task IDs. For equivalence, also read
  `missing_equivalence`; it qualifies the headline metric and emits the exact
  `stet runs repair-ai-coverage` command to refresh only those tasks. Until
  that repair succeeds, keep the recommendation inspect-only for rollout, but
  still summarize `evidence_quality.directional_read` and taskwise quality/cost
  movement as iteration signal when `directional_read.status` is `usable` or
  `limited`.
- Read `decision_receipt.compare.behavior_coverage` before claiming behavioral
  or process-efficiency differences. If it is blocked, report captured/total
  counts and the listed `missing_task_ids`; do not silently omit the behavior
  read or imply telemetry was complete.
- For footprint reads, prefer the `surface_breakdown` block on
  `footprint_risk` (and the per-task `footprint_surface_breakdown` summary):
  it splits agent vs gold patches into `implementation` vs `test_fixture`
  sides with subkind counts (`test`, `fixture`, `expected_output`) and a
  `test_fixture_added_share`. Use it to explain footprint deltas in terms of
  what the patch actually touched, not just total churn.
- Compare automatically includes explicit `--grader` entries plus any
  additional grader that has usable aggregate evidence on both arms. Graders
  present on only one arm, missing on all tasks, or unavailable are excluded
  from comparison math and rollout recommendations, but remain visible in
  `grader_coverage` as asymmetric or missing evidence.
- `--baseline-root`/`--candidate-root` compares warn at run time (default on)
  when the candidate root is missing graders the baseline ran, naming the
  missing graders and printing the exact `stet runs regrade-graders --out
  <candidate-root> --model-key <candidate> --grader craft --grader discipline`
  recovery command. `stet eval status` then surfaces this as active repair work
  (`missing grader coverage: N/M`) on both in-flight and COMPLETE runs, so a
  degraded candidate cannot read as finished. Pass `--match-baseline-graders=false`
  to opt out for intentionally asymmetric compares.
- For AGENTS.md, CLAUDE.md, skill, or policy compares where custom, bundled, or
  repo-configured quality graders are expected, verify those grader IDs survived
  into `grader_coverage`,
  `experiment.json.graders`, or arm `decision_metrics.graders` before giving a
  final verdict. If an explicitly requested additive grader is asymmetric or
  absent, fail closed to `inspect`.
- For custom rubric compares, keep the exact rubric file path in follow-up
  commands and receipts. If the operator asked for
  `--grader /path/to/custom.yaml`, reruns, config-diff repros, and
  `stet runs regrade-graders` should keep that same path rather than replacing
  it with the resolved grader ID.
- To add bundled or repo-configured quality graders after completion, use
  `stet runs regrade-graders --grader craft --grader discipline` or
  `stet runs regrade-graders --repo <repo> --from-repo-quality`; this preserves
  the completed harness/test evidence and regenerates run summaries from
  canonical task details.
- For custom-grader timeout gaps, use the report/status `stet runs
  regrade-graders ... --task-id ... --grading-timeout 45m` repair instead of a
  full model rerun.
- When a task failed the verifier for environment reasons (e.g. a snapshot
  toolchain that needs `GOTOOLCHAIN=go1.25.1`) rather than the patch, use
  `stet runs repair-patches --out <root> --model <arm> --task-id <id> --test
  '<corrected command>'`. This reuses the existing model-under-test
  `agent.patch`, reruns validation/evidence repair, refreshes summaries, and
  does not rerun the model-under-test agent. It fails closed if a selected cell
  lacks a regular non-empty patch; those cells need a real narrowed
  `stet eval run --stitch-rerun` instead. `repair-tests` remains lower-level
  compatibility plumbing only when you already have a separate retest
  `validation.json` to stitch as explicit repaired provenance.
- LLM-backed grader repairs must carry evaluator provenance. When overriding
  the evaluator command, pass the true `--ai-model-id`; deterministic graders
  such as `footprint_risk` should not be treated as missing LLM provenance.
- If `validity` is partial/invalid, `evidence_quality` is degraded/insufficient,
  or status/report surfaces contradict each other, lower confidence and fail
  closed to `inspect`.
- If `evidence_quality.factors` includes `signal=provenance` or
  `evidence.mixed_arm_provenance`, treat the compare as inspect-only until the
  affected arm is rerun or repaired.
- Authorized smoke-seeded tasks pass silently: their authorization is recorded
  as a `smoke_preflight` phase in `experiment.json` `task_provenance.arms[*].phases`,
  with `evidence_quality.factors` left at `ok` for provenance.
- When `mixed_arm_provenance` does fire on a frozen-baseline compare, read the
  per-arm `smoke_suspected_task_ids`, `smoke_source_root_path`, and
  `recommended_action` fields before deciding what to repair:
  - `recommended_action="repair_frozen_baseline_smoke_evidence"` means smoke
    artifacts were found but failed strict authorization (e.g., harness
    mismatch, legacy baseline without persisted smoke evidence). Re-freeze the
    baseline with the current `stet` build so `evidence.smoke_preflight` is
    populated, or rerun the affected arm with `--skip-smoke-preflight`.
  - `recommended_action="rerun_affected_arm"` means the leftover artifacts are
    not smoke-shaped; rerun or repair the arm before claiming results.

Before launching a frozen-baseline rules compare, read
`eval_rules_plan.v1.json.reuse.baseline_compatibility` or the matching
`stet eval status --change-manifest ...` check-in. `incompatible` blocks
candidate spend and names a blocker/remediation; common fixes are to use a
baseline-stable harness manifest path, regrade/repair the frozen baseline grader
set, refreeze on the current harness surface, or intentionally opt into
`--force-fresh-baseline`. `stale_but_usable` and `directional_only` are
screening labels only. Candidate-only harness prompt-template changes are
labeled `application_surface=candidate_harness_prompt_template`.

On a frozen-baseline compare, read `decision_receipt.baseline_freshness` (also at
`evidence.baseline_freshness`) before trusting the delta — the stale-digest
verdict lives in the artifact, not just a stderr warning. Its `evidence_class` is
the gate:
- `valid`: the frozen baseline's harness surface matches the current run
  (`cache_status=hit`); reuse it.
- `directional`: the harness-surface digest drifted within the same kind; read
  the delta as directional only and `refreeze` for a decision-grade compare.
- `inspect_only`: freshness could not be proven (legacy baseline with no recorded
  digest, or no current digest); `refreeze`/rerun before relying on it.
- `invalid`: the harness-surface kind itself changed; the comparison frame is
  broken — `abort`, or rerun a matched A/A on the current kind to re-establish.
  `invalid`/`inspect_only` also fail `evidence_quality` closed (not decision-grade).
The block also carries the exact `frozen_harness_surface_digest` /
`current_harness_surface_digest` (and kinds) and the operator's `next_action`
(`reuse | refreeze | rerun_matched_aa | abort`) with a human `next_command`.

The `failure_taxonomy` field in compare JSON also carries these counts so
programmatic consumers can distinguish `no_patch` from ordinary test failures.

If `experiment.json.compare_state.status=incomplete`, do not present the result
as a finished win/loss verdict. Read:
- `compare_state.next_action` for the safe machine-legible follow-up
- `requested_grader_coverage` for the exact missing or unavailable grader/task work
- `recommendation` as fail-closed context only, usually `inspect_mixed_results`

Common next steps in this flow:
- `gate`: `stet eval workbench gate --from <compare-root>`
- `refresh baseline`: `stet baseline freeze --from <winning-candidate-root> --name <baseline-id> --json`
- `inspect`: `task_detail.json`, `trajectory.json`, or local inspect bundle

Baseline reference rules:
- Prefer `--baseline <reference>` when the operator already froze benchmark
  evidence with `stet baseline freeze`.
- Treat the reference as the frozen slice and provenance authority. Do not
  re-explain the flow as "rediscover the baseline root."
- If the reference is a replayable baseline snapshot and the operator wants
  fresh evidence for the same frozen baseline, use
  `stet baseline rerun --baseline <snapshot>` before comparing again.
- If the candidate wins clearly against a frozen baseline and the operator is
  updating the "current" baseline for future work, recommend
  `stet baseline freeze --from <winning-candidate-root> --name <baseline-id>`
  before suggesting another improvement loop.
- If this is the first valid model or harness-setting result for a repo,
  recommend freezing the leading arm as a directional baseline before asking the
  operator to spend on another comparison. Make clear that the baseline is a
  reusable reference, not a release promotion.
- For dataset-backed or existing-root compare, task selectors are optional.
  When `--task-id` / `--task-pr` are omitted, compare uses the full realized
  task slice.
- Do not recommend `--baseline-instruction-file` /
  `--candidate-instruction-file` for raw file A/B. Those flags are only for
  operators intentionally supplying full prompt templates with
  `{{ instruction }}`.

## Active Check-In

Use [status-checkin](status-checkin.md) for active status, heartbeat, waiting,
blockers, inspect-or-wait decisions, and status receipts. Keep this file focused
on compare interpretation and recovery.

## Inspect Handoff

`inspect` should not be vague.

Use it this way:
- task-level anomaly: point to `task_detail.json` and `trajectory.json`
- many mixed tasks or richer walkthrough needed: build a local inspect bundle
- custom-rubric artifact check: point to weakest-risk output plus the artifact
  slice that caused it

Inspect should tell the user:
- what changed
- where the evidence lives
- what they will learn by opening it

## Recovery

Use recovery when evidence is incomplete or partially degraded.

Flow-specific recovery steps:
- `repair`: repair missing quality evidence without full rerun
- `repair compare`: recover an incomplete rules compare without
  recomputing completed baseline work; this can rerun a missing or partial
  candidate arm before repairing requested grader coverage
- `retry grader`: finish retryable artifact-graded task; checks
  `validation/<model_key>/<task_id>/task_decision.json`
- `revalidate`: rerun tests only when that is the missing signal; prefer
  `stet runs repair-patches` for patch-present cells because it wraps the
  no-agent `--revalidate-tests-only` path and follow-on evidence repair

Recovery rules:
- If the compare is blocked by invalid or partially valid evidence, explain that
  as a validity problem first, not as a model-quality regression.
- When grader coverage is partial, prefer `repair compare` or `retry grader`
  over a blind full rerun.
- For rules-backed compares, `repair compare` should start with
  `stet eval rules repair --change-manifest <stet.change.yaml> --json` or
  `--rules-root <dir>` so Stet reuses the persisted runtime and arm artifacts.
- If an arm is missing tasks or has retryable harness failures, resume reruns
  only those tasks, then rebuilds compare evidence. Do not delete the compare
  root just to recover an OOM/rate-limit interruption; file-backed
  AGENTS.md/CLAUDE.md treatments are replayed from the change manifest when the
  candidate digest still matches the persisted runtime.
- When the compare root projects recoverable requested grader gaps, follow the
  surfaced ordered sequence on the existing commands: `stet runs repair-ai-coverage`
  for missing built-in AI coverage, then `stet runs regrade-graders` for custom,
  bundled, or repo-configured quality gaps, then re-check with
  `stet eval status` / `stet eval report`.
  Those repair steps preserve compare-critical metadata and existing custom
  grader surfaces so the arm stays compare-compatible while recovering
  coverage. Add `--parse-retries N` when saved grader prompts failed
  JSON/schema parsing. Keep the original custom rubric file path on the regrade
  command.
- If `stet runs repair-ai-coverage --cr-only` still leaves `code_review`
  unresolved, use the summary's stable `unresolved[].reason` and optional
  `category`/`detail` fields to separate `model_output_shape`,
  `rubric_schema`, and `runtime_failure` before escalating.
- For stranded patches (non-empty `agent.patch` with no `validation/`), `eval
  report`/`eval status` fail closed and `eval combine` refuses to merge; run the
  no-spend `stet runs repair-patches --out <root>` recovery first. See
  [full-evals](full-evals.md) for the full stranded-patches rule.

Do not use rerun when status says the current run is still healthy.
