package com.boscs.citadel.viewmodel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.boscs.citadel.crypto.VaultCrypto
import com.boscs.citadel.data.SecurePrefs
import com.boscs.citadel.data.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AuthViewModel(private val securePrefs: SecurePrefs) : ViewModel() {
    private val _authState = MutableStateFlow<AuthState>(AuthState.Unauthenticated)
    val authState: StateFlow<AuthState> = _authState
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    init {
        if (securePrefs.authToken != null) {
            _authState.value = AuthState.Authenticated(email = securePrefs.userEmail ?: "", userId = securePrefs.userId ?: "")
        }
    }

    fun register(email: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true; _error.value = null
            try {
                val salt = VaultCrypto.generateSalt()
                val authHash = VaultCrypto.deriveAuthHash(password, salt)
                val response = apiService.register(RegisterRequest(email = email, auth_hash = authHash, salt = salt))
                saveSession(response, email)
                _authState.value = AuthState.Authenticated(email = email, userId = response.user_id)
            } catch (e: Exception) { _error.value = e.message ?: "Registration failed" }
            finally { _isLoading.value = false }
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true; _error.value = null
            try {
                val salt = securePrefs.userSalt ?: VaultCrypto.generateSalt()
                val authHash = VaultCrypto.deriveAuthHash(password, salt)
                val response = apiService.login(LoginRequest(email = email, auth_hash = authHash))
                saveSession(response, email)
                _authState.value = AuthState.Authenticated(email = email, userId = response.user_id)
            } catch (e: Exception) { _error.value = e.message ?: "Login failed" }
            finally { _isLoading.value = false }
        }
    }

    fun logout() { securePrefs.clear(); _authState.value = AuthState.Unauthenticated }

    private fun saveSession(response: TokenResponse, email: String) {
        securePrefs.authToken = response.access_token
        securePrefs.userId = response.user_id
        securePrefs.userSalt = response.salt
        securePrefs.userEmail = email
    }

    sealed class AuthState {
        object Unauthenticated : AuthState()
        data class Authenticated(val email: String, val userId: String) : AuthState()
    }
}
