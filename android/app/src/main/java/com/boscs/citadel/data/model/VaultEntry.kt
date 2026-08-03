package com.boscs.citadel.data.model
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "vault_entries")
data class VaultEntry(
    @PrimaryKey val id: String,
    val serviceName: String,
    val username: String,
    val encryptedPassword: String,
    val url: String?,
    val notes: String?,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
