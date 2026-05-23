import asyncio
import importlib
import json
import os
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass
from pathlib import Path


def install_fake_harbor_modules(with_exec_input=True):
    harbor = types.ModuleType("harbor")
    agents = types.ModuleType("harbor.agents")
    installed = types.ModuleType("harbor.agents.installed")
    base = types.ModuleType("harbor.agents.installed.base")
    codex = types.ModuleType("harbor.agents.installed.codex")
    environments = types.ModuleType("harbor.environments")
    environments_base = types.ModuleType("harbor.environments.base")
    models = types.ModuleType("harbor.models")
    models_agent = types.ModuleType("harbor.models.agent")
    models_agent_context = types.ModuleType("harbor.models.agent.context")
    models_trial = types.ModuleType("harbor.models.trial")
    models_trial_paths = types.ModuleType("harbor.models.trial.paths")

    @dataclass
    class ExecInput:
        command: str
        cwd: str | None = None
        env: dict | None = None
        timeout_sec: int | None = None

    class BaseEnvironment:
        def __init__(self):
            self.commands = []
            self.execs = []

        async def exec(self, command: str, **kwargs):
            self.commands.append(command)
            self.execs.append({"command": command, **kwargs})

            class Result:
                return_code = 0
                stdout = ""
                stderr = ""

            return Result()

    class AgentContext:
        pass

    class EnvironmentPaths:
        agent_dir = Path("/logs/agent")

    if with_exec_input:
        class Codex:
            _OUTPUT_FILENAME = "agent.log"

            def __init__(self, model_name=None, *args, **kwargs):
                self.model_name = model_name
                self._extra_env = kwargs.get("extra_env", {})
                self._reasoning_effort = kwargs.get("reasoning_effort")
                self._should_fail_setup = False
                self._should_fail_run = False
                self.last_instruction = None

            def _build_register_mcp_servers_command(self):
                return ""

            async def setup(self, environment):
                if self._should_fail_setup:
                    raise RuntimeError(self._should_fail_setup)
                return None

            async def run(self, instruction: str, environment, context):
                if self._should_fail_run:
                    raise RuntimeError("boom")
                self.last_instruction = instruction
                return None

        base.ExecInput = ExecInput
    else:
        class Codex:
            _OUTPUT_FILENAME = "agent.log"

            def __init__(self, model_name=None, *args, **kwargs):
                self.model_name = model_name
                self._extra_env = kwargs.get("extra_env", {})
                self._flag_kwargs = {
                    "reasoning_effort": kwargs.get("reasoning_effort")
                }
                self._should_fail_setup = False
                self._should_fail_run = False
                self.populated_context = False

            def _build_register_mcp_servers_command(self):
                return ""

            def build_cli_flags(self):
                reasoning_effort = self._flag_kwargs.get("reasoning_effort")
                if not reasoning_effort:
                    return ""
                return f"-c model_reasoning_effort={reasoning_effort}"

            def render_instruction(self, instruction: str):
                return instruction

            async def exec_as_agent(
                self,
                environment,
                command: str,
                env=None,
                cwd=None,
                timeout_sec=None,
            ):
                return await environment.exec(
                    command=command,
                    env=env,
                    cwd=cwd,
                    timeout_sec=timeout_sec,
                )

            async def setup(self, environment):
                if self._should_fail_setup:
                    raise RuntimeError(self._should_fail_setup)
                return None

            async def run(self, instruction: str, environment, context):
                raise AssertionError("Stet compatibility run should handle Harbor 0.3")

            def populate_context_post_run(self, context):
                self.populated_context = True

    codex.Codex = Codex
    environments_base.BaseEnvironment = BaseEnvironment
    models_agent_context.AgentContext = AgentContext
    models_trial_paths.EnvironmentPaths = EnvironmentPaths

    sys.modules["harbor"] = harbor
    sys.modules["harbor.agents"] = agents
    sys.modules["harbor.agents.installed"] = installed
    sys.modules["harbor.agents.installed.base"] = base
    sys.modules["harbor.agents.installed.codex"] = codex
    sys.modules["harbor.environments"] = environments
    sys.modules["harbor.environments.base"] = environments_base
    sys.modules["harbor.models"] = models
    sys.modules["harbor.models.agent"] = models_agent
    sys.modules["harbor.models.agent.context"] = models_agent_context
    sys.modules["harbor.models.trial"] = models_trial
    sys.modules["harbor.models.trial.paths"] = models_trial_paths


class CodexAuthAgentTests(unittest.TestCase):
    def setUp(self):
        install_fake_harbor_modules()
        sys.modules.pop("stet_harbor_agents.compat", None)
        sys.modules.pop("stet_harbor_agents.patch_capture", None)
        sys.modules.pop("stet_harbor_agents.codex_auth", None)
        self.module = importlib.import_module("stet_harbor_agents.codex_auth")
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.module.EnvironmentPaths.agent_dir = Path(self.tmpdir.name) / "agent"
        self.auth_file = Path(self.tmpdir.name) / "auth.json"
        self.auth_file.write_text('{"OPENAI_API_KEY":"test-key"}', encoding="utf-8")

    def tearDown(self):
        for key in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "CODEX_AUTH_FILE",
            "CODEX_LB_API_KEY",
            "CODEX_LB_BASE_URL",
            "STET_SKILL_ACTIVATION_TARGETS_JSON",
        ):
            os.environ.pop(key, None)

    def test_create_run_agent_commands_includes_bootstrap_verification_and_markers(self):
        os.environ["OPENAI_BASE_URL"] = "https://example.invalid/v1"
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(self.auth_file),
            reasoning_effort="high",
        )

        commands = agent.create_run_agent_commands("PR #1076: fix the task")

        self.assertEqual(len(commands), 2)
        run_command = commands[1]
        self.assertIn("bootstrap_check=$(mktemp", run_command.command)
        self.assertIn("emit_bootstrap_marker()", run_command.command)
        self.assertIn("codex --version", run_command.command)
        self.assertIn("codex_optional_dependency_missing", run_command.command)
        self.assertIn("mkdir -p \"$(dirname \"$agent_log\")\"", run_command.command)
        self.assertIn("tee -a \"$agent_log\"", run_command.command)
        self.assertIn("--model gpt-5.4", run_command.command)
        self.assertIn("-c model_reasoning_effort=high", run_command.command)
        self.assertIn("STET_TARGET_PR_NUMBER", run_command.command)
        self.assertEqual(run_command.timeout_sec, 1800)
        self.assertEqual(run_command.env["OPENAI_BASE_URL"], "https://example.invalid/v1")
        self.assertEqual(run_command.env["STET_HUMAN_PATCH_GUARD"], "1")
        self.assertEqual(run_command.env["STET_TARGET_PR_NUMBER"], "1076")
        self.assertIn("CODEX_HOME", run_command.env)
        self.assertNotIn("model_provider=\"codex-lb\"", run_command.command)

    def test_create_run_agent_commands_routes_through_codex_lb_when_key_is_set(self):
        os.environ["CODEX_LB_API_KEY"] = "fake-codex-lb-key"
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.3-codex",
            auth_path=str(self.auth_file),
            reasoning_effort="high",
        )

        commands = agent.create_run_agent_commands("fix the task")

        run_command = commands[1]
        self.assertEqual(
            run_command.env["CODEX_LB_API_KEY"],
            "fake-codex-lb-key",
        )
        self.assertEqual(
            run_command.env["CODEX_LB_BASE_URL"],
            "http://host.docker.internal:2455/backend-api/codex",
        )
        self.assertIn("-c 'model_provider=\"codex-lb\"'", run_command.command)
        self.assertIn(
            "-c 'model_providers.codex-lb.wire_api=\"responses\"'",
            run_command.command,
        )
        self.assertIn(
            "-c 'model_providers.codex-lb.env_key=\"CODEX_LB_API_KEY\"'",
            run_command.command,
        )
        self.assertIn(
            '-c "model_providers.codex-lb.base_url=\\"$CODEX_LB_BASE_URL\\""',
            run_command.command,
        )
        self.assertNotIn("fake-codex-lb-key", run_command.command)

    def test_setup_failure_writes_classified_bootstrap_marker(self):
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(self.auth_file),
        )
        agent._should_fail_setup = (
            "Missing optional dependency @openai/codex-linux-arm64"
        )
        environment = sys.modules["harbor.environments.base"].BaseEnvironment()

        with self.assertRaises(RuntimeError):
            asyncio.run(agent.setup(environment))

        marker_path = self.module.EnvironmentPaths.agent_dir / agent._OUTPUT_FILENAME
        self.assertTrue(marker_path.exists())
        lines = marker_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 1)
        marker = json.loads(lines[-1])
        self.assertEqual(marker["type"], "stet.bootstrap")
        self.assertEqual(marker["status"], "failed")
        self.assertEqual(
            marker["failure_class"], "codex_optional_dependency_missing"
        )

    def test_setup_failure_classifies_x64_optional_dependency_marker(self):
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(self.auth_file),
        )
        agent._should_fail_setup = (
            "Missing optional dependency @openai/codex-linux-x64"
        )
        environment = sys.modules["harbor.environments.base"].BaseEnvironment()

        with self.assertRaises(RuntimeError):
            asyncio.run(agent.setup(environment))

        marker_path = self.module.EnvironmentPaths.agent_dir / agent._OUTPUT_FILENAME
        marker = json.loads(
            marker_path.read_text(encoding="utf-8").strip().splitlines()[-1]
        )
        self.assertEqual(marker["type"], "stet.bootstrap")
        self.assertEqual(marker["status"], "failed")
        self.assertEqual(
            marker["failure_class"], "codex_optional_dependency_missing"
        )

    def test_imports_when_harbor_base_does_not_export_execinput(self):
        install_fake_harbor_modules(with_exec_input=False)
        sys.modules.pop("stet_harbor_agents.compat", None)
        sys.modules.pop("stet_harbor_agents.patch_capture", None)
        sys.modules.pop("stet_harbor_agents.codex_auth", None)

        module = importlib.import_module("stet_harbor_agents.codex_auth")

        self.assertFalse(module.ExecInput.__module__.startswith("harbor."))

    def test_harbor_without_execinput_run_uses_auth_file_commands(self):
        install_fake_harbor_modules(with_exec_input=False)
        sys.modules.pop("stet_harbor_agents.compat", None)
        sys.modules.pop("stet_harbor_agents.patch_capture", None)
        sys.modules.pop("stet_harbor_agents.codex_auth", None)
        module = importlib.import_module("stet_harbor_agents.codex_auth")
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        module.EnvironmentPaths.agent_dir = Path(tmpdir.name) / "agent"
        auth_file = Path(tmpdir.name) / "auth.json"
        auth_file.write_text('{"OPENAI_API_KEY":"test-key"}', encoding="utf-8")
        os.environ["OPENAI_BASE_URL"] = "https://example.invalid/v1"
        agent = module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(auth_file),
            reasoning_effort="high",
        )
        environment = sys.modules["harbor.environments.base"].BaseEnvironment()
        context = sys.modules["harbor.models.agent.context"].AgentContext()

        asyncio.run(agent.run("fix it", environment, context))

        self.assertGreaterEqual(len(environment.execs), 3)
        setup_exec = environment.execs[0]
        run_exec = environment.execs[1]
        self.assertIn("CODEX_AUTH_JSON_B64", setup_exec["command"])
        self.assertIn("CODEX_AUTH_JSON_B64", setup_exec["env"])
        self.assertEqual(
            run_exec["env"]["OPENAI_BASE_URL"],
            "https://example.invalid/v1",
        )
        self.assertIn("emit_bootstrap_marker()", run_exec["command"])
        cleanup_exec = environment.execs[2]
        self.assertIn("/tmp/codex-secrets", cleanup_exec["command"])
        self.assertIn('"$CODEX_HOME/auth.json"', cleanup_exec["command"])
        self.assertEqual(
            cleanup_exec["env"]["CODEX_HOME"],
            module.EnvironmentPaths.agent_dir.as_posix(),
        )
        self.assertTrue(agent.populated_context)

    def test_create_run_agent_commands_prepends_skill_activation_instruction(self):
        os.environ["STET_SKILL_ACTIVATION_TARGETS_JSON"] = json.dumps([
            {
                "path": "/skills/capability-dogfood/SKILL.md",
                "relative_path": "capability-dogfood/SKILL.md",
                "sha256": "abc123",
            }
        ])
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(self.auth_file),
        )

        commands = agent.create_run_agent_commands("fix the task")

        run_command = commands[1]
        self.assertIn("/skills/capability-dogfood/SKILL.md", run_command.command)
        self.assertIn("abc123", run_command.command)
        self.assertIn("Before doing any repository inspection or task work", run_command.command)

    def test_run_with_exec_input_prepends_skill_activation_instruction(self):
        os.environ["STET_SKILL_ACTIVATION_TARGETS_JSON"] = json.dumps([
            {
                "path": "/skills/capability-dogfood/SKILL.md",
                "relative_path": "capability-dogfood/SKILL.md",
                "sha256": "abc123",
            }
        ])
        agent = self.module.CodexAuthAgent(
            model_name="openai/gpt-5.4",
            auth_path=str(self.auth_file),
        )
        environment = sys.modules["harbor.environments.base"].BaseEnvironment()
        context = sys.modules["harbor.models.agent.context"].AgentContext()

        asyncio.run(agent.run("fix it", environment, context))

        self.assertIn("/skills/capability-dogfood/SKILL.md", agent.last_instruction)
        self.assertIn("fix it", agent.last_instruction)
        self.assertNotEqual(agent.last_instruction, "fix it")


if __name__ == "__main__":
    unittest.main()
