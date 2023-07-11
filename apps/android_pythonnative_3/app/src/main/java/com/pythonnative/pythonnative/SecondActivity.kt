package com.pythonnative.pythonnative

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class SecondActivity : AppCompatActivity() {
    private val TAG = javaClass.simpleName
    private lateinit var page: PyObject

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate() called")
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val pyModule = py.getModule("app/second_page")
        page = pyModule.callAttr("SecondPage", this)
        page.callAttr("on_create")
    }

    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart() called")
        page.callAttr("on_start")
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume() called")
        page.callAttr("on_resume")
    }

    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause() called")
        page.callAttr("on_pause")
    }

    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop() called")
        page.callAttr("on_stop")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy() called")
        page.callAttr("on_destroy")
    }

    override fun onRestart() {
        super.onRestart()
        Log.d(TAG, "onRestart() called")
        page.callAttr("on_restart")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        Log.d(TAG, "onSaveInstanceState() called")
        page.callAttr("on_save_instance_state")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        Log.d(TAG, "onRestoreInstanceState() called")
        page.callAttr("on_restore_instance_state")
    }
}