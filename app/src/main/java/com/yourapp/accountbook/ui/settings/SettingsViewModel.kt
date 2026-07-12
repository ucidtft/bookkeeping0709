package com.yourapp.accountbook.ui.settings

import androidx.lifecycle.ViewModel
import com.yourapp.accountbook.BuildConfig

class SettingsViewModel : ViewModel() {
    fun getVersionName(): String = BuildConfig.VERSION_NAME
}
