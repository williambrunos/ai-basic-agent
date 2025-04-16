import requests


def check_weather(location: str) -> str:
    """
    Check the weather and temperature for a given location using public APIs.
    
    1. Faz uma requisição para a API do Nominatim (OpenStreetMap) para obter latitude e longitude.
    2. Usa essas coordenadas para consultar a API Open-Meteo e obter o clima atual.
    """
    geocode_url = "https://nominatim.openstreetmap.org/search"
    geocode_params = {
        "q": location,
        "format": "json",
        "limit": 1  
    }
    geocode_resp = requests.get(geocode_url, params=geocode_params, headers={"User-Agent": "Mozilla/5.0"})
    if geocode_resp.status_code != 200 or not geocode_resp.json():
        return f"Could not find location: {location}"
    geocode_data = geocode_resp.json()[0]
    lat = geocode_data["lat"]
    lon = geocode_data["lon"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true"
    }
    weather_resp = requests.get(weather_url, params=weather_params)
    if weather_resp.status_code != 200:
        return f"Failed to get weather data for {location}"
    
    weather_data = weather_resp.json()
    if "current_weather" not in weather_data:
        return f"No weather data available for {location}"
    
    current_weather = weather_data["current_weather"]
    temperature = current_weather.get("temperature")
    windspeed = current_weather.get("windspeed")
    weather_code = current_weather.get("weathercode")
    
    return (
        f"The weather in {location} is as follows: "
        f"Temperature: {temperature}°C, Wind Speed: {windspeed} km/h, "
        f"Weather Code: {weather_code}."
    )