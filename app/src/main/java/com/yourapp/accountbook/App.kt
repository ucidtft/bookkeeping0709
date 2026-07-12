package com.yourapp.accountbook

import android.app.Application
import com.yourapp.accountbook.data.db.AppDatabase
import com.yourapp.accountbook.util.BillExporter
import com.yourapp.accountbook.BuildConfig
import kotlinx.coroutines.runBlocking

class App : Application() {

    val database: AppDatabase by lazy {
        AppDatabase.getInstance(this)
    }

    override fun onCreate() {
        super.onCreate()
        instance = this

        // Warm up Room on background thread for faster cold start
        Thread { database }.start()

        // 版本升级时自动导出 CSV 备份到 Download/导出账单/auto_backup/
        val prefs = getSharedPreferences("app_prefs", MODE_PRIVATE)
        val lastVersion = prefs.getInt("last_version_code", 0)
        val currentVersion = BuildConfig.VERSION_CODE
        if (currentVersion > lastVersion) {
            Thread {
                try {
                    val file = runBlocking { BillExporter(this@App).exportAllToCSV() }
                    android.util.Log.i("App", "版本升级自动备份成功: ${file.absolutePath}")
                } catch (e: java.lang.Exception) {
                    android.util.Log.w("App", "版本升级自动备份失败: ${e.message}")
                }
            }.start()
            prefs.edit().putInt("last_version_code", currentVersion).apply()
        }

        // 统计 ping
        com.yourapp.accountbook.util.AnalyticsHelper.trackLaunch(this)
    }

    companion object {
        lateinit var instance: App
            private set
    }
}
