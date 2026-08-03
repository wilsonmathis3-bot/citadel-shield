package com.boscs.citadel.ui.vault
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import com.boscs.citadel.data.model.VaultEntry
import com.boscs.citadel.viewmodel.VaultViewModel
import java.util.UUID

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VaultScreen(viewModel: VaultViewModel, onBack: () -> Unit) {
    val entries by viewModel.entries.collectAsState(initial = emptyList())
    var showAddDialog by remember { mutableStateOf(false) }
    val clipboard = LocalClipboardManager.current
    Scaffold(topBar = { TopAppBar(title = { Text("Password Vault") }, navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") } }, actions = { IconButton(onClick = { showAddDialog = true }) { Icon(Icons.Default.Add, "Add") } }) }) { padding ->
        LazyColumn(modifier = Modifier.fillMaxSize().padding(padding)) {
            items(entries) { entry ->
                VaultEntryCard(entry = entry, onCopyPassword = { clipboard.setText(AnnotatedString("••••••••")) }, onDelete = { viewModel.deleteEntry(entry) })
            }
        }
        if (showAddDialog) {
            AddEntryDialog(onDismiss = { showAddDialog = false }, onConfirm = { service, user, pass -> viewModel.addEntry(service, user, pass); showAddDialog = false })
        }
    }
}

@Composable
fun VaultEntryCard(entry: VaultEntry, onCopyPassword: () -> Unit, onDelete: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
        Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(1f)) {
                Text(text = entry.serviceName, style = MaterialTheme.typography.titleMedium)
                Text(text = entry.username, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Row {
                IconButton(onClick = onCopyPassword) { Icon(Icons.Default.ContentCopy, "Copy") }
                IconButton(onClick = onDelete) { Icon(Icons.Default.Delete, "Delete", tint = MaterialTheme.colorScheme.error) }
            }
        }
    }
}

@Composable
fun AddEntryDialog(onDismiss: () -> Unit, onConfirm: (String, String, String) -> Unit) {
    var service by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    AlertDialog(onDismissRequest = onDismiss, title = { Text("Add Password") }, text = {
        Column {
            OutlinedTextField(value = service, onValueChange = { service = it }, label = { Text("Service") })
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(value = username, onValueChange = { username = it }, label = { Text("Username") })
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(value = password, onValueChange = { password = it }, label = { Text("Password") })
        }
    }, confirmButton = { TextButton(onClick = { onConfirm(service, username, password) }) { Text("Save") } }, dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } })
}
