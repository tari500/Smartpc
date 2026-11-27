#!/usr/bin/env bash
set -euo pipefail

# Install every component required by the remote desktop, not just XFCE.
required_commands=(xfce4-session Xvfb x11vnc websockify dbus-launch)
missing=0
for cmd in "${required_commands[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing=1
    break
  fi
done

if [ "$missing" -eq 1 ] || [ ! -f /usr/share/novnc/vnc.html ]; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal dbus-x11 xvfb x11vnc novnc websockify
fi

# Confirm the noVNC web client was installed.
if [ ! -f /usr/share/novnc/vnc.html ]; then
  echo "ERROR: noVNC web files were not found at /usr/share/novnc."
  exit 1
fi

mkdir -p "$HOME/.vnc"
echo "SmartPC desktop dependencies are installed."
