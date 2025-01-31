import vertexai
from vertexai.preview.generative_models import GenerativeModel, Tool
import requests

# Google Cloud-Projekt und Standort
PROJECT_ID = "your-google-cloud-project-id"
LOCATION = "us-central1"  # oder andere Region, falls konfiguriert

# Funktion zur API-Abfrage (z. B. OpenWeatherMap)
def get_weather(city: str):
    api_key = "YOUR_WEATHER_API_KEY"  # Ersetze mit deinem API-Schlüssel
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"Das Wetter in {city}: {data['weather'][0]['description']}, Temperatur: {data['main']['temp']}°C"
    else:
        return f"Fehler beim Abrufen der Wetterdaten für {city}."

# Definition der Funktion für Function Calling
weather_function = Tool(
    function_declarations=[
        {
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
    ]
)

# Initialisiere Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Lade das Gemini-Modell mit Function Calling
model = GenerativeModel("gemini-pro", tools=[weather_function])

# Anfrage an Gemini mit Function Calling
response = model.generate_content(
    "Gib mir das aktuelle Wetter für Berlin.", tool_config={"function_calling": "auto"}
)

# Ausgabe des Ergebnisses
print(response.text)
