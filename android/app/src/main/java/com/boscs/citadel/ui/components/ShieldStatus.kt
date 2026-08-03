package com.boscs.citadel.ui.components
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

sealed class ShieldState { object Secure : ShieldState(); object Warning : ShieldState(); object Critical : ShieldState() }

@Composable
fun ShieldStatus(state: ShieldState, score: Int, modifier: Modifier = Modifier) {
    val color = when (state) { is ShieldState.Secure -> Color(0xFF00C853); is ShieldState.Warning -> Color(0xFFFFD600); is ShieldState.Critical -> Color(0xFFFF1744) }
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(initialValue = 1f, targetValue = 1.05f, animationSpec = infiniteRepeatable(animation = tween(2000, easing = FastOutSlowInEasing), repeatMode = RepeatMode.Reverse), label = "scale")
    Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = modifier.padding(24.dp)) {
        Box(modifier = Modifier.size(180.dp).scale(scale).background(brush = Brush.radialGradient(colors = listOf(color.copy(alpha = 0.3f), Color.Transparent)), shape = CircleShape), contentAlignment = Alignment.Center) {
            Box(modifier = Modifier.size(120.dp).background(color.copy(alpha = 0.2f), CircleShape), contentAlignment = Alignment.Center) {
                Text(text = "🛡️", fontSize = 64.sp)
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        Text(text = when (state) { is ShieldState.Secure -> "SECURE"; is ShieldState.Warning -> "CAUTION"; is ShieldState.Critical -> "THREAT DETECTED" }, fontSize = 28.sp, fontWeight = FontWeight.Bold, color = color)
        Text(text = "Score: $score/100", fontSize = 16.sp, color = Color.Gray)
    }
}
