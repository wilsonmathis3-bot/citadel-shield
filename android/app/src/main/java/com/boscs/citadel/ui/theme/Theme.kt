package com.boscs.citadel.ui.theme
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(primary = Color(0xFF00C853), secondary = Color(0xFF00B0FF), tertiary = Color(0xFFFFD600))
private val LightColorScheme = lightColorScheme(primary = Color(0xFF00C853), secondary = Color(0xFF00B0FF), tertiary = Color(0xFFFFD600))

@Composable
fun CitadelTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme, typography = Typography(), content = content)
}
