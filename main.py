from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import AgentWorkflow, AgentStream, ToolCallResult
import asyncio
import yaml
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


def load_agent_config(yaml_path: str):
    """Load agent configuration from a YAML file."""
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


async def main():
    agent_config = load_agent_config("agent_config/agent_config.yaml")
    llm = Ollama(
        model=agent_config["llm"]["model"],
        temperature=agent_config["llm"].get("temperature", 0.7),
        request_timeout=agent_config["llm"].get("request_timeout", 60.0)
    )

    # Creating an agent with the check weather tool
    agent = AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[
            FunctionTool.from_defaults(
                name="check_weather",
                description="Checks weather for a specific location.",
                fn=check_weather
            )
        ],
        llm=llm,
        system_prompt=agent_config["prompt"]["system_prompt"]
    )
    handler = agent.run(user_msg="How is the weather in Sobral Ceará, Brazil right now?")
                              
    print("\n--- Agent Reasoning Trace ---")
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallResult):
            print("")
            print("Called tool: ", ev.tool_name, ev.tool_kwargs, "=>", ev.tool_output)
        elif isinstance(ev, AgentStream): 
            print(ev.delta, end="", flush=True)

    resp = await handler
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())
