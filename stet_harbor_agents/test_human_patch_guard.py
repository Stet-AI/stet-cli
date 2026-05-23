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
        self.assertEqual(target_pr_from_instruction("MR !42: fix race"), "42")

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

    def test_guard_blocks_glab_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "glab")
            env = self._guard_env(fake_bin, guard_bin)

            blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; glab auth status",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(blocked.returncode, 126, blocked.stderr)
            self.assertIn("GitLab CLI is not available", blocked.stderr)

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

    def test_guard_blocks_gitlab_mr_urls_and_allows_other_gitlab_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")
            env = self._guard_env(fake_bin, guard_bin)

            for url, reason in (
                (
                    "https://gitlab.com/group/project/-/merge_requests/42.diff",
                    "GitLab MR diff/patch URL",
                ),
                (
                    "https://gitlab.com/group/project/-/merge_requests/42.patch",
                    "GitLab MR diff/patch URL",
                ),
                (
                    "https://gitlab.example.com/group/nested/project/-/merge_requests/42",
                    "GitLab MR page is not available",
                ),
            ):
                with self.subTest(url=url):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("MR !42: fix")
                            + "; curl -L "
                            + shlex.quote(url),
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn(reason, blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; curl -L https://gitlab.com/group/project/-/tree/main",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake curl ok", allowed.stdout)

    def test_guard_blocks_gitlab_api_merge_request_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")
            env = self._guard_env(fake_bin, guard_bin)

            for url in (
                "https://gitlab.com/api/v4/projects/group%2Fproject/merge_requests/42",
                "https://gitlab.example.com/api/v4/projects/123/merge_requests/42/changes",
            ):
                with self.subTest(url=url):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("MR !42: fix")
                            + "; curl -L "
                            + shlex.quote(url),
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn("GitLab API merge request access", blocked.stderr)

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

    def test_guard_blocks_gitlab_commit_and_raw_commit_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "curl")
            sha = "79d7e799aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            env = self._guard_env(fake_bin, guard_bin)

            for url, reason in (
                (
                    f"https://gitlab.com/group/project/-/commit/{sha}",
                    "GitLab commit URL can expose the target human solution",
                ),
                (
                    f"https://gitlab.com/group/project/-/raw/{sha}/pkg/foo.go",
                    "raw GitLab head-commit file URL",
                ),
                (
                    f"https://gitlab.com/api/v4/projects/group%2Fproject/repository/files/pkg%2Ffoo.go/raw?ref={sha}",
                    "raw GitLab head-commit file URL",
                ),
            ):
                with self.subTest(url=url):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("MR !42: fix")
                            + "; curl -L "
                            + shlex.quote(url),
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn(reason, blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; curl -L https://gitlab.com/api/v4/projects/group%2Fproject/repository/files/pkg%2Ffoo.go/raw?ref=main",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake curl ok", allowed.stdout)

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

    def test_guard_blocks_git_apply_downloaded_mr_patch_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")
            env = self._guard_env(fake_bin, guard_bin)
            redirected_patch = Path(tmp) / "mr42.patch"
            redirected_patch.write_text("diff --git a/a b/a\n", encoding="utf-8")

            for command in (
                "git apply /tmp/mr42.patch",
                "git apply /tmp/mr-42.diff",
                "git am /tmp/merge-request-42.patch",
                "git apply /tmp/merge-requests-42.patch",
                "git apply /tmp/merge_requests_42.diff",
                "git -C /tmp apply /tmp/mr_42.patch",
            ):
                with self.subTest(command=command):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("MR !42: fix") + "; " + command,
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn("applying downloaded review patch", blocked.stderr)

            allowed = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; git apply < "
                    + shlex.quote(str(redirected_patch)),
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertIn("fake git ok", allowed.stdout)

    def test_guard_blocks_git_pr_ref_fetch_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")
            env = self._guard_env(fake_bin, guard_bin)

            for command in (
                "git fetch --depth=1 https://github.com/wundergraph/graphql-go-tools.git pull/828/head:pr-828",
                "git fetch origin refs/pull/828/head",
                "git fetch --depth=1 origin +refs/pull/828/merge:refs/remotes/origin/pr-828",
                "git fetch origin +refs/pull/*:refs/remotes/origin/pr/*",
                "git fetch origin +refs/pull/828/*:refs/remotes/origin/pr-828/*",
                "git -C /app fetch origin pull/828/head:pr-828",
                "git ls-remote https://github.com/wundergraph/graphql-go-tools.git refs/pull/828/head",
                "git -c remote.origin.fetch=+refs/pull/828/head:refs/remotes/origin/pr-828 fetch origin",
                "git -c remote.origin.fetch=+refs/pull/*:refs/remotes/origin/pr/* fetch origin",
                "git config remote.origin.fetch +refs/pull/828/head:refs/remotes/origin/pr-828",
                "git clone -c remote.origin.fetch=+refs/pull/*/head:refs/remotes/origin/pr/* https://github.com/wundergraph/graphql-go-tools.git repo",
            ):
                with self.subTest(command=command):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("PR #828: minify") + "; " + command,
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn("GitHub PR ref", blocked.stderr)

            stdin_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; printf '%s\\n' '+refs/pull/828/head:refs/remotes/origin/pr-828' | git fetch --stdin origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(stdin_blocked.returncode, 126, stdin_blocked.stderr)
            self.assertIn("GitHub PR ref", stdin_blocked.stderr)

            env_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "remote.origin.fetch",
                    "GIT_CONFIG_VALUE_0": "+refs/pull/828/head:refs/remotes/origin/pr-828",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(env_config_blocked.returncode, 126, env_config_blocked.stderr)
            self.assertIn("GitHub PR ref", env_config_blocked.stderr)

            config_env_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git --config-env=remote.origin.fetch=STET_TEST_PR_REFSPEC fetch origin",
                ],
                env={
                    **env,
                    "STET_TEST_PR_REFSPEC": "+refs/pull/828/head:refs/remotes/origin/pr-828",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(config_env_blocked.returncode, 126, config_env_blocked.stderr)
            self.assertIn("GitHub PR ref", config_env_blocked.stderr)

            config_env_space_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git --config-env remote.origin.fetch=STET_TEST_PR_REFSPEC fetch origin",
                ],
                env={
                    **env,
                    "STET_TEST_PR_REFSPEC": "+refs/pull/828/head:refs/remotes/origin/pr-828",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(config_env_space_blocked.returncode, 126, config_env_space_blocked.stderr)
            self.assertIn("GitHub PR ref", config_env_space_blocked.stderr)

            repo = Path(tmp) / "repo"
            git_dir = repo / ".git"
            git_dir.mkdir(parents=True)
            (git_dir / "config").write_text(
                "[remote \"origin\"]\n"
                "\turl = https://github.com/wundergraph/graphql-go-tools.git\n"
                "\tfetch = +refs/pull/828/head:refs/remotes/origin/pr-828\n",
                encoding="utf-8",
            )
            repo_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git -C "
                    + shlex.quote(str(repo))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(repo_config_blocked.returncode, 126, repo_config_blocked.stderr)
            self.assertIn("GitHub PR ref", repo_config_blocked.stderr)

            git_dir_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={**env, "GIT_DIR": str(git_dir)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(git_dir_blocked.returncode, 126, git_dir_blocked.stderr)
            self.assertIn("GitHub PR ref", git_dir_blocked.stderr)

            include_config = Path(tmp) / "pr-ref.cfg"
            include_config.write_text(
                "[remote \"origin\"]\n"
                "\tfetch = +refs/pull/828/head:refs/remotes/origin/pr-828\n",
                encoding="utf-8",
            )
            (git_dir / "config").write_text(
                "[include]\n"
                f"\tpath = {include_config}\n",
                encoding="utf-8",
            )
            include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git -C "
                    + shlex.quote(str(repo))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(include_blocked.returncode, 126, include_blocked.stderr)
            self.assertIn("GitHub PR ref", include_blocked.stderr)

            argv_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git -c include.path="
                    + shlex.quote(str(include_config))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(argv_include_blocked.returncode, 126, argv_include_blocked.stderr)
            self.assertIn("GitHub PR ref", argv_include_blocked.stderr)

            clone_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git -c include.path="
                    + shlex.quote(str(include_config))
                    + " clone https://github.com/wundergraph/graphql-go-tools.git repo-from-include",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(clone_include_blocked.returncode, 126, clone_include_blocked.stderr)
            self.assertIn("GitHub PR ref", clone_include_blocked.stderr)

            env_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git --config-env=include.path=STET_TEST_INCLUDE fetch origin",
                ],
                env={**env, "STET_TEST_INCLUDE": str(include_config)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(env_include_blocked.returncode, 126, env_include_blocked.stderr)
            self.assertIn("GitHub PR ref", env_include_blocked.stderr)

            env_config_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "include.path",
                    "GIT_CONFIG_VALUE_0": str(include_config),
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(env_config_include_blocked.returncode, 126, env_config_include_blocked.stderr)
            self.assertIn("GitHub PR ref", env_config_include_blocked.stderr)

            parameters_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={**env, "GIT_CONFIG_PARAMETERS": f"'include.path={include_config}'"},
                text=True,
                capture_output=True,
            )
            self.assertEqual(parameters_include_blocked.returncode, 126, parameters_include_blocked.stderr)
            self.assertIn("GitHub PR ref", parameters_include_blocked.stderr)

            real_parameters_ref_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_PARAMETERS": "'remote.origin.fetch'='+refs/pull/828/head:refs/remotes/origin/pr-828'",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(real_parameters_ref_blocked.returncode, 126, real_parameters_ref_blocked.stderr)
            self.assertIn("GitHub PR ref", real_parameters_ref_blocked.stderr)

            real_parameters_include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_PARAMETERS": f"'include.path'='{include_config}'",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(real_parameters_include_blocked.returncode, 126, real_parameters_include_blocked.stderr)
            self.assertIn("GitHub PR ref", real_parameters_include_blocked.stderr)

            (git_dir / "config").write_text(
                "# padding\n"
                + ("#" * (1024 * 1024 + 1))
                + "\n[remote \"origin\"]\n"
                "\tfetch = +refs/pull/828/head:refs/remotes/origin/pr-828\n",
                encoding="utf-8",
            )
            padded_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify")
                    + "; git -C "
                    + shlex.quote(str(repo))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(padded_config_blocked.returncode, 126, padded_config_blocked.stderr)
            self.assertIn("GitHub PR ref", padded_config_blocked.stderr)

            home = Path(tmp) / "home"
            home.mkdir()
            (home / ".gitconfig").write_text(
                "[remote \"origin\"]\n"
                "\tfetch = +refs/pull/828/head:refs/remotes/origin/pr-828\n",
                encoding="utf-8",
            )
            global_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={**env, "HOME": str(home)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(global_config_blocked.returncode, 126, global_config_blocked.stderr)
            self.assertIn("GitHub PR ref", global_config_blocked.stderr)

            xdg_home = Path(tmp) / "xdg"
            xdg_config = xdg_home / "git"
            xdg_config.mkdir(parents=True)
            (xdg_config / "config").write_text(
                "[include]\n"
                f"\tpath = {include_config}\n",
                encoding="utf-8",
            )
            xdg_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("PR #828: minify") + "; git fetch origin",
                ],
                env={**env, "HOME": str(Path(tmp) / "empty-home"), "XDG_CONFIG_HOME": str(xdg_home)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(xdg_config_blocked.returncode, 126, xdg_config_blocked.stderr)
            self.assertIn("GitHub PR ref", xdg_config_blocked.stderr)

    def test_guard_blocks_gitlab_mr_ref_fetch_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")
            env = self._guard_env(fake_bin, guard_bin)

            for command in (
                "git fetch origin refs/merge-requests/42/head",
                "git fetch --depth=1 origin +refs/merge-requests/42/head:refs/remotes/origin/mr-42",
                "git fetch origin +refs/merge-requests/*/head:refs/remotes/origin/mr/*",
                "git -C /tmp fetch origin refs/merge-requests/42/head",
                "git ls-remote https://gitlab.com/group/project.git refs/merge-requests/42/head",
                "git -c remote.origin.fetch=+refs/merge-requests/42/head:refs/remotes/origin/mr-42 fetch origin",
                "git clone -c remote.origin.fetch=+refs/merge-requests/*/head:refs/remotes/origin/mr/* https://gitlab.com/group/project.git repo",
            ):
                with self.subTest(command=command):
                    blocked = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("MR !42: fix") + "; " + command,
                        ],
                        env=env,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(blocked.returncode, 126, blocked.stderr)
                    self.assertIn("GitLab MR ref", blocked.stderr)

            env_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "remote.origin.fetch",
                    "GIT_CONFIG_VALUE_0": "+refs/merge-requests/42/head:refs/remotes/origin/mr-42",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(env_config_blocked.returncode, 126, env_config_blocked.stderr)
            self.assertIn("GitLab MR ref", env_config_blocked.stderr)

            config_env_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; git --config-env=remote.origin.fetch=STET_TEST_MR_REFSPEC fetch origin",
                ],
                env={
                    **env,
                    "STET_TEST_MR_REFSPEC": "+refs/merge-requests/42/head:refs/remotes/origin/mr-42",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(config_env_blocked.returncode, 126, config_env_blocked.stderr)
            self.assertIn("GitLab MR ref", config_env_blocked.stderr)

            repo = Path(tmp) / "repo"
            git_dir = repo / ".git"
            git_dir.mkdir(parents=True)
            (git_dir / "config").write_text(
                "[remote \"origin\"]\n"
                "\turl = https://gitlab.com/group/project.git\n"
                "\tfetch = +refs/merge-requests/42/head:refs/remotes/origin/mr-42\n",
                encoding="utf-8",
            )
            repo_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; git -C "
                    + shlex.quote(str(repo))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(repo_config_blocked.returncode, 126, repo_config_blocked.stderr)
            self.assertIn("GitLab MR ref", repo_config_blocked.stderr)

            include_config = Path(tmp) / "mr-ref.cfg"
            include_config.write_text(
                "[remote \"origin\"]\n"
                "\tfetch = +refs/merge-requests/42/head:refs/remotes/origin/mr-42\n",
                encoding="utf-8",
            )
            (git_dir / "config").write_text(
                "[include]\n"
                f"\tpath = {include_config}\n",
                encoding="utf-8",
            )
            include_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix")
                    + "; git -C "
                    + shlex.quote(str(repo))
                    + " fetch origin",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(include_blocked.returncode, 126, include_blocked.stderr)
            self.assertIn("GitLab MR ref", include_blocked.stderr)

            parameters_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix") + "; git fetch origin",
                ],
                env={
                    **env,
                    "GIT_CONFIG_PARAMETERS": "'remote.origin.fetch'='+refs/merge-requests/42/head:refs/remotes/origin/mr-42'",
                },
                text=True,
                capture_output=True,
            )
            self.assertEqual(parameters_blocked.returncode, 126, parameters_blocked.stderr)
            self.assertIn("GitLab MR ref", parameters_blocked.stderr)

            home = Path(tmp) / "home"
            home.mkdir()
            (home / ".gitconfig").write_text(
                "[remote \"origin\"]\n"
                "\tfetch = +refs/merge-requests/42/head:refs/remotes/origin/mr-42\n",
                encoding="utf-8",
            )
            global_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix") + "; git fetch origin",
                ],
                env={**env, "HOME": str(home)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(global_config_blocked.returncode, 126, global_config_blocked.stderr)
            self.assertIn("GitLab MR ref", global_config_blocked.stderr)

            xdg_home = Path(tmp) / "xdg"
            xdg_config = xdg_home / "git"
            xdg_config.mkdir(parents=True)
            (xdg_config / "config").write_text(
                "[remote \"origin\"]\n"
                "\tfetch = +refs/merge-requests/42/head:refs/remotes/origin/mr-42\n",
                encoding="utf-8",
            )
            xdg_config_blocked = subprocess.run(
                [
                    "sh",
                    "-c",
                    guard_setup_command("MR !42: fix") + "; git fetch origin",
                ],
                env={**env, "HOME": str(Path(tmp) / "empty-home"), "XDG_CONFIG_HOME": str(xdg_home)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(xdg_config_blocked.returncode, 126, xdg_config_blocked.stderr)
            self.assertIn("GitLab MR ref", xdg_config_blocked.stderr)

    def test_guard_allows_ordinary_git_fetch_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "fake-bin"
            guard_bin = Path(tmp) / "guard-bin"
            fake_bin.mkdir()
            self._write_fake_tool(fake_bin / "git")
            env = self._guard_env(fake_bin, guard_bin)
            env["GITHUB_REF"] = "refs/pull/999/merge"
            env["UNRELATED_REFSPEC"] = "+refs/pull/999/head:refs/remotes/origin/pr-999"

            for command in (
                "git fetch origin main",
                "git fetch https://github.com/wundergraph/graphql-go-tools.git main",
                "git fetch https://gitlab.com/group/project.git main",
                "git fetch origin refs/heads/main:refs/remotes/origin/main",
                "git ls-remote https://github.com/wundergraph/graphql-go-tools.git refs/heads/main",
                "git ls-remote https://gitlab.com/group/project.git refs/heads/main",
            ):
                with self.subTest(command=command):
                    allowed = subprocess.run(
                        [
                            "sh",
                            "-c",
                            guard_setup_command("PR #828: minify") + "; " + command,
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
