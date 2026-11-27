#!/usr/bin/env sh
set -eu

PANDAY_REPO="${PANDAY_REPO:-GG-Santos/panday}"
PANDAY_VERSION="${PANDAY_VERSION:-v1.0.0}"
PANDAY_ARCHIVE="${PANDAY_ARCHIVE:-panday-finished-2026-11-27.zip}"
PANDAY_HOME="${PANDAY_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/panday}"
URL="${PANDAY_URL:-https://github.com/${PANDAY_REPO}/releases/download/${PANDAY_VERSION}/${PANDAY_ARCHIVE}}"

command -v uv >/dev/null 2>&1 || {
  printf '%s\n' 'uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/' >&2
  exit 2
}
command -v unzip >/dev/null 2>&1 || {
  printf '%s\n' 'unzip is required.' >&2
  exit 2
}

archive="$(mktemp "${TMPDIR:-/tmp}/panday.XXXXXX.zip")"
trap 'rm -f "$archive"' EXIT
printf 'Downloading Panday from %s\n' "$URL"
if command -v curl >/dev/null 2>&1; then
  curl -fL "$URL" -o "$archive"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$archive" "$URL"
else
  printf '%s\n' 'curl or wget is required.' >&2
  exit 2
fi

mkdir -p "$PANDAY_HOME"
unzip -q -o "$archive" -d "$PANDAY_HOME"
uv tool install --editable --force "$PANDAY_HOME/cli"
panday init

printf '\nPanday is installed. Add this path to %s if it is not already registered:\n' "$HOME/.panday/config.toml"
printf '[registries]\npaths = ["%s/skills"]\n\n' "$PANDAY_HOME"
printf 'Verify with: panday --version && panday --json doctor\n'
