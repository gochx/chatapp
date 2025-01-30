import google.generativeai as genai
import requests
import json

# Set up Gemini API Key (ersetze 'YOUR_GEMINI_API_KEY' mit deinem tatsächlichen API-Schlüssel)
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def get_weather(city: str):
    """Ruft die Wetterdaten für eine gegebene Stadt von einer freien API ab."""
    api_key = "YOUR_WEATHER_API_KEY"  # Ersetze mit deinem API-Schlüssel
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Das Wetter in {city}: {data['weather'][0]['description']}, Temperatur: {data['main']['temp']}°C"
    else:
        return f"Fehler beim Abrufen der Wetterdaten für {city}."

# Definition der Funktion für Gemini Function Calling
function_definition = {
    "name": "get_weather",
    "description": "Get weather information for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Name of the city to get the weather for."}
        },
        "required": ["city"]
    }
}

# Gemini Model mit Function Calling
model = genai.GenerativeModel(model_name="gemini-pro",
                              tools=[{"type": "function", "function": function_definition}])

# Anfrage an Gemini mit Function Calling
response = model.generate_content("Gib mir das aktuelle Wetter für Berlin.", tool_config={"function_calling": "auto"})

# Ausgabe des Ergebnisses
print(response.text)