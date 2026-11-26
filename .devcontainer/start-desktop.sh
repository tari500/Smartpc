#!/usr/bin/env bash
set -euo pipefail

if pgrep -f "Xvfb :1" >/dev/null; then
  echo "SmartPC display already running"
  exit 0
fi

mkdir -p "$HOME/.vnc"
Xvfb :1 -screen 0 1280x800x24 -ac +extension RANDR >/tmp/smartpc-xvfb.log 2>&1 &
sleep 2
export DISPLAY=:1
dbus-launch --exit-with-session xfce4-session >/tmp/smartpc-xfce.log 2>&1 &
sleep 3
x11vnc -display :1 -rfbport 5901 -localhost -rfbauth "$HOME/.vnc/passwd" -forever -shared >/tmp/smartpc-vnc.log 2>&1 &
sleep 2
websockify --web=/usr/share/novnc/ 0.0.0.0:6080 localhost:5901 >/tmp/smartpc-novnc.log 2>&1 &
echo "SmartPC XFCE desktop started on port 6080"
