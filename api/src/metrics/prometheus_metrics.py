"""
Métriques Prometheus personnalisées pour CY Weather API
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info as MetricInfo
from functools import wraps
import time

# ============================================================================
# COMPTEURS - Pour suivre le nombre total d'événements
# ============================================================================

# Compteur des requêtes météo par ville
weather_requests_total = Counter(
    "cy_weather_requests_total",
    "Nombre total de requêtes météo",
    ["endpoint", "city", "status"]
)

# Compteur des erreurs API externe (Open-Meteo)
external_api_errors_total = Counter(
    "cy_weather_external_api_errors_total",
    "Nombre total d'erreurs lors des appels à l'API externe",
    ["api_name", "error_type"]
)

# Compteur des requêtes par code HTTP
http_requests_by_status = Counter(
    "cy_weather_http_requests_by_status_total",
    "Nombre de requêtes HTTP par code de statut",
    ["method", "endpoint", "status_code"]
)

# ============================================================================
# HISTOGRAMMES - Pour mesurer les distributions (temps de réponse, etc.)
# ============================================================================

# Temps de réponse pour les requêtes météo
weather_request_duration = Histogram(
    "cy_weather_request_duration_seconds",
    "Durée des requêtes météo en secondes",
    ["endpoint", "city"],
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0]
)

# Temps de réponse pour les appels à l'API externe
external_api_duration = Histogram(
    "cy_weather_external_api_duration_seconds",
    "Durée des appels à l'API externe en secondes",
    ["api_name", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# ============================================================================
# JAUGES - Pour les valeurs qui peuvent monter et descendre
# ============================================================================

# Température actuelle par ville (dernière valeur récupérée)
current_temperature = Gauge(
    "cy_weather_current_temperature_celsius",
    "Température actuelle en degrés Celsius",
    ["city", "country"]
)

# Humidité actuelle par ville
current_humidity = Gauge(
    "cy_weather_current_humidity_percent",
    "Humidité actuelle en pourcentage",
    ["city", "country"]
)

# Nombre de villes actuellement suivies
cities_tracked = Gauge(
    "cy_weather_cities_tracked",
    "Nombre de villes pour lesquelles des données ont été récupérées"
)

# ============================================================================
# INFO - Métadonnées sur l'application
# ============================================================================

app_info = Info(
    "cy_weather_app",
    "Informations sur l'application CY Weather"
)

# Initialisation des infos de l'application
app_info.info({
    "version": "0.1.0",
    "api_provider": "open-meteo",
    "description": "CY Weather API - Application météo"
})

# ============================================================================
# FONCTIONS UTILITAIRES POUR LE TRACKING
# ============================================================================

# Set pour garder trace des villes uniques
_tracked_cities = set()


def track_weather_request(endpoint: str, city: str, status: str = "success"):
    """Enregistre une requête météo"""
    weather_requests_total.labels(endpoint=endpoint, city=city.lower(), status=status).inc()


def track_external_api_error(api_name: str, error_type: str):
    """Enregistre une erreur d'API externe"""
    external_api_errors_total.labels(api_name=api_name, error_type=error_type).inc()


def track_http_request(method: str, endpoint: str, status_code: int):
    """Enregistre une requête HTTP"""
    http_requests_by_status.labels(
        method=method, 
        endpoint=endpoint, 
        status_code=str(status_code)
    ).inc()


def update_weather_metrics(city: str, country: str, temperature: float, humidity: int):
    """Met à jour les métriques météo pour une ville"""
    city_lower = city.lower()
    country_upper = country.upper() if country else "UNKNOWN"
    
    current_temperature.labels(city=city_lower, country=country_upper).set(temperature)
    current_humidity.labels(city=city_lower, country=country_upper).set(humidity)
    
    # Tracker les villes uniques
    _tracked_cities.add(city_lower)
    cities_tracked.set(len(_tracked_cities))


class MetricsTimer:
    """Context manager pour mesurer le temps d'exécution"""
    
    def __init__(self, histogram, labels: dict):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.histogram.labels(**self.labels).observe(duration)
        return False


def time_weather_request(endpoint: str, city: str):
    """Timer pour les requêtes météo"""
    return MetricsTimer(weather_request_duration, {"endpoint": endpoint, "city": city.lower()})


def time_external_api_call(api_name: str, endpoint: str):
    """Timer pour les appels API externes"""
    return MetricsTimer(external_api_duration, {"api_name": api_name, "endpoint": endpoint})


# ============================================================================
# CONFIGURATION DE L'INSTRUMENTATOR FASTAPI
# ============================================================================

def create_instrumentator() -> Instrumentator:
    """Crée et configure l'instrumentator Prometheus pour FastAPI"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/api/health"],
        inprogress_name="cy_weather_http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Ajouter les métriques par défaut
    instrumentator.add(
        default_metrics()
    )
    
    return instrumentator


def default_metrics() -> callable:
    """Retourne une fonction qui ajoute des métriques par défaut"""
    def instrumentation(info: MetricInfo) -> None:
        # Les métriques par défaut sont automatiquement ajoutées
        pass
    return instrumentation
