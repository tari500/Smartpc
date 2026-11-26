#!/usr/bin/env bash
set -euo pipefail

if ! command -v xfce4-session >/dev/null 2>&1; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal dbus-x11 xvfb x11vnc novnc websockify
fi

mkdir -p "$HOME/.vnc"
if [ ! -f "$HOME/.vnc/passwd" ]; then
  x11vnc -storepasswd "SmartPC-temp-$(openssl rand -hex 8)" "$HOME/.vnc/passwd" >/dev/null
fi
