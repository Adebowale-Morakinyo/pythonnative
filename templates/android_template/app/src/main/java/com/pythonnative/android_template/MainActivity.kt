package com.pythonnative.android_template

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(R.layout.activity_main)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val pyModule = py.getModule("app/main")
        val pyLayout = pyModule.callAttr("main", this).toJava(View::class.java)
        setContentView(pyLayout)
    }
}