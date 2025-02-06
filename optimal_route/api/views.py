from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.route import lvs_to_la # used for tests
from utils.route_2 import la_to_ny  # used for tests

from managers.route_manager import RouteManager
from clients.ors_client import OrsClient
import time

@api_view(["GET"])
def get_route(request):
    """API endpoint to get the best route with fuel stops."""
    start = request.GET.get("start")
    finish = request.GET.get("finish")

    if not start or not finish:
        return Response({"error": "Start and finish locations are required"}, status=400)

    api_start_time = time.time()
    ors_client = OrsClient()
    route_data = ors_client.get_route(start,finish)
    api_end_time = time.time()

    calc_start_time = time.time()
    route_manager = RouteManager()
    data = route_manager.calc_optimized_route(route_data)
    calc_end_time = time.time()

    api_runtime = api_end_time - api_start_time
    calc_runtime = calc_end_time - calc_start_time
    print(f"api_runtime: {api_runtime:.6f} seconds")
    print(f"calc_runtime: {calc_runtime:.6f} seconds")
    response = {**data,"api_runtime":api_runtime,'calc_runtime':calc_runtime}
    return Response(response)
