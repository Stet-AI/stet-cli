#!/bin/sh
set -eu

DEFAULT_REPO="${STET_DIST_REPO:-Stet-AI/stet-cli}"
DEFAULT_BIN_DIR="${STET_INSTALL_DIR:-$HOME/.local/bin}"

repo="$DEFAULT_REPO"
bin_dir="$DEFAULT_BIN_DIR"
version=""
repo_overridden=0

die() {
  printf '%s\n' "stet install: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
usage: install.sh [--version <tag>] [--repo <owner/repo>] [--bin-dir <path>]

Install the latest stable Stet binary release.
Use --version to pin or roll back to an exact release tag.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --version)
      [ "$#" -ge 2 ] || die "--version requires a value"
      version="$2"
      shift 2
      ;;
    --repo)
      [ "$#" -ge 2 ] || die "--repo requires a value"
      repo="$2"
      repo_overridden=1
      shift 2
      ;;
    --bin-dir)
      [ "$#" -ge 2 ] || die "--bin-dir requires a value"
      bin_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unexpected argument: $1"
      ;;
  esac
done

command -v tar >/dev/null 2>&1 || die "tar is required"

use_public_download=0
if [ "$repo" = "Stet-AI/stet-cli" ] && [ "$repo_overridden" = "0" ]; then
  use_public_download=1
fi

if [ "$use_public_download" = "1" ]; then
  command -v curl >/dev/null 2>&1 || die "curl is required"
else
  command -v gh >/dev/null 2>&1 || die "gh is required for --repo/private installs; run: gh auth login"
fi

if command -v sha256sum >/dev/null 2>&1; then
  sha256_file() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
  sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }
else
  die "sha256sum or shasum is required"
fi

case "$(uname -s)" in
  Darwin) os_name="Darwin" ;;
  Linux) os_name="Linux" ;;
  *) die "unsupported OS: $(uname -s)" ;;
esac

case "$(uname -m)" in
  arm64|aarch64)
    arch_name="arm64"
    ;;
  x86_64|amd64)
    arch_name="x86_64"
    ;;
  *)
    die "unsupported architecture: $(uname -m)"
    ;;
esac

case "$os_name/$arch_name" in
  Darwin/arm64|Darwin/x86_64|Linux/x86_64|Linux/arm64) ;;
  *) die "unsupported platform: $os_name/$arch_name" ;;
esac

asset_name="stet_${os_name}_${arch_name}.tar.gz"

if [ -z "$version" ]; then
  if [ "$use_public_download" = "1" ]; then
    version="$(curl -fsSL "https://api.github.com/repos/$repo/releases/latest" | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | tr -d '\r' | sed -n '1p')"
  else
    version="$(gh api "repos/$repo/releases" --jq '.[] | select((.draft | not) and (.prerelease | not)) | .tag_name' | sed -n '1p')"
  fi
  [ -n "$version" ] || die "no stable release found in $repo"
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/stet-install.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT INT TERM

archive="$tmp_dir/$asset_name"
checksums="$tmp_dir/checksums.txt"

if [ "$use_public_download" = "1" ]; then
  curl -fsSL "https://github.com/$repo/releases/download/$version/$asset_name" > "$archive"
  curl -fsSL "https://github.com/$repo/releases/download/$version/checksums.txt" > "$checksums"
else
  asset_url="$(gh api "repos/$repo/releases/tags/$version" --jq ".assets[] | select(.name == \"$asset_name\") | .url")"
  [ -n "$asset_url" ] || die "release $version is missing $asset_name"
  checksums_url="$(gh api "repos/$repo/releases/tags/$version" --jq '.assets[] | select(.name == "checksums.txt") | .url')"
  [ -n "$checksums_url" ] || die "release $version is missing checksums.txt"
  gh api "$asset_url" -H "Accept: application/octet-stream" > "$archive"
  gh api "$checksums_url" -H "Accept: application/octet-stream" > "$checksums"
fi

expected="$(awk -v name="$asset_name" '($2 == name || $2 == "*" name) { print $1; exit }' "$checksums")"
[ -n "$expected" ] || die "checksums.txt has no entry for $asset_name"
actual="$(sha256_file "$archive")"
[ "$actual" = "$expected" ] || die "checksum mismatch for $asset_name: expected $expected, got $actual"

member_list="$tmp_dir/members.txt"
tar -tzf "$archive" > "$member_list"
[ "$(wc -l < "$member_list" | tr -d ' ')" = "1" ] || die "archive must contain exactly one member named stet"
[ "$(cat "$member_list")" = "stet" ] || die "archive contains unsafe member: $(cat "$member_list")"

type_char="$(tar -tzvf "$archive" | awk 'NR == 1 { print substr($0, 1, 1) }')"
[ "$type_char" = "-" ] || die "archive member stet must be a regular file"

extract_dir="$tmp_dir/extract"
mkdir -p "$extract_dir"
tar -xzf "$archive" -C "$extract_dir"
[ ! -L "$extract_dir/stet" ] || die "archive member stet must not be a symlink"
[ -f "$extract_dir/stet" ] || die "archive member stet must be a regular file"
[ -x "$extract_dir/stet" ] || die "archive member stet must be executable"

mkdir -p "$bin_dir"
bin_dir_abs="$(cd "$bin_dir" && pwd -P)"
target="$bin_dir_abs/stet"
if [ -L "$target" ]; then
  link_target="$(readlink "$target")"
  case "$link_target" in
    /*)
      resolved="$link_target"
      ;;
    *)
      resolved="$(cd "$(dirname "$target")" && cd "$(dirname "$link_target")" && pwd -P)/$(basename "$link_target")"
      ;;
  esac
  case "$resolved" in
    "$bin_dir_abs"/*) target="$resolved" ;;
    *) die "$target is a symlink outside $bin_dir_abs; rerun with --bin-dir pointing at the real install directory" ;;
  esac
fi

	legacy_support_root="$HOME/.local/share/stet/harbor-agents"
	case "$legacy_support_root" in
	  ""|"/"|"$HOME"|"$HOME/")
	    die "unsafe legacy Stet support directory: $legacy_support_root"
	    ;;
	esac
	rm -rf "$legacy_support_root"

	tmp_target="$(mktemp "$bin_dir_abs/.stet-update.XXXXXX")"
	cp "$extract_dir/stet" "$tmp_target"
	chmod 0755 "$tmp_target"
	mv -f "$tmp_target" "$target"

	printf 'installed %s to %s\n' "$version" "$target"
