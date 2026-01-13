"""Tests essentiels pour l'API CY Weather"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """Vérifie que l'API est en ligne"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint():
    """Vérifie que les métriques Prometheus sont exposées"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "python_info" in response.text


def test_current_weather_missing_city():
    """Vérifie la validation du paramètre city"""
    response = client.get("/api/weather/current")
    assert response.status_code == 422


def test_forecast_missing_city():
    """Vérifie la validation du paramètre city pour forecast"""
    response = client.get("/api/weather/forecast")
    assert response.status_code == 422
