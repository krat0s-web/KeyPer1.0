"""
Module pour les appels API externes (météo, etc.)
"""
import requests
from django.conf import settings

def get_weather_data(city):
    """
    Récupère les données météo pour une ville via OpenWeatherMap API.
    
    Args:
        city (str): Nom de la ville
        
    Returns:
        dict: Données météo formatées ou None en cas d'erreur
    """
    api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
    api_url = getattr(settings, 'OPENWEATHERMAP_URL', 'http://api.openweathermap.org/data/2.5/weather')
    
    if not api_key:
        return None
    
    try:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',  # Température en Celsius
            'lang': 'fr'  # Langue française
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Formater les données pour le template
        weather_data = {
            'city': data.get('name', city),
            'temp': int(data['main']['temp']),
            'temp_min': int(data['main']['temp_min']),
            'temp_max': int(data['main']['temp_max']),
            'description': data['weather'][0]['description'].capitalize(),
            'main': data['weather'][0]['main'],  # État principal (Rain, Clear, etc.)
            'icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
        }
        
        return weather_data
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur API météo: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Erreur format données météo: {e}")
        return None

