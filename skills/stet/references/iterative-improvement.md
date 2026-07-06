# Iterative Improvement

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

```
baseline eval/freeze -> inspect -> edit one thing -> rerun with frozen baseline -> threshold?
     ^                                                                 |-> met -> gate/baseline
     |                                                                 |-> not -> loop
     `------------ calibrate if grader trust is low -------------------'
```

Use this when one-shot execution is weak and the task gets better through a
scored loop. Treat the loop as bounded harness search: read the Trial Result,
choose one bottleneck, mutate one allowed Search Space lever, and rerun.
Current status tells you what is running; native loop state and check-ins tell
you why it is running. Keep that reasoning state durable so compaction,
automation turns, or long waits do not turn the next cycle into "continue
whatever was last active."

## When To Use

- "Keep iterating until the eval passes."
- "Do not stop at the first acceptable result."
- "The result is visual or subjective, but we can still score it."
- "Track progress across a long session."
- "`$stet optimize agents.md`" or another explicit optimize request on
  `AGENTS.md`, `CLAUDE.md`, a skill, model, harness bundle, tool policy,
  reasoning level, or runtime surface.

Do not use this for one-shot repo safety, model comparison, or rollout
questions. Use the main routing table for those.

## Reporting

```text
STET :: LOOP

answer      improving
confidence  medium
target      recommendation_quality >= 3.6
cycle       3
best        3.4 / 4
latest      3.4 / 4
baseline    2.8 / 4
dim         rec_quality 2.8 -> 3.4  trust=med
weakest     recommendation_quality
driver      recommendation_quality improved +0.6 but trust is medium
evidence    summary.md:L42-L67
why         Rerun is next because the gain needs confirmation as stable, not
            one noisy grade.
recommend   rerun same iteration lane
command     <same eval command that produced this loop root>
other       calibrate the grader if trust stays medium; gate only when thresholds are met
```

## Preconditions

Have:
- a repeatable eval command
- machine-readable scores or a stable report
- inspectable artifacts when logs are not enough
- an explicit stop rule (separate overall and judge thresholds)
- a known Search Space, so the agent knows which lever may change next
- a native `loop_state.v1.json` path or change manifest that resolves to one
- native optimize receipts for spend-bearing launches; do not replace them with
  a standalone Markdown ledger or direct rules launch in an optimization loop
- separate study suites when the corpus is small or credibility matters:
  iteration for learning, optional checkpoint for sparse validation feedback,
  and holdout for the finalist

If the grader is mushy, split or calibrate the rubric first with
[rubric-authoring](rubric-authoring.md).

## Driver And Subagents

The driver agent owns the loop contract: Search Space, approvals, native
`loop_state.v1.json`, canonical Trial Result reads, final interpretation, and
what gets reported to the operator. Subagents are driver-plane helpers, not
Trial evidence, but they should do real loop work in nontrivial optimization
cycles when available. Invoking the Stet skill authorizes Stet-scoped subagent
use for this work; ask only when a subagent would cross the declared Search
Space, mutate lifecycle state, exceed approved spend, or touch unrelated repo
surfaces.

Use at least one bounded subagent role before the next substantive mutation
unless the cycle is only a small status read, deterministic repair, or the tool
surface is unavailable:

- trajectory/evidence scan: inspect representative weak, flipped, failed,
  no-patch, surprising-tie, or strongest examples
- validity scan: check evidence quality, grader coverage, task adequacy,
  provenance, stale baseline, and adjacent-surface drift
- candidate synthesis: propose exactly one in-search-space mutation with a
  falsifiable hypothesis and quality risk
- candidate experiment: apply and run one narrow mutation in an isolated
  subagent workspace or bounded write scope so the driver preserves context for
  artifact reads, loop-state updates, and the next decision
- independent review: verify the proposed accept, reject, holdout, or stop
  decision before final closeout

Do not paste raw subagent notes into the loop. Summarize their useful findings
into `stet optimize checkin` with evidence refs and let the driver read the
next canonical Trial Result.

## Screening Triage

Classify every completed iteration before editing, reverting, or stopping:

- `reject`: invalid evidence, hard-gate failure, clear objective regression, or
  a repeated lever class that the contradiction check has refuted
- `iterate`: useful learning but no credible finalist; choose the next bounded
  lever inside the Search Space
- `ready_for_holdout_review`: the finalist improved the primary target or most
  emphasized dimensions, but iteration evidence is mixed, small-n, degraded, or
  missing holdout support
- `repair`: missing coverage, stale or contradictory authority, invalid subject
  posture, or incomplete evidence blocks interpretation
- `stop`: budget, Search Space, eval design, or operator boundary prevents a
  responsible next action

Do not make hard rejection the default for a promising mixed finalist. If an
`AGENTS.md`, skill, model, reasoning, tool-policy, or harness candidate improves
the main target and most emphasized dimensions but has nonfatal quality risks,
surface the tradeoff and ask whether to spend holdout instead of silently
discarding it. Holdout is still an approval boundary: the agent may recommend
`ready_for_holdout_review`, but it must not launch holdout or claim promotion
without operator approval and a clean holdout Trial Result.

Finalist/holdout gate:

- If the operator says "this or consolidated candidate" and the candidate choice
  is ambiguous, ask one routing question before changing files or launching
  holdout.
- A prior iteration can go to holdout only as the exact restored treatment. Check
  candidate id, treatment digest, and historical Trial Result/runtime authority;
  if the live `working_tree` no longer contains that treatment, restore it or
  select a new candidate.
- A consolidated candidate may combine learned patterns inside the declared
  Search Space, but it is a new candidate and needs fresh screening before
  holdout, promotion, defaults, or public claims.
- Before spending holdout, run `stet optimize launch --change-manifest <path>
  --lane holdout --probe --json` and route on blockers. If no replay-ready
  disjoint holdout suite exists, choose only: build or repair a fresh holdout
  set, accept weak diagnostic evidence with no promotion claim, or stop without
  promotion. Do not hand-wire stale suites such as `old-testcmd` without explicit
  operator approval.

## Loop

1. Read `AGENTS.md` and find the scoring command before editing.
2. Identify the current Search Space. If the next desired edit is outside it,
   stop and ask to change the search boundary instead of silently widening it.
3. Locate or freeze/reuse the baseline eval and record the current Trial Result.
   Run the baseline fresh only when no complete, compatible frozen baseline or
   comparable root exists. If the baseline eval is new and will anchor later
   cycles, freeze it before the next rerun.
4. Read persisted `eval_report.v1.json` first. Use `decision_receipt` for
   recommendation/confidence/readiness/next action and `trial_context` for task
   corpus, task selection, Harness Surface, Search Space, baseline/candidate,
   supporting evidence, freshness, and machine recommendation.
   For profile-backed loops, read
   `decision_receipt.optimization_decision.{profile_id,primary_axis,primary_metric,grader_policy}`
   and `decision_receipt.decision_subject` before ranking candidates.
   Required graders are hard coverage gates; emphasized dimensions shape
   diagnosis and ordering; diagnostic graders are explanation-only.
   Decision-subject labels are scoped: `valid_model_comparison` is not a
   prompt, reasoning-effort, or tool-policy claim; `inspect_only_*` is
   iteration evidence; `invalid_*_drift` must be repaired before using the
   result for the claimed lever.
5. Read or create native loop state before choosing the next edit. Use
   `stet optimize status --loop-state <path> --json` or
   `stet optimize status --change-manifest <path> --json` to recover the
   current hypothesis, rejected levers, latest evidence, and next allowed
   action. If the previous cycle is only in chat, automation text, or status
   prose, import a compact summary with `stet optimize checkin` before spending
   again. Use `stet optimize status --workbench` when you need a compact
   candidate tradeoff view over lineage, decision subject, subject/candidate
   validity, metric movement, quality gate, holdout status, rejected levers,
   conditional policies, next action, and canonical report links. Missing,
   invalid, inspect-only, or partial report authority must stay visible as an
   evidence state rather than being treated as success.
   A prompt like `$stet optimize agents.md` is already in this route: it may use
   `stet eval rules plan` as the replay-readiness check, but the first durable
   control-plane artifact must be native loop state or an optimize launch
   receipt, not `.stet/.../loop-ledger.md`.
6. Run bounded post-run learning before choosing the next edit. When
   `stet optimize status` reports `next_allowed_action=scan` or
   `trajectory_scan.status=needed`, spawn read-only trajectory scan subagents
   as the next product step: one inspects representative weakest-dimension
   trajectories from flips, failures, no-patch cases, surprising ties, and
   strongest/weakest graded examples; one checks evidence validity, grader
   coverage, sample adequacy, runtime failures, and stale or mixed provenance;
   one synthesizes exactly one concrete mutation candidate within the current
   Search Space. Scan subagents must not edit files or create research files.
   Persist their structured findings with
   `stet optimize checkin --loop-state <path> --trajectory-scan <path>
   --finding-ref <id> ...` or the equivalent `--change-manifest` form before
   using them to justify the next branch or a rejected lever. Do not inspect
   every trajectory by default.
7. Persist the native frontier decision before editing again. Run
   `stet optimize select --loop-state <path> --next-intent "<intent>"` or the
   equivalent `--change-manifest` form with a strategy such as `best_credible`,
   `uncertainty_sampling`, or `hard_task_focus` to record the selected parent
   or conditional harness policy, alternatives considered, constraints,
   evidence refs, and the risk or hypothesis the next branch will test. The
   receipt can choose what to try next, but it is not promotion evidence.
8. Inspect lower-level evidence only for diagnosis. Use weakest-risk output,
   `decision_receipt.tasks`, `task_detail.json`, `trajectory.json`, or direct
   artifact inspection to find the current bottleneck. If the output is visual,
   use `view_image`.
9. Synthesize post-run learning for the operator before editing: what happened,
   what trajectories suggest caused it, what is candidate behavior versus
   dataset/grader/runtime/provenance artifact, the most plausible next lever,
   a single `proposed_edit` block, and what evidence would confirm or refute it
   on the next run. This synthesis is a traceable rationale, not an approval
   pause, when the operator already asked for iteration and the next mutation is
   inside the declared Search Space. Do not paste raw subagent notes.
10. State a hypothesis before changing anything: "I believe ___ is causing this
   bottleneck because ___. If I change ___, I expect ___ to happen." If you
   cannot fill this in, you are guessing, not searching.
11. Run each candidate experiment in a subagent when available so the driver can
   preserve context for canonical Stet reads and loop decisions. The subagent
   applies one allowed lever, runs the exact native Stet command, and reports
   changed files, commands, result paths, and blockers. The driver then reads
   the returned artifacts and new Trial Result before deciding. If subagents are
   unavailable, apply the same focused mutation locally and say so. Do not add a
   separate CLI apply workflow.
12. Re-run the eval immediately with the frozen baseline when compatible, then
    read the new Trial Result.
13. Read the result against the hypothesis: confirmed, refuted, or inconclusive?
   Record the implication with check-in: what does this result teach you about
   the next hypothesis?
14. Run the contradiction check before launching another candidate: did the last
    result refute the hypothesis, refute the lever class, merely calibrate it,
    or reveal an eval-design blocker? If evidence is invalid or a hard gate
    failed, reject the candidate and pivot or stop instead of tuning around the
    failure. If the candidate improved the primary target or most emphasized
    dimensions but carries nonfatal regressions, classify it as
    `ready_for_holdout_review` and ask the operator whether to run holdout or
    reject now.
    If the optimization decision is `reject_invalid`, repair the missing metric,
    hard gate, or required grader coverage before treating the candidate as
    evidence for the loop.
15. Keep the current best version. Revert only if the new result is clearly
    worse in scores or artifacts.
16. Continue until thresholds are met, evidence quality blocks the decision, or
    the eval design itself is the blocker.

Never end a loop update with scores alone. The user should always know whether
the next move is "iterate again", "calibrate the grader", or "stop and ship."
For ongoing work, persist the compact loop state with `stet optimize checkin`
and include only a short human mirror in the status update. A compacted agent
should resume from native loop state, optimize status, and the linked Trial
Result instead of asking the operator to reconstruct the loop.

When an analysis spans multiple roots, retries, frozen baselines, reports, logs,
or notes, create or consult a named study before doing manual artifact
accounting. For fresh work, start the analysis receipt before running evals:

```bash
stet study start <study-id> \
  --corpus <stet.suite.yaml|dataset-dir|selection_receipt.v1.json> \
  --select <selector> \
  --question "<analysis question>" \
  --json

stet eval report --out <root> --study <study-id> --json
stet study scan <root-or-artifact> [<root-or-artifact>...] --name <study-id> --mode study --write --json
stet study status <study-id> --json
stet study report <study-id>
```

`stet study` is the analysis receipt. It references an existing suite, dataset,
selection receipt, or future corpus contract; it does not define tasks or parse
task.yaml. It groups refs, roles, inclusion classes, task-selection hashes,
slices, comparisons, readability, provenance warnings, and the canonical
`eval_report.v1.json` authority to read first. It does not copy or replace
`decision_receipt` as the authority for promotion or public claims.

When `--study` is omitted, `stet eval report` auto-attaches only if exactly one
existing non-inventory study matches the report's corpus/task identity. Use
`study scan --write` for already-sprawled evidence or migration from old roots.

Use `--mode study` for a named claim over one intended denominator. Use
`--mode inventory` for collection roots such as `.stet/leaderboard`; inventories
map many nested run/compare roots into task slices and stay inspect-only until an
agent chooses a narrower study/slice for a denominator claim. Stet skips task
bundles and scratch directories during recursive discovery. Re-running
`study scan --write` appends/merges refs; use a new study id when the intended
denominator changes.

## Stet Pattern

For shared skill improvement, use the rules skill loop so the iteration stays on
the canonical rules surface and records durable loop state:

```bash
stet eval rules skill \
  --skill .agents/skills/planner/SKILL.md \
  --repo . \
  --model claude-sonnet-4-20250514 \
  --goal "improve planning specificity without increasing scope risk" \
  --out .stet/skill-loops/planner \
  --tasks 12 \
  --json

stet eval report \
  --change-manifest .stet/skill-loops/planner/stet.change.yaml \
  --json
```

If the generated or hand-written change manifest declares
`change.rules.checkpoint_suite` or `change.rules.holdout_suite`, do not run those
suites during normal cycles. `stet eval rules skill` records the suite paths but
delegates only the iteration suite. After `stet eval rules plan`, use the native
launch gate:

```bash
stet optimize launch --change-manifest .stet/skill-loops/planner/stet.change.yaml --probe --json
stet optimize launch --change-manifest .stet/skill-loops/planner/stet.change.yaml --lane iteration --json
stet optimize launch --change-manifest .stet/skill-loops/planner/stet.change.yaml --lane checkpoint --json
stet optimize launch --change-manifest .stet/skill-loops/planner/stet.change.yaml --lane holdout --json
```

Checkpoint output is full diagnostic feedback, but treat it as validation
feedback after meaningful changes, plateaus, or low-n wins that look too good.
`stet optimize launch --probe` writes `optimize_launch_receipt.v1.json` without
starting Harbor, model, or evaluator work. Real launch records the same receipt
and dispatches the existing eval-rules lane only when the gate is ready. Stale
task-slice artifacts fail closed unless `--restart` records explicit
restart/resume intent. Checkpoint launch requires a prior Trial Result with
`lane_eligibility=accept_for_expansion`. Holdout is finalist-only by default and
requires explicit `--lane holdout` launch intent. Holdout launch receipt JSON
labels the active lane slice separately from `iteration_task_slice`; status JSON
projects the active `launch.task_slice`. Holdout summaries redact task IDs, and
`launch.lane_evidence` exposes the holdout suite, study artifact, runtime/report
paths, task count, and lane status. The report's
`study.readiness` is
`iteration_only`, `checkpoint_regressed`, `ready_for_holdout`,
`holdout_failed`, or `decision_grade`; a declared holdout must pass before
promotion or public study claims. For optimization loops, also read
`decision_receipt.optimization_decision.promotion_status`: a screening pass is
still blocked at `screen_passed_holdout_required` until the receipt links a clean
`holdout` Trial Result and reaches `ready_to_promote`.

For non-skill shared-surface loops, use the same control-plane rule: manifest
resolution and `stet eval rules plan` can prepare the replay workbench, but a
spend-bearing iteration should launch through `stet optimize launch` when the
CLI supports it. If the installed skill or CLI lacks native optimize commands,
stop as stale infrastructure instead of silently falling back to direct
`stet eval rules` plus manual loop notes.

When the loop needs native task selection, run `stet suite select
--plan-task-slices` before launch so `iteration`, `checkpoint`, and `holdout`
suites have a machine-readable `task_slice_plan.v1.json` receipt. A contaminated
or inadequate planner-backed holdout blocks decision-grade readiness; repair the
slice plan instead of reusing exposed holdout tasks. Loop state may expose
`screening_slice` as the optimization-facing alias for the public `checkpoint`
lane; holdout task IDs are redacted from agent-facing summaries.

Read `decision_receipt` first, then import the Trial Result into loop state:

```bash
stet optimize checkin \
  --change-manifest .stet/skill-loops/planner/stet.change.yaml \
  --from-report <eval_report.v1.json-or-output-root> \
  --summary "candidate result interpreted from decision_receipt" \
  --next "scan, select, expand, holdout, repair, reject, or stop" \
  --json
```

If a rules-skill report also exposes `evidence.skill_loop_path`, read the linked
`skill_loop.v1.json` as supporting skill-loop evidence: it can explain cycle,
best/latest scores, weakest dimension, diagnosis, next recommended change, and
any persisted `proposed_edit`. Do not treat it as the primary optimization
control plane when `loop_state.v1.json` and `stet optimize` receipts exist. Do
not infer a new cycle from a fresh report timestamp alone; only a substantively
different candidate result should advance the cycle.

On resume or after context compaction, reconstruct state from the durable
anchors before asking the operator: change manifest or output root, persisted
`eval_report.v1.json`, `decision_receipt`, `trial_context`,
`loop_state.v1.json`, optimize status, and any supporting
`evidence.skill_loop_path`. Continue from the recorded `next_executable_action`
when it is still inside the approved Search Space and spend boundary. If the
previous test has a `pending` result, finish that test first; if it was refuted
or inconclusive, use the recorded `implication` and contradiction check to form
the next one-change hypothesis. If loop state says the lever class was rejected,
do not continue that class without a new rationale recorded in loop state.

For custom-rubric quality work:

```bash
stet eval workbench probe ... --out ./stet-loop
stet eval report --out ./stet-loop --json
stet eval workbench risks --grades-dir ./stet-loop/graded/candidate --weakest --json
```

Then inspect the artifact, apply one change, and repeat.

Use `stet optimize checkin` for each cycle, but only through the current command
surface. The native fields are candidate id, hypothesis, lever, axis, imported
report, trajectory findings, summary, next action/command, blocked status,
rejected lever, rejection reason, and revisit rationale. Put mechanism, risk,
implication, and contradiction detail into `--summary` or the operator response;
do not invent a second durable row schema.

```bash
stet optimize checkin \
  --loop-state <loop_state.v1.json> \
  --candidate-id H3 \
  --lever instruction_scope_control \
  --axis quality \
  --from-report <eval_report.v1.json-or-output-root> \
  --summary "equiv +4pp; review regressed on task 12; implication: scope wording helped but became too rigid; contradiction: lever remains viable with narrower guardrail" \
  --next "select a narrower scope-control branch" \
  --next-command "stet optimize select --loop-state <loop_state.v1.json> --next-intent '<intent>' --json" \
  --json
```

Minimum native check-in data per cycle: `candidate-id`, `hypothesis`, `lever`,
`axis`, imported report or evidence ref, `summary`, `next`, and `next-command`
when a command is known. Without a summary of implication and contradiction,
the next cycle starts from scratch instead of building on what you learned.

Post-run learning receipt:

```text
POST-RUN LEARNING

observed    candidate improved skill_actionability but regressed specificity
cause       trajectories show agents followed broad guidance but guessed stack flow
artifact    inspect-only evidence: partial grader coverage and small sample
next lever  tighten skill instructions around report/status interpretation
confirm     rerun same task slice; expect fewer missed decision-receipt obligations
check       current lever class is still viable; result isolated the missing
            report/status obligation
decision    iterate with one skill-text change

proposed_edit {
  "path": "skills/stet/SKILL.md",
  "diff_or_rewrite": "diff --git ...",
  "trajectory_refs": ["task-18 trajectory.json", "task-25 decision_receipt.tasks"],
  "rationale": "Weakest traces show agents read summary text before the receipt."
}
```

`proposed_edit.path` may target any allowed Search Space lever: skill text,
`AGENTS.md`, cost instructions, grader wording, harness configuration, or a
similar bounded surface. Keep it to one section or bullet group when possible.
The block is a mutation candidate, not a reviewed diff; the operator owns the
merge decision, and promotion or public claims still require the normal holdout
and evidence-quality gates.

## Stop Condition

The loop is done when ALL three criteria are met:

1. Every dimension meets its target threshold.
2. Grader trust is high on the weakest dimension for 2 consecutive runs.
3. No dimension regressed from best.

If any criterion fails, iterate, calibrate, pivot, or stop according to the
contradiction check and evidence posture.

## Common Next Steps

- `calibrate`: `stet eval calibrate ...` — tighten weakest/noisiest rubric
- `holdout`: `stet optimize launch --change-manifest <path> --lane holdout --json`
  — finalist-only before promotion/default/public claims
- `promote`: `stet promote --change-manifest <path> --reason "<...>"` — only
  after `decision_receipt.optimization_decision.promotion_status=ready_to_promote`
  with linked decision-grade holdout evidence

## Decision Rules

- If the same weakest dimension repeats twice with low trust, calibrate.
- If the artifact looks better but the score stays flat, inspect rubric trust.
- If the candidate wins clearly and the weakest remaining risk is acceptable,
  run the finalist holdout. Promote or ship only after the Trial Result reports
  `promotion_status=ready_to_promote` with linked decision-grade holdout
  evidence.
- If evidence is stale, missing requested graders, or outside the declared
  Search Space, inspect or repair/resume before another edit. If a complete
  compare is non-decision-grade only because of sample size/history, or because
  a named repairable cell such as missing equivalence blocks the rollout claim,
  and `evidence_quality.directional_read.status` is `usable` or `limited`, use
  it for one hypothesis-backed iteration only when the operator requested
  optimization; record the caveat and do not make rollout or superiority
  claims.
- When `evidence_quality.posture` is `directional`, treat the run as expected
  small-sample iteration signal: read the per-arm dim deltas and weakest-risk
  artifacts to pick one lever, then widen the task slice before any
  release-grade run. When posture is `inspect`, stop iterating until the
  non-small-n factor (grader_coverage, grader_profile, grader_discrimination,
  provenance, validity, compare_state, skill_activation) is resolved —
  directional reads from an inspect-posture run are not credible iteration signal.
- If the candidate wins a baseline-first loop, refresh the baseline reference;
  do not describe that as release promotion.
- If an iteration needs A/A confirmation or a candidate repair/rerun, reuse the
  frozen baseline unless freshness/provenance/grader coverage makes it
  incompatible. Do not rerun a clean matched baseline just because the command
  template still contains `baseline_model`.

## Common Mistakes

- Changing the candidate without stating what you expect to happen. If you
  cannot fill in "I believe ___ because ___", you are guessing, not searching.
- Treating each iteration as independent instead of reading the previous
  cycle's implication before forming the next hypothesis.
- Asking the operator what to do next when native loop state already records an
  in-scope `next_executable_action`.
- Letting compaction erase the hypothesis/test/result/implication chain and
  continuing from a score summary alone.
- Changing several things at once, then not knowing what moved the score.
- Stopping at the first pass instead of the target threshold.
- Trusting scores without looking at the generated artifact.
- Using thread memory or a standalone Markdown log instead of `loop_state.v1.json`.
- Routing `$stet optimize agents.md` as a one-shot `AGENTS.md` rollout and
  starting direct `stet eval rules` runs instead of the native optimize loop.
- Reconstructing the verdict from summaries when a persisted Trial Result is
  available.
- Re-running checkpoint so often that it becomes another optimization target.
- Reading holdout task-level diagnostics as normal loop feedback instead of
  using the aggregate result to decide whether the finalist is credible.
