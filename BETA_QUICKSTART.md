# Beta quickstart

This guide is the first-session path for a beta customer. The goal is not to
learn every Stet command. The goal is to prove that the machine is ready, one
repo can be onboarded, and the first Stet evidence can be read without guessing.

## What you will accomplish

By the end of this session, your agent should have:

1. Verified the Stet CLI, Stet auth, Docker/Harbor or an explicitly selected
   worktree backend, GitHub auth, and the Stet skill.
2. Read your repo's CI and selected the real repo-level test command.
3. Created or reviewed the repo's Stet harness files.
4. Built a representative starter dataset from real merged work.
5. Verified enough Docker/test setup to trust the starter slice.
6. Returned an onboarding receipt and a concrete next-step recommendation.

The first session should stop before an expensive eval unless you explicitly
approve the launch.

## Before you start

Use a repo with:

- real Git history
- merged PRs or commits representative of the work you care about
- CI or documented test commands
- a test suite that can run in Docker, or an explicit plan to use the opt-in
  worktree backend for supported local checks

Then start Docker unless you are intentionally using the worktree backend. If
your first run will discover tasks from GitHub PRs, confirm GitHub CLI auth as
well:

```sh
docker info
gh auth status
```

If you have not installed Stet yet, start with [README.md](README.md).

## Step 1: ask your agent to check setup

In your coding agent, from the repo you want to evaluate, ask:

```text
Use the Stet skill. Check whether this machine is ready to run Stet. Verify Stet, Stet auth, Docker/Harbor or the explicitly selected worktree backend, GitHub auth, model-provider auth, and the Stet skill. Do not run an eval yet.
```

Expected checks:

```sh
stet --version
stet auth status
gh auth status
docker info
command -v uv
npx skills list
```

If any check fails, fix setup before onboarding the repo. Stet should fail
closed on missing commercial auth, missing model-provider auth, unavailable
Docker on the default path, or an unverified worktree backend rather than
launching ambiguous work.

## Step 2: ask your agent to onboard the repo

Use this prompt:

```text
Use the Stet skill. Onboard this repo for Stet evals.

Your first and main priority is to build a high-quality representative starter dataset from real merged work. First ask what product areas, PR types, and difficulty mix I want Stet to track. If I do not answer, infer a reasonable first-pass slice from repo history and say what you assumed.

Use subagents when available to make this efficient: delegate independent read-only checks for CI/test setup, merged PR/commit sampling, important subsystems, and starter-slice representativeness. Integrate their findings yourself. If subagents are unavailable, do the same bounded sampling yourself and say so.

Read CI and package/build files, choose the real repo-level test command, then sample merged PRs/commits to understand where meaningful work happens in this repo. Prefer a starter dataset that covers several important subsystems and a mix of features, fixes, refactors, infra/setup work, and tests, rather than many similar tasks from one package.

Create or update the Stet harness files, run init/discover/build as needed, and verify that the retained starter slice is executable enough to trust as onboarding evidence. Return an onboarding receipt that explains the task funnel, selected slice, representativeness, coverage, setup validation, confidence, and the next recommended action.

Stop before launching model smoke, probe, or rules evals.
```

Your agent should inspect CI first. CI is more trustworthy than README prose for
test setup. The selected test command should run the actual repo test suite, not
only lint, build, `echo`, or `true`.

The starter dataset is the main artifact from day-one onboarding. It should be
large and varied enough to support an initial shared-behavior decision later,
not merely prove that one task can run. Dataset selection is the most important
onboarding choice: the agent should not take the newest PRs by default. It
should interview you long enough to learn which work you want Stet to measure,
then inspect merged PRs or commits for real clusters of work: product features,
bug fixes, refactors, migrations, infra changes, test-heavy changes, and any
repo-specific workflows that matter. The starter slice should cover the
important paths and include a reasonable mix of easy, medium, and hard tasks.
If the agent cannot build a representative slice, it should report dataset or
setup remediation as the next step rather than switching to a cheaper signal.

The Harbor Dockerfile should encode the dependencies the real tests need:
language runtimes, package managers, system packages, service clients, build
tools, and any repo-specific setup visible in CI. Before treating the dataset
as ready, the agent should run the cheapest local replay or test smoke that
proves at least one representative task can execute inside Docker. That check
is setup validation, not a model eval.

If Docker is unavailable by design, the agent can use the opt-in worktree
backend for a supported local check. It should say so explicitly, keep Docker
as the default recommendation, and read the resulting evidence from
`stet eval status` / `stet eval report` before inspecting worktree-specific
integrity artifacts.

The agent should create or update:

- `.stet/stet.yaml`
- `.stet/harbor.Dockerfile`
- `.stet/stet.harness.yaml`
- a dataset root under `.stet/` or another agreed output path
- `onboarding_receipt.v1.json` in the dataset root

## Step 3: review the onboarding receipt

Ask:

```text
Use the Stet skill. Read the Stet onboarding receipt. Summarize the candidate-task funnel, selected starter slice, representativeness rationale, subsystem/path coverage, difficulty mix, skipped-task reasons, Docker/test setup validation, confidence, and recommended next step. Do not launch more work yet.
```

The receipt should answer:

- how many candidate tasks were scanned
- how many passed discover and build
- which tasks are in the starter slice
- why the slice represents the work you want to track
- what subsystem/path coverage and difficulty mix it has
- why tasks were rejected or skipped
- what test command and setup source were used
- what Docker/test smoke was run, or why it could not run
- whether the starter slice is high, medium, or low confidence

If the confidence is low, improve repo setup, Docker dependencies, test signal,
or task selection before running a larger eval.

## Step 4: choose the first run

Use one of these paths.

For a cheap calibration read:

```text
Use the Stet skill. Run a small first Stet smoke on this repo using the starter dataset. Keep it cheap, explain what evidence it produces, and do not make rollout claims from it.
```

For a directional read on a specific change:

```text
Use the Stet skill. Probe this change with Stet on the starter dataset. Report whether the result is usable for iteration, and do not describe it as rollout evidence.
```

For an `AGENTS.md`, `CLAUDE.md`, shared-skill, model, or harness-policy decision:

```text
Use the Stet skill. Evaluate whether this shared behavior change is ready for a Stet rules decision.

First read the onboarding receipt and confirm that the starter dataset is representative enough for this kind of change. Use subagents when available to inspect dataset coverage, task diversity, replay readiness, and plan blockers in parallel. Integrate their findings yourself.

If the dataset is missing, too small, too narrow, replay-invalid, or low-confidence, treat that as onboarding work: expand or repair the dataset and report what changed before evaluating the behavior change.

Once the dataset is credible, use the manifest-backed Stet rules flow. Run the plan first, explain task count, task coverage, graders, cost risk, evidence quality, and any blockers, then ask before launching the full run.
```

The rules path is the right path when you intend to keep, recommend, baseline,
promote, or roll back a shared behavior change. For shared behavior changes,
the agent should not substitute a cheaper first signal for a missing or weak
dataset. A blocked plan usually means "continue onboarding the dataset," not
"downgrade the evidence target."

## Step 5: read the result

Ask your agent:

```text
Use the Stet skill. Read the current Stet result from status/report surfaces. Tell me the recommendation, confidence, evidence quality, grader coverage, task coverage, next action, and residual risk. Do not reconstruct the verdict from pass rate alone.
```

The important lifecycle words are:

- `promote`: the evidence supports keeping the candidate as the current release
  state.
- `hold`: the evidence does not support promotion.
- `inspect`: the evidence is useful for diagnosis or iteration, but not strong
  enough for a rollout decision.

`inspect` is common on small or degraded samples. It is not the same as failure.
It means the evidence should guide the next bounded action rather than justify a
ship/no-ship claim.

## What not to do on day one

- Do not start with a 50+ task dataset unless you are deliberately doing heavy
  dataset onboarding.
- Do not compare many models at once.
- Do not treat a quick smoke or probe as a rollout decision.
- Do not promote from stale, partial, missing-grader, or replay-invalid evidence.
- Do not delete or restart a partial rules run before checking
  `stet eval status`.

## Next docs

- Use [PROMPT_COOKBOOK.md](PROMPT_COOKBOOK.md) for copy-paste prompts.
- Use [ONBOARDING.md](ONBOARDING.md) to understand how replay and grading work.
- Use [TROUBLESHOOTING.md](TROUBLESHOOTING.md) when setup or a run blocks.
