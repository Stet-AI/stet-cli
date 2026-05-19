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

            def looks_like_github_pr_ref(arg):
                return re.search(
                    r"(?:^|[=+:])(?:refs/)?pull/(?:\d+|\*)(?:/(?:head|merge|\*))?(?::|$)",
                    arg,
                    re.IGNORECASE,
                ) is not None

            def config_env_names(command_args):
                names = []
                i = 0
                while i < len(command_args):
                    arg = command_args[i]
                    value = ""
                    if arg == "--config-env" and i + 1 < len(command_args):
                        value = command_args[i + 1]
                        i += 2
                    elif arg.startswith("--config-env="):
                        value = arg.split("=", 1)[1]
                        i += 1
                    else:
                        i += 1
                        continue
                    if "=" in value:
                        names.append(value.rsplit("=", 1)[1])
                return names

            def split_config_assignment(value):
                value = (value or "").strip().strip("'\"")
                if "=" not in value:
                    return "", ""
                key, assignment_value = value.split("=", 1)
                return key.strip().lower(), assignment_value.strip().strip("'\"")

            def env_config_assignments(command_args):
                assignments = []
                for i in range(int(os.environ.get("GIT_CONFIG_COUNT", "0") or "0")):
                    key = os.environ.get(f"GIT_CONFIG_KEY_{i}", "").strip().lower()
                    value = os.environ.get(f"GIT_CONFIG_VALUE_{i}", "").strip()
                    if key:
                        assignments.append((key, value))
                parameters = os.environ.get("GIT_CONFIG_PARAMETERS", "")
                for match in re.finditer(
                    r"'([^']+)'\s*=\s*'([^']*)'|\"([^\"]+)\"\s*=\s*\"([^\"]*)\"|(\S+)",
                    parameters,
                ):
                    groups = match.groups()
                    if groups[0] is not None:
                        assignments.append((groups[0].strip().lower(), groups[1].strip()))
                        continue
                    if groups[2] is not None:
                        assignments.append((groups[2].strip().lower(), groups[3].strip()))
                        continue
                    key, value = split_config_assignment(groups[4])
                    if key:
                        assignments.append((key, value))
                i = 0
                while i < len(command_args):
                    arg = command_args[i]
                    raw = ""
                    if arg == "--config-env" and i + 1 < len(command_args):
                        raw = command_args[i + 1]
                        i += 2
                    elif arg.startswith("--config-env="):
                        raw = arg.split("=", 1)[1]
                        i += 1
                    else:
                        i += 1
                        continue
                    key, env_name = split_config_assignment(raw)
                    if key:
                        assignments.append((key, os.environ.get(env_name, "")))
                return assignments

            def git_config_env_contains_github_pr_ref(command_args):
                for _, value in env_config_assignments(command_args):
                    if looks_like_github_pr_ref(value or ""):
                        return True
                return False

            def config_include_paths_from_env(command_args):
                paths = []
                for key, value in env_config_assignments(command_args):
                    if key == "include.path" or (key.startswith("includeif.") and key.endswith(".path")):
                        paths.append(value)
                return paths

            def config_file_contains_github_pr_ref(path):
                return config_file_contains_github_pr_ref_seen(path, set())

            def config_file_contains_github_pr_ref_seen(path, seen):
                if not path:
                    return False
                path = os.path.abspath(os.path.expanduser(path))
                if path in seen:
                    return False
                seen.add(path)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                        content = handle.read()
                except OSError:
                    return False
                if looks_like_github_pr_ref(content):
                    return True
                base = os.path.dirname(path)
                in_include = False
                for line in content.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith(("#", ";")):
                        continue
                    if stripped.startswith("[") and stripped.endswith("]"):
                        section = stripped[1:-1].strip().lower()
                        in_include = section == "include" or section.startswith("includeif ")
                        continue
                    if not in_include or "=" not in stripped:
                        continue
                    key, value = stripped.split("=", 1)
                    if key.strip().lower() != "path":
                        continue
                    include_path = value.strip().strip('"')
                    if not os.path.isabs(include_path):
                        include_path = os.path.join(base, include_path)
                    if config_file_contains_github_pr_ref_seen(include_path, seen):
                        return True
                return False

            def config_include_paths_from_args(command_args):
                paths = []
                i = 0
                while i < len(command_args):
                    arg = command_args[i]
                    value = ""
                    if arg == "-c" and i + 1 < len(command_args):
                        value = command_args[i + 1]
                        i += 2
                    elif arg.startswith("-c") and len(arg) > 2:
                        value = arg[2:]
                        i += 1
                    else:
                        i += 1
                        continue
                    if "=" not in value:
                        continue
                    key, include_path = value.split("=", 1)
                    key = key.lower()
                    if key == "include.path" or (key.startswith("includeif.") and key.endswith(".path")):
                        paths.append(include_path)
                return paths

            def git_config_paths(command_args):
                paths = []
                cwd = os.getcwd()
                git_dir = ""
                i = 0
                while i < len(command_args):
                    arg = command_args[i]
                    if arg == "--":
                        break
                    if arg == "-C" and i + 1 < len(command_args):
                        next_cwd = command_args[i + 1]
                        if not os.path.isabs(next_cwd):
                            next_cwd = os.path.join(cwd, next_cwd)
                        cwd = os.path.abspath(next_cwd)
                        i += 2
                        continue
                    if arg == "--git-dir" and i + 1 < len(command_args):
                        git_dir = command_args[i + 1]
                        i += 2
                        continue
                    if arg.startswith("--git-dir="):
                        git_dir = arg.split("=", 1)[1]
                        i += 1
                        continue
                    if arg.startswith("-"):
                        if arg in {"-c", "--config-env", "--exec-path", "--namespace", "--super-prefix", "--work-tree"}:
                            i += 2
                        else:
                            i += 1
                        continue
                    break
                if not git_dir:
                    git_dir = os.environ.get("GIT_DIR", "")
                if git_dir:
                    if not os.path.isabs(git_dir):
                        git_dir = os.path.join(cwd, git_dir)
                    paths.append(os.path.join(git_dir, "config"))
                else:
                    dotgit = os.path.join(cwd, ".git")
                    if os.path.isdir(dotgit):
                        paths.append(os.path.join(dotgit, "config"))
                    elif os.path.isfile(dotgit):
                        try:
                            with open(dotgit, "r", encoding="utf-8", errors="ignore") as handle:
                                first_line = handle.readline().strip()
                            if first_line.lower().startswith("gitdir:"):
                                git_dir = first_line.split(":", 1)[1].strip()
                                if not os.path.isabs(git_dir):
                                    git_dir = os.path.join(cwd, git_dir)
                                paths.append(os.path.join(git_dir, "config"))
                        except OSError:
                            pass
                for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"):
                    path = os.environ.get(key, "")
                    if path:
                        paths.append(path)
                home = os.environ.get("HOME", "")
                if home:
                    paths.append(os.path.join(home, ".gitconfig"))
                xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
                if xdg_config_home:
                    paths.append(os.path.join(xdg_config_home, "git", "config"))
                elif home:
                    paths.append(os.path.join(home, ".config", "git", "config"))
                return paths

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
                    "--config-env",
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
                for arg in lowered:
                    if looks_like_github_pr_ref(arg):
                        block("GitHub PR ref")
                if git_config_env_contains_github_pr_ref(args):
                    block("GitHub PR ref")
                subcommand_index = git_subcommand_index(lowered)
                if subcommand_index >= 0 and lowered[subcommand_index] in {"apply", "am"}:
                    file_args = command_file_args(lowered[subcommand_index + 1:])
                    for arg in file_args:
                        if looks_like_pr_patch_arg(arg):
                            block("applying downloaded PR patch file")
                if subcommand_index >= 0 and lowered[subcommand_index] in {"clone", "fetch", "pull", "ls-remote"}:
                    if "--stdin" in lowered[subcommand_index + 1:]:
                        block("GitHub PR ref")
                    for path in config_include_paths_from_env(args):
                        if config_file_contains_github_pr_ref(path):
                            block("GitHub PR ref")
                    for path in config_include_paths_from_args(args):
                        if config_file_contains_github_pr_ref(path):
                            block("GitHub PR ref")
                    for path in git_config_paths(args):
                        if config_file_contains_github_pr_ref(path):
                            block("GitHub PR ref")
                    for arg in lowered[subcommand_index + 1:]:
                        if looks_like_github_pr_ref(arg):
                            block("GitHub PR ref")
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
