package com.boscs.citadel.data
import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecurePrefs(context: Context) {
    private val masterKey = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(context, "citadel_secure", masterKey, EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)

    var authToken: String? get() = prefs.getString(KEY_TOKEN, null); set(value) = prefs.edit().putString(KEY_TOKEN, value).apply()
    var userId: String? get() = prefs.getString(KEY_USER_ID, null); set(value) = prefs.edit().putString(KEY_USER_ID, value).apply()
    var userSalt: String? get() = prefs.getString(KEY_SALT, null); set(value) = prefs.edit().putString(KEY_SALT, value).apply()
    var userEmail: String? get() = prefs.getString(KEY_EMAIL, null); set(value) = prefs.edit().putString(KEY_EMAIL, value).apply()

    fun clear() { prefs.edit().clear().apply() }

    companion object {
        private const val KEY_TOKEN = "auth_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_SALT = "user_salt"
        private const val KEY_EMAIL = "user_email"
    }
}
