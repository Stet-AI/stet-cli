from __future__ import annotations

import re
import shlex
import textwrap


_PR_PATTERNS = (
    re.compile(r"\bPR\s*#\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\bstet-pr-(\d+)\b", re.IGNORECASE),
)


def target_pr_from_instruction(instruction: str) -> str:
    for pattern in _PR_PATTERNS:
        match = pattern.search(instruction or "")
        if match:
            return match.group(1)
    return ""


def guard_env(instruction: str) -> dict[str, str]:
    env = {"STET_HUMAN_PATCH_GUARD": "1"}
    target_pr = target_pr_from_instruction(instruction)
    if target_pr:
        env["STET_TARGET_PR_NUMBER"] = target_pr
    return env


def guard_setup_command(instruction: str) -> str:
    target_pr = target_pr_from_instruction(instruction)
    target_assignment = ""
    if target_pr:
        target_assignment = f"export STET_TARGET_PR_NUMBER={shlex.quote(target_pr)}; "
    return (
        target_assignment
        + textwrap.dedent(
            r'''
            stet_guard_dir="${STET_HUMAN_PATCH_GUARD_DIR:-/tmp/stet-human-patch-guard/bin}"
            mkdir -p "$stet_guard_dir"
            cat > "$stet_guard_dir/stet-human-patch-guard.py" <<'PY'
            import os
            import re
            import sys

            tool = sys.argv[1] if len(sys.argv) > 1 else ""
            args = sys.argv[2:]
            text = "\n".join(args)

            def block(reason):
                print(
                    "Stet blocked target public human-patch access: " + reason,
                    file=sys.stderr,
                )
                sys.exit(126)

            def has(pattern):
                return re.search(pattern, text, re.IGNORECASE) is not None

            def patch_arg_name(arg):
                return arg.lower().rsplit("/", 1)[-1]

            def looks_like_pr_patch_arg(arg):
                return re.fullmatch(
                    r"pr[-_]?\d+.*\.(?:diff|patch)",
                    patch_arg_name(arg),
                ) is not None

            def command_file_args(command_args):
                return [
                    arg
                    for arg in command_args
                    if arg and not arg.startswith("-") and arg not in {"-", "--"}
                ]

            def git_subcommand_index(command_args):
                option_with_value = {
                    "-c",
                    "-C",
                    "--exec-path",
                    "--git-dir",
                    "--namespace",
                    "--super-prefix",
                    "--work-tree",
                }
                i = 0
                while i < len(command_args):
                    arg = command_args[i]
                    if arg == "--":
                        i += 1
                        break
                    if arg in option_with_value:
                        i += 2
                        continue
                    if any(arg.startswith(option + "=") for option in option_with_value):
                        i += 1
                        continue
                    if arg.startswith("-"):
                        i += 1
                        continue
                    return i
                if i < len(command_args):
                    return i
                return -1

            if tool == "gh":
                block("GitHub CLI is not available during candidate evals")
            if has(r"\bapi\.github\.com\b"):
                block("GitHub API access is not available during candidate evals")
            if has(r"github\.com/[^/\s'\"<>]+/[^/\s'\"<>]+/pull/\d+\.(?:diff|patch)\b"):
                block("GitHub PR diff/patch URL")
            if has(r"github\.com/[^/\s'\"<>]+/[^/\s'\"<>]+/pull/\d+(?:[/?#\s'\"<>]|$)"):
                block("GitHub PR page is not available to candidate agents")
            if has(r"patch-diff\.githubusercontent\.com/raw/[^/\s'\"<>]+/[^/\s'\"<>]+/pull/\d+\.(?:diff|patch)\b"):
                block("GitHub PR diff/patch redirect URL")

            if has(r"github\.com/[^/\s'\"<>]+/[^/\s'\"<>]+/commit/[0-9a-f]{40}\b"):
                block("GitHub commit URL can expose the target human solution")
            if has(r"github\.com/[^/\s'\"<>]+/[^/\s'\"<>]+/raw/[0-9a-f]{40}/"):
                block("raw GitHub head-commit file URL")
            if has(r"raw\.githubusercontent\.com/[^/\s'\"<>]+/[^/\s'\"<>]+/[0-9a-f]{40}/"):
                block("raw GitHub head-commit file URL")
            if has(r"\b(?:diff_url|patch_url)\b") and has(r"\bgithub\b"):
                block("GitHub API diff_url/patch_url fields")

            if tool == "git":
                lowered = [arg.lower() for arg in args]
                subcommand_index = git_subcommand_index(lowered)
                if subcommand_index >= 0 and lowered[subcommand_index] in {"apply", "am"}:
                    file_args = command_file_args(lowered[subcommand_index + 1:])
                    for arg in file_args:
                        if looks_like_pr_patch_arg(arg):
                            block("applying downloaded PR patch file")
            PY
            chmod +x "$stet_guard_dir/stet-human-patch-guard.py"
            for _stet_guard_tool in curl wget git gh python python3 node; do
              cat > "$stet_guard_dir/$_stet_guard_tool" <<'SH'
            #!/bin/sh
            tool="$(basename "$0")"
            guard_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
            find_real() {
              name="$1"
              old_path="$PATH"
              PATH=$(printf '%s' "$PATH" | awk -v RS=: -v ORS=: -v d="$guard_dir" '$0 != d { print }' | sed 's/:$//')
              command -v "$name" 2>/dev/null || true
              PATH="$old_path"
            }
            guard_python="$(find_real python3)"
            if [ -z "$guard_python" ]; then
              guard_python="$(find_real python)"
            fi
            if [ -z "$guard_python" ]; then
              echo "Stet human-patch guard could not find python3" >&2
              exit 127
            fi
            "$guard_python" "$guard_dir/stet-human-patch-guard.py" "$tool" "$@" || exit $?
            real="$(find_real "$tool")"
            if [ -z "$real" ]; then
              echo "Stet human-patch guard could not find real $tool" >&2
              exit 127
            fi
            exec "$real" "$@"
            SH
              chmod +x "$stet_guard_dir/$_stet_guard_tool"
            done
            export STET_HUMAN_PATCH_GUARD=1
            export STET_HUMAN_PATCH_GUARD_DIR="$stet_guard_dir"
            export PATH="$stet_guard_dir:$PATH"
            '''
        ).strip()
    )
