package com.boscs.citadel.ui.dashboard
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.boscs.citadel.ui.components.ShieldState
import com.boscs.citadel.ui.components.ShieldStatus
import com.boscs.citadel.data.api.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(onNavigateToVault: () -> Unit) {
    val scope = rememberCoroutineScope()
    var urlToCheck by remember { mutableStateOf("") }
    var scanResult by remember { mutableStateOf<String?>(null) }
    var isScanning by remember { mutableStateOf(false) }
    Scaffold(topBar = { TopAppBar(title = { Text("CITADEL") }, colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) }) { padding ->
        LazyColumn(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            item { ShieldStatus(state = ShieldState.Secure, score = 97, modifier = Modifier.fillMaxWidth()) }
            item {
                Spacer(modifier = Modifier.height(24.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                    QuickActionButton(icon = Icons.Default.Lock, label = "Vault", onClick = onNavigateToVault)
                    QuickActionButton(icon = Icons.Default.Shield, label = "Scan", onClick = {})
                    QuickActionButton(icon = Icons.Default.VpnKey, label = "VPN", onClick = {})
                }
            }
            item {
                Spacer(modifier = Modifier.height(32.dp))
                Text(text = "Link Scanner", style = MaterialTheme.typography.titleLarge)
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(value = urlToCheck, onValueChange = { urlToCheck = it }, label = { Text("Paste suspicious link") }, modifier = Modifier.fillMaxWidth(), trailingIcon = {
                    IconButton(onClick = {
                        scope.launch {
                            isScanning = true
                            try {
                                val result = apiService.checkUrl(URLCheckRequest(urlToCheck))
                                scanResult = if (result.safe) "✅ SAFE: ${result.reasons.firstOrNull() ?: "No threats"}" else "🚨 DANGER (Score: ${result.score}): ${result.reasons.joinToString()}"
                            } catch (e: Exception) { scanResult = "Error: ${e.message}" }
                            isScanning = false
                        }
                    }, enabled = urlToCheck.isNotBlank() && !isScanning) { Icon(Icons.Default.Search, "Scan") }
                })
                if (isScanning) CircularProgressIndicator(modifier = Modifier.padding(16.dp))
                scanResult?.let {
                    Card(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), colors = CardDefaults.cardColors(containerColor = if (it.contains("SAFE")) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.errorContainer)) {
                        Text(text = it, modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.bodyLarge)
                    }
                }
            }
        }
    }
}

@Composable
fun QuickActionButton(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, onClick: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        FilledIconButton(onClick = onClick, modifier = Modifier.size(64.dp)) { Icon(icon, label, modifier = Modifier.size(32.dp)) }
        Spacer(modifier = Modifier.height(4.dp))
        Text(label, style = MaterialTheme.typography.labelMedium)
    }
}
