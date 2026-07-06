# Quick Probe

Inherits [operator-contract](operator-contract.md) for receipt format and
next-step recommendations.

```
probe ──► report ──► safe?
                     ├─ yes ──► gate / baseline / stop
                     ├─ uncertain ──► inspect / rerun / stop
                     └─ no ──► inspect / revise / stop
```

Use this for the smallest repo-local answer.

Do not use quick probe as the main path for a first-run repo onboarding. When
the repo lacks a build-ready Stet dataset, load [onboarding](onboarding.md) and
make dataset quality the primary deliverable before attempting a file signal.
If the user says "set up Stet" and "get an initial AGENTS.md/CLAUDE.md signal"
in the same request, that is still onboarding first. A tiny 1-3 task discover
or `--skip-quality-lanes` run is only a smoke/no-spend preflight when the user
explicitly asks for that lower-confidence mode.

For first-run AGENTS.md/CLAUDE.md changes, do not translate "initial signal"
into `config-diff`. Build or expand the onboarding dataset first, then use the
manifest-backed rules flow when the operator may keep, recommend, baseline, or
claim the instruction change. Use `probe --file` only for a clearly throwaway
directional read after the dataset has at least 10 retained ready tasks.

## Repo candidate

```bash
stet probe --model "sonnet 4.6" --repo . --json
stet eval report --out <probe-root> --json
```

## Config or instruction file

```bash
stet probe --file AGENTS.md --dataset .stet/dataset --model "sonnet 4.6" --json
stet eval report --out <probe-root> --json
```

`stet probe --file ...` is the fastest directional read for an instruction or
skill file on a real repo. It is not the release-grade path for "is this
AGENTS.md / CLAUDE.md / shared skill safe to ship?", "is this helping?", or
"should this become the default?" Use the manifest-backed rules flow for those
questions. For AGENTS.md/CLAUDE.md onboarding, a `probe --file` run below 10
retained ready tasks is setup-incomplete, not interpretable evidence.

When the target lives under `.agents/skills/...` or `.claude/skills/...`,
`stet eval config-diff --file ...` evaluates the managed-skill runtime envelope,
not just an isolated prompt-template file.

## Explicit file diff

Use `config-diff` when the operator is thinking in terms of before/after files
or wants a cheap A/B prefilter. This is not the onboarding path for AGENTS.md or
CLAUDE.md. Do not use config-diff to skip failed first-run onboarding; if no
build-ready dataset exists, repair onboarding first. For AGENTS.md/CLAUDE.md,
config-diff also requires at least 10 selected retained ready tasks.

```bash
stet eval config-diff --repo . --file CLAUDE.md --dataset .stet/dataset --model "sonnet 4.6" --json
```

Add `--agent <provider>` with `--ai-cmd` only when you need to override the
runtime provider that Stet would infer from the model and repo config.
If configured quality graders require an evaluator model, pass
`--grader-ai-model-id <model>`; keep this evaluator independent from the model
under test.

Or with explicit files:

```bash
stet eval config-diff \
  --repo . \
  --before ./.tmp/stet-config-diff/claude.before.md \
  --after ./CLAUDE.md \
  --logical-path CLAUDE.md \
  --dataset .stet/dataset \
  --model "sonnet 4.6" \
  --json
```

Treat the config-diff root itself as the canonical operator surface. If both
arms finish but `experiment.json` is missing, Stet now either materializes the
compare on that same root or fails closed with an inspect receipt that includes
the exact `stet eval config-diff ... --out <same-root>` rerun command.

If `probe --file` or `config-diff` reports `zero_ready_recent_slice`,
`no_eval_ready_tasks`, zero PASS tasks, `instruction_dataset_too_small`, or an
AGENTS.md/CLAUDE.md "selected N task(s)" floor error, do not interpret that as
a verdict on the config change. Follow the emitted next command, widen or shift
`--rev-range`, add `--allow-no-test-changes` when repo-level tests exist but
commits rarely edit tests, or pass `--dataset <built-dataset>` from onboarding.

For pairwise compare semantics over arbitrary plain files without template
authoring:

```bash
stet eval compare \
  --dataset ./.tmp/my-dataset \
  --out ./.tmp/stet-compare \
  --baseline-model "sonnet 4.6" \
  --candidate-model "sonnet 4.6" \
  --baseline-file ./.tmp/agents.before.md \
  --candidate-file ./AGENTS.md \
  --logical-path AGENTS.md \
  --grader equivalence \
  --grader code_review \
  --grader footprint_risk \
  --json
```

**Use the manifest-backed rules flow** for AGENTS.md / CLAUDE.md A/B testing
when the result will guide a retained candidate, rollout, baseline refresh, or
claim that shared agent behavior improved. The rules flow (`stet eval rules`
with `stet.change.yaml` + `stet.suite.yaml`) provides provenance, release
lifecycle integration, and the custom grader surface. Use `config-diff` and
`--baseline-file`/`--candidate-file` only as prefilters for throwaway
iterations, and label their results as directional. See
[rules-flow](rules-flow.md) for the manifest-backed approach.

## Quick model calibration after setup

Use `eval smoke` when the user wants a tiny multi-model read after repo setup,
not a formal benchmark suite and not first-run onboarding for a new repo or
AGENTS.md/CLAUDE.md change.

```bash
stet eval smoke --repo . --models "opus 4.6,sonnet 4.6" --tasks 5 --json
```

Add `--agent <provider>` with `--ai-cmd` only when smoke must use a specific
harness provider instead of Stet's inferred runtime.

## Escalate Only When Needed

- Need a reusable frozen "before" object for later compare or rerun continuity:
  `stet baseline freeze --from <probe-root> --name <capability> --json`
- Need a read-only baseline snapshot check after freezing:
  `stet baseline status --baseline <snapshot> --json`
- Need trust state, rollout state, or a release path: run a gated flow.
- Need a broader benchmark: move to [full-evals](full-evals.md).
- Need to grade a skill, research note, or plan: first define a custom rubric
  with [rubric-authoring](rubric-authoring.md).

## Reporting Contract

When you report a quick-probe result:
- say whether this was a `probe`, `report`, or `status` read
- answer the user first with `safe`, `not safe`, or `inconclusive`
- include `confidence: high|medium|low`
- show baseline vs candidate, sample size, and explicit deltas
- name the dominant driver behind the call
- explain why the recommended next action is next and what it means
- end with keyed next actions so the user can reply with one keystroke
- use an instrument-style ASCII receipt when the probe already finished

Example:

```text
STET :: QUICK PROBE

answer      inconclusive
confidence  medium
step        probe -> inspect
compare     candidate vs baseline
sample      5 tasks
delta       pass -0pp  equiv -6pp  review +3pp
driver      review risk rose on 2/5 tasks
why         Inspect is next because the regression signal is real, but still
            too small to treat as either a release block or a false alarm.
recommend   inspect task-level evidence
command     <open task_detail.json, trajectory.json, or local inspect bundle>
other       rerun after revising the candidate; stop with current bounded verdict
```

Outcome recommendations:
- safe with benchmark intent: baseline, then gate only if shipping now
- safe: gate or inspect before rollout mutation
- inconclusive: inspect or rerun after a targeted change
- not safe: inspect, revise, then rerun

Flow-specific step:
- `baseline`
  command: `stet baseline freeze --from <probe-root> --name <capability> --json`
  use when the operator wants a trackable snapshot before gate or promotion

## Rules

- Read completed quick-probe roots with `stet eval report --out ... --json`.
- For machine reads, prefer persisted `eval_report.v1.json` when present. Read
  `decision_receipt` for the verdict and next action, then `trial_context` for
  task selection, Harness Surface, Search Space, baseline/candidate, freshness,
  and machine recommendation. Use outer `lifecycle`, `validity`,
  `evidence_quality`, and `arms` to interpret the verdict.
- For dataset-backed `config-diff` and plain-file `compare`, Stet uses all
  realized tasks by default; add `--task-id` / `--task-pr` only when you need a
  narrower slice. Do not narrow AGENTS.md/CLAUDE.md reads below 10 retained
  ready tasks.
- Do not tell the operator to repair `origin/HEAD` or default-branch metadata
  for repo-file flows unless the command actually failed. Stet now falls back to
  repo-local default-branch resolution when possible.
- If the next operator question is "freeze this as the baseline" or "rerun this
  same baseline later," prefer `stet baseline freeze` over telling them to
  preserve a raw probe root by path convention.
- Use `stet eval status` only when a run is active or the user explicitly wants
  status/health.
- Prefer repo-local `.tmp/stet-*` roots over system `/tmp` because they are
  easier to inspect later and avoid macOS symlink-ancestor surprises.
- If the user only asked for a quick safety read, do not dump extra commands
  without giving keyed next actions that make the next step obvious.
- Do not recommend `gate` by default on an inconclusive or unsafe quick probe.
