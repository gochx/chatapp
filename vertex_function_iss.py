import vertexai

from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
import requests
from datetime import datetime

# Initialize Vertex AI
vertexai.init(project="vertex2025", location="us-central1")

# Initialize Gemini model
model = GenerativeModel("gemini-1.5-flash-002")

# Define the user's prompt in a Content object that we can reuse in model calls
user_prompt_content = Content(
    role="user",
    parts=[
        Part.from_text("What is the current Position of the ISS?"),
    ],
)

# Specify a function declaration and parameters for an API request
function_name = "get_current_weather"
get_current_weather_func = FunctionDeclaration(
    name=function_name,
    description="Get the current weather in a given location",
    # Function parameters are specified in JSON schema format
    parameters={
        "type": "object",
        "properties": {"location": {"type": "string", "description": "Location"}},
    },
)

# Funktion zur API-Abfrage (Alternative API für ISS-Position)
def get_iss_position():
    url = "https://api.wheretheiss.at/v1/satellites/25544"  # Alternative API, da Open Notify unzuverlässig ist
    try:
        response = requests.get(url, timeout=10)  # Timeout für Stabilität setzen
        response.raise_for_status()  # Hebt HTTP-Fehler hervor

        data = response.json()
        latitude = data["latitude"]
        longitude = data["longitude"]
        timestamp = datetime.utcfromtimestamp(data["timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC')

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Fehler beim Abrufen der Positionsdaten für die ISS: {str(e)}"}

# Specify a function declaration and parameters for an API request
get_current_iss = FunctionDeclaration(
    name="get_iss_position",
    description="Get the current position of the ISS",
    # Function parameters are specified in JSON schema format
    parameters={
        "type": "object",  # Explizit als leeres Objekt definieren
        "properties": {}
    },
)



# Define a tool that includes the above get_current_weather_func
weather_tool = Tool(
    function_declarations=[get_current_weather_func],
)

iss_tool = Tool(
    function_declarations=[get_current_iss],
)

# Send the prompt and instruct the model to generate content using the Tool that you just created
response = model.generate_content(
    user_prompt_content,
    generation_config=GenerationConfig(temperature=0),
    tools=[iss_tool],
)
function_call = response.candidates[0].function_calls[0]
print(function_call)

# Check the function name that the model responded with, and make an API call to an external system
# Check the function name that the model responded with, and make an API call to an external system
if function_call.name == "get_iss_position":  # Stelle sicher, dass du den richtigen Funktionsnamen verwendest
    api_response = get_iss_position()  # Rufe die API auf, um die ISS-Position zu bekommen
elif function_call.name == "get_current_weather":
    location = function_call.args["location"]  # Hier wird der Location-Parameter für Wetterabfragen genutzt
    api_response = """{ "location": "Boston, MA", "temperature": 38, "description": "Partly Cloudy",
                        "icon": "partly-cloudy", "humidity": 65, "wind": { "speed": 10, "direction": "NW" } }"""
else:
    api_response = {"error": "Unknown function call"}

# Wähle das richtige Tool basierend auf der aufgerufenen Funktion
selected_tool = iss_tool if function_call.name == "get_iss_position" else weather_tool

# Rückgabe der API-Daten an Gemini
response = model.generate_content(
    [
        user_prompt_content,  # User prompt
        response.candidates[0].content,  # Function call response
        Content(
            parts=[
                Part.from_function_response(
                    name=function_call.name,  # Dynamisch den Namen der Funktion setzen
                    response=api_response,  # API-Response übergeben
                ),
            ],
        ),
    ],
    tools=[selected_tool],  # Nur das relevante Tool übergeben
)

# Get the model response
print(response.text)

# Get the model response
print(response.text)
