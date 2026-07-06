# Interaction Examples

Three complete multi-turn traces showing the agent protocol in action. Use
these to pattern-match on routing decisions, receipt composition, and keyed
action handling.

## Trace 1: Rules Flow - Happy Path

**User:** "Is our new CLAUDE.md helping on this repo?"

Agent routes to: rules flow (`claude_md` treatment).
Agent reads: `references/rules-flow.md`

```bash
stet manifest resolve --change-manifest .stet/rules/stet.change.yaml
stet manifest resolve --suite-manifest .stet/rules/stet.suite.yaml
stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml
stet eval report --change-manifest .stet/rules/stet.change.yaml --json
```

Agent reads the Trial Result first: `decision_receipt` for the verdict and next
action, `trial_context` for task selection and baseline/candidate context, then
outer `lifecycle` and `evidence_quality` for readiness and trust posture. It
then projects the compact terminal receipt:

Agent reports:

```text
STET :: RULES REPORT

answer      safe
confidence  medium
phase       report
compare     candidate (with CLAUDE.md) vs baseline (without)
sample      12 tasks
delta       pass +0pp  equiv +10pp  review +3pp
driver      equivalence improved on 7/12 tasks without review regression
evidence    .stet/rules/stet.change.yaml
why         Promote is available because this is the formal rollout decision
            surface and the required graders are present.

recommend   promote current release state
command     stet promote --change-manifest .stet/rules/stet.change.yaml --reason "..."
other       inspect task-level evidence; stop without rollout mutation
```

**User:** stop

Agent acknowledges stop, names the change manifest and rules report path. Done
in 2 turns.

---

## Trace 2: Config Diff Prefilter - Rules Handoff

**User:** "I have several AGENTS.md wording drafts. Give me a cheap first pass
before we spend on the release eval."

Agent routes to: quick-probe prefilter.
Agent reads: `references/quick-probe.md`

```bash
stet eval config-diff --repo . --file AGENTS.md --dataset .stet/dataset --model "sonnet 4.6" --json
```

Agent treats the result as directional only and says so explicitly.

Agent reports:

```text
STET :: CONFIG DIFF PREFILTER

answer      inconclusive
confidence  medium
step        probe -> inspect
compare     candidate (new AGENTS.md) vs baseline (git HEAD~1)
sample      12 tasks
delta       pass +0pp  equiv -4pp  review +1pp
driver      equivalence dropped on 3/12 tasks; review gain is noise
evidence    .tmp/stet-config-diff
why         This can prune a weak draft, but it is not release evidence for
            AGENTS.md and does not prove custom agents_* grader coverage.

recommend   inspect task-level evidence
command     <open task_detail.json, trajectory.json, or local inspect bundle>
other       rerun after a change; stop with the bounded verdict
```

**User:** inspect

Agent forms a hypothesis before inspecting:

> **Hypothesis:** I believe the equiv drop is caused by scope creep in the
> candidate's edits — the original AGENTS.md had a "prefer minimal diffs"
> constraint that the new version removed. If that constraint was the
> guardrail, I expect tasks with multi-file changes to show the largest
> regressions.

Agent inspects `.tmp/stet-config-diff` task evidence and reports:

> **Result:** Confirmed. Tasks 18 and 25 both show the agent touching 3-4
> files when the baseline touched 1. Task 12 is a direct regression — the
> agent rewrote a helper it didn't need to.
>
> **Implication:** The "prefer minimal diffs" constraint was load-bearing.
> Restoring it with tighter wording should recover equiv without regressing
> review. The next hypothesis should check whether tighter wording
> introduces rigidity on tasks that legitimately need multi-file changes.

```text
recommend   revise the constraint and rerun
command     <edit AGENTS.md, then rerun the same probe>
other       rerun as-is to confirm the signal; stop with current diagnosis
```

**User:** restores the constraint with clearer wording, says "try again"

Agent recognizes this as another cheap prefilter pass. The prior implication
said to watch for rigidity on legitimate multi-file tasks, so the agent
carries that forward:

> **Hypothesis:** The tighter wording ("never touch files outside the issue
> scope") will recover equiv on tasks 18/25/12, but may cause the agent to
> under-edit on tasks that legitimately span multiple files.

```bash
stet eval config-diff --repo . --file AGENTS.md --dataset .stet/dataset --model "sonnet 4.6" --json
```

> **Result:** Equiv recovered +2pp overall. Tasks 18 and 25 improved. No
> rigidity regression visible in this retained sample — but sample is only 12 tasks,
> so confidence is medium.

```text
STET :: CONFIG DIFF

answer      safe
confidence  medium
step        directional prefilter
compare     candidate (revised AGENTS.md) vs baseline (git HEAD~1)
sample      12 tasks
delta       pass +0pp  equiv +2pp  review +1pp
driver      equivalence recovered; revised constraint is working
evidence    .tmp/stet-config-diff

recommend   run manifest-backed rules eval
command     stet eval rules --change-manifest .stet/rules/stet.change.yaml --json
other       spot-check recovered tasks; stop with only the directional read
```

**User:** `R`

Agent runs the retained candidate through the rules flow:

```bash
stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml
stet eval report --change-manifest .stet/rules/stet.change.yaml --json
```

Done in 5 turns. The inspect -> revise -> rerun cycle recovered a regression,
and the retained AGENTS.md candidate still had to pass the rules flow before
the agent could recommend it.

---

## Trace 3: Onboard → Rules

**User:** "Set up Stet in this repo and get an initial AGENTS.md signal"

Agent routes to: onboarding.
Agent reads: `references/onboarding.md`

Agent asks which work Stet should track. The user names API, auth,
validation, and CLI work, with a mix of product features and bug fixes. Agent
inspects CI (`.github/workflows/test.yml`), finds `npm test`, then uses
read-only PR/history sampling to confirm those areas show up in merged work.
Agent authors `.stet/harbor.Dockerfile` and `.stet/stet.harness.yaml` with
`environment.dockerfile: .stet/harbor.Dockerfile` and the Node/system
dependencies used by CI.

Agent defaults to recommended quality graders for the first AGENTS.md signal.

```bash
stet init --repo . --yes --ai-provider <codex|claude|gemini|cursor> --quality recommended --test "npm test"
stet suite discover --repo . --rev-range main~200..main --limit 200 --target-pass 25
stet suite build --repo . --manifest .stet/discover-manifest.yaml
# Agent runs the cheapest Docker-backed local replay/test check for one
# representative task. This validates setup; it is not a model smoke/probe/eval.
```

Agent reports:

```text
STET :: DATASET

answer      starter slice ready
confidence  medium
step        onboard -> rules
funnel      240 scanned -> 32 passed discover -> 15 build-ready
dropoff     208 rejected: no_test_changes 96, llm_gate_fail 64, oversize 22
build       15 materialized, 4 skipped (unsafe_external_symlink)
coverage    api, auth, validation, cli, docs/runtime
difficulty  easy 3, medium 8, hard 4
gap         db migrations (low representation; report as confidence limit)
setup       Docker-backed local test check passed on one representative task
why         Rules is next because AGENTS.md is shared behavior; probe/config-diff
            are optional prefilters only after setup.

recommend   launch the first manifest-backed AGENTS.md rules signal
command     create .stet/rules/agents-md/stet.change.yaml and
            .stet/rules/agents-md/stet.suite.yaml over the retained dataset,
            then run stet manifest resolve and stet eval rules plan
other       run an explicit prefilter only if requested; stop with dataset
            receipt only when spend is not approved
```

**User:** `R`

Agent writes:

```yaml
# .stet/rules/agents-md/stet.change.yaml
version: 1
schema: stet.change/v1
name: agents-md-onboarding
change:
  kind: rules
  rules:
    treatments:
      - kind: agents_md
```

```yaml
# .stet/rules/agents-md/stet.suite.yaml
version: 1
schema: stet.suite/v1
repo: .
eval:
  dataset: .stet/dataset
  baseline_model: model:sonnet 4.6
  candidate_model: model:sonnet 4.6
  grader_ai_model_id: claude-sonnet-4-6
```

```bash
stet manifest resolve --change-manifest .stet/rules/agents-md/stet.change.yaml
stet eval rules plan --change-manifest .stet/rules/agents-md/stet.change.yaml --suite-manifest .stet/rules/agents-md/stet.suite.yaml --json
stet eval rules --change-manifest .stet/rules/agents-md/stet.change.yaml --suite-manifest .stet/rules/agents-md/stet.suite.yaml
stet eval report --change-manifest .stet/rules/agents-md/stet.change.yaml --json
```

```text
STET :: RULES

answer      inspect
confidence  medium
step        rules -> inspect
compare     candidate AGENTS.md vs baseline
sample      15 tasks
delta       pass 78%  equiv 3.2/4  review 3.0/4
driver      AGENTS.md changed shared behavior across api/auth/validation/cli
evidence    .stet/eval-rules/<run>/eval_report.v1.json
why         The retained dataset produced a first instruction-surface signal;
            the db-migration coverage gap remains a confidence limit.

recommend   inspect weakest tasks, then revise or keep
command     stet eval status --change-manifest .stet/rules/agents-md/stet.change.yaml --json
other       run a checkpoint/holdout lane before promotion
```

Done in 3 turns. The onboard → rules pipeline produced the repo's first
manifest-backed AGENTS.md signal.

When the first real evidence is a small pairwise model compare instead of a
probe, keep the same baseline-first posture:

```text
STET :: COMPARE

answer      directional: opus 4.7 leads
confidence  low
step        compare -> baseline capture
baseline    opus 4.6
candidate   opus 4.7
sample      3 tasks (below promote-grade threshold)
driver      opus 4.7 wins every requested quality dimension, with validity ok;
            the sample is useful for future reference but not for promotion.

recommend   freeze opus 4.7 as the current Opus baseline
command     stet baseline freeze --from <winning-candidate-root> --name <baseline-id> --json
other       scale to the full task slice for promote-grade evidence; stop with only the directional result
```

---

## Trace 4: Active Status With Heartbeat And Lineage

**User:** "What is this eval doing right now?"

Agent routes to: compare-and-checkin (status).
Agent reads: `references/compare-and-checkin.md`

```bash
stet eval status --out .tmp/stet-run --json
```

Agent reads `activity_state`, `active_work`, `blocking_tasks`, `last_artifact`,
and `lifecycle` from status JSON. The terminal `STET_STATUS_SUMMARY ...` lines
are treated as operator-facing mirrors, not the primary contract.

Agent reports:

```text
STET :: STATUS

step        eval run
state       waiting_on_evaluator
health      active
progress    18/40 tasks
idle        4m
last_seen   validation/candidate/task-18
blocker     candidate/task-19 waiting on evaluator
lineage     smoke complete -> full active
evidence    .tmp/stet-run
why         Wait is next because the run still has fresh task heartbeat and a
            specific blocker, not a no-progress stall.

recommend   wait and check status again
command     stet eval status --out <root> --json
other       inspect blocking task evidence if progress stops; stop with this status read
```

Done in 1 turn. The agent reports liveness and lineage from status JSON rather
than inferring from directory shape or partial logs.

---

## Trace 5: Shared Skill Loop

**User:** "Is my updated planning skill better?"

Agent routes to: rules skill loop.
Agent reads: `references/rules-flow.md` and
`references/iterative-improvement.md`.

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

Agent reads the Trial Result first, then opens the linked
`evidence.skill_loop_path` for the loop ledger.

Agent reports:

```text
STET :: SKILL LOOP

answer      improving
confidence  medium
cycle       2
compare     candidate skill vs baseline skill
sample      12 tasks
best        3.1 / 4
latest      3.1 / 4
weakest     skill_specificity
driver      routing improved, but planning instructions still stay generic on
            setup-heavy tasks
evidence    .stet/skill-loops/planner/stet.change.yaml
loop        skill_loop.v1.json
why         Iterate is next because the weakest dimension points to one
            specific edit: make setup-heavy planning guidance concrete.

recommend   revise one weakest-dimension lever and rerun
command     <apply one proposed edit, then rerun the same iteration lane>
other       inspect task-level risks before editing; promote only after rules evidence is trusted
```

Done in 2 turns. The wrapper generated the change/search-space/suite bundle,
built the replay dataset, delegated into rules, and persisted `skill_loop.v1.json`
so the next iteration starts from the weakest dimension instead of thread memory.
