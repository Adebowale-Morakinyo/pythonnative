package com.pythonnative.pythonnative

import android.graphics.BitmapFactory
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.graphics.Color
import androidx.constraintlayout.widget.ConstraintLayout
import com.chaquo.python.PyException
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        val py = Python.getInstance()

        // Generate UI from Python
        val uiLayoutModule = py.getModule("ui_layout")
        val layoutJson = uiLayoutModule.callAttr("generate_layout").toString()
        val layout = JSONObject(layoutJson)
        val widgets = layout.getJSONArray("widgets")

        for (i in 0 until widgets.length()) {
            val widget = widgets.getJSONObject(i)
            when (widget.getString("type")) {
                "Button" -> {
                    val button = Button(this)
                    button.text = widget.getJSONObject("properties").getString("text")
                    button.setTextColor(Color.parseColor(widget.getJSONObject("properties").getString("textColor")))
                    button.setBackgroundColor(Color.parseColor(widget.getJSONObject("properties").getString("backgroundColor")))

                    if (widget.has("eventHandlers") && widget.getJSONObject("eventHandlers").has("onClick")) {
                        val onClickFunctionName = widget.getJSONObject("eventHandlers").getString("onClick")
                        val onClickFunction = py.getModule("ui_layout").get(onClickFunctionName)

                        button.setOnClickListener {
                            onClickFunction?.call()
                        }
                    }

                    // Add button to your layout here
                    val layoutMain = findViewById<ConstraintLayout>(R.id.layout_main)
                    layoutMain.addView(button)
                }
                // Handle other widget types...
            }
        }

        // Existing code for displaying plot
//        val imageView = findViewById<ImageView>(R.id.image_home)
//        val plotModule = py.getModule("plot")
//        val xInput = "1 2 3 4 5"
//        val yInput = "1 4 9 16 25"
//        CoroutineScope(Dispatchers.Main).launch {
//            try {
//                val bytes = plotModule.callAttr(
//                    "plot",
//                    xInput,
//                    yInput
//                ).toJava(ByteArray::class.java)
//                withContext(Dispatchers.IO) {
//                    val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
//                    withContext(Dispatchers.Main) {
//                        imageView.setImageBitmap(bitmap)
//                    }
//                }
//            } catch (e: PyException) {
//                Log.e("Python Error", "Error executing Python code", e)
//            }
//        }
    }
}
