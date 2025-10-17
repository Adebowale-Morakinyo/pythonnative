package com.pythonnative.android_template

import android.os.Bundle
import androidx.core.os.bundleOf
import androidx.fragment.app.FragmentActivity
import androidx.navigation.fragment.NavHostFragment

object Navigator {
    @JvmStatic
    fun push(activity: FragmentActivity, pagePath: String, argsJson: String?) {
        val navHost = activity.supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHost.navController
        val args = Bundle()
        args.putString("page_path", pagePath)
        if (argsJson != null) {
            args.putString("args_json", argsJson)
        }
        navController.navigate(R.id.pageFragment, args)
    }

    @JvmStatic
    fun pop(activity: FragmentActivity) {
        val navHost = activity.supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navHost.navController.popBackStack()
    }
}
