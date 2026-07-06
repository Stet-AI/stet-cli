# Rules Skill Loop

Use this when the question is about adding a shared skill, revising an existing
shared skill, or improving a repo-managed skill through replay-backed rules
evidence.

## Classify The Skill Question

Classify before choosing a command:

| Question | Baseline | Surface | Graders |
|---|---|---|---|
| Does adding this skill help? | no usable skill guidance | manifest-backed `stet eval rules`, or frozen-baseline compare | `equivalence`, `footprint_risk`, and custom behavior rubrics; use `quality_only` rubrics when repo tests are not signal |
| Is this skill revision better? | committed prior skill | `stet eval rules skill` | wrapper defaults, or explicit `--grader` overrides |
| Is the `SKILL.md` itself well written? | prior or candidate skill text | `skill_workbench` | `skill_workbench` dimensions |

For new-skill A/B tests, do not commit a vague v0 skill just to create an
anchor. Prefer a true skill-absent baseline. If `skill_diff` needs exactly one
baseline match, a committed placeholder is acceptable only when it has an
impossible trigger and no actionable guidance; report it as "effectively no
skill", not literal absence.

For manifest-backed `stet eval rules`, put custom graders in
`change.rules.grader_profile.graders`; legacy `change.rules.graders` still
works. `stet eval rules` does not accept `--grader` launch flags. For
`stet eval rules skill`, repeated `--grader` flags are wrapper inputs and
replace the default grader set.

Use `skill_workbench` when the decision is about skill text quality. For the
first "with skill vs without skill" sanity check, behavior graders should carry
the decision because they grade the agent's output on replay tasks.

Choose test posture before launch. Use `tests_gated` only when repo test
pass/fail is part of the skill decision. If the skill is intended to improve
agent process, routing, or transcript behavior and repo tests add no signal,
use `quality_only` in `change.rules.mode` and make custom behavior rubrics
`mode: quality_only`. Do not tell the operator tests will be skipped unless the
chosen flow actually avoids fresh Harbor validation; validation-backed runs may
still materialize task details even when tests are non-decisive.

## Shared Skill Wrapper

For repo-managed shared skill iteration, prefer the wrapper instead of
hand-writing the first change/search-space/suite bundle:

```bash
stet eval rules skill --plan \
  --skill .agents/skills/planner/SKILL.md \
  --repo . \
  --model claude-sonnet-4-20250514 \
  --goal "improve planning specificity without increasing scope risk" \
  --out .stet/skill-loops/planner \
  --tasks 12 \
  --grader-ai-model-id claude-sonnet-4-6 \
  --json

stet eval rules skill \
  --skill .agents/skills/planner/SKILL.md \
  --repo . \
  --model claude-sonnet-4-20250514 \
  --goal "improve planning specificity without increasing scope risk" \
  --out .stet/skill-loops/planner \
  --tasks 12 \
  --test "go test ./..." \
  --grader-ai-model-id claude-sonnet-4-6 \
  --json

stet eval status --change-manifest .stet/skill-loops/planner/stet.change.yaml --json
stet eval report --change-manifest .stet/skill-loops/planner/stet.change.yaml --json
```

Use `--plan` before launch when the operator needs a budget decision. It does
not write the wrapper bundle, build the replay dataset, or launch `eval rules`.
It runs a buildability preflight against the resolved rev-range and surfaces it
as `tasks.rev_range` in JSON. If 0 change requests match, widen with
`--rev-range` before charging the launch. If `stet eval rules plan` is blocked
by commercial entitlement, treat that as access/preflight limitation rather
than manifest invalidity.

For wrapper runs, put any `--ai-cmd` on the non-plan launch; the wrapper
forwards it to delegated `stet eval rules`.

Replay-task discovery defaults to `main~25..main` against `--repo`. On squash,
rebased, tag-based, or otherwise nonstandard histories, pass `--rev-range` to
widen or shift the slice. Also bump `--tasks` when the first N merged change
requests in the chosen range are not buildable; today `--tasks N` is both the
task target and the upper bound on how many merged change requests the dataset
build fetches.

For GitLab repos on ambiguous self-hosted remotes, pass
`--change-provider gitlab` and, when needed, `--change-remote <remote-or-url>`;
the wrapper stores those hints in the generated suite manifest.

The wrapper writes:

- `.stet/skill-loops/<name>/stet.change.yaml` with a single `skill_diff`
  treatment.
- `stet.search_space.yaml` with treatments as the only mutable lever.
- `stet.suite.yaml` and a replay dataset under `dataset/`.

`stet.change.yaml` records the `skill_workbench` grader pack as a bundle id.
Plan and runtime expand that bundle into the `skill_*` dimensions at launch
time; bundle id in the manifest and expanded dimensions in plan output are the
same coverage.

The `dataset/` directory may be empty when the dataset build yields zero
buildable replay tasks after preflight. Read `dataset/build-summary.json` before
retrying with larger `--tasks` and/or tighter `--rev-range`.

## Recovery And Restart

Re-running the wrapper against a populated `--out` directory:

- If `dataset/build-summary.json` is present, the wrapper reuses the dataset and
  proceeds directly to `stet eval rules`.
- If task directories exist but no `build-summary.json`, the wrapper exits with
  remediation pointing at `--restart` or a fresh `--out` directory.
- `--restart` discards `<out>/dataset` before rebuilding and forwards
  `--restart` to delegated `stet eval rules`, clearing prior rules evidence
  under the same `--out`. Treat this as a destructive reset of both replay
  dataset and compare evidence.
- If suite build fails with `build completed with N errors`, the wrapper stops
  at that step and never launches `eval rules` on a failed build.

In v1, `--task-source replay` is the only executable source. `scenarios` and
`hybrid` are accepted by the parser but rejected at launch. Relative `--out`
paths are repo-relative. The wrapper accepts an absolute `--skill` path under
the repo, while rules runtime sees the logical repo path such as
`.agents/skills/planner/SKILL.md`; this preserves repo-managed skill staging and
`.agents/skills` over `.claude/skills` precedence.

## Default Graders

Default wrapper graders are:

- `equivalence`
- `code_review`
- `footprint_risk`
- `skill_routing`
- `skill_actionability`
- `skill_specificity`
- `skill_command_exactness`
- `skill_tool_selection`
- `skill_regression_risk`

All wrapper default graders except `footprint_risk` are LLM-backed, including
`equivalence`, `code_review`, and the `skill_workbench` pack. Supply
`--grader-ai-model-id` so Stet uses provider-native structured output through
the matching local CLI. Use `--grader-ai-cmd` with `--grader-ai-model-id` only
when forcing the legacy shell-text evaluator path. `--no-quality` drops only
auto-bundled quality graders; it does not bypass the evaluator
preflight for wrapper defaults. To run without an evaluator, override the
bundle, for example `--grader footprint_risk`.

## Preflight

Before launching a skill compare:

- Verify whether the baseline ref contains the skill file. If not, this is a
  new-skill A/B, not a normal revision loop.
- Decide whether repo tests are decision signal. If not, avoid `tests_gated`
  custom rubrics and prefer `quality_only` or existing-details quality-only
  evidence before launching fresh Harbor work.
- Check `.agents/skills` and `.claude/skills` precedence. The wrapper refuses
  symlinks under either staged root. Resolve symlinks before launch, or move the
  affected skill out of the staged root.
- Inspect `--plan` output for arms, task count, grader IDs, evaluator model, and
  whether the wrapper will build a fresh replay dataset.
- If the repo already has a reusable dataset but lacks `.stet/stet.harness.yaml`,
  use a hand-authored manifest-backed `stet eval rules` flow against that
  dataset instead of forcing the wrapper.
- After a `START stet-eval-rules` line or CLI timeout, do not relaunch blindly.
  Use `stet eval status --change-manifest <stet.change.yaml> --json`.

## Loop Handoff

After the report materializes, read `decision_receipt` and import the Trial
Result into native loop state:

```bash
stet optimize checkin \
  --change-manifest <stet.change.yaml> \
  --from-report <eval_report.v1.json-or-output-root> \
  --summary "candidate result interpreted from decision_receipt" \
  --next "scan, select, expand, holdout, repair, reject, or stop" \
  --json
```

If the report exposes `evidence.skill_loop_path`, read the linked
`skill_loop.v1.json` as supporting skill-loop evidence for cycle, best/latest
scores, weakest dimension, diagnosis, recommendation, next change, and any
persisted `proposed_edit`. Do not treat it as the primary optimization control
plane when `loop_state.v1.json` and `stet optimize` receipts exist.

Re-running `stet eval report --change-manifest` over unchanged evidence is a
read path; it must not advance the loop cycle.
