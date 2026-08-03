package com.boscs.citadel.data.api
import com.boscs.citadel.BuildConfig
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

object RetrofitClient {
    private val logging = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY }
    private val client = OkHttpClient.Builder().addInterceptor(logging).build()
    val retrofit: Retrofit = Retrofit.Builder().baseUrl(BuildConfig.API_BASE_URL).client(client).addConverterFactory(GsonConverterFactory.create()).build()
}

interface ApiService {
    @retrofit2.http.POST("/auth/register") suspend fun register(@retrofit2.http.Body req: RegisterRequest): TokenResponse
    @retrofit2.http.POST("/auth/login") suspend fun login(@retrofit2.http.Body req: LoginRequest): TokenResponse
    @retrofit2.http.POST("/vault/sync") suspend fun syncVault(@retrofit2.http.Header("Authorization") token: String, @retrofit2.http.Body req: VaultSyncRequest): VaultSyncResponse
    @retrofit2.http.GET("/vault/fetch") suspend fun fetchVault(@retrofit2.http.Header("Authorization") token: String): VaultFetchResponse
    @retrofit2.http.POST("/threat/check-url") suspend fun checkUrl(@retrofit2.http.Body req: URLCheckRequest): URLCheckResponse
}

data class RegisterRequest(val email: String, val auth_hash: String, val salt: String)
data class LoginRequest(val email: String, val auth_hash: String)
data class TokenResponse(val access_token: String, val token_type: String, val user_id: String, val salt: String)
data class VaultSyncRequest(val encrypted_data: String, val nonce: String, val checksum: String, val version: Int = 1)
data class VaultSyncResponse(val status: String, val version: Int, val updated_at: String)
data class VaultFetchResponse(val exists: Boolean, val encrypted_data: String?, val nonce: String?, val checksum: String?, val version: Int?, val updated_at: String?)
data class URLCheckRequest(val url: String)
data class URLCheckResponse(val url: String, val safe: Boolean, val score: Int, val reasons: List<String>)

val apiService: ApiService = RetrofitClient.retrofit.create(ApiService::class.java)
