import json
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from stet_harbor_agents.install_cache import (
    HarnessCLICacheDescriptor,
    build_cache_key,
    setup_with_cli_cache,
    validate_cache_tree_for_credentials,
)


class HarnessCLIInstallCacheTests(unittest.TestCase):
    def _codex_cache_key(self) -> dict[str, str]:
        return build_cache_key(
            HarnessCLICacheDescriptor(
                harness_name="codex",
                harness_version="0.52.0",
                install_method="npm-global",
                os_release_id="debian",
                os_release_version_id="12",
                arch="x86_64",
                runtime_abi="glibc-2.36",
                extra={"package": "@openai/codex"},
            )
        )

    def _write_cache_entry(self, root: Path, *, created_at: float) -> None:
        key = self._codex_cache_key()
        cache_dir = root / "v1" / key["cache_key"]
        (cache_dir / "bin").mkdir(parents=True)
        (cache_dir / "bin" / "codex").write_text("#!/bin/sh\n", encoding="utf-8")
        manifest = dict(key)
        manifest["binary_name"] = "codex"
        manifest["created_at"] = created_at
        (cache_dir / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _cache_identity_patches(self):
        return (
            mock.patch(
                "stet_harbor_agents.install_cache._os_release_value",
                side_effect=lambda name: {"ID": "debian", "VERSION_ID": "12"}[name],
            ),
            mock.patch(
                "stet_harbor_agents.install_cache.platform.machine",
                return_value="x86_64",
            ),
            mock.patch(
                "stet_harbor_agents.install_cache._runtime_abi",
                return_value="glibc-2.36",
            ),
        )

    def test_cache_key_is_generic_and_excludes_credentials(self):
        descriptor = HarnessCLICacheDescriptor(
            harness_name="codex",
            harness_version="0.52.0",
            install_method="npm-global",
            os_release_id="debian",
            os_release_version_id="12",
            arch="x86_64",
            runtime_abi="node20-glibc",
            extra={
                "OPENAI_API_KEY": "sk-secret",
                "package": "@openai/codex",
            },
        )

        key = build_cache_key(descriptor)

        encoded = json.dumps(key, sort_keys=True)
        self.assertIn("codex", encoded)
        self.assertIn("0.52.0", encoded)
        self.assertIn("node20-glibc", encoded)
        self.assertIn("@openai/codex", encoded)
        self.assertNotIn("sk-secret", encoded)
        self.assertNotIn("OPENAI_API_KEY", encoded)

    def test_cache_tree_rejects_credential_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "bin").mkdir()
            (root / "bin" / "codex").write_text("#!/bin/sh\n", encoding="utf-8")
            (root / ".codex").mkdir()
            (root / ".codex" / "auth.json").write_text(
                '{"OPENAI_API_KEY":"sk-secret"}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "credential material"):
                validate_cache_tree_for_credentials(root)

    def test_cache_key_supports_non_claude_harnesses(self):
        descriptor = HarnessCLICacheDescriptor(
            harness_name="future-agent",
            harness_version="2026.4.16",
            install_method="curl-script",
            os_release_id="ubuntu",
            os_release_version_id="24.04",
            arch="arm64",
            runtime_abi="glibc-2.39",
        )

        key = build_cache_key(descriptor)

        self.assertEqual(key["harness_name"], "future-agent")
        self.assertEqual(key["install_method"], "curl-script")
        self.assertEqual(key["arch"], "arm64")

    def test_failed_credential_validation_removes_partial_cache(self):
        class Environment:
            async def exec(self, command: str, **kwargs):
                return None

        async def setup():
            return None

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / ".codex").mkdir(parents=True)
            (cache_dir / ".codex" / "auth.json").write_text(
                '{"OPENAI_API_KEY":"sk-secret"}',
                encoding="utf-8",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                },
                clear=False,
            ), mock.patch("stet_harbor_agents.install_cache._populate_cache", populate):
                with self.assertRaisesRegex(ValueError, "credential material"):
                    import asyncio

                    asyncio.run(
                        setup_with_cli_cache(
                            environment=Environment(),
                            harness_name="codex",
                            harness_version="0.52.0",
                            install_method="npm-global",
                            binary_name="codex",
                            setup=setup,
                        )
                    )

            self.assertFalse(any(Path(tmpdir).glob("v1/*")))

    def test_expired_manifest_refreshes_cache(self):
        class Environment:
            async def exec(self, command: str, **kwargs):
                return None

        setup_calls = []
        metadata_writes = []

        async def setup():
            setup_calls.append(True)

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / "bin").mkdir(parents=True)
            (cache_dir / "bin" / "codex").write_text("#!/bin/sh\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_cache_entry(root, created_at=1.0)
            os_patch, arch_patch, runtime_patch = self._cache_identity_patches()
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                    "STET_HARNESS_CLI_CACHE_TTL_SEC": "86400",
                },
                clear=False,
            ), os_patch, arch_patch, runtime_patch, mock.patch(
                "stet_harbor_agents.install_cache._populate_cache", populate
            ), mock.patch(
                "stet_harbor_agents.install_cache._write_metadata",
                side_effect=lambda metadata: metadata_writes.append(dict(metadata)),
            ):
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=Environment(),
                        harness_name="codex",
                        harness_version="0.52.0",
                        install_method="npm-global",
                        binary_name="codex",
                        setup=setup,
                        extra={"package": "@openai/codex"},
                    )
                )

            self.assertEqual(len(setup_calls), 1)
            self.assertEqual(metadata["status"], "miss")
            self.assertEqual(metadata["miss_reason"], "cache_expired")
            self.assertEqual(metadata["ttl_seconds"], 86400)
            self.assertEqual(metadata_writes[-1]["miss_reason"], "cache_expired")

    def test_fresh_manifest_uses_cache(self):
        class Environment:
            def __init__(self):
                self.commands = []

            async def exec(self, command: str, **kwargs):
                self.commands.append(command)

        async def setup():
            raise AssertionError("fresh cache hit must not run setup")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_cache_entry(root, created_at=1.0)
            environment = Environment()
            os_patch, arch_patch, runtime_patch = self._cache_identity_patches()
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                    "STET_HARNESS_CLI_CACHE_TTL_SEC": "999999999999",
                },
                clear=False,
            ), os_patch, arch_patch, runtime_patch:
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=environment,
                        harness_name="codex",
                        harness_version="0.52.0",
                        install_method="npm-global",
                        binary_name="codex",
                        setup=setup,
                        extra={"package": "@openai/codex"},
                    )
                )

            self.assertEqual(metadata["status"], "hit")
            self.assertEqual(metadata["ttl_seconds"], 999999999999)
            # Two commands: the baked-binary pre-check + cache activation.
            self.assertEqual(len(environment.commands), 2)

    def test_fractional_age_past_ttl_refreshes_cache(self):
        class Environment:
            async def exec(self, command: str, **kwargs):
                return None

        setup_calls = []

        async def setup():
            setup_calls.append(True)

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / "bin").mkdir(parents=True)
            (cache_dir / "bin" / "codex").write_text("#!/bin/sh\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_cache_entry(root, created_at=100.0)
            os_patch, arch_patch, runtime_patch = self._cache_identity_patches()
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                    "STET_HARNESS_CLI_CACHE_TTL_SEC": "86400",
                },
                clear=False,
            ), os_patch, arch_patch, runtime_patch, mock.patch(
                "stet_harbor_agents.install_cache._now_seconds",
                return_value=86500.1,
            ), mock.patch(
                "stet_harbor_agents.install_cache._populate_cache", populate
            ):
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=Environment(),
                        harness_name="codex",
                        harness_version="0.52.0",
                        install_method="npm-global",
                        binary_name="codex",
                        setup=setup,
                        extra={"package": "@openai/codex"},
                    )
                )

            self.assertEqual(len(setup_calls), 1)
            self.assertEqual(metadata["status"], "miss")
            self.assertEqual(metadata["miss_reason"], "cache_expired")
            self.assertGreater(metadata["cache_age_seconds"], 86400)

    def test_lock_timeout_does_not_populate_without_lock(self):
        class Environment:
            async def exec(self, command: str, **kwargs):
                return None

        async def setup():
            raise AssertionError("setup must not run without a lock")

        async def acquire(_lock_dir):
            raise TimeoutError("cache lock timed out")

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                },
                clear=False,
            ), mock.patch("stet_harbor_agents.install_cache._acquire_lock", acquire):
                with self.assertRaisesRegex(TimeoutError, "cache lock timed out"):
                    import asyncio

                    asyncio.run(
                        setup_with_cli_cache(
                            environment=Environment(),
                            harness_name="codex",
                            harness_version="0.52.0",
                            install_method="npm-global",
                            binary_name="codex",
                            setup=setup,
                        )
                    )


class BakedBinaryShortCircuitTests(unittest.TestCase):
    @staticmethod
    def _exec_result(return_code: int, stdout: str):
        class ExecResult:
            pass

        result = ExecResult()
        result.return_code = return_code
        result.stdout = stdout
        return result

    @classmethod
    def _environment(cls, exec_result):
        class Environment:
            def __init__(self):
                self.commands = []

            async def exec(self_inner, command: str, **kwargs):
                self_inner.commands.append(command)
                return exec_result

        return Environment()

    def test_baked_binary_short_circuits_install(self):
        environment = self._environment(
            self._exec_result(0, "/usr/local/bin/claude\n2.1.126 (Claude Code)\n")
        )
        setup_calls = []

        async def setup():
            setup_calls.append(True)

        metadata_writes = []
        with mock.patch(
            "stet_harbor_agents.install_cache._write_metadata",
            side_effect=lambda m: metadata_writes.append(dict(m)),
        ):
            import asyncio

            metadata = asyncio.run(
                setup_with_cli_cache(
                    environment=environment,
                    harness_name="claude-code",
                    harness_version="default",
                    install_method="harbor-installed-agent",
                    binary_name="claude",
                    setup=setup,
                )
            )

        self.assertEqual(setup_calls, [])
        self.assertEqual(metadata["status"], "skipped_image_baked")
        self.assertEqual(metadata["baked_binary_path"], "/usr/local/bin/claude")
        self.assertEqual(metadata["baked_binary_version"], "2.1.126 (Claude Code)")
        self.assertEqual(metadata_writes[-1]["status"], "skipped_image_baked")
        self.assertEqual(len(environment.commands), 1)

    def test_missing_baked_binary_falls_through_to_install(self):
        environment = self._environment(self._exec_result(1, ""))
        setup_calls = []

        async def setup():
            setup_calls.append(True)

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / "bin").mkdir(parents=True)
            (cache_dir / "bin" / "claude").write_text("#!/bin/sh\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                },
                clear=False,
            ), mock.patch(
                "stet_harbor_agents.install_cache._populate_cache", populate
            ):
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=environment,
                        harness_name="claude-code",
                        harness_version="default",
                        install_method="harbor-installed-agent",
                        binary_name="claude",
                        setup=setup,
                    )
                )

        self.assertEqual(len(setup_calls), 1)
        self.assertEqual(metadata["status"], "miss")

    def test_baked_binary_short_circuits_when_cache_disabled(self):
        environment = self._environment(
            self._exec_result(0, "/usr/local/bin/claude\n2.1.126\n")
        )
        setup_calls = []

        async def setup():
            setup_calls.append(True)

        with mock.patch.dict(
            os.environ,
            {"STET_HARNESS_CLI_CACHE_MODE": "off"},
            clear=False,
        ):
            import asyncio

            metadata = asyncio.run(
                setup_with_cli_cache(
                    environment=environment,
                    harness_name="claude-code",
                    harness_version="default",
                    install_method="harbor-installed-agent",
                    binary_name="claude",
                    setup=setup,
                )
            )

        self.assertEqual(setup_calls, [])
        self.assertEqual(metadata["status"], "skipped_image_baked")
        self.assertEqual(metadata["mode"], "off")
        self.assertEqual(metadata["baked_binary_path"], "/usr/local/bin/claude")
        self.assertFalse(metadata["enabled"])

    def test_baked_binary_version_mismatch_falls_through(self):
        environment = self._environment(
            self._exec_result(0, "/usr/local/bin/claude\n2.1.126 (Claude Code)\n")
        )
        setup_calls = []

        async def setup():
            setup_calls.append(True)

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / "bin").mkdir(parents=True)
            (cache_dir / "bin" / "claude").write_text("#!/bin/sh\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                },
                clear=False,
            ), mock.patch(
                "stet_harbor_agents.install_cache._populate_cache", populate
            ):
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=environment,
                        harness_name="claude-code",
                        harness_version="1.9.0",
                        install_method="harbor-installed-agent",
                        binary_name="claude",
                        setup=setup,
                    )
                )

        self.assertEqual(len(setup_calls), 1)
        self.assertEqual(metadata["status"], "miss")

    def test_baked_binary_substring_version_does_not_match(self):
        # Reviewer #2: requesting "2.1.1" must NOT match a baked "2.1.126";
        # version match is a whole-token check, not substring containment.
        environment = self._environment(
            self._exec_result(0, "/usr/local/bin/claude\n2.1.126 (Claude Code)\n")
        )
        setup_calls = []

        async def setup():
            setup_calls.append(True)

        async def populate(_environment, cache_dir: Path, _binary_name: str):
            (cache_dir / "bin").mkdir(parents=True)
            (cache_dir / "bin" / "claude").write_text("#!/bin/sh\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                os.environ,
                {
                    "STET_HARNESS_CLI_CACHE_DIR": tmpdir,
                    "STET_HARNESS_CLI_CACHE_MODE": "on",
                },
                clear=False,
            ), mock.patch(
                "stet_harbor_agents.install_cache._populate_cache", populate
            ):
                import asyncio

                metadata = asyncio.run(
                    setup_with_cli_cache(
                        environment=environment,
                        harness_name="claude-code",
                        harness_version="2.1.1",
                        install_method="harbor-installed-agent",
                        binary_name="claude",
                        setup=setup,
                    )
                )

        self.assertEqual(len(setup_calls), 1)
        self.assertEqual(metadata["status"], "miss")

    def test_baked_binary_exact_version_match(self):
        environment = self._environment(
            self._exec_result(0, "/usr/local/bin/claude\n2.1.126 (Claude Code)\n")
        )

        async def setup():
            raise AssertionError("exact version match must short-circuit install")

        metadata = __import__("asyncio").run(
            setup_with_cli_cache(
                environment=environment,
                harness_name="claude-code",
                harness_version="2.1.126",
                install_method="harbor-installed-agent",
                binary_name="claude",
                setup=setup,
            )
        )
        self.assertEqual(metadata["status"], "skipped_image_baked")
        self.assertEqual(metadata["baked_binary_version"], "2.1.126 (Claude Code)")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", ".")
    unittest.main()
