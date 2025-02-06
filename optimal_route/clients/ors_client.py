import requests
from rest_framework.response import Response
import os

class OrsClient:
    def __init__(self):
        self.api_url = f"https://api.openrouteservice.org/v2/directions/driving-car"
        self.ORS_API_KEY = os.getenv("ORS_API_KEY")

    def get_route(self, start: str, finish:str) -> dict:
        headers = {
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        }
        params = {"api_key": self.ORS_API_KEY, "start": start, "end": finish}
        response = requests.get(self.api_url, params=params, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Failed to fetch route data"}, status=500)
        route_data = response.json()
        return route_data
