import numpy as np
from utils.stations import stations_points
from sklearn.neighbors import BallTree

def find_optimized_fuel_station(current_point, look_radius_m):
    # List of fuel stations (latitude, longitude, price per gallon)
    stations = stations_points

    # Extract coordinates and prices separately
    station_coords = [(lat, lon) for lat, lon, _ in stations]
    station_prices = [price for _, _, price in stations]

    # Convert coordinates to radians for BallTree
    stations_rad = np.radians(station_coords)

    # Build BallTree
    tree = BallTree(stations_rad, metric="haversine")

    # Current location - converted to radians
    current_location = np.radians([current_point])  #

    # Define the search radius (in km)
    radius_km = look_radius_m / 1000
    radius_rad = radius_km / 6371.0  # Convert km to radians
    
    # Query the tree for stations within the radius
    indices = tree.query_radius(current_location, r=radius_rad)[0]

    # Get nearby stations, distances, and prices
    nearby_stations = [stations[i] for i in indices]
    nearby_prices = [station_prices[i] for i in indices]

    # Compute actual Haversine distances (in km)
    distances = [tree.query([stations_rad[i]], k=1)[0][0][0] * 6371 for i in indices]

    # Weights for price and distance
    alpha = 1.0  # Weight for price (adjust this)
    beta = 0.1  # Weight for distance (adjust this)

    # Compute scores: lower score is better
    scores = [alpha * price + beta * distance for price, distance in zip(nearby_prices, distances)]

    # Find the best station (lowest score)
    best_index = np.argmin(scores)
    best_station = nearby_stations[best_index]

    return best_station
