"""
Weather API Tool
Provides access to current weather information
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from time import sleep

logger = logging.getLogger(__name__)


class WeatherTool:
    """
    Wrapper for OpenWeatherMap API
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Weather API client
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            logger.warning("Weather API key not found - API calls will fail")
        else:
            logger.info("Weather API initialized")
    
    def get_weather(
        self, 
        city: str, 
        units: str = "metric",
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Get current weather for a city
        
        Args:
            city: City name (e.g., "Bangalore", "New York")
            units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
            retry_count: Number of retries on failure
            
        Returns:
            Weather information dictionary
        """
        if not self.api_key:
            return self._fallback_response("API key not configured")
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Fetching weather for: {city}")
                response = requests.get(self.BASE_URL, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    weather_data = {
                        "city": data.get("name"),
                        "country": data.get("sys", {}).get("country"),
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "condition": data.get("weather", [{}])[0].get("main", "Unknown"),
                        "description": data.get("weather", [{}])[0].get("description", ""),
                        "humidity": data.get("main", {}).get("humidity"),
                        "pressure": data.get("main", {}).get("pressure"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "units": "°C" if units == "metric" else "°F"
                    }
                    
                    logger.info(f"Weather fetched: {weather_data['city']}, {weather_data['temperature']}{weather_data['units']}")
                    return weather_data
                    
                elif response.status_code == 404:
                    logger.error(f"City not found: {city}")
                    return self._fallback_response(f"City '{city}' not found")
                    
                elif response.status_code == 401:
                    logger.error("Invalid Weather API key")
                    return self._fallback_response("Invalid API key")
                    
                else:
                    logger.error(f"Weather API error: {response.status_code} - {response.text}")
                    if attempt < retry_count - 1:
                        sleep(1)
                        continue
                    return self._fallback_response(f"API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"Weather API timeout (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    sleep(1)
                    continue
                return self._fallback_response("Request timeout")
                
            except Exception as e:
                logger.error(f"Weather API request failed: {e}")
                if attempt < retry_count - 1:
                    sleep(1)
                    continue
                return self._fallback_response(str(e))
        
        return self._fallback_response("Max retries exceeded")
    
    def get_weather_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast (requires different API endpoint)
        
        Args:
            city: City name
            days: Number of days (max 5 for free tier)
            
        Returns:
            Forecast data
        """
        # This would require the forecast API endpoint
        # Placeholder for future implementation
        logger.info(f"Forecast API not implemented yet for {city}")
        return {
            "city": city,
            "forecast": [],
            "error": "Forecast not implemented"
        }
    
    def _fallback_response(self, error_msg: str) -> Dict[str, Any]:
        """Return partial/error response"""
        return {
            "city": "Unknown",
            "temperature": None,
            "condition": "Error",
            "description": error_msg,
            "humidity": None,
            "error": True
        }
