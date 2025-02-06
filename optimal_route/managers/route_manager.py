import math
from utils.kd import find_optimized_fuel_station

class RouteManager:

    def __init__(self):
        self.CAR_FUEL_CONSUMPTION = 4251.44  # m per Liter  (e.g. 10 miles per gallon)
        self.TANK_CAPACITY = (
            189.271  # Full tank capacity in liters (e.g maximum range of 500 miles with 10 miles per gallon)
        )
        self.START_FUEL_LEVEL = 180  # Current fuel level in tank in liters
        self.FUEL_RESERVE_THRESHOLD = 20  # Minimum fuel volume in liters before looking for gas station

    def haversine_distance(self, point1, point2)->float:
        """Calculate the distance in m between two lat/lon points."""
        # Radius of the Earth in kilometers
        lon1, lat1, lon2, lat2 = point1[0], point1[1], point2[0], point2[1]
        R = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Differences between latitudes and longitudes
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in meters
        distance = R * c * 1000
        return distance

    def usd_per_gallon_to_liter(self, price_per_gallon:float)->float:
        """Convert USD per gallon to USD per liter"""
        liters_per_gallon = 3.78541  # 1 gallon = 3.78541 liters
        price_per_liter = price_per_gallon / liters_per_gallon
        return price_per_liter

    def calc_fuel_consumption(self, distance:float)->float:
        return distance / self.CAR_FUEL_CONSUMPTION

    def refuel_full_tank(self, gas_price_per_gallon: float):
        gas_price_per_liter = self.usd_per_gallon_to_liter(gas_price_per_gallon)
        self.total_cost += gas_price_per_liter * (self.TANK_CAPACITY - self.current_fuel)
        self.current_fuel = self.TANK_CAPACITY

    def drive(self, distance):
        fuel_consumption = self.calc_fuel_consumption(distance)
        self.current_fuel -= fuel_consumption

    def find_fuel_station_and_refuel(self, current_point):
        car_lat, car_lon = current_point[1], current_point[0]
        best_station = find_optimized_fuel_station((car_lat, car_lon), self.look_radius_m)
        gas_price_per_gallon = best_station[2]
        gs_lat, gs_lon = best_station[1], best_station[0]
        gas_station_point = (gs_lat, gs_lon)
        self.best_gas_stations.append(gas_station_point)

        distance_to_fuel_station = self.haversine_distance(current_point, gas_station_point)
        # drive to gas station
        self.drive(distance_to_fuel_station)
        # refuel
        self.refuel_full_tank(gas_price_per_gallon)
        # drive back from gas station
        self.drive(distance_to_fuel_station)

    def calc_optimized_route(self, route_data):
        route_steps = route_data["features"][0]["properties"]["segments"][0]["steps"]
        route_way_points = route_data["features"][0]["geometry"]["coordinates"]
        self.total_cost = 0
        self.best_gas_stations = []
        self.current_fuel = self.START_FUEL_LEVEL
        self.look_radius_m = self.FUEL_RESERVE_THRESHOLD * self.CAR_FUEL_CONSUMPTION

        for step in route_steps:
            step_distance = step["distance"]
            step_fuel_consumption = self.calc_fuel_consumption(step_distance)
            # if dont have enough fuel for the whole step
            if self.current_fuel - step_fuel_consumption < self.FUEL_RESERVE_THRESHOLD:
                start_index = step["way_points"][0]
                current_index = start_index
                end_index = step["way_points"][1]

                current_point = route_way_points[current_index]
                next_point = route_way_points[current_index + 1]
                dist_to_next_point = self.haversine_distance(current_point, next_point)
                while current_index <= end_index:
                    dist_to_next_point = self.haversine_distance(current_point, next_point)
                    self.drive(dist_to_next_point)
                    if self.current_fuel < self.FUEL_RESERVE_THRESHOLD:
                        self.find_fuel_station_and_refuel(current_point)
                    current_point = next_point
                    current_index += 1
                    next_point = route_way_points[current_index]
            else:
                self.drive(step_distance)
        return {"total_cost": self.total_cost, 
                "best_gas_stations": self.best_gas_stations,
                "route_steps": route_steps,
                "route_way_points":route_way_points}
