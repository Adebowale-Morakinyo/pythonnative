package com.pythonnative.pythonnative

import android.graphics.BitmapFactory
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import com.chaquo.python.PyException
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val imageView = findViewById<ImageView>(R.id.image_home)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val plotModule = py.getModule("plot")
//        val createButtonModule = py.getModule("create_button")
        val xInput = "1 2 3 4 5"
        val yInput = "1 4 9 16 25"
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val bytes = plotModule.callAttr(
                    "plot",
                    xInput,
                    yInput
                ).toJava(ByteArray::class.java)
                withContext(Dispatchers.IO) {
                    val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                    withContext(Dispatchers.Main) {
                        imageView.setImageBitmap(bitmap)
                    }
                }
            } catch (e: PyException) {
                Log.e("Python Error", "Error executing Python code", e)
            }
        }
    }
}