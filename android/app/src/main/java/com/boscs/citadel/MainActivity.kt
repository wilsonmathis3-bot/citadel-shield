package com.boscs.citadel
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.boscs.citadel.data.SecurePrefs
import com.boscs.citadel.ui.auth.LoginScreen
import com.boscs.citadel.ui.auth.RegisterScreen
import com.boscs.citadel.ui.dashboard.DashboardScreen
import com.boscs.citadel.ui.theme.CitadelTheme
import com.boscs.citadel.ui.vault.VaultScreen
import com.boscs.citadel.viewmodel.AuthViewModel
import com.boscs.citadel.viewmodel.VaultViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val securePrefs = SecurePrefs(this)
        val database = (application as CitadelApp).database
        val authViewModel = AuthViewModel(securePrefs)
        val vaultViewModel = VaultViewModel(database.vaultEntryDao(), securePrefs)
        setContent {
            CitadelTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    val navController = rememberNavController()
                    val authState by authViewModel.authState.collectAsState()
                    val startDestination = when (authState) { is AuthViewModel.AuthState.Authenticated -> "dashboard"; else -> "login" }
                    NavHost(navController = navController, startDestination = startDestination) {
                        composable("login") { LoginScreen(viewModel = authViewModel, onLoginSuccess = { navController.navigate("dashboard") { popUpTo("login") { inclusive = true } } }, onNavigateToRegister = { navController.navigate("register") }) }
                        composable("register") { RegisterScreen(viewModel = authViewModel, onRegisterSuccess = { navController.navigate("dashboard") { popUpTo("register") { inclusive = true } } }, onNavigateToLogin = { navController.popBackStack() }) }
                        composable("dashboard") { DashboardScreen(onNavigateToVault = { navController.navigate("vault") }) }
                        composable("vault") { VaultScreen(viewModel = vaultViewModel, onBack = { navController.popBackStack() }) }
                    }
                }
            }
        }
    }
}
