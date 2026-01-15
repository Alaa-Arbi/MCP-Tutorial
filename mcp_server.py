from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from mcp.server.fastmcp.prompts import base

from pydantic import BaseModel, Field

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""

class Confirm(BaseModel):
    """Model for confirmation elicitation."""
    confirmed: bool = Field(..., description="Whether the user confirmed the action.")

@mcp.tool()
async def get_alerts(state: str, ctx: Context) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """

    result = await ctx.elicit(
        message=f"Do you want to fetch weather alerts for the state '{state}'? (yes/no)",
        schema=Confirm,
    )
    if isinstance(result, AcceptedElicitation):
        if result.data.confirmed is False:
            return "User declined to fetch alerts."
        else:   
            url = f"{NWS_API_BASE}/alerts/active/area/{state}"
            data = await make_nws_request(url)

            if not data or "features" not in data:
                return "Unable to fetch alerts or no alerts found."

            if not data["features"]:
                return "No active alerts for this state."

            alerts = [format_alert(feature) for feature in data["features"]]
            answer = "\n---\n".join(alerts)
    else:
        answer = "Operation cancelled by user."
    return answer


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.resource("config://weather/station/{station_id}/info")
async def get_station_info(station_id: str) -> str:
    """Get information about a weather station.
    """
    return f"Information for station {station_id} is currently unavailable."


@mcp.resource("config://weather/station_ids")
async def get_station_ids() -> str:
    """List all possible station IDs.
    """
    
    return """["STN001", "STN002", "STN003"]"""

@mcp.prompt()
async def weather_summary_prompt(city: str)->str:
    return f"You are a weather assistant. Use station data and weather tools to answer accurately. Provide a weather summary for {city} using tools like get_forecast and get_alert."

def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()