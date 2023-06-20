package com.pythonnative.pythonnative

import android.graphics.BitmapFactory
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.graphics.Color
import android.widget.LinearLayout
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.RecyclerView
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
        val layoutMain = findViewById<ConstraintLayout>(R.id.layout_main)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()

//        val createButtonModule = py.getModule("create_button")
//        val pyButton = createButtonModule.callAttr("create_button", this).toJava(Button::class.java)
//        layoutMain.addView(pyButton)

        val createWidgetsModule = py.getModule("create_widgets")
        val pyLayout = createWidgetsModule.callAttr("create_widgets", this).toJava(LinearLayout::class.java)
        layoutMain.addView(pyLayout)

//        val createLayoutModule = py.getModule("create_pn_layout")
//        val pyLayout = createLayoutModule.callAttr("create_pn_layout").toJava(LinearLayout::class.java)
//        layoutMain.addView(pyLayout)

//        val createConstraintLayoutModule = py.getModule("create_constraint_layout")
//        val pyLayout = createConstraintLayoutModule.callAttr("create_constraint_layout", this).toJava(ConstraintLayout::class.java)
//        layoutMain.addView(pyLayout)

//        val createRecyclerViewModule = py.getModule("create_recycler_view")
//        val pyRecyclerView = createRecyclerViewModule.callAttr("create_recycler_view", this).toJava(RecyclerView::class.java)
//        layoutMain.addView(pyRecyclerView)

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
