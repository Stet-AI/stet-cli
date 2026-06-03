# Release Lifecycle

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

```
gate ──► promote ──► monitor
  ▲        │           │
  │        │       ┌───┴────┐
  │        ▼       ▼        ▼
  │    promoted  status    monitor
  │        │
  │        └── rollback ──► revoked
  │                               │
  └────── rerun ─────────────────┘
```

Use this for gate, promote, monitor, and rollback after a compare or workbench
flow produced a bounded decision candidate.

Decision Policy v1 is projected through lifecycle fields, not a separate
manifest or object. Read the Trial Result first, then use `lifecycle` fields
such as `trust_state`, `rollout_state`, `freshness_status`, `gateable`,
`promotable`, `monitorable`, `next_action`, and `next_command` to decide
whether the safe move is promote, monitor, rerun, inspect, or stop.

Do not collapse baseline refresh into release promotion. Baseline refresh
changes the frozen reference for future searches; release promotion changes
rollout state for a gated capability.

Common custom-rubric quality path:

```bash
stet eval workbench probe ...
stet eval report --out <probe-root> --json
stet eval workbench gate --from <probe-root> --json
stet promote --out <compare-gate-root> --reason "..." --json
```

## Gate

Gate is the canonical handoff from bounded evidence to release state.
Gate should follow a completed Trial Result whose `decision_receipt`,
`trial_context`, and lifecycle posture make the candidate gateable. If evidence
is stale, partial, or outside the Search Space, inspect or rerun before gate.

Gate receipt:

```text
STET :: GATE

answer      safe
confidence  medium
decision    promote_candidate
trust       gated
rollout     eligible_for_monitoring
freshness   fresh
evidence    .tmp/stet-compare
why         Promote is next because gate has already established trust, and
            promotion is what turns that bounded win into current release state.
recommend   promote gated release state
command     stet promote --out <compare-gate-root> --reason "..." --json
other       inspect release evidence before mutating rollout; stop without promoting
```

State vocabulary:
- `trust`: `inspect`, `hold`, `gated`, `promoted`, `revoked`
- `rollout`: `none`, `candidate_only`, `eligible_for_monitoring`,
  `monitoring`, `rolled_back`
- `freshness`: `fresh`, `aging`, `stale`

Common next steps:
- `promote`: `stet promote --out <compare-gate-root> --reason "..."`
- `monitor`: `stet monitor run --release release.v1.json --out ./monitor-rerun`
- `rollback`: `stet rollback --out <compare-gate-root> --reason "..."`
- `status`: `stet monitor status --release release.v1.json --json`

## Promote

```bash
stet promote --out <compare-gate-root> --reason "quality improved without regressions" --json
```

Promote normally requires a trusted release.
Read `release.v1.json` only as the lifecycle authority for diagnosis or
post-gate state. The completed Trial Result remains the first read for the
decision that made promotion eligible.

If trust is still `inspect` but the operator intentionally wants to ship
despite inconclusive evidence, use an explicit override:

```bash
stet promote --out <compare-gate-root> --reason "shipping with operator override" --allow-inspect --json
```

This preserves `trust_state=inspect`, marks the rollout as operator override,
and should be treated as a higher-risk launch than a trusted promotion.
Do not use this for `hold` results.

When release metadata exists, show it in an instrument-style ASCII receipt:

```text
STET :: RELEASE

answer      safe
confidence  medium
trust       promoted
rollout     monitoring
freshness   aging
data        monitor 5/5 green  last delta +0.04
why         Monitor is next because the candidate is unchanged and the only
            missing thing is fresh evidence, not a new compare decision.
recommend   monitor frozen release contract
command     stet monitor run --release release.v1.json --out ./monitor-rerun
other       rerun if the candidate or policy changed; rollback if new risk outweighs confidence
```

## Monitor

```bash
stet monitor status --release release.v1.json --json
stet monitor run --release release.v1.json --out ./monitor-rerun --json
```

Use `monitor status` for a read-only posture check.

Use `monitor run` to execute a fresh monitoring rerun from the promoted release
contract. It writes a new monitoring output root and refreshes monitoring
evidence on the release. It is not just a status read.

Do not pass a baseline snapshot to `stet monitor run --release ...`. Baseline
snapshots stop at compare or gate; monitor remains release-only.

Release paths must point to regular release artifact files. Treat symlinked
`release.v1.json` paths as invalid rather than lifecycle authority.

Replay contract:
- `monitor run` should be explained as replaying the promoted release's frozen
  `task_selection` and arm provenance, not rediscovering tasks from the current
  repo.
- `task_selection` carries the frozen `requested`, `recommended`, and
  `realized` task ids for replay.
- If replay detects drift in the stored slice, repo-state bindings, skill
  digest, context-pack digest, or managed-baseline provenance, the correct
  operator explanation is fail-closed and reprobe, not silent refresh.

When to choose what:
- `monitor status`: read-only posture check
- `monitor run`: unchanged candidate, stale or aging evidence
- `reprobe`: model, policy, artifact, or dataset contract changed

## Monitor Decision Function

Use this to decide which monitor action to take. Read `freshness_status`
and candidate state from the release JSON.

| Condition | Action | Command |
|---|---|---|
| Just checking posture | `monitor status` | `stet monitor status --release release.v1.json --json` |
| freshness=`aging` or `stale`, candidate unchanged | `monitor run` | `stet monitor run --release release.v1.json --out ./monitor-rerun --json` |
| Candidate, model, policy, artifact, or dataset changed | `reprobe` | return to probe or compare flow |
| Trust regression detected | `rollback` or `reprobe` | `stet rollback --out <root> --reason "..."` |

Machine-readable contract:
- `monitor status` is read-only. It queries the release record and returns
  posture without executing work. `lifecycle.execution_status` reflects the
  last known state, not a fresh measurement.
- Monitoring history entries carry their source `release_id`; treat trust drops
  as monitor regressions only when adjacent explicit history entries belong to
  the same release.
- `monitor run` is execute. It replays the promoted release's frozen
  `task_selection`, runs the evaluator, and writes fresh monitoring evidence.
  `lifecycle.freshness_status` updates to `fresh` on success.
- If the operator only wants refreshed benchmark evidence for a baseline
  snapshot, the correct command is `stet baseline rerun --baseline <snapshot>`,
  not `stet monitor run`.

Never recommend `monitor run` when the candidate has changed. The correct
action is `reprobe` because the frozen task selection contract may no longer
apply.

## Roll Back

```bash
stet rollback --out <compare-gate-root> --reason "regression detected" --json
```

Rollback postconditions:
- `trust = revoked`
- `rollout = rolled_back`
- monitoring should halt until new evidence exists
- the default next step is inspect or reprobe, not promote again

## Rules

- Release path, trust state, and rollout state appear only after gate.
- Promote, monitor, and rollback are lifecycle actions, not first-line eval
  entry points.
- Decision Policy v1 is the lifecycle projection; do not invent a separate
  policy artifact or override `next_action` without explicit operator intent.
- `monitor status` reads the promoted release; `monitor run` executes work
  again and merges fresh evidence back into that release record.
- When a release regresses, the next step is usually re-probe or re-run after
  fixing the candidate, not repeated promote attempts.
- Always end lifecycle answers with one recommended next step so the operator
  knows whether to monitor, re-probe, roll back, or stop.
- Use state-conditioned recommendations:
  `hold|inspect` -> inspect, rerun after a targeted fix, or stop
  `promoted+fresh` -> read status, monitor, or rollback if new risk appears
  `promoted+stale` -> monitor, rerun after a policy change, or rollback
  `rolled_back` -> inspect, rerun after a targeted fix, or stop
