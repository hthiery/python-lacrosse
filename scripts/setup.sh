#!/usr/bin/env bash
# Setups the repository.

# Stop on errors
set -e

cd "$(dirname "$0")/.."

# Add default vscode settings if not existing
SETTINGS_FILE=./.vscode/settings.json
SETTINGS_TEMPLATE_FILE=./.vscode/settings.default.jsonc
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Copy $SETTINGS_TEMPLATE_FILE to $SETTINGS_FILE."
    cp "$SETTINGS_TEMPLATE_FILE" "$SETTINGS_FILE"
fi

mkdir -p config

if [ ! -n "$VIRTUAL_ENV" ]; then
  if [ -x "$(command -v uv)" ]; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
  source .venv/bin/activate
fi

touch "$HOME/.bashrc"
VENV_ACTIVATION="$PWD/.venv/bin/activate"
if ! grep -Fqx "source \"$VENV_ACTIVATION\"" "$HOME/.bashrc"; then
  printf '\nsource "%s"\n' "$VENV_ACTIVATION" >> "$HOME/.bashrc"
fi

if ! [ -x "$(command -v uv)" ]; then
  python3 -m pip install uv
fi

scripts/bootstrap.sh
