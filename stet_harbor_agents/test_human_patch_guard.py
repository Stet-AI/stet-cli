import os
import shlex
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from stet_harbor_agents.human_patch_guard import (
    guard_setup_command,
    target_pr_from_instruction,
)


class HumanPatchGuardTests(unittest.TestCase):
    def test_target_pr_from_instruction_accepts_pr_title_and_task_id(self):
        self.assertEqual(target_pr_from_instruction("PR #1076: fix race"), "1076")
        self.assertEqual(target_pr_from_instruction("work on stet-pr-1268"), "1268")

    def test_guard_blocks_target_pr_diff_and_allows_other_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")

            env = dict(os.environ)
            env["PATH"] = str(fake_bin) + os.pathsep + env["PATH"]
            env["STET_HUMAN_PATCH_GUARD_DIR"] = str(guard_bin)

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; curl -L https://github.com/wundergraph/graphql-go-tools/pull/1076.diff",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitHub PR diff/patch URL", blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; curl -L https://pkg.go.dev/github.com/wundergraph/graphql-go-tools",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake curl ok", allowed.stdout)

    def test_guard_blocks_target_pr_redirect_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; curl -L https://patch-diff.githubusercontent.com/raw/wundergraph/graphql-go-tools/pull/1076.patch",
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitHub PR diff/patch redirect URL", blocked.stderr)

    def test_guard_blocks_pr_diff_without_pr_number_in_instruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("Update subscription concurrency handling")
                    + "; curl -L https://github.com/wundergraph/graphql-go-tools/pull/1076.diff",
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitHub PR diff/patch URL", blocked.stderr)

    def test_guard_blocks_gh_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "gh")
            env = self._guard_env(fake_bin, guard_bin)

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; gh auth status",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitHub CLI is not available", blocked.stderr)

    def test_guard_blocks_github_api_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; curl -L https://api.github.com/repos/wundergraph/graphql-go-tools/pulls/1076",
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitHub API access is not available", blocked.stderr)

    def test_guard_does_not_expose_real_tool_env_vars(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")

            exposed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; env | grep '^STET_REAL_'",
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(exposed.returncode, 1, exposed.stdout)
            self.assertEqual(exposed.stdout, "")

            shell_vars = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + '; test -z "${_stet_guard_real_curl+x}"',
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(shell_vars.returncode, 0, shell_vars.stderr)

            wrapper = guard_bin / "curl"
            self.assertNotIn(str(fake_bin), wrapper.read_text(encoding="utf-8"))

    def test_guard_blocks_raw_commit_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")
            sha = "79d7e799aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1309: fix")
                    + f"; curl -L https://github.com/wundergraph/graphql-go-tools/raw/{sha}/pkg/foo.go",
                ],
                env=self._guard_env(fake_bin, guard_bin),
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("raw GitHub head-commit file URL", blocked.stderr)

    def test_guard_blocks_git_apply_downloaded_pr_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")

            env = dict(os.environ)
            env["PATH"] = str(fake_bin) + os.pathsep + env["PATH"]
            env["STET_HUMAN_PATCH_GUARD_DIR"] = str(guard_bin)

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; git apply /tmp/pr1076.patch",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("applying downloaded PR patch", blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; git status --short",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake git ok", allowed.stdout)

    def test_guard_blocks_git_patch_application_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")
            env = self._guard_env(fake_bin, guard_bin)
            redirected_patch = Path(tmp) / "pr1076.patch"
            redirected_patch.write_text("diff --git a/a b/a\n", encoding="utf-8")

            for command in (
                "git apply /tmp/pr-1076.patch",
                "git apply /tmp/pr_1076.diff",
                "git am /tmp/pr1076.patch",
                "git -C /tmp apply /tmp/pr1076.patch",
                "git -c user.name=Stet apply /tmp/pr1076.patch",
                "git --git-dir=/tmp/.git am /tmp/pr1076.patch",
            ):
                with self.subTest(command=command):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("PR #1076: fix") + "; " + command,
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn("Stet blocked target", blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #1076: fix")
                    + "; git apply < "
                    + shlex.quote(str(redirected_patch)),
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake git ok", allowed.stdout)

    @staticmethod
    def _guard_env(fake_bin: Path, guard_bin: Path) -> dict[str, str]:
        env = dict(os.environ)
        for key in list(env):
            if key.startswith("STET_REAL_") or key == "STET_GUARD_PYTHON":
                del env[key]
        env["PATH"] = str(fake_bin) + os.pathsep + env["PATH"]
        env["STET_HUMAN_PATCH_GUARD_DIR"] = str(guard_bin)
        return env

    @staticmethod
    def _write_fake_tool(path: Path) -> None:
        path.write_text("#!/bin/sh\necho fake $(basename \"$0\") ok\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
