package com.boscs.citadel
import android.app.Application
import com.boscs.citadel.data.db.AppDatabase
class CitadelApp : Application() {
    val database by lazy { AppDatabase.getDatabase(this) }
}
