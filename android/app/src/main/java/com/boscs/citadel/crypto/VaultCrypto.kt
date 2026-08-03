package com.boscs.citadel.crypto
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import android.util.Base64
import java.security.MessageDigest
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

object VaultCrypto {
    private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    private const val KEY_ALIAS = "citadel_master_key"
    private const val AES_MODE = "AES/GCM/NoPadding"
    private const val GCM_TAG_LENGTH = 128
    private const val PBKDF2_ITERATIONS = 600000
    private const val KEY_LENGTH = 256

    fun deriveAuthHash(password: String, salt: String): String {
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = PBEKeySpec(password.toCharArray(), salt.toByteArray(), PBKDF2_ITERATIONS, KEY_LENGTH)
        val key = factory.generateSecret(spec)
        return Base64.encodeToString(key.encoded, Base64.NO_WRAP)
    }

    fun deriveVaultKey(password: String, salt: String): ByteArray {
        val combined = password + salt + "CITADEL_VAULT_PEPPER_v1"
        val digest = MessageDigest.getInstance("SHA-256")
        return digest.digest(combined.toByteArray(Charsets.UTF_8))
    }

    fun encryptVault(plaintext: String, key: ByteArray): Pair<String, String> {
        val cipher = Cipher.getInstance(AES_MODE)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        val iv = cipher.iv
        val ciphertext = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))
        val nonce = Base64.encodeToString(iv, Base64.NO_WRAP)
        val encrypted = Base64.encodeToString(ciphertext, Base64.NO_WRAP)
        return Pair(encrypted, nonce)
    }

    fun decryptVault(encrypted: String, nonce: String, key: ByteArray): String {
        val cipher = Cipher.getInstance(AES_MODE)
        val iv = Base64.decode(nonce, Base64.NO_WRAP)
        val spec = GCMParameterSpec(GCM_TAG_LENGTH, iv)
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), spec)
        val ciphertext = Base64.decode(encrypted, Base64.NO_WRAP)
        val plaintext = cipher.doFinal(ciphertext)
        return String(plaintext, Charsets.UTF_8)
    }

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
        keyStore.load(null)
        keyStore.getKey(KEY_ALIAS, null)?.let { return it as SecretKey }
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        val builder = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(false)
        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }

    fun generateSalt(): String {
        val bytes = ByteArray(32)
        java.security.SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.NO_WRAP)
    }

    fun sha256(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        return Base64.encodeToString(digest.digest(input.toByteArray()), Base64.NO_WRAP)
    }
}
