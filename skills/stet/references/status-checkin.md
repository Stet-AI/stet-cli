# Status Check-In

Use this when the user asks "what is it doing?", "is it stuck?", "should we
wait?", or when a run is active, waiting, blocked, or partially complete.

```bash
stet eval status --out /path/to/run-root --json
stet eval status --change-manifest /path/to/stet.change.yaml --json
```

Machine-readable default:

- `stet eval status --json` is the canonical health surface for active work.
- Prefer `activity_state`, `active_work`, `last_artifact`, `blocking_tasks`, and
  `lifecycle` from the JSON payload.
- Use `lifecycle.smoke` / `lifecycle.full` when present to explain smoke-to-full
  lineage instead of guessing from sibling directories.
- Treat `STET_STATUS_SUMMARY ...` stderr lines as operator-facing mirrors of the
  same state, not the primary automation contract.
- During an active compare, absence of `experiment.json` by itself is not a
  failure signal. Compare-only roots may write it only at completion, so use
  status JSON instead of inferring failure from partial directory contents.
- For `--change-manifest` check-ins, a payload with `reasons` and no
  `run_status` or `report` is inspect-class evidence; do not treat the current
  phase alone as a clean wait signal.

## Receipt

```text
STET :: STATUS

step        eval run
state       waiting_on_model
health      active
progress    18/40 tasks
idle        6m
last_seen   validation/model-x/task-18
blocker     candidate/task-19 waiting on evaluator
lineage     smoke complete -> full active
evidence    .tmp/stet-run
why         Wait is next because artifacts are still arriving and the current
            idle window does not yet look like a stall.

recommend   wait and check status again
command     stet eval status --out <root> --json
other       inspect latest task evidence if progress stops; stop with this status read
```

## State Meanings

- `active`: new artifacts are appearing.
- `waiting_on_model`: execution is blocked on model runtime.
- `waiting_on_evaluator`: execution is blocked on grading.
- `waiting_on_quota`: execution is intentionally paused until `retry_after`;
  do not delete or relaunch completed task evidence.
- `no_progress`: no meaningful artifact progress; inspect before rerun.

## Status Reading Rules

- If `blocking_tasks` is non-empty, name the first blocker explicitly in the
  terminal receipt before recommending wait or inspect.
- Prefer blocker-first explanations over generic "still running" text.
- If status is healthy and heartbeat/progress is advancing, do not recommend a
  rerun just because logs are quiet.
- If status and persisted evidence disagree, follow evidence refs and persisted
  reports before deciding. Explain the contradiction and fail closed to inspect
  when the evidence remains degraded.

## Common Next Steps

- `wait`: run `stet eval status --out <root> --json` again after a reasonable
  interval.
- `inspect`: open the last task detail, trajectory, or runtime status artifact
  when progress stops or evidence is contradictory.
- `repair`: follow the exact emitted repair command when status exposes a
  repairable missing-grader, partial-task, or rules-runtime condition.
- `resume`: resume only when the active process has exited or status says the
  flow is stalled/retryable; do not resume over a healthy active run.
