#!/usr/bin/env bash
set -Eeuo pipefail

mkdir -p "$HOME/.vnc"
export DISPLAY=:1

# Start a persistent virtual X display.
if ! pgrep -u "$USER" -f '[X]vfb :1' >/dev/null 2>&1; then
  Xvfb :1 -screen 0 1600x900x24 -dpi 110 -ac +extension RANDR >/tmp/smartpc-xvfb.log 2>&1 &
  for _ in {1..20}; do
    pgrep -u "$USER" -f '[X]vfb :1' >/dev/null 2>&1 && break
    sleep 0.5
  done
fi
if ! pgrep -u "$USER" -f '[X]vfb :1' >/dev/null 2>&1; then
  echo "ERROR: Xvfb did not start. See /tmp/smartpc-xvfb.log" >&2
  exit 1
fi

# Start XFCE in its own D-Bus session.
if ! pgrep -u "$USER" -f 'xfce4-session' >/dev/null 2>&1; then
  dbus-launch --exit-with-session xfce4-session >/tmp/smartpc-xfce.log 2>&1 &
  sleep 4
fi
if ! pgrep -u "$USER" -f 'xfce4-session' >/dev/null 2>&1; then
  echo "ERROR: XFCE did not start. See /tmp/smartpc-xfce.log" >&2
  exit 1
fi

# Expose VNC only on loopback; Codespaces reaches it through noVNC.
if ! pgrep -u "$USER" -f 'x11vnc.*5901' >/dev/null 2>&1; then
  x11vnc -display :1 -rfbport 5901 -localhost -nopw -forever -shared -noxdamage >/tmp/smartpc-vnc.log 2>&1 &
  sleep 2
fi
if ! pgrep -u "$USER" -f 'x11vnc.*5901' >/dev/null 2>&1; then
  echo "ERROR: x11vnc did not start. See /tmp/smartpc-vnc.log" >&2
  exit 1
fi

# Serve the noVNC client on the forwarded Codespaces port.
if ! pgrep -u "$USER" -f '[w]ebsockify.*6080' >/dev/null 2>&1; then
  websockify --web=/usr/share/novnc 0.0.0.0:6080 127.0.0.1:5901 >/tmp/smartpc-novnc.log 2>&1 &
  sleep 2
fi
if ! pgrep -u "$USER" -f '[w]ebsockify.*6080' >/dev/null 2>&1; then
  echo "ERROR: noVNC gateway did not start. See /tmp/smartpc-novnc.log" >&2
  exit 1
fi

echo "SmartPC desktop is running. Open forwarded port 6080, then visit /vnc.html."
