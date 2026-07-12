package com.yourapp.accountbook.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.yourapp.accountbook.data.db.converter.Converters
import com.yourapp.accountbook.data.db.dao.BillDao
import com.yourapp.accountbook.data.db.entity.BillEntity

@Database(entities = [BillEntity::class], version = 1, exportSchema = false)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun billDao(): BillDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "accountbook.db"
                )
                .fallbackToDestructiveMigration()  // schema不匹配时重建而非崩溃，配合自动备份使用
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
