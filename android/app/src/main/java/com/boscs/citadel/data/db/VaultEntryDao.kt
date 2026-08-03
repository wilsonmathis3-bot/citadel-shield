package com.boscs.citadel.data.db
import androidx.room.*
import com.boscs.citadel.data.model.VaultEntry
import kotlinx.coroutines.flow.Flow

@Dao
interface VaultEntryDao {
    @Query("SELECT * FROM vault_entries ORDER BY serviceName ASC")
    fun getAll(): Flow<List<VaultEntry>>
    @Query("SELECT * FROM vault_entries WHERE serviceName LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<VaultEntry>>
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entry: VaultEntry)
    @Delete
    suspend fun delete(entry: VaultEntry)
    @Query("DELETE FROM vault_entries")
    suspend fun clearAll()
}
