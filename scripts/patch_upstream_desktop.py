from pathlib import Path

ops = Path("android/app/src/main/java/id/or/oo/pr/DistroOperations.kt")
s = ops.read_text()
old_kind = 'enum class Kind(val label: String) { Install("Installing"), Remove("Removing"), Test("Testing") }'
new_kind = 'enum class Kind(val label: String) { Install("Installing"), Remove("Removing"), Test("Testing"), Desktop("Preparing desktop"), StartDesktop("Starting desktop") }'
if old_kind not in s:
    raise SystemExit("DistroOperations Kind declaration not found")
s = s.replace(old_kind, new_kind, 1)

needle = """    fun test(alias: String, displayName: String): Boolean =
        start(Operation(Kind.Test, alias, displayName, emptyList(), true)) {
            execute(listOf("test", alias))
        }
"""
addition = needle + """
    fun setupDesktop(alias: String, displayName: String): Boolean =
        start(Operation(Kind.Desktop, alias, displayName, emptyList(), true)) {
            execute(listOf("login", alias, "--", "sh", "-lc", DESKTOP_SETUP_SCRIPT))
        }

    fun startDesktop(alias: String, displayName: String): Boolean =
        start(Operation(Kind.StartDesktop, alias, displayName, emptyList(), true)) {
            execute(listOf("login", alias, "--", "sh", "-lc", DESKTOP_START_SCRIPT))
        }
"""
if needle not in s:
    raise SystemExit("DistroOperations.test method not found")
s = s.replace(needle, addition, 1)

marker = """    companion object {
        fun isValidOverrideAlias(alias: String): Boolean {"""
replacement = """    companion object {
        private val DESKTOP_SETUP_SCRIPT = listOf(
            "set -e",
            "export DEBIAN_FRONTEND=noninteractive",
            "dpkg --configure -a",
            "apt-get update",
            "apt-get install -y xfce4 xfce4-terminal tigervnc-standalone-server dbus-x11",
            "mkdir -p /root/.vnc",
            "printf '%s\\n' '#!/bin/sh' 'unset SESSION_MANAGER' 'unset DBUS_SESSION_BUS_ADDRESS' 'exec startxfce4' > /root/.vnc/xstartup",
            "chmod 700 /root/.vnc",
            "chmod +x /root/.vnc/xstartup",
            "echo 'XFCE desktop is installed. Choose Start XFCE desktop to launch it.'"
        ).joinToString("\\n")

        private val DESKTOP_START_SCRIPT = listOf(
            "set -e",
            "mkdir -p /root/.vnc",
            "if [ ! -x /usr/bin/vncserver ]; then echo 'Desktop is not installed. Choose Install XFCE desktop first.'; exit 1; fi",
            "if vncserver -list 2>/dev/null | grep -q ':1'; then vncserver -kill :1 >/dev/null 2>&1 || true; fi",
            "VNC_PASS=$(od -An -N8 -tx1 /dev/urandom | tr -d ' \\n')",
            "printf '%s\\n' \"$VNC_PASS\" | vncpasswd -f > /root/.vnc/passwd",
            "chmod 600 /root/.vnc/passwd",
            "vncserver :1 -localhost no -geometry 1280x720 -depth 24",
            "echo 'XFCE desktop started.'",
            "echo 'VNC address: 127.0.0.1:5901'",
            "echo \"VNC password: $VNC_PASS\"",
            "echo 'Connect with a VNC Viewer app on this same phone.'"
        ).joinToString("\\n")

        fun isValidOverrideAlias(alias: String): Boolean {"""
if marker not in s:
    raise SystemExit("DistroOperations companion object not found")
s = s.replace(marker, replacement, 1)
ops.write_text(s)

main = Path("android/app/src/main/java/id/or/oo/pr/MainActivity.kt")
s = main.read_text()
old = """                        onRemove = { app.operations.remove(distro.alias, distro.displayName) },
                        onTest = { app.operations.test(distro.alias, distro.displayName) },
                    )"""
new = """                        onRemove = { app.operations.remove(distro.alias, distro.displayName) },
                        onTest = { app.operations.test(distro.alias, distro.displayName) },
                        onDesktopSetup = { app.operations.setupDesktop(distro.alias, distro.displayName) },
                        onDesktopStart = { app.operations.startDesktop(distro.alias, distro.displayName) },
                    )"""
if old not in s:
    raise SystemExit("DistroCard call site not found")
s = s.replace(old, new, 1)
old = """    onRemove: () -> Unit,
    onTest: () -> Unit,
) {"""
new = """    onRemove: () -> Unit,
    onTest: () -> Unit,
    onDesktopSetup: () -> Unit,
    onDesktopStart: () -> Unit,
) {"""
if old not in s:
    raise SystemExit("DistroCard callback signature not found")
s = s.replace(old, new, 1)
old = """                            DropdownMenuItem(
                                text = { Text("Test") },
                                leadingIcon = {
                                    Icon(Icons.Default.BugReport, contentDescription = null)
                                },
                                onClick = {
                                    showMenu = false
                                    onTest()
                                }
                            )
                            HorizontalDivider()"""
new = """                            DropdownMenuItem(
                                text = { Text("Test") },
                                leadingIcon = {
                                    Icon(Icons.Default.BugReport, contentDescription = null)
                                },
                                onClick = {
                                    showMenu = false
                                    onTest()
                                }
                            )
                            DropdownMenuItem(
                                text = { Text("Install XFCE desktop") },
                                leadingIcon = {
                                    Icon(Icons.Default.Download, contentDescription = null)
                                },
                                onClick = {
                                    showMenu = false
                                    onDesktopSetup()
                                }
                            )
                            DropdownMenuItem(
                                text = { Text("Start XFCE desktop") },
                                leadingIcon = {
                                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                                },
                                onClick = {
                                    showMenu = false
                                    onDesktopStart()
                                }
                            )
                            HorizontalDivider()"""
if old not in s:
    raise SystemExit("Distro overflow menu insertion point not found")
s = s.replace(old, new, 1)
main.write_text(s)
