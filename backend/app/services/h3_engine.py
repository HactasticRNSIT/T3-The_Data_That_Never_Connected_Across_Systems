import h3
import math
from datetime import datetime

def bin_to_hex(lat: float, lon: float, resolution: int = 9) -> str:
    return h3.latlng_to_cell(lat, lon, resolution)

def compute_risk_score(hex_signals: list[dict]) -> float:
    sector_weights = {
        "police": 0.40,
        "healthcare": 0.30,
        "transport": 0.15,
        "community": 0.15
    }
    raw_score = 0.0
    now = datetime.utcnow()
    
    for signal in hex_signals:
        # Time decay lambda = 0.15
        hours_elapsed = (now - signal['received_at']).total_seconds() / 3600
        recency_weight = math.exp(-0.15 * hours_elapsed)
        raw_score += float(signal["severity"]) * sector_weights.get(signal["sector"], 0.1) * recency_weight
    
    if raw_score == 0:
        return 0.0
        
    # Normalize to 0-10 scale with sigmoid smoothing
    normalized = 10 / (1 + math.exp(-5 * (raw_score - 0.5)))
    return round(normalized, 2)

def classify_tier(score: float) -> str:
    if score <= 2.5:
        return 'LOW'
    elif score <= 5.0:
        return 'MODERATE'
    elif score <= 7.5:
        return 'HIGH'
    else:
        return 'CRITICAL'
