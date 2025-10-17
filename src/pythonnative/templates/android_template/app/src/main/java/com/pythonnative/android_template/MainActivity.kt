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
            // Set content view to the NavHost layout; the initial page loads via nav_graph startDestination
            setContentView(R.layout.activity_main)
            // Optionally, bootstrap Python so first fragment can create the initial page onCreate
            val py = Python.getInstance()
            // Touch module to ensure bundled Python code is available; actual instantiation happens in PageFragment
            py.getModule("app.main_page")
        } catch (e: Exception) {
            Log.e("PythonNative", "Bootstrap failed", e)
            val tv = TextView(this)
            tv.text = "Hello from PythonNative (Android template)"
            setContentView(tv)
        }
    }
}
