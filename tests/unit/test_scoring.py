from app.core.scoring.rules import fast_score


def test_call_forwarding_triggers_hold() -> None:
    result = fast_score({"call_forwarding_active": True})
    assert result is not None
    assert result["risk_score"] == 95
    assert result["recommended_action"] == "HOLD"
    assert result["fast_path"] is True


def test_sim_plus_device_swap_triggers_hold() -> None:
    result = fast_score({"sim_swapped_recent": True, "device_swapped": True})
    assert result is not None
    assert result["risk_score"] == 92
    assert result["recommended_action"] == "HOLD"


def test_number_recycled_triggers_hold() -> None:
    result = fast_score({"number_recycled": True})
    assert result is not None
    assert result["risk_score"] == 88


def test_clean_signals_pass_to_ai() -> None:
    signals = {
        k: False
        for k in [
            "call_forwarding_active",
            "sim_swapped_recent",
            "device_swapped",
            "number_recycled",
            "number_verification_failed",
        ]
    }
    assert fast_score(signals) is None


def test_partial_signals_no_fast_path() -> None:
    result = fast_score({"sim_swapped_recent": True, "device_swapped": False})
    assert result is None  # only sim swap alone doesn't trigger fast path
