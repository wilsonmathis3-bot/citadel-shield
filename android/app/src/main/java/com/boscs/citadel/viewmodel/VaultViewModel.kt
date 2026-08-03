package com.boscs.citadel.viewmodel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.boscs.citadel.crypto.VaultCrypto
import com.boscs.citadel.data.SecurePrefs
import com.boscs.citadel.data.api.*
import com.boscs.citadel.data.db.VaultEntryDao
import com.boscs.citadel.data.model.VaultEntry
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class VaultViewModel(private val dao: VaultEntryDao, private val securePrefs: SecurePrefs) : ViewModel() {
    val entries: Flow<List<VaultEntry>> = dao.getAll()
    private val _syncState = MutableStateFlow<SyncState>(SyncState.Idle)
    val syncState: StateFlow<SyncState> = _syncState

    fun addEntry(serviceName: String, username: String, password: String) {
        viewModelScope.launch {
            val key = VaultCrypto.deriveVaultKey(securePrefs.userEmail ?: "", securePrefs.userSalt ?: "")
            val (encrypted, nonce) = VaultCrypto.encryptVault(password, key)
            val entry = VaultEntry(id = UUID.randomUUID().toString(), serviceName = serviceName, username = username, encryptedPassword = "$nonce:$encrypted", url = null, notes = null)
            dao.insert(entry)
        }
    }

    fun deleteEntry(entry: VaultEntry) { viewModelScope.launch { dao.delete(entry) } }

    fun syncToCloud() {
        viewModelScope.launch {
            _syncState.value = SyncState.Syncing
            try {
                val token = securePrefs.authToken ?: throw Exception("Not authenticated")
                val response = apiService.syncVault(token = "Bearer $token", req = VaultSyncRequest(encrypted_data = VaultCrypto.sha256("vault_placeholder"), nonce = VaultCrypto.generateSalt(), checksum = VaultCrypto.sha256("vault_placeholder"), version = 1))
                _syncState.value = SyncState.Success(response.status)
            } catch (e: Exception) { _syncState.value = SyncState.Error(e.message ?: "Sync failed") }
        }
    }

    sealed class SyncState {
        object Idle : SyncState()
        object Syncing : SyncState()
        data class Success(val message: String) : SyncState()
        data class Error(val message: String) : SyncState()
    }
}
