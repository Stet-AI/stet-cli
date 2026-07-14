<p align="center">
  <img src="docs/assets/stet-mark.svg" width="64" height="64" alt="Stet logo">
</p>

<p align="center"><strong>Change control for AI coding agents</strong></p>

# Improve the instructions, skills, and model settings your coding agents use

Stet turns accepted repository work into replayable tasks so you can measure
whether an `AGENTS.md` change, shared skill, model, or reasoning setting is
safe to keep rolling out. The coding agent proposes changes; Stet measures
matched work and returns a scoped decision.

[Get started](BETA_QUICKSTART.md) · [Quickstart source](docs/quickstart.mdx) ·
[Understand the workflow](docs/workflows.mdx)

## What do you want to improve?

### A/B test an instruction change

Compare current and proposed instructions on the same retained repository tasks
with the model fixed across both arms. Stet returns `promote`, `hold`, or
`inspect` for the selected corpus and recorded harness.

> Use the Stet skill to A/B test my proposed `AGENTS.md` change. Keep the model
> fixed, plan before launch, and return the canonical Trial Result with its
> recommendation, evidence limitations, and next action.

### Improve an instruction file iteratively

Let your coding agent change one allowed instruction lever at a time while Stet
persists loop state, measures each candidate, and protects holdout and
promotion boundaries.

> Use the Stet skill to improve `AGENTS.md` within a bounded search space and
> stop rule. Test one change at a time and ask before using holdout evidence or
> promoting a finalist.

### Test whether a skill helps

Compare behavior with a true skill-absent baseline or compare a committed skill
with a revision, using behavior-relevant graders and the same replayable work.

> Use the Stet skill to test whether this repo-managed skill helps. Plan before
> launch, use the right baseline, and report `promote`, `hold`, or `inspect`.

### Choose a model or reasoning effort

Compare models or reasoning settings on the same retained tasks. Read
correctness, quality, cost, uncertainty, validity, and residual risk
separately; unavailable dimensions stay visible.

> Use the Stet skill to compare these configurations on the same repository
> tasks. First ask whether I want a cheap diagnostic read or a gateable rollout
> decision. Keep diagnostic evidence labeled directional.

## How Stet works

![Stet turns merged repository work into replayable tasks, evaluates baseline and candidate behavior, and returns a scoped Trial Result.](docs/assets/stet-loop.svg)

Stet packages selected history as replayable tasks, declares the treatment,
runs baseline and candidate arms over the same task slice, evaluates tests and
declared graders, and writes a canonical Trial Result with one recommendation
and next action.

## Example Trial Result

Historical April 2026 model comparison across 28 paired Zod tasks, with Opus
4.6 and Opus 4.7 at identical high reasoning.

| Observed measure | Opus 4.6 | Opus 4.7 |
| --- | ---: | ---: |
| Test pass rate | 42.9% | 42.9% |
| Equivalence rate | 32.1% | 46.4% |
| Observed cost per task | $19.96 | $8.11 |
| Mean agent duration | 7m 58s | 3m 12s |

**Historical receipt: `PROMOTE` candidate Opus 4.7, high confidence.**

On this task corpus, the historical receipt recommended Opus 4.7 after it held
the observed test pass rate steady, improved observed equivalence, and used less
observed cost and time. These are selected observations; the receipt also used
declared grader evidence not reproduced here.

This result is scoped to the 28-task Zod corpus and recorded harness. It
predates Stet's current calibration and claim-readiness fields, so the displayed
metrics are observations, not generalized or uncertainty-calibrated improvement
claims.

## Install and get a first result

The CLI ships for macOS, Linux, and Windows. The documented end-to-end
Docker-backed evaluation workflow is currently for macOS and Linux.

macOS and Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.ps1 | iex
```

Sign in, then install the Stet agent skill:

```sh
stet auth login
stet auth status
npx skills add https://github.com/Stet-AI/stet-cli.git --skill stet --all
stet --version
npx skills list
```

The default evaluation path also needs Docker, Python 3.12+, `uv`, and model
provider authentication. See [BETA_QUICKSTART.md](BETA_QUICKSTART.md) for the
full setup path.

In the repository you want to evaluate, ask your coding agent:

```text
Use the Stet skill to onboard this repo for Stet evals.

Ask what work I want tracked. Read CI and build files, then choose the
narrowest credible bounded verifier and pass it explicitly with --test. Treat
`bazel test //...`, unfiltered `pytest`, `go test ./...`, and workspace-wide
scripts as broad. If only a broad verifier exists, stop before build and
propose bounded alternatives; do not broaden verification to increase yield.

Inspect representative merged work, create the Harbor setup, build the starter
slice, and run the smallest setup smoke available. Return a receipt with
verifier scope, skipped scope, coverage, confidence, and next action. Stop
before model smoke, probe, or rules evals.
```

## Why trust the result?

Stet keeps correctness, quality, cost, uncertainty, validity, and grader
coverage separate. Recommendations apply only to the declared change, selected
task corpus, and recorded harness. Missing, stale, partial, invalid, or
under-graded evidence cannot support promotion; Stet preserves the blocker and
next action instead of presenting it as rollout proof.

Evaluation artifacts normally remain in local Stet output roots. Configured
coding-agent and grader providers can receive task instructions, repository
context, patches, tests, and grading context. When signed in, the CLI also
sends best-effort command-category and status events associated with the
authenticated user; the CLI currently exposes no telemetry opt-out.

## Learn more

- [Beta quickstart](BETA_QUICKSTART.md) · [source](docs/quickstart.mdx)
- [Prompt cookbook](PROMPT_COOKBOOK.md) · [source](docs/prompts.mdx)
- [How Stet works](docs/concepts/how-stet-works.mdx)
- [Workflows](docs/workflows.mdx)
- [Troubleshooting](TROUBLESHOOTING.md)

The install script and agent skill are available under the [MIT License](LICENSE).
The distributed binary is governed by the [Stet Binary Terms](TERMS.md).
