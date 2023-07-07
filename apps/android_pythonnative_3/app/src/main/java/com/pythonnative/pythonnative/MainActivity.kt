package com.pythonnative.pythonnative

import android.graphics.BitmapFactory
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.graphics.Color
import android.view.View
import android.widget.LinearLayout
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.RecyclerView
import com.chaquo.python.PyException
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    private val TAG = javaClass.simpleName
    private lateinit var page: PyObject

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate() called")

//        setContentView(R.layout.activity_main)
//        val layoutMain = findViewById<ConstraintLayout>(R.id.layout_main)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()

        // Create an instance of the Page class
        val pyModule = py.getModule("app/main_2")
        page = pyModule.callAttr("Page", this)

        val pyLayout = page.callAttr("on_create").toJava(View::class.java)
        setContentView(pyLayout)

//        val pyModule = py.getModule("app/main")
//        val pyLayout = pyModule.callAttr("on_create", this).toJava(View::class.java)
//        setContentView(pyLayout)

//        val createButtonModule = py.getModule("create_button")
//        val pyButton = createButtonModule.callAttr("create_button", this).toJava(Button::class.java)
//        layoutMain.addView(pyButton)

//        val createWidgetsModule = py.getModule("create_widgets")
//        val pyLayout = createWidgetsModule.callAttr("create_widgets", this).toJava(LinearLayout::class.java)
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
