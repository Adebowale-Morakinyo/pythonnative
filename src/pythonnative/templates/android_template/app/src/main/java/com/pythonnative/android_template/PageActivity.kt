package com.pythonnative.android_template

import android.os.Bundle
import android.util.Log
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.PyObject
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject

class PageActivity : AppCompatActivity() {
    private val TAG = javaClass.simpleName
    private var page: PyObject? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate() called")

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        try {
            val py = Python.getInstance()
            val pagePath = intent.getStringExtra("PY_PAGE_PATH") ?: "app.main_page.MainPage"
            val argsJson = intent.getStringExtra("PY_PAGE_ARGS_JSON")
            val moduleName = pagePath.substringBeforeLast('.')
            val className = pagePath.substringAfterLast('.')
            val pyModule = py.getModule(moduleName)
            val pageClass = pyModule.get(className)
            page = pageClass?.call(this)
            if (!argsJson.isNullOrEmpty()) {
                // Let Python handle JSON decoding in set_args
                page?.callAttr("set_args", argsJson)
            }
            page?.callAttr("on_create")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to instantiate page", e)
            // Fallback UI
            val tv = TextView(this)
            tv.text = "Navigation target failed to load"
            setContentView(tv)
        }
    }

    override fun onStart() {
        super.onStart()
        try { page?.callAttr("on_start") } catch (e: Exception) { Log.w(TAG, "on_start failed", e) }
    }

    override fun onResume() {
        super.onResume()
        try { page?.callAttr("on_resume") } catch (e: Exception) { Log.w(TAG, "on_resume failed", e) }
    }

    override fun onPause() {
        super.onPause()
        try { page?.callAttr("on_pause") } catch (e: Exception) { Log.w(TAG, "on_pause failed", e) }
    }

    override fun onStop() {
        super.onStop()
        try { page?.callAttr("on_stop") } catch (e: Exception) { Log.w(TAG, "on_stop failed", e) }
    }

    override fun onDestroy() {
        super.onDestroy()
        try { page?.callAttr("on_destroy") } catch (e: Exception) { Log.w(TAG, "on_destroy failed", e) }
    }

    override fun onRestart() {
        super.onRestart()
        try { page?.callAttr("on_restart") } catch (e: Exception) { Log.w(TAG, "on_restart failed", e) }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        try { page?.callAttr("on_save_instance_state") } catch (e: Exception) { Log.w(TAG, "on_save_instance_state failed", e) }
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        try { page?.callAttr("on_restore_instance_state") } catch (e: Exception) { Log.w(TAG, "on_restore_instance_state failed", e) }
    }
}
