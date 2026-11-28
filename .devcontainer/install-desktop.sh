#!/usr/bin/env bash
set -Eeuo pipefail

# Install the complete XFCE + virtual display + VNC + browser gateway stack.
required_commands=(xfce4-session Xvfb x11vnc websockify dbus-launch)
missing=()
for cmd in "${required_commands[@]}"; do
  command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done

if (("${#missing[@]}" > 0)) || [[ ! -f /usr/share/novnc/vnc.html ]]; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal dbus-x11 xvfb x11vnc novnc websockify
fi

# Fail here with a useful message rather than leaving a half-working Codespace.
for cmd in "${required_commands[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: required desktop command is still missing: $cmd" >&2
    exit 1
  fi
done
if [[ ! -f /usr/share/novnc/vnc.html ]]; then
  echo "ERROR: noVNC was installed but /usr/share/novnc/vnc.html is missing." >&2
  exit 1
fi

mkdir -p "$HOME/.vnc"
echo "SmartPC desktop dependencies are installed."
