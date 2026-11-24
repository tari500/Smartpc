from pathlib import Path

# Android sessions are attached to a PTY, but explicitly request an interactive
# login shell so the prompt and terminal input are initialized consistently.
login = Path("src/pr-cli/src/login.rs")
login_text = login.read_text()
old_shell = 'let mut cmd_args = vec!["/bin/sh".to_string(), "-l".to_string()];'
new_shell = 'let mut cmd_args = vec!["/bin/sh".to_string(), "-l".to_string(), "-i".to_string()];'
if old_shell not in login_text:
    raise SystemExit("PRoot login shell initialization not found")
login_text = login_text.replace(old_shell, new_shell, 1)
login_text = login_text.replace('strings(&["/bin/sh", "-l"])', 'strings(&["/bin/sh", "-l", "-i"])')
login_text = login_text.replace('strings(&["/bin/sh", "-l", "-c",', 'strings(&["/bin/sh", "-l", "-i", "-c",')
login.write_text(login_text)

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
            "apt-get install -y xfce4 xfce4-terminal tigervnc-standalone-server dbus-x11 websockify",
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
            "printf '%s\\n' smartpc | vncpasswd -f > /root/.vnc/passwd",
            "chmod 600 /root/.vnc/passwd",
            "vncserver :1 -localhost yes -geometry 1280x720 -depth 24",
            "echo 'XFCE desktop started.'",
            "echo 'VNC address: 127.0.0.1:5901'",
            "echo 'VNC password: smartpc'",
            "nohup websockify 6080 127.0.0.1:5901 >/tmp/smartpc-websockify.log 2>&1 </dev/null &",\n            "echo 'Open Desktop inside SmartPC to view XFCE.'"
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


# Install an embedded noVNC screen in the Android app.
main = Path("android/app/src/main/java/id/or/oo/pr/MainActivity.kt")
main_text = main.read_text()
if "class DesktopActivity" not in main_text:
    marker = "\n@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nfun DistroListScreen"
    activity = r"""

class DesktopActivity : ComponentActivity() {
    @Suppress("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val viewer = android.webkit.WebView(this)
        viewer.settings.javaScriptEnabled = true
        viewer.settings.domStorageEnabled = true
        viewer.settings.allowFileAccess = true
        viewer.webViewClient = android.webkit.WebViewClient()
        viewer.loadUrl("file:///android_asset/novnc/vnc.html?host=127.0.0.1&port=6080&autoconnect=true&resize=scale")
        setContentView(viewer)
    }
}
"""
    if marker not in main_text:
        raise SystemExit("Desktop viewer insertion point not found")
    main_text = main_text.replace(marker, activity + marker, 1)

old_call = """                    onClose = ::dismissOutput,
                    onCancel = app.operations::cancel,
                )"""
new_call = """                    onClose = ::dismissOutput,
                    onCancel = app.operations::cancel,
                    onOpenDesktop = if (current.kind == DistroOperations.Kind.StartDesktop && !current.running && current.exitCode == 0) {
                        { context.startActivity(Intent(context, DesktopActivity::class.java)) }
                    } else null,
                )"""
if old_call in main_text:
    main_text = main_text.replace(old_call, new_call, 1)
elif "onOpenDesktop =" not in main_text:
    raise SystemExit("Output console call site not found")

old_signature = """    onClose: () -> Unit,
    onCancel: () -> Unit,
) {"""
new_signature = """    onClose: () -> Unit,
    onCancel: () -> Unit,
    onOpenDesktop: (() -> Unit)? = null,
) {"""
if old_signature in main_text:
    main_text = main_text.replace(old_signature, new_signature, 1)

old_buttons = """            if (isRunning) {
                OutlinedButton(onClick = onCancel, modifier = Modifier.weight(1f)) {
                    Text("Cancel")
                }
            }
            Button(
                onClick = onClose,
                enabled = !isRunning,
                modifier = Modifier.weight(1f)
            ) {
                Text(if (isRunning) "Running…" else "Close")
            }"""
new_buttons = """            if (isRunning) {
                OutlinedButton(onClick = onCancel, modifier = Modifier.weight(1f)) {
                    Text("Cancel")
                }
            }
            if (onOpenDesktop != null) {
                Button(onClick = onOpenDesktop, modifier = Modifier.weight(1f)) {
                    Text("Open Desktop")
                }
            }
            Button(
                onClick = onClose,
                enabled = !isRunning,
                modifier = Modifier.weight(1f)
            ) {
                Text(if (isRunning) "Running…" else "Close")
            }"""
if old_buttons in main_text:
    main_text = main_text.replace(old_buttons, new_buttons, 1)
main.write_text(main_text)

manifest = Path("android/app/src/main/AndroidManifest.xml")
manifest_text = manifest.read_text()
if 'android:name=".DesktopActivity"' not in manifest_text:
    manifest_text = manifest_text.replace("</application>", '<activity android:name=".DesktopActivity" android:exported="false" />\n    </application>')
manifest_text = manifest_text.replace('android:usesCleartextTraffic="false"', 'android:usesCleartextTraffic="true"')
manifest.write_text(manifest_text)
