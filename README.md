<p align="center">
  <img src="assets/stet-mark.svg" width="64" height="64" alt="Stet logo">
</p>

<p align="center"><strong>Change control for AI coding agents</strong></p>

# Improve the instructions, skills, and model settings your coding agents actually use

You change your coding agent's setup constantly — a new model, a rewritten
`AGENTS.md`, a new skill, a different reasoning setting. Stet tells you which
changes are safe to keep. It replays your repository's real accepted work under
the proposed change and returns a scoped decision. Your agent runs Stet on your
behalf; you set the question, approve the spend, and make the call.

**Full documentation lives at [docs.stet.sh](https://docs.stet.sh).**

[Get started](https://docs.stet.sh/quickstart) ·
[Run your first eval](https://docs.stet.sh/first-eval) ·
[See an example result](#example-trial-result) ·
[How Stet works](https://docs.stet.sh/concepts/how-stet-works)

## What do you want to improve?

- **Is my `AGENTS.md` change helping?** Compare current and proposed
  instructions on the same retained tasks —
  [instruction-file A/B](https://docs.stet.sh/guides/instruction-file-ab).
- **Improve my `AGENTS.md`.** Iterate one instruction lever at a time with a
  bounded stop rule —
  [iterative improvement](https://docs.stet.sh/guides/iterative-improvement).
- **Is this skill helping?** Test a skill against an appropriate absent or
  committed baseline —
  [skill evaluation](https://docs.stet.sh/guides/skill-evaluation).
- **Which model or reasoning effort should I use?** Compare configurations on
  the same repository task slice —
  [model comparison](https://docs.stet.sh/guides/model-comparison).

The prompts you say to your agent for each workflow are in the
[prompt cookbook](https://docs.stet.sh/prompts).

## How Stet works

![Stet turns merged repository work into replayable tasks, evaluates a baseline and candidate with tests and graders, and returns a promote, hold, or inspect Trial Result.](assets/stet-loop.svg)

Accepted repository work becomes replayable tasks. Stet runs a baseline and a
candidate against the same task slice, evaluates their patches with tests and
graders, and writes a Trial Result with one scoped recommendation. The evidence
is produced independently of the agent whose change is under test, and weak,
stale, or contaminated evidence blocks a strong claim.

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

On this corpus, Opus 4.7 held test pass rate steady, showed higher equivalence,
and used less cost and time. The receipt's declared grader evidence is part of
the example: mean scores on a 0-4 rubric from a declared gpt-5.4 grader across
all 28 tasks, on which Opus 4.7 showed higher means on seven of the eight craft
dimensions. The full example, including the grader table and machine-readable
receipt, is on the [docs overview](https://docs.stet.sh#example-trial-result).

Historical April 2026 result, scoped to this 28-task Zod corpus and recorded
harness. The legacy report predates Stet's current calibration and
claim-readiness fields.

## Install and get a first result

The CLI ships for macOS and Linux on x86_64 and arm64, and for Windows on amd64.
The documented end-to-end Docker-backed evaluation workflow is currently for
macOS and Linux.

macOS and Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/Stet-AI/stet-cli/main/install.ps1 | iex
```

Signing in creates your account and starts a trial (no payment details
collected); it is required only for commands that launch AI evaluation or
regrading, and model tokens are always billed to your own provider account,
never by Stet. Sign in, then install the Stet agent skill:

```sh
stet auth login
stet auth status
npx skills add https://github.com/Stet-AI/stet-cli.git --skill stet --all
stet --version
npx skills list
```

The default evaluation path also needs a running Docker daemon, Python 3.12+,
`uv`, and authentication for the model provider you plan to evaluate. The
[quickstart](https://docs.stet.sh/quickstart) covers platform setup and
verification, and [Your first eval](https://docs.stet.sh/first-eval) takes the
onboarded repository to a first bounded measurement.

Then, in the repository you want to evaluate, ask your coding agent:

```text
Use the Stet skill to onboard this repo. Ask me what work I want Stet to
track, build a starter slice from real merged work, and stop with an
onboarding receipt before any model evaluation.
```

Onboarding spends nothing on models. Evaluations spend model tokens through
the provider account your agent already uses — your existing usage limits, not
a separate bill — and a full eval can consume a substantial portion of a $100
or $200 monthly subscription tier's limits, so your agent states expected
spend and waits for approval before launch.

## Why trust the result?

Stet keeps correctness, quality, cost, uncertainty, validity, and grader
coverage separate. Recommendations apply only to the declared change, selected
task corpus, and recorded harness. Missing, stale, partial, invalid, or
under-graded evidence cannot support promotion; Stet preserves the actual
blocker status and exact next action instead of presenting it as rollout proof.

Stet is local-first: evaluations run on your machine, evaluation artifacts
remain in local Stet output roots, and the audited Stet control-plane client
path does not upload repository contents or evaluation artifacts — Stet stores
none of your code or evaluation data. The coding-agent and grader providers
you configure can receive task instructions, repository context, patches,
tests, and grading context — that traffic goes to your providers, under your
credentials, not to Stet. Separately, when you are signed in, the CLI sends
best-effort command-category and status events to the Stet control plane so we
can see where evaluations succeed or get stuck during the beta; a
first-evaluation success or failure can queue a support follow-up. Event
metadata may include the root command, selected model or models, mode,
output-directory basename, a generic failure classification, and entitlement
status or reason — never repository contents, prompts, or diffs. Events are
persisted server-side and tied to the authenticated account; signing out stops
them, and the CLI currently exposes no telemetry opt-out while signed in. Stet
does not claim a universal network sandbox.

## Learn more

- [Quickstart](https://docs.stet.sh/quickstart)
- [Your first eval](https://docs.stet.sh/first-eval)
- [Choose a workflow](https://docs.stet.sh/workflows)
- [Prompt cookbook](https://docs.stet.sh/prompts)
- [Read a Trial Result](https://docs.stet.sh/concepts/trial-result)
- [Troubleshooting](https://docs.stet.sh/troubleshooting)

Questions or issues of any kind: [ben@stet.sh](mailto:ben@stet.sh).

The install script and agent skill are available under the [MIT License](LICENSE).
The distributed Stet binary is governed by the [Stet Binary Terms](TERMS.md).
