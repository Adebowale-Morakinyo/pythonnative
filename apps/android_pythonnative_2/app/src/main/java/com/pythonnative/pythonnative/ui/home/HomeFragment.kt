package com.pythonnative.pythonnative.ui.home

import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.pythonnative.pythonnative.databinding.FragmentHomeBinding
import com.chaquo.python.PyException
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(requireContext()))
        }
        val py = Python.getInstance()
        val plotModule = py.getModule("plot")

        // Variables to keep the user's input
        val xInput = "1 2 3 4 5"
        val yInput = "1 4 9 16 25"

        lifecycleScope.launch {
            try {
                val bytes = plotModule.callAttr(
                    "plot",
                    xInput,
                    yInput
                ).toJava(ByteArray::class.java)
                withContext(Dispatchers.IO) {
                    val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                    binding.imageHome.setImageBitmap(bitmap)
                }
            } catch (e: PyException) {
                binding.textHome.text = e.message
            }
        }

        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}