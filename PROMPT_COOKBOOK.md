# Prompt cookbook

Use these prompts with your coding agent. They are written to keep Stet
agent-driven: you state the outcome, and the agent chooses the right Stet
surface, reads the canonical artifacts, and reports the decision.

## Setup

```text
Use the Stet skill. Install and verify Stet for this machine using the beta
docs. Verify GitHub access, CLI/auth, Docker or Harbor, model-provider auth,
and the skill. Stop after setup verification; do not run evaluations yet.
```

```text
Use the Stet skill. Check whether this repo is ready for Stet. Inspect CI,
build files, test commands, Docker assumptions, and provider auth. Report
blockers before editing files or launching evals.
```

```text
Use the Stet skill. Docker is intentionally unavailable. Use the opt-in Harbor
worktree backend only if this surface supports it. Keep the task source tied to
a local commit, read status/report as authority, and inspect integrity artifacts
only for diagnosis.
```

## Repo onboarding

```text
Use the Stet skill to onboard this repo for Stet evals. Ask what product areas,
PR types, and difficulty mix I want Stet to track. Read CI, documentation,
package/build files, and build graphs. Choose the narrowest credible verifier
that is affordable to run repeatedly and pass it explicitly with `--test`.
Treat `bazel test //...`, unfiltered `pytest`, `go test ./...`, and
workspace-wide test scripts as broad. If no credible bounded verifier exists,
stop before `stet suite build`; report the broad command you withheld and
propose two or three bounded alternatives for my approval.

Use read-only subagents when available to sample merged PRs/commits and map
where representative work happens. Create the Harbor Dockerfile and harness,
then run a manifest-backed build with conservative concurrency. Keep the
verifier boundary fixed if yield is low. Wait for `build-summary.json`, report
the onboarding receipt, and stop before model smoke, probe, or rules evals.
```

```text
Use the Stet skill to expand this bounded onboarding slice without changing its
evidence bar. Read the receipt and skipped-task reasons. Add the smallest
bounded set of representative tasks that improves missing subsystem or
difficulty coverage. Keep the approved verifier explicit with `--test`. If
yield is low, widen or shift candidate history or propose another bounded
subsystem cohort. Do not switch to a repository-wide verifier without my
explicit approval. Report what was added, what remains skipped, verifier
scope, subsystem coverage, and updated confidence. Do not launch a model eval.
```

```text
Use the Stet skill. Read the onboarding receipt. Summarize the candidate funnel,
selected slice, representativeness, path coverage, difficulty mix, skipped-task
reasons, setup validation, confidence, and next step. Do not launch more work.
```

```text
Use the Stet skill. Confidence is low. Diagnose whether the blocker is test
setup, Docker/Harbor setup, weak task history, path-sensitive tests, verifier
scope, or task selection. Propose the smallest fix before running more Stet
work. Do not increase yield by switching to an unapproved repository-wide
verifier.
```

## First evaluation

```text
Use the Stet skill. Run a small first Stet smoke on this repo using the starter
dataset. Keep it cheap, explain the evidence it produces, and do not make
rollout claims from it.
```

```text
Use the Stet skill. Probe this change with Stet on the starter dataset. Report
whether the result is usable for iteration; do not call it rollout evidence.
```

```text
Use the Stet skill. Read the current Stet result from status/report surfaces.
Tell me the recommendation, confidence, evidence quality, grader coverage, task
coverage, next action, and residual risk. Do not reconstruct the verdict from
pass rate alone.
```

## AGENTS.md or CLAUDE.md changes

```text
Use the Stet skill. Evaluate whether this `AGENTS.md` change helps. Use the
manifest-backed rules flow. Run the plan first, explain task count, graders,
cost risk, and evidence quality, then ask before launching.
```

```text
Use the Stet skill. Evaluate whether this `CLAUDE.md` change is safe to ship.
Keep the model fixed across baseline and candidate. Run the rules plan first
and tell me whether the evidence will be decision-grade.
```

```text
Use the Stet skill. Improve this instruction file one lever at a time. After
each run, read the Trial Result, explain the bottleneck, make one scoped edit,
and stop when evidence is inspect-only or not improving.
```

## Model comparisons

```text
Use the Stet skill. Compare these two models on my repo. Use frozen baseline
evidence if available; otherwise start with the smallest useful smoke or probe.
Report correctness, quality dimensions, cost, and residual risk.
```

```text
Use the Stet skill. Compare these two reasoning levels on the same model. Keep
every other harness setting fixed, expose both effective settings, and report
whether the evidence is decision-grade or directional.
```

```text
Use the Stet skill. Tell me which model should be my default for this repo. Use
Stet history if available, separate model variance from workflow/setup risk,
and do not recommend a default from stale or partial evidence.
```

## Skill evaluation

```text
Use the Stet skill. Test whether this skill improves agent behavior. Compare a
skill-absent baseline with the skill present, use behavior-relevant graders,
and report whether evidence supports keeping it.
```

```text
Use the Stet skill. Improve this shared skill with Stet. Keep the search space
to skill text, run the plan before launch, and after each result choose exactly
one next change or stop.
```

```text
Use the Stet skill. Before I publish this skill revision, verify whether the
latest evidence supports promote, hold, or inspect. Include task coverage,
grader coverage, freshness, and the exact next action.
```

## Status and recovery

```text
Use the Stet skill. Check the current Stet run using status/report surfaces.
Tell me whether it is running, stalled, exited, repairable, or complete, and
give the exact next command.
```

```text
Use the Stet skill. This rules run looks incomplete. Check status first, identify
whether the launcher is active, and use repair only if it exited or stalled.
Do not restart unless I approve discarding evidence.
```

```text
Use the Stet skill. This run returned inspect. Explain whether it came from a
small sample, stale evidence, missing graders, replay validity, infrastructure,
mixed results, or another concrete reason. Recommend one bounded next action.
```

## Promotion safety

```text
Use the Stet skill. Before recommending promotion, verify decision-grade
evidence: freshness, expected graders, task coverage, replay validity, a compare
decision, and no inspect-only lifecycle state.
```

```text
Use the Stet skill. Summarize this result for a PR or Slack thread. Lead with
promote, hold, or inspect; include why, evidence run, remaining risk, and next
action. Keep it readable for an engineering lead new to Stet.
```

## Custom quality criteria

```text
Use the Stet skill. Help me write a custom grader for this repo. Ask what
behavior I care about, draft a small rubric, calibrate it against existing
patches if possible, and wait for report coverage before rollout use.
```

```text
Use the Stet skill. Evaluate this research or plan artifact with Stet. Choose
or write a custom rubric first, explain what it measures, and report artifact
quality rather than code correctness.
```

## Good default instruction to your agent

```text
Use the Stet skill. Keep the workflow bounded. During unfamiliar-repo
onboarding, never launch a repository-wide verifier without explicit approval.
Read status/report artifacts as the source of truth, change one lever at a
time, treat inspect as a diagnostic state, and ask before launching expensive
evals or discarding existing evidence.
```
