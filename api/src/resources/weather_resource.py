import httpx
from fastapi import APIRouter, HTTPException, Query

from src.metrics.prometheus_metrics import (
    time_weather_request,
    track_external_api_error,
    track_weather_request,
    update_weather_metrics,
)
from src.models.Weather import ForecastResponse, WeatherResponse
from src.services.weather_service import weather_service

# Router pour les endpoints météo
router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    city: str = Query(..., description="Nom de la ville", min_length=1),
    country_code: str | None = Query(
        None, description="Code pays ISO (ex: FR, US)", max_length=2
    ),
):
    """
    Récupère la météo actuelle pour une ville donnée.

    Args:
        city: Nom de la ville
        country_code: Code pays ISO optionnel (ex: FR, US)

    Returns:
        WeatherResponse: Données météo actuelles avec température, humidité, etc.

    Raises:
        HTTPException: 404 si la ville n'est pas trouvée, 500 en cas d'erreur serveur
    """
    try:
        with time_weather_request("current", city):
            weather_data = await weather_service.get_current_weather(city, country_code)

        # Enregistrer les métriques de succès
        track_weather_request("current", city, "success")

        # Mettre à jour les métriques de température et humidité
        update_weather_metrics(
            city=weather_data.city,
            country=weather_data.country or "",
            temperature=weather_data.weather.temperature,
            humidity=weather_data.weather.humidity,
        )

        return weather_data
    except httpx.HTTPStatusError as e:
        track_weather_request("current", city, "error")
        track_external_api_error("open-meteo", "http_status_error")
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Ville '{city}' non trouvée. Vérifiez l'orthographe ou ajoutez le code pays.",
            ) from e
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erreur lors de la récupération des données météo: {str(e)}",
        ) from e
    except httpx.HTTPError as e:
        track_weather_request("current", city, "error")
        track_external_api_error("open-meteo", "connection_error")
        raise HTTPException(
            status_code=500, detail=f"Erreur de connexion à l'API météo: {str(e)}"
        ) from e
    except Exception as e:
        track_weather_request("current", city, "error")
        track_external_api_error("open-meteo", "unknown_error")
        raise HTTPException(
            status_code=500, detail=f"Erreur interne du serveur: {str(e)}"
        ) from e


@router.get("/forecast", response_model=ForecastResponse)
async def get_weather_forecast(
    city: str = Query(..., description="Nom de la ville", min_length=1),
    country_code: str | None = Query(
        None, description="Code pays ISO (ex: FR, US)", max_length=2
    ),
):
    """
    Récupère les prévisions météo sur 7 jours pour une ville donnée.

    Args:
        city: Nom de la ville
        country_code: Code pays ISO optionnel (ex: FR, US)

    Returns:
        ForecastResponse: Prévisions météo pour les 7 prochains jours avec températures min/max,
                         humidité, vitesse du vent, etc.

    Raises:
        HTTPException: 404 si la ville n'est pas trouvée, 500 en cas d'erreur serveur
    """
    try:
        with time_weather_request("forecast", city):
            forecast_data = await weather_service.get_forecast(city, country_code)

        # Enregistrer les métriques de succès
        track_weather_request("forecast", city, "success")

        return forecast_data
    except httpx.HTTPStatusError as e:
        track_weather_request("forecast", city, "error")
        track_external_api_error("open-meteo", "http_status_error")
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Ville '{city}' non trouvée. Vérifiez l'orthographe ou ajoutez le code pays.",
            ) from e
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erreur lors de la récupération des prévisions météo: {str(e)}",
        ) from e
    except httpx.HTTPError as e:
        track_weather_request("forecast", city, "error")
        track_external_api_error("open-meteo", "connection_error")
        raise HTTPException(
            status_code=500, detail=f"Erreur de connexion à l'API météo: {str(e)}"
        ) from e
    except Exception as e:
        track_weather_request("forecast", city, "error")
        track_external_api_error("open-meteo", "unknown_error")
        raise HTTPException(
            status_code=500, detail=f"Erreur interne du serveur: {str(e)}"
        ) from e
