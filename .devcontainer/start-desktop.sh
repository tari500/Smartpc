#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/.vnc"

# Start a virtual display if one is not already running.
if ! pgrep -f '[X]vfb :1' >/dev/null 2>&1; then
  Xvfb :1 -screen 0 1600x900x24 -dpi 110 -ac +extension RANDR >/tmp/smartpc-xvfb.log 2>&1 &
  sleep 2
fi

export DISPLAY=:1

# Start the XFCE desktop if it is not already running.
if ! pgrep -f '[x]fce4-session' >/dev/null 2>&1; then
  dbus-launch --exit-with-session xfce4-session >/tmp/smartpc-xfce.log 2>&1 &
  sleep 3
fi

# Start the VNC server if it is not already listening.
if ! pgrep -f '[x]11vnc.*5901' >/dev/null 2>&1; then
  x11vnc -display :1 -rfbport 5901 -localhost -nopw -forever -shared >/tmp/smartpc-vnc.log 2>&1 &
  sleep 2
fi

# Start the browser gateway if it is not already running.
if ! pgrep -f '[w]ebsockify.*6080' >/dev/null 2>&1; then
  websockify --web=/usr/share/novnc/ 0.0.0.0:6080 localhost:5901 >/tmp/smartpc-novnc.log 2>&1 &
  sleep 2
fi

echo "SmartPC XFCE desktop started. Open the forwarded port 6080 and choose Connect."
