# Troubleshooting

Start here when setup or a Stet run blocks. The goal is to identify whether the
problem is local setup, auth, Docker/Harbor, model-provider access, task replay,
or incomplete evidence.

## Fast setup checks

```sh
gh auth status
stet --version
stet auth status
docker info
command -v uv
npx skills list
```

If one of these fails, fix it before launching evals.

## `stet` not found

The default install directory is `$HOME/.local/bin`. Add it to `PATH`, then
verify:

```sh
export PATH="$HOME/.local/bin:$PATH"
stet --version
```

If the binary is old, update:

```sh
stet update
```

`stet update` refreshes the CLI. It does not mutate the separately installed
Stet agent skill. Refresh the skill through the skill manager:

```sh
npx skills update stet -y
```

For a prerelease or exact beta tag:

```sh
stet update --prerelease
stet update --version v0.1.0-rc.3
```

## GitHub auth or private repo access

The default installer and skill use the public `benredmond/stet-cli` repo. You
only need GitHub CLI auth for private release overrides or PR/MR-backed repo
discovery.

```sh
gh auth status || gh auth login
```

If a private override repo fails, confirm the account has access to that repo
before debugging Stet itself.

## Stet commercial auth missing

Commercial beta workflows require local Stet auth for eval execution, replay,
evaluator AI, grader repair, and monitor reruns.

```sh
stet auth login
stet auth status
```

Local setup, suite discover/build, status/report, rollback, and artifact
inspection can still be useful without commercial auth, but execution should
fail closed until access is verified.

## Docker unavailable

Start Docker Desktop on macOS or the Docker service on Linux, then run:

```sh
docker info
```

If Docker is running but Stet jobs fail with stale state or exhausted Docker
resources, first confirm no Stet/Harbor run is active. Then inspect stale state:

```sh
stet harbor cleanup
```

Apply cleanup only when it is safe to remove stale Stet-owned Docker resources:

```sh
stet harbor cleanup --apply
```

Use BuildKit pruning only when you intentionally want broader Docker cache
cleanup:

```sh
stet harbor cleanup --apply --prune-buildkit
```

## `uv` not found

Stet owns Harbor invocation through `uv tool run`. Install `uv`:

```sh
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `uv` is still not found, add the `uv` bin directory to `PATH`, usually
`$HOME/.local/bin`.

## Claude Code auth failure

Claude Code models need host auth before Stet can run them inside Harbor.

```sh
claude setup-token
mkdir -p ~/.config/stet
chmod 700 ~/.config/stet
printf '%s\n' '<printed token>' > ~/.config/stet/claude-oauth-token
chmod 600 ~/.config/stet/claude-oauth-token
unset CLAUDE_CODE_OAUTH_TOKEN
```

Stet reads `~/.config/stet/claude-oauth-token` and forwards
`CLAUDE_CODE_OAUTH_TOKEN` only to Stet-managed Claude runs. Do not commit the
token, put it in repo `.env` files, or export it broadly from shell profiles.

If Claude still asks for `/login` inside a Stet run, refresh the binary:

```sh
stet update
```

If Stet warns that the agent skill is missing or cannot be inspected, refresh
or install it separately:

```sh
npx skills update stet -y
npx skills add https://github.com/benredmond/stet-cli.git --skill stet --all
```

## Rules plan seems slow

`stet eval rules plan` is the preflight before a charged rules launch, but it is
not a sub-second syntax check. It may run Harbor gold-replay validation and
LLM-grader preflight. On real repos, 8 to 10 minutes can be normal.

For a quick manifest-shape check, use:

```sh
stet manifest resolve --change-manifest .stet/rules/stet.change.yaml
stet manifest resolve --suite-manifest .stet/rules/stet.suite.yaml
```

Use the full rules plan when you need tasks, arms, graders, replay validity,
cost risk, and launch readiness.

## Docker OOM or capacity problems

If containers are killed with `ENOMEM`, exit 137, or setup-only failures, reduce
concurrency before treating the result as model quality. For Claude Code
compare/rules runs, start with lower Harbor concurrency:

```sh
stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml --harbor-concurrency 2
```

For suite-backed rules runs, prefer persistent Harbor resource settings in
`.stet/stet.harness.yaml`:

```yaml
version: 1
schema: stet.harness/v1
runner:
  harbor_cmd:
    - harbor
  harbor_args:
    - --override-memory-mb
    - "8192"
environment:
  dockerfile: .stet/harbor.Dockerfile
```

## Run stalled or incomplete

Do not rerun or restart a rules flow blindly. Check status first:

```sh
stet eval status --change-manifest .stet/rules/stet.change.yaml --json
```

If the active process has exited or status is stalled and the run has persisted
rules evidence, use repair:

```sh
stet eval rules repair --change-manifest .stet/rules/stet.change.yaml --json
```

Use `--restart` only when you intentionally want to discard existing evidence:

```sh
stet eval rules --change-manifest .stet/rules/stet.change.yaml --suite-manifest .stet/rules/stet.suite.yaml --restart
```

## Replay-invalid or no gold-pass commands

Errors such as `no_gold_pass_commands`,
`all_commands_ignored_gold_failure_mode_unset`, or replay-validity failures mean
the selected slice is not decision-grade evidence yet. Do not treat this as a
model-quality verdict.

Ask your agent to inspect the failed task artifacts, validation output, verifier
commands, and task IDs. The next action is usually one of:

- fix the Harbor/test setup
- choose a different task slice
- rebuild the dataset with better task selection
- stop with an inspect-only diagnosis

Relaunch only after the evidence input changes or the agent can explain why the
same input is now plausibly gold-valid.

## Missing grader coverage

If a completed run is missing additive grader coverage, use the repair or
regrade command emitted by `stet eval status` or `stet eval report`. Common
forms are:

```sh
stet runs repair-ai-coverage --out <run-root> --model-key <model-key>
stet runs regrade-graders --out <run-root> --model-key <model-key> --grader craft --grader discipline
```

If saved grader prompts failed JSON parsing, add parse retries when the emitted
command supports it:

```sh
--parse-retries 3
```

## `inspect` result

`inspect` is not necessarily a failure. It means the evidence is useful for
diagnosis or iteration, but not strong enough for a rollout decision.

Ask your agent:

```text
Use the Stet skill. This Stet run returned inspect. Explain whether inspect came from small sample size, stale evidence, missing graders, replay validity, infrastructure failure, mixed results, or another concrete reason. Recommend one bounded next action.
```

Do not promote from inspect-only evidence unless you are intentionally overriding
the gate and understand the risk.

## When to contact Ben

Contact Ben when:

- Ben gave you a private release repo and your GitHub account cannot access it
- `stet auth status` says your account lacks commercial access
- a fresh install repeatedly cannot fetch the pinned Harbor packages through `uv`
- a normal repo with working CI cannot produce a viable starter slice
- a reproducible Harbor setup failure blocks the first evaluation
