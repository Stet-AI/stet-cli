---
name: stet
description: >-
  Use Stet to measure whether an AI coding change is safe to ship. Trigger on
  model comparisons, AGENTS.md or CLAUDE.md effectiveness, shared instruction,
  policy, skill, harness, tool-policy, reasoning, or runtime rollouts, repo eval
  setup, dataset building, regression detection, benchmarking, promote/rollback
  decisions, and questions like "is this helping", "compare models on my repo",
  "test this change", "what regressed", "keep improving until it passes",
  "which model should I use", or "should this become the default".
---

# Stet

Stet is change control for AI coding behavior. It replays real repo work and
scores agent output on correctness, quality, cost, provenance, validity, and
confidence so an operator can decide whether a model, instruction, skill,
harness, or workflow change is safe to keep rolling out.

Use this skill as the agent-facing optimization interface. The coding agent is
the optimizer; Stet is the Evaluation Function. Pick the cheapest flow that
preserves the decision the operator needs. Shared behavior changes such as
`AGENTS.md`, `CLAUDE.md`, skills, policies, model choices, harness bundles, and
tool policies need manifest-backed rules evidence before they are kept,
recommended, baselined, promoted, or described as improvements.

## Root Contract

Keep these constraints in the hot path:

- Keep planes separate. The measured agent is inside a Stet Trial; the
  measuring or driver agent is outside the Trial and owns synthesis, branch
  choice, loop state, approvals, and evidence interpretation. Driver-plane
  subagent notes are not Trial Results, graders, or decision-grade evidence.
- Declare or read the Harness Surface, Search Space, and decision subject before
  interpreting optimization results. The optimized metric is not the decision
  subject: token, latency, or quality movement is usable only for the declared
  harness surface and only when receipts show no invalid adjacent-surface drift.
- Mutate one allowed lever at a time unless the operator explicitly changes the
  Search Space.
- Missing, stale, partial, inspect-only, invalid, under-graded, or degraded
  evidence fails closed for promotion, rollback, superiority, default, and
  public claims. A good score on degraded evidence is still degraded evidence.
- Baseline refresh is not promotion. Baseline refresh updates the frozen
  reference for future compares; promotion mutates rollout state and requires
  promotion-grade Trial Result evidence.
- `screen_passed_holdout_required` is blocked from promotion. Only
  `promotion_status=ready_to_promote` with linked decision-grade holdout
  evidence can support promotion, default, or public claims.
- The agent owns eval, repair, resume, optimization, and "keep improving" loops
  until a stop rule is reached. Execute the next in-scope, non-lifecycle,
  approved-spend action by default; ask only when the next action crosses
  Search Space, spend, lifecycle, destructive recovery, auth, or invalid
  evidence boundaries.
- Optimize for the declared objective, not for the smallest plausible edit. In
  shared-behavior loops such as `AGENTS.md`, do not shrink a candidate merely
  because it has nonfatal regressions or feels safer. If a broader candidate
  improves the primary metric, weighted quality target, or operator-stated goal,
  keep it in contention and classify the regressions as tradeoffs unless they
  violate hard gates, Search Space, required graders, or promotion criteria.
- Use iteration evidence to synthesize the strongest in-scope candidate, not the
  least controversial one. A final candidate may combine multiple learned
  patterns from prior iterations when each pattern is supported by evidence and
  remains inside the declared Search Space. Treat "one concise bullet" or
  "minimal diff" as a tactic, not a default selection rule.
- When the operator states that a regression is acceptable because the candidate
  improves higher-priority outcomes, record that preference in loop state and
  continue from that tradeoff posture. Do not keep re-litigating the same
  acceptable regression unless new evidence shows a hard gate failure or a worse
  regression class.
- Use `loop_state.v1.json` and native `stet optimize` commands as the durable
  reasoning state. Do not create parallel Markdown ledgers, launch scripts,
  health receipts, or adjudicators as control planes.
- Treat `optimize`, `iterate`, `keep improving`, or max-iteration prompts as
  native optimization-loop requests even when the target is `AGENTS.md`,
  `CLAUDE.md`, a skill, model, harness bundle, tool policy, or other shared
  behavior surface. The rules flow is the replay workbench; `stet optimize` is
  the loop control plane. Do not satisfy these prompts with standalone
  `stet eval rules` plus a Markdown ledger.
- Keep `SKILL.md` as the router. When the native optimization route triggers,
  load [iterative-improvement](references/iterative-improvement.md) before
  charged work. Ordinary one-shot rules runs, model comparisons,
  reasoning-effort comparisons, status reads, and direct rollout checks stay on
  their normal routes unless the operator asks for iterative optimization or a
  promotion/default claim.
- For nontrivial optimization loops, use available subagents for bounded scan,
  candidate, patch, or review work; do not reserve them only for final review.
  The driver still owns artifact authority, loop state, approvals, and final
  interpretation. Subagents must not create research files.
- Invoking this skill authorizes Stet-scoped subagent use for eval setup,
  trajectory inspection, candidate experiments, repair diagnosis, and review.
  Ask before subagents cross the declared Search Space, mutate lifecycle state,
  exceed approved spend, or touch unrelated repo surfaces.
- The operator-facing answer must include the verdict, confidence or readiness,
  decisive deltas, evidence quality, grader coverage, main risks, and one next
  action before report paths, HTML paths, commands, or raw status output.
- If status or a partial receipt reports `zero_ready_recent_slice`,
  `no_eval_ready_tasks`, or zero PASS tasks, treat it as task-slice setup, not a
  verdict on the model or config change. Follow the emitted next command; widen
  or shift `--rev-range`, use `--allow-no-test-changes` when repo-level tests
  exist but commits rarely edit tests, or provide a known dataset before giving
  up.
- For first-run repo setup or a first AGENTS.md/CLAUDE.md signal, the driver
  agent's first and main priority is a high-quality dataset. The driver owns
  setup: inspect CI and repo history, initialize config, discover and build a
  representative starter slice, repair or widen zero-ready slices, and validate
  a meaningful build-ready slice before launching an AGENTS.md/CLAUDE.md read.
  A 1-3 task run is a smoke, not onboarding; for AGENTS.md/CLAUDE.md, fewer
  than 10 retained ready tasks means setup is not ready for an instruction
  signal. Leave quality lanes on unless the operator explicitly asks for
  no-spend preflight. For first AGENTS.md/CLAUDE.md onboarding, pass
  `--quality recommended` by default; use `standard`, `custom`, or no-quality
  only when the operator explicitly asks for that. Do not route around failed
  onboarding with config-diff or probe. Ask only for auth, spend, lifecycle
  mutation, destructive recovery, private dependency access, or an explicit
  dataset approval boundary.
- "Initial signal" does not downshift first-run setup into a tiny prefilter. If
  the repo is not already build-ready in Stet, start with onboarding-scale
  discovery before any `probe --file` or `config-diff` read.

## Canonical Read Path

1. For active work, read `stet eval status --json`.
   Prefer `activity_state`, `active_work`, `blocking_tasks`, `last_artifact`,
   and `lifecycle`. Treat `waiting_on_quota` as an intentional automatic pause:
   read `retry_after`, `completed_tasks`, `remaining_tasks`, and `next_action`
   instead of deleting artifacts or relaunching completed task evidence. Treat
   `STET_STATUS_SUMMARY ...` stderr lines as human mirrors, not automation
   truth.
2. For completed work, read the persisted `eval_report.v1.json` when it exists.
   Common locations are `<root>/.stet/eval-report/eval_report.v1.json` and the
   resolved rules runtime under `.stet/eval-rules/...`. If the locator is
   unclear, materialize or locate it with `stet eval report --out <root> --json`
   or `stet eval report --change-manifest <stet.change.yaml> --json`.
3. Inside the Trial Result, read `decision_receipt` first. The verdict string is
   `decision_receipt.recommendation`; the top-level `lifecycle.decision` mirrors
   it. `decision_receipt` does not have a top-level `decision` field.
4. For optimization loops, also read
   `decision_receipt.optimization_decision`, `decision_subject`,
   `candidate_identity`, objective profile fields, grader policy, uncertainty
   posture, lane eligibility, and holdout state. Near-miss acceptance is valid
   only when encoded by the objective profile and supported by uncertainty and
   quality evidence; it remains iteration evidence until holdout is ready.
5. Read `trial_context` for Task Corpus, task selection, Harness Surface, Search
   Space, baseline, candidate, supporting evidence, freshness, and raw
   machine-recommendation refs.
6. Read `quality`, `validity`, `evidence_quality`, `lifecycle`, and `arms`.
   Route on `evidence_quality.posture`: `actionable` means act on the
   recommendation, `directional` means iterate or widen the slice before
   promotion, and `inspect` means investigate the non-small-n evidence issue
   before reasoning from the result. When present,
   `evidence_quality.readiness_state` is the compact machine-readable readiness
   reason (`decision_grade`, `directional`, `abstained`,
   `insufficient_evidence`, or `needs_review`); it explains the posture but
   does not override the recommendation or claim gates.
   `evidence_quality.directional_read` can guide iteration, not promotion.
   If the verdict is `inspect` but `directional_read.status` is `usable` or
   `limited`, report that directional signal plainly, then name the blocker and
   repair command before making any rollout claim.
7. Before external claims, read `claim_readiness` or
   `decision_receipt.claim_readiness`. It separates claim types as `ready`,
   `directional`, or `blocked` and carries grader admissibility, evaluator
   provenance, judge-noise status, blockers, and optional per-claim
   `readiness_state`. Status controls the gate; readiness explains why.
8. Drill into lower-level artifacts only for diagnosis: `experiment.json`,
   `release.v1.json`, `task_decision.json`, `task_detail.json`,
   `trajectory.json`, logs, patches, and per-task artifacts. Do not reconstruct
   the primary verdict from summaries, pass rates, or raw p-values when a Trial
   Result exists.

## Route By Intent

When ambiguous, ask one question: "Are you testing a config change, comparing
models, setting up a repo, improving a skill, or checking a release?"

| User intent | Start here | Load |
|---|---|---|
| `$stet optimize ...`, "optimize", "iterate", "keep improving", or max-iteration request on `AGENTS.md`, `CLAUDE.md`, a skill, model, harness, tool-policy, or rollout surface | Read or create native loop state, then use `stet optimize status`, `checkin`, `select`, and `launch`; use rules only as the replay lane under that control plane; select candidates by declared objective and evidence-weighted tradeoffs, not by minimal diff size; surface holdout approval for promising mixed finalists | [iterative-improvement](references/iterative-improvement.md), [rules-flow](references/rules-flow.md) |
| Set up Stet on a new repo or get a first AGENTS.md/CLAUDE.md signal | If no ready dataset/config exists, run onboarding autonomously first: use onboarding-scale discovery, keep quality lanes on, and do not stop at a 1-3 task smoke. For AGENTS.md/CLAUDE.md first signals, default automated init to `--quality recommended` unless the operator explicitly requests `standard`, `custom`, or no-quality. Stop on a concrete `setup_required` blocker rather than substituting config-diff/probe. For AGENTS.md/CLAUDE.md, get at least 10 retained ready tasks, then use manifest-backed rules for the instruction signal; use probe/config-diff only as an explicit prefilter on that larger retained slice | [onboarding](references/onboarding.md), [rules-flow](references/rules-flow.md), [quick-probe](references/quick-probe.md) |
| Shared `AGENTS.md`, `CLAUDE.md`, policy, model, harness, tool-policy, or rollout question that is not an optimization loop | `stet context --repo <repo> --json`; if setup is missing or zero-ready, onboard and repair the task slice first; then use reusable baseline check, `stet manifest resolve`, `stet eval rules plan`, `stet eval rules` | [onboarding](references/onboarding.md), [rules-flow](references/rules-flow.md) |
| Fast local directional read or throwaway candidate check | `stet probe` or `stet probe --file`; use `stet eval config-diff` only for an explicit before/after file-diff prefilter, not as the first-run setup driver; if no eval-ready tasks exist, widen/repair the slice or use onboarding before interpreting the result | [quick-probe](references/quick-probe.md), [onboarding](references/onboarding.md) |
| Docker-free / local / worktree execution of a rules eval | `stet eval rules --harbor-backend worktree` (origin-less local checkouts supported; evidence is inspect-only and non-decision-grade by default) | [rules-flow](references/rules-flow.md) |
| Model, reasoning, CLI version, or harness-setting comparison | `stet context --repo <repo> --json`, then reuse/report comparable roots or run a pinned eval; use smoke only for explicit model/harness calibration after setup, not for new-repo AGENTS.md onboarding | [full-evals](references/full-evals.md), [compare-and-checkin](references/compare-and-checkin.md) |
| Fresh model, reasoning, harness, or corpus-slice study | `stet study start <study-id> --corpus <stet.suite.yaml|dataset-dir|selection_receipt.v1.json> --select <selector> --question "..."`, then run `stet eval report --out <root> --study <study-id>` when the report exists; omitted `--study` auto-attaches only when one existing study matches | [iterative-improvement](references/iterative-improvement.md), [compare-and-checkin](references/compare-and-checkin.md) |
| Sprawled or resumed analysis with multiple roots, retries, baselines, logs, or notes | If a named registry exists, start with `stet study status <study-id> --json` or `stet study report <study-id>`; otherwise scan direct claim roots with `--mode study`; scan broad corpora such as `.stet/leaderboard` with `--mode inventory` | [iterative-improvement](references/iterative-improvement.md), [compare-and-checkin](references/compare-and-checkin.md) |
| Baseline vs candidate compare | `stet eval compare`, preferably against a frozen baseline when compatible | [compare-and-checkin](references/compare-and-checkin.md) |
| Active run status, stuckness, waiting, heartbeat, or blocker check | `stet eval status --json` | [status-checkin](references/status-checkin.md) |
| Repair incomplete or under-graded evidence | Follow emitted status/report repair commands before rerun or restart | [status-checkin](references/status-checkin.md), [compare-and-checkin](references/compare-and-checkin.md), [rules-flow](references/rules-flow.md) |
| Shared skill addition or skill revision | Classify new-skill A/B vs revision, choose test posture, then use rules evidence or `stet eval rules skill` | [rules-skill-loop](references/rules-skill-loop.md), [iterative-improvement](references/iterative-improvement.md) |
| Optimization loop or "keep improving" | Read native loop state, update check-in, select/launch one allowed next action | [iterative-improvement](references/iterative-improvement.md) |
| Repo eval setup | Inspect CI/history, infer a starter slice, default AGENTS.md/CLAUDE.md first signals to recommended graders, clarify only when the non-instruction setup grader setting is ambiguous, then init/discover/build and repair/widen until ready or concretely blocked | [onboarding](references/onboarding.md) |
| Large reusable dataset | `stet suite discover` and `stet suite build` | [dataset-build](references/dataset-build.md) |
| Research, plan, or custom artifact quality | Choose or write custom rubrics first | [rubric-authoring](references/rubric-authoring.md) |
| Promote, monitor, or roll back | Lifecycle commands after canonical Trial Result evidence | [release-lifecycle](references/release-lifecycle.md) |
| Find where Stet is using disk or reclaim run/scratch artifacts | `stet artifacts doctor` to discover repo + cache + Docker pressure, then `stet artifacts compact --dry-run` to preview and `--apply` to reclaim; never raw `du`/`rm` on `.stet` roots | [dataset-build](references/dataset-build.md) |

## Eval Rules Workbench

Use `stet eval rules` as the main replay-backed workbench for shared behavior
changes. `stet optimize` is the loop-state and launch-control layer on top of
rules work; it is not a substitute for reading rules status, rules reports, or
the Trial Result.

Black-box routing invariant: if the operator prompt says `$stet optimize` or
otherwise asks for an optimization loop, create or read native loop state before
launching charged work. `stet eval rules plan` may inspect readiness, but the
real iteration launch should go through `stet optimize launch` so the loop has
`loop_state.v1.json`, `optimize_launch_receipt.v1.json`, frontier selection, and
check-in evidence. A direct `stet eval rules` launch is the one-shot rollout
path, not the optimization-loop control plane.

Default rules path:

```text
stet context --repo <repo> --json
-> resolve or author stet.change.yaml / stet.suite.yaml
-> check compatible frozen baseline or freeze-eligible completed evidence
-> stet manifest resolve --change-manifest <stet.change.yaml> --json
-> stet eval rules plan --change-manifest <stet.change.yaml> --json
-> stet eval rules --change-manifest <stet.change.yaml> --json
-> stet eval status --change-manifest <stet.change.yaml> --json
-> stet eval report --change-manifest <stet.change.yaml> --json
```

Rules workbench obligations:

- Use rules evidence for any shared behavior candidate the operator might keep,
  recommend, baseline, promote, or call an improvement. Probes and config-diff
  runs are prefilters only.
- Keep the treatment mechanism explicit: file overlays for `agents_md`,
  `claude_md`, `skill_diff`, and `harness_bundle`; prompt-template context for
  `docs_glob`; runtime selector for `model_update`.
- Plan before charging meaningful work. Read plan output for arms, task count,
  graders, evaluator requirements, baseline reuse, replay validity, and budget
  posture.
- If status/report emits a repair command, prefer that evidence-preserving
  repair before a rerun. Use `--restart` only when intentionally discarding
  partial rules evidence.
- For skill loops, use `stet eval rules skill` and
  [rules-skill-loop](references/rules-skill-loop.md). For ordinary rollout
  manifests, keep detailed commands in [rules-flow](references/rules-flow.md).

## Baselines And Freshness

- Before fresh Stet work on a repo, orient with `stet context --repo <repo>
  --json` unless you are already anchored on a specific active run, completed
  root, report, or setup artifact.
- Before any launch that would spend a baseline arm, check for an exact reusable
  frozen baseline or a complete arm/root that can be frozen. Use `--baseline
  <reference>` when task slice, Harness Surface, Search Space, grader set, and
  evidence validity match.
- Do not spend a fresh baseline arm to paper over a wrong slice, invalid frame,
  stale evidence, missing coverage, or provenance mismatch. Use
  `--force-fresh-baseline` only when the operator intentionally needs fresh
  matched baseline evidence for a compatible slice and harness surface.
- Partial arms are not freeze-eligible. Let running or incomplete baseline arms
  finish or repair first, then freeze before A/A repeats, candidate reruns, or
  the next optimization cycle.
- First valid model, reasoning, or harness-setting results are often worth
  freezing as directional baselines for future compares. Label sample size and
  confidence, and do not call the frozen baseline promote-grade evidence.

## Optimization Loops

Legal loop:

```text
operator question -> identify Harness Surface and Search Space
-> choose the cheapest valid Trial -> execute or resume Stet
-> read status or Trial Result -> state hypothesis/test
-> update loop_state.v1.json with stet optimize checkin
-> execute one authorized diagnostic or iteration action
-> read evidence -> continue, refresh baseline, inspect, repair, scale, or stop
```

Use native loop commands:

- `stet optimize status --loop-state <path> --json`
- `stet optimize status --change-manifest <path> --json`
- `stet optimize status --workbench`
- `stet optimize checkin`
- `stet optimize select --loop-state <path> --next-intent "<intent>"`
- `stet optimize launch --change-manifest <path> --probe --json`
- `stet optimize launch --change-manifest <path> --lane holdout --json`

If these commands are missing or the installed skill copy does not mention them,
fail closed and say the Stet skill or CLI is stale. Do not silently downgrade an
optimization prompt to a standalone rules run with an ad hoc ledger.

For check-ins, use the fields the command actually accepts:
`--from-report`, `--candidate-id`, `--hypothesis`, `--lever`, `--axis`,
`--summary`, `--next`, `--next-command`, `--blocked`, `--reject-lever`,
`--rejection-reason`, `--revisit-rationale`, `--reason`, `--trajectory-scan`,
and `--finding-ref`. Put richer implication and contradiction detail in
`--summary`, the operator response, and canonical receipts; do not invent a
second durable row schema.

Before another Trial, answer whether the previous result confirmed the
hypothesis, refuted the hypothesis or lever class, merely calibrated the lever,
or exposed an eval-design blocker. If a secondary metric improved while the
primary objective or quality gate regressed, record the candidate as rejected
and pivot or stop. Do not keep tuning a rejected lever class unless native loop
state records a new rationale.

Checkpoint is validation feedback, not the optimization target. Run holdout
only for the finalist. Promotion, default, and public claims require canonical
Trial Result and decision-grade holdout evidence.

## Operator Output

The agent owns interpretation. A completed eval, failed eval, inspect-state
eval, or check-in is not done until the agent has read the relevant JSON
evidence and translated it into an operator-facing judgment.

For active runs, explain liveness, phase, progress, blockers, latest artifact,
and whether wait, inspect, resume, or repair is next. For completed or
inspect-state runs, answer with verdict, confidence/readiness, lifecycle state,
decisive metric deltas, evidence quality, effective grader coverage, main risks,
and one concrete next action. Surface JSON and sibling `eval_report.v1.html`
paths only as supporting evidence.

If status and persisted evidence disagree, follow `evidence_refs`, the rules
runtime, and persisted reports; explain the contradiction and fail closed to
inspect when evidence remains degraded.

## Gotchas

- `probe` answers quick safety questions directly. Gate is optional, not the
  default.
- `INSPECT` and `HOLD` are completed decision states, not broken runs.
- Quiet logs are normal. Read status JSON before assuming a stall.
- Tests are the gate, not the whole source of truth. Quality dimensions above
  the gate are where strong models, skills, and instructions differentiate.
- Cheap `probe --file` runs can discard weak drafts only after setup has a
  build-ready dataset. For AGENTS.md/CLAUDE.md, keep at least 10 retained ready
  tasks before interpreting a probe/config-diff read. `config-diff` is for
  explicit file-diff prefilters, not failed onboarding. Kept or promoted shared
  behavior needs rules evidence.
- Required grader coverage that is missing, asymmetric, unavailable, or
  provenance-mismatched fails closed. Use emitted repair commands instead of
  rerunning clean evidence by hand.
- Auth, license, Claude `/login`, Harbor setup, Docker capacity, and runtime
  setup failures are infrastructure risk before they are candidate quality
  evidence. Read the relevant reference before spending again.

## Read As Needed

Only load the reference doc that matches the current route:

- [references/operator-contract.md](references/operator-contract.md): receipt
  format, reporting rules, next-step execution, and error handling.
- [references/status-checkin.md](references/status-checkin.md): active status,
  heartbeat, waiting, blockers, and inspect-or-wait check-ins.
- [references/quick-probe.md](references/quick-probe.md): probes, file-mode
  config checks, config-diff, and quick smoke.
- [references/full-evals.md](references/full-evals.md): eval run, eval smoke,
  suite discover/build, and larger reusable benchmarks.
- [references/compare-and-checkin.md](references/compare-and-checkin.md):
  pairwise compare, machine-readable compare fields, inspect handoff, recovery.
- [references/rules-flow.md](references/rules-flow.md): manifest resolve,
  eval rules, manifest-backed rollout decisions, repair, restart, overlays.
- [references/rules-skill-loop.md](references/rules-skill-loop.md): skill A/B,
  skill revision, shared skill wrapper, and rules-skill loop specifics.
- [references/iterative-improvement.md](references/iterative-improvement.md):
  native optimize-loop state, check-ins, frontier selection, holdout, stop rules.
- [references/release-lifecycle.md](references/release-lifecycle.md): gate,
  promote, monitor, rollback.
- [references/onboarding.md](references/onboarding.md): first-run repo setup,
  quality defaults, dataset building, starter-slice approval.
- [references/dataset-build.md](references/dataset-build.md): heavy dataset
  builds, Docker debug loops, ecosystem templates, scaling, and disk reclaim
  (`stet artifacts doctor` / `compact`).
- [references/rubric-authoring.md](references/rubric-authoring.md): custom
  grader design, calibration, scored rubric templates.
- [references/examples.md](references/examples.md): examples only; do not load
  for ordinary routing unless a concrete trace would resolve ambiguity.
