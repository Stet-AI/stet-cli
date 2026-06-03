# Operator Contract

Every Stet answer should be legible in one scan. This document defines the
shared terminal receipt format, next-step recommendations, and error handling
that all flows inherit. The top-level skill defines the agent-facing
optimization interface; this file defines how to project that machine contract
back to a human operator.

## Machine Contract vs Human Receipt

- `Trial Result`: canonical completed-trial object, persisted at
  `eval_report.v1.json` and emitted by `stet eval report --json`
- `status`: canonical active health/check-in object from
  `stet eval status --json`
- `terminal receipt`: compact text projection for humans in chat

Use Trial Results and status JSON for machine consumption. Use terminal
receipts to summarize the result in one scan for the operator.

The agent owns interpretation. A completed run, failed run, inspect-state run,
or check-in is not finished until the agent has read the relevant JSON,
extracted the decision/status data, and translated it into an operator-facing
judgment. Do not respond with only paths, commands, report links, or raw status
output; use those as evidence links after the verdict, evidence quality,
effective grader coverage, risks, and next action.

If the persisted `eval_report.v1.json` for the flow already exists, reuse it.
Ordinary output roots commonly persist it at
`<root>/.stet/eval-report/eval_report.v1.json`; change-manifest rules flows
persist it next to the resolved rules runtime under `.stet/eval-rules/...`.
When the locator is unclear, use the matching `stet eval report --out ... --json`
or `stet eval report --change-manifest ... --json` command to locate or
materialize it. Read `decision_receipt` for recommendation, confidence, readiness,
grader coverage, and next action (the verdict string lives on
`decision_receipt.recommendation`; the top-level `lifecycle.decision`
sibling mirrors it). Read top-level `trial_context` for task
corpus, task selection, Harness Surface, Search Space, baseline/candidate,
supporting evidence, freshness, and raw machine recommendation refs.

Authority tiers:
- `eval_report.v1.json`: first read for completed optimizer Trial Results
- `stet eval status --json`: first read for active liveness and blockers
- `experiment.json`: compare evidence authority for diagnosis
- `release.v1.json`: lifecycle authority for release and monitoring diagnosis
- `task_decision.json`: task-level scoring authority
- `task_detail.json`, `trajectory.json`, logs: inspectability and debugging

Do not reconstruct a verdict from `experiment.json`, `summary.json`, pass-rate
heuristics, or task files unless you are explicitly inspecting supporting
evidence or handling an old root without a persisted Trial Result.

If status and persisted evidence disagree, do not stop at the first payload.
Follow `evidence_refs`, the rules runtime, and any persisted
`eval_report.v1.json` / compare report, then explain the contradiction and fail
closed to inspect when the evidence remains degraded.

After the operator-facing judgment, use post-run learning when the user is
debugging, improving, or optimizing behavior. Prefer subagents when available:
one can inspect representative trajectories, one can check evidence validity
and grader/provenance gaps, and one can synthesize candidate improvements
within the current Search Space. Subagent findings are diagnosis, not graders;
summarize them as causes, artifacts, one recommended next lever, and the
evidence that would confirm or refute that lever on the next run. Skip this
extra QA for healthy active runs unless the operator asks for diagnosis.

## Core Agent Loop

```
user question
     │
     ▼
identify Search Space + route (SKILL.md)
     │
     ▼
execute or resume Trial (`stet` command)
     │
     ▼
read status or Trial Result JSON
     │
     ▼
terminal receipt (human projection)
     │
     ▼
recommended next step
     │
     └──► next command ──► terminal receipt ──► ...
```

## Receipt Format

Always:
- Answer the user's actual question first: `safe`, `not safe`, or `inconclusive`
- Include `confidence: high|medium|low`
- Name the current pipeline step
- Show a tiny data view (delta, count, bar) so the user sees what changed
- Explain why the recommended next action is next
- End with one recommended next step, including the exact command when there is
  a concrete command to run

Use compact instrument-style ASCII receipts. Prefer plain aligned lines over
heavy box borders.

### Finished Receipt

```text
STET :: <FLOW NAME>

answer      <safe | not safe | inconclusive>
confidence  <high | medium | low>
step        <current> -> <next>
compare     <what vs what>
sample      <N tasks>
delta       <dimension deltas>
driver      <dominant reason>
evidence    <path to root>
why         <why the recommended action is next>
recommend   <one next step>
command     <exact command, if applicable>
other       <material alternatives, if useful>
```

### Running Receipt

```text
STET :: STATUS

step        <current step>
state       <active | waiting_on_model | waiting_on_evaluator | no_progress>
health      <active | stalled>
progress    <N/M tasks>
idle        <time since last artifact>
evidence    <path>
why         <why wait/inspect/stop>
recommend   <wait | inspect | stop>
command     <exact status or inspect command, if applicable>
other       <material alternatives, if useful>
```

### Receipt Rules

- ASCII only, instrument-grade: measured, aligned, signal-first
- Minimum rows: `answer`, `confidence`, `step/state`, data/compare, `driver`,
  `evidence`, `why`, `recommend`
- The recommended next step is a real action the agent can take with normal
  tools, not a synthetic menu item.
- Include `command` only when the next step is a command. For edits, state the
  target file and hypothesis instead of inventing a command.
- If no real result exists yet, skip the terminal receipt but still name the
  next useful command or wait/inspect step.
- `STET_STATUS_SUMMARY ...` stderr lines are operator-facing mirrors of status,
  not the primary automation contract. For automation, read
  `stet eval status --json`.

### Per-Flow Data Minimums

- Quick probe / config diff: comparator, sample size, pass/equiv/review delta,
  dominant driver
- Smoke / full eval: verdict, confidence, leading model/arm, main
  differentiator, main risk
- Compare: baseline, candidate, delta, decisive dimension, confidence
- Artifact loop: weakest dimension, best/latest delta, target threshold,
  evidence hook
- Release / monitor: trust state, rollout state, freshness, rerun delta

## Next-Step Recommendations

Recommend exactly one next step unless the user asks for options. Use ordinary
verbs the agent can act on: `inspect`, `repair`, `rerun`, `revise`, `wait`,
`baseline`, `promote`, `rollback`, or `stop`.

For command-backed steps, include the exact command. For edit-backed steps,
name the file, the one-lever hypothesis, and the rerun command that will test
it. For stateful release steps, name the release artifact or change manifest
that the command will mutate.

Alternatives are allowed when they change the operator's real choice, but keep
them prose-first:

```text
recommend   repair grader coverage
command     stet eval rules repair --change-manifest .stet/rules/stet.change.yaml --json
other       inspect task evidence before repairing; stop with current inspect verdict
```

## Error Handling

When a `stet` command fails, do not silently retry. Report, diagnose, offer
recovery.

| Error pattern | Agent action |
|---|---|
| Command not found / CLI error | Check `stet` installed and on PATH. Report. |
| Auth failure / 401 / 403 | Report credential issue. Do not retry. |
| `waiting_on_quota` | Wait until `retry_after`; Stet will resume automatically and reuse completed artifacts. |
| Timeout | Read `stet eval status --out <root>` first. Recommend wait when healthy, rerun only after a real stall or explicit discard. |
| Docker / container failure | Run `stet harbor cleanup` first. If no run is active, offer `stet harbor cleanup --apply`; add `--prune-buildkit` only for explicit BuildKit cache cleanup. Then rerun with lower effective concurrency. |
| Partial / incomplete compare | Read `compare_state.next_action`. Offer recovery. |
| Invalid or degraded evidence | Read `validity` / `evidence_quality`. Lower confidence, explain the degradation, and fail closed to inspect when needed. |
| Empty / zero-score grading | Check grader cmd. Recommend rerun only after fixing the grader path/config; otherwise inspect. |
| `HOLD` / `INSPECT` state | Valid terminal states, not errors. Recommend the evidence inspection that resolves the uncertainty. |

### Error Receipt

```text
STET :: ERROR

step        <flow that failed>
error       <one-line summary>
evidence    <root or log path>
why         <diagnosis and what to try>
recommend   inspect error evidence
command     <exact inspect/status command, if applicable>
other       rerun only after fixing the input; stop with current state
```
