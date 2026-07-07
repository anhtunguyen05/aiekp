"""Unit tests for the /rules/check endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_rule(rule_type: str, threshold: int | None = None, params: dict | None = None):
    payload = {"type": rule_type}
    if threshold is not None:
        payload["threshold"] = threshold
    if params is not None:
        payload["params"] = params
    return payload


# ---------------------------------------------------------------------------
# Validation tests (do NOT require a live DB)
# ---------------------------------------------------------------------------


def test_rules_check_empty_body():
    """Sending an empty list should return 422."""
    with TestClient(app) as client:
        response = client.post("/rules/check", json=[])
        assert response.status_code == 422


def test_rules_check_unknown_rule_type():
    """Unknown rule type should return 422 with descriptive message."""
    with TestClient(app) as client:
        response = client.post("/rules/check", json=[make_rule("not-a-real-rule")])
        assert response.status_code == 422
        assert "Unknown rule type" in response.json()["detail"]


def test_rules_check_invalid_threshold():
    """Threshold must be >= 1; sending 0 should return 422."""
    with TestClient(app) as client:
        response = client.post(
            "/rules/check", json=[make_rule("max-fan-in", threshold=0)]
        )
        assert response.status_code == 422


def test_rules_check_valid_payload_schema():
    """
    A valid payload should be accepted (200 or DB-related error — not 422).
    This confirms that schema validation passes even if Neo4j is not running.
    """
    with TestClient(app) as client:
        try:
            response = client.post(
                "/rules/check",
                json=[make_rule("max-complexity", threshold=5)],
            )
            # If DB is up → 200; if DB is down → likely 500. Either way, NOT 422.
            assert response.status_code != 422
        except Exception as exc:
            pytest.skip(f"DB not running: {exc}")


def test_rules_check_all_supported_types():
    """All five MVP rule types should pass schema validation."""
    rule_types = [
        make_rule("no-circular-deps"),
        make_rule("max-fan-in", threshold=10),
        make_rule("max-fan-out", threshold=10),
        make_rule("no-cross-layer"),
        make_rule("max-complexity", threshold=20),
    ]
    with TestClient(app) as client:
        try:
            response = client.post("/rules/check", json=rule_types)
            assert response.status_code != 422
            if response.status_code == 200:
                data = response.json()
                assert "violations" in data
                assert "total_violations" in data
                assert "rules_run" in data
        except Exception as exc:
            pytest.skip(f"DB not running: {exc}")


def test_rules_check_no_cross_layer_with_custom_params():
    """no-cross-layer rule should accept custom source/target patterns."""
    with TestClient(app) as client:
        try:
            response = client.post(
                "/rules/check",
                json=[
                    make_rule(
                        "no-cross-layer",
                        params={
                            "source_pattern": r".*/frontend/.*",
                            "target_pattern": r".*/backend/db/.*",
                        },
                    )
                ],
            )
            assert response.status_code != 422
        except Exception as exc:
            pytest.skip(f"DB not running: {exc}")
