import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city_name):
    try:
        params = {"name": city_name, "count": 1, "language": "es", "format": "json"}
        response = requests.get(GEOCODING_URL, params=params)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "success": True,
                "city": result["name"],
                "country": result.get("country", ""),
                "latitude": result["latitude"],
                "longitude": result["longitude"]
            }
        return {"success": False, "error": "Ciudad no encontrada"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_weather(latitude, longitude):
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,apparent_temperature,uv_index,precipitation,surface_pressure,is_day",
            "timezone": "auto"
        }
        response = requests.get(WEATHER_URL, params=params)
        data = response.json()
        
        if "current" in data:
            current = data["current"]
            return {
                "success": True,
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "wind_direction": current["wind_direction_10m"],
                "apparent_temperature": current["apparent_temperature"],
                "uv_index": current["uv_index"],
                "precipitation": current["precipitation"],
                "pressure": current["surface_pressure"],
                "weather_code": current["weather_code"],
                "is_day": current["is_day"],
                "time": current["time"]
            }
        return {"success": False, "error": "No se pudo obtener el clima"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_weather_by_city(city_name):
    coords = get_coordinates(city_name)
    if not coords["success"]:
        return coords
    
    weather = get_current_weather(coords["latitude"], coords["longitude"])
    if not weather["success"]:
        return weather
    
    return {
        "success": True,
        "city": coords["city"],
        "country": coords["country"],
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "wind_direction": weather["wind_direction"],
        "apparent_temperature": weather["apparent_temperature"],
        "uv_index": weather["uv_index"],
        "precipitation": weather["precipitation"],
        "pressure": weather["pressure"],
        "weather_code": weather["weather_code"],
        "is_day": weather["is_day"],
        "time": weather["time"]
    }


def get_forecast(latitude, longitude, start_date=None, days=7):
    try:
        from datetime import datetime, timedelta
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = start + timedelta(days=days - 1)
            end_date = end.strftime("%Y-%m-%d")
            
            today = datetime.now().date()
            start_d = start.date()
            
            if start_d < today:
                api_url = "https://archive-api.open-meteo.com/v1/archive"
            else:
                api_url = WEATHER_URL
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
                "timezone": "auto",
                "start_date": start_date,
                "end_date": end_date
            }
        else:
            api_url = WEATHER_URL
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": days
            }
        
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if "daily" in data:
            daily = data["daily"]
            forecast = []
            
            for i in range(len(daily["time"])):
                precip = None
                if "precipitation_probability_max" in daily and daily["precipitation_probability_max"]:
                    precip = daily["precipitation_probability_max"][i]
                
                forecast.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "weather_code": daily["weather_code"][i],
                    "precipitation": precip if precip is not None else 0
                })
            
            return {"success": True, "forecast": forecast}
        return {"success": False, "error": "No se pudo obtener el pronóstico"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_forecast_by_city(city_name, days=7, start_date=None):
    coords = get_coordinates(city_name)
    if not coords["success"]:
        return coords
    
    forecast = get_forecast(coords["latitude"], coords["longitude"], start_date, days)
    if not forecast["success"]:
        return forecast
    
    return {
        "success": True,
        "city": coords["city"],
        "country": coords["country"],
        "forecast": forecast["forecast"]
    }


def get_recommendation(temperature, humidity, wind_speed, weather_code, precipitation):
    recommendations = []
    
    if temperature < 10:
        recommendations.append("🧥 Hace frío, abrígate bien")
    elif temperature > 30:
        recommendations.append("🌡️ Mucho calor, mantente hidratado")
    
    if precipitation > 60:
        recommendations.append("☔ Alta probabilidad de lluvia, lleva paraguas")
    
    if humidity > 80:
        recommendations.append("💧 Humedad alta, puede sentirse bochornoso")
    
    if wind_speed > 40:
        recommendations.append("💨 Vientos fuertes, ten precaución")
    
    if weather_code in [0, 1]:
        recommendations.append("☀️ Día despejado, ideal para actividades al aire libre")
    
    if not recommendations:
        recommendations.append("✅ Condiciones normales")
    
    return " | ".join(recommendations)

def get_hourly_forecast(latitude, longitude, date):
    try:
        from datetime import datetime
        
        today = datetime.now().date()
        selected = datetime.strptime(date, "%Y-%m-%d").date()
        
        if selected < today:
            api_url = "https://archive-api.open-meteo.com/v1/archive"
            hourly_params = "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation"
        else:
            api_url = WEATHER_URL
            hourly_params = "temperature_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m,wind_direction_10m,uv_index"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": hourly_params,
            "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,wind_speed_10m_max",
            "timezone": "auto",
            "start_date": date,
            "end_date": date
        }
        
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if "hourly" not in data:
            return {"success": False, "error": "No se pudo obtener el pronóstico por horas"}
        
        hourly = data["hourly"]
        daily = data.get("daily", {})
        
        hours = []
        for i in range(len(hourly["time"])):
            hour_data = {
                "time": hourly["time"][i],
                "temperature": hourly["temperature_2m"][i],
                "apparent_temperature": hourly["apparent_temperature"][i],
                "weather_code": hourly["weather_code"][i],
                "wind_speed": hourly["wind_speed_10m"][i],
                "wind_direction": hourly["wind_direction_10m"][i],
            }
            if "precipitation_probability" in hourly:
                hour_data["precipitation_probability"] = hourly["precipitation_probability"][i]
            else:
                hour_data["precipitation_probability"] = 0
            if "uv_index" in hourly:
                hour_data["uv_index"] = hourly["uv_index"][i]
            else:
                hour_data["uv_index"] = 0
            hours.append(hour_data)
        
        summary = {}
        if daily:
            summary = {
                "sunrise": daily.get("sunrise", [None])[0],
                "sunset": daily.get("sunset", [None])[0],
                "temp_max": daily.get("temperature_2m_max", [None])[0],
                "temp_min": daily.get("temperature_2m_min", [None])[0],
                "precipitation_max": daily.get("precipitation_probability_max", [None])[0],
                "uv_max": daily.get("uv_index_max", [None])[0],
                "wind_max": daily.get("wind_speed_10m_max", [None])[0],
            }
        
        return {"success": True, "hours": hours, "summary": summary}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_hourly_forecast_by_city(city_name, date):
    coords = get_coordinates(city_name)
    if not coords["success"]:
        return coords
    
    result = get_hourly_forecast(coords["latitude"], coords["longitude"], date)
    if not result["success"]:
        return result

    return {
        "success": True,
        "city": coords["city"],
        "country": coords["country"],
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "hours": result["hours"],
        "summary": result["summary"]
    }

if __name__ == "__main__":
    result = get_weather_by_city("Bogotá")
    print(result)