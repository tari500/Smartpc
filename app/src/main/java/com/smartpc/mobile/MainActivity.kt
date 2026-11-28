package com.smartpc.mobile

import android.app.Activity
import android.os.Bundle
import android.webkit.CookieManager
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import android.view.View
import android.view.WindowManager
import android.graphics.Color
import android.os.Build

class MainActivity : Activity() {
    private lateinit var web: WebView
    private var showingDesktop = false
    private val prefs by lazy { getSharedPreferences("smartpc", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(7, 17, 31)
        window.navigationBarColor = Color.rgb(7, 17, 31)
        window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)

        web = WebView(this)
        web.setBackgroundColor(Color.rgb(7, 17, 31))
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.settings.databaseEnabled = true
        web.settings.allowFileAccess = false
        web.settings.allowContentAccess = false
        web.settings.javaScriptCanOpenWindowsAutomatically = false
        web.settings.setSupportMultipleWindows(false)
        web.settings.useWideViewPort = true
        web.settings.loadWithOverviewMode = true
        web.settings.builtInZoomControls = true
        web.settings.displayZoomControls = false
        web.settings.mediaPlaybackRequiresUserGesture = false

        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true)

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                return !(url.startsWith("https://") || url.startsWith("http://"))
            }
        }
        web.webChromeClient = WebChromeClient()
        web.addJavascriptInterface(SmartPCBridge(), "SmartPC")
        setContentView(web)
        showHome()
    }

    private fun showHome() {
        showingDesktop = false
        web.loadUrl("file:///android_asset/index.html")
        window.decorView.systemUiVisibility = 0
    }

    private fun connectToDesktop(raw: String) {
        val value = raw.trim()
        if (value.isEmpty()) {
            Toast.makeText(this, "Paste your Codespaces port 6080 address first", Toast.LENGTH_LONG).show()
            return
        }
        val safe = if (value.startsWith("https://")) value else if (value.startsWith("http://")) value else "https://$value"
        if (!safe.startsWith("https://")) {
            Toast.makeText(this, "Please use the secure HTTPS address from Codespaces", Toast.LENGTH_LONG).show()
            return
        }
        val base = safe.substringBefore("?").trimEnd('/')
        val page = if (base.endsWith("/vnc.html")) base else "$base/vnc.html"
        val query = if (safe.contains("?")) safe.substringAfter("?") else "autoconnect=true&resize=remote"
        val finalUrl = "$page?$query"
        prefs.edit().putString("desktop_url", page).apply()
        showingDesktop = true
        web.loadUrl(finalUrl)
    }

    inner class SmartPCBridge {
        @JavascriptInterface
        fun getSavedUrl(): String = prefs.getString("desktop_url", "") ?: ""

        @JavascriptInterface
        fun saveUrl(value: String) {
            val clean = value.trim()
            prefs.edit().putString("desktop_url", clean).apply()
        }

        @JavascriptInterface
        fun connect(value: String) {
            runOnUiThread { connectToDesktop(value) }
        }

        @JavascriptInterface
        fun toast(message: String) {
            runOnUiThread { Toast.makeText(this@MainActivity, message, Toast.LENGTH_SHORT).show() }
        }

        @JavascriptInterface
        fun home() {
            runOnUiThread { showHome() }
        }
    }

    @Deprecated("Deprecated in Android")
    override fun onBackPressed() {
        if (::web.isInitialized && showingDesktop) {
            showHome()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        if (::web.isInitialized) {
            web.stopLoading()
            web.removeJavascriptInterface("SmartPC")
            web.destroy()
        }
        super.onDestroy()
    }
}
