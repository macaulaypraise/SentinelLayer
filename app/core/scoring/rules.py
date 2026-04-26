def fast_score(signals: dict) -> dict | None:
    """Short-circuit HOLD for definitive fraud signals. Returns None → AI scoring."""
    if signals.get("call_forwarding_active"):
        return {
            "risk_score": 95,
            "recommended_action": "HOLD",
            "fast_path": True,
            "trigger": "call_forwarding_active",
            "signal_drivers": ["call_forwarding_active"],
        }
    if signals.get("sim_swapped_recent") and signals.get("device_swapped"):
        return {
            "risk_score": 92,
            "recommended_action": "HOLD",
            "fast_path": True,
            "trigger": "sim_swap_plus_device_swap",
            "signal_drivers": ["sim_swapped_recent", "device_swapped"],
        }
    if signals.get("number_recycled"):
        return {
            "risk_score": 88,
            "recommended_action": "HOLD",
            "fast_path": True,
            "trigger": "number_recycled",
            "signal_drivers": ["number_recycled"],
        }
    if signals.get("number_verification_failed") and signals.get("sim_swapped_recent"):
        return {
            "risk_score": 85,
            "recommended_action": "HOLD",
            "fast_path": True,
            "trigger": "verification_plus_simswap",
            "signal_drivers": ["number_verification_failed", "sim_swapped_recent"],
        }
    return None
