package com.pythonnative.android_template

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.TextView
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity() {
    private val TAG = javaClass.simpleName

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate() called")

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        try {
            // Set content view to the NavHost layout; the initial screen loads via nav_graph startDestination
            setContentView(R.layout.activity_main)
            // Optionally, bootstrap Python so first fragment can create the initial screen onCreate
            val py = Python.getInstance()
            py.getModule("pythonnative.hot_reload").callAttr(
                "configure_dev_environment",
                filesDir.absolutePath
            )
            // Warm the framework's bootstrap module; it resolves the root
            // component (the configured app, or the PythonNative Go dev
            // client for a `pn go` build). Actual instantiation happens in
            // ScreenFragment. We avoid importing "app.main" directly here so
            // PythonNative Go (which ships no user app) still boots.
            py.getModule("pythonnative.bootstrap")
        } catch (e: Exception) {
            Log.e("PythonNative", "Bootstrap failed", e)
            val tv = TextView(this)
            tv.text = "Hello from PythonNative (Android template)"
            setContentView(tv)
        }
    }
}
