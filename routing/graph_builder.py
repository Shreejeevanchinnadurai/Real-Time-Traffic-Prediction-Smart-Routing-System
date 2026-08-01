"""
Road Network Graph Builder
==========================
Builds a weighted NetworkX graph representing Chennai's road network.
Nodes are traffic locations (intersections/landmarks).
Edges are road segments with distance, speed limit, and capacity attributes.

Usage:
    from routing.graph_builder import build_road_graph, get_graph
"""

import networkx as nx
from typing import Dict, List, Optional, Tuple

from database.queries import get_all_locations
from utils.helpers import haversine_distance
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level graph cache
_road_graph: Optional[nx.DiGraph] = None


# ═══════════════════════════════════════════════════════════════════════
# ROAD NETWORK DEFINITION
# ═══════════════════════════════════════════════════════════════════════

# Road connections: (from_location, to_location, distance_km, speed_limit, capacity)
# These represent real Chennai road connections (approximate distances)
ROAD_SEGMENTS = [
    # OMR Corridor
    ("Sholinganallur", "Thiruvanmiyur", 6.5, 60, 600),
    ("Thiruvanmiyur", "Sholinganallur", 6.5, 60, 600),
    ("Thiruvanmiyur", "Adyar", 3.5, 50, 500),
    ("Adyar", "Thiruvanmiyur", 3.5, 50, 500),
    ("Thiruvanmiyur", "Besant Nagar", 2.0, 40, 350),
    ("Besant Nagar", "Thiruvanmiyur", 2.0, 40, 350),

    # Mount Road (Anna Salai) Corridor
    ("Guindy", "T. Nagar", 4.5, 50, 550),
    ("T. Nagar", "Guindy", 4.5, 50, 550),
    ("T. Nagar", "Nungambakkam", 2.5, 40, 400),
    ("Nungambakkam", "T. Nagar", 2.5, 40, 400),
    ("Nungambakkam", "Egmore", 2.0, 50, 500),
    ("Egmore", "Nungambakkam", 2.0, 50, 500),

    # GST Road Corridor
    ("Tambaram", "Chromepet", 5.0, 60, 550),
    ("Chromepet", "Tambaram", 5.0, 60, 550),
    ("Chromepet", "Pallavaram", 3.5, 50, 450),
    ("Pallavaram", "Chromepet", 3.5, 50, 450),
    ("Pallavaram", "Guindy", 6.0, 50, 500),
    ("Guindy", "Pallavaram", 6.0, 50, 500),

    # Inner Ring Road & Cross Routes
    ("Velachery", "Guindy", 5.0, 50, 500),
    ("Guindy", "Velachery", 5.0, 50, 500),
    ("Velachery", "Adyar", 4.5, 50, 450),
    ("Adyar", "Velachery", 4.5, 50, 450),
    ("Adyar", "Guindy", 5.5, 50, 500),
    ("Guindy", "Adyar", 5.5, 50, 500),
    ("Adyar", "Mylapore", 3.0, 40, 350),
    ("Mylapore", "Adyar", 3.0, 40, 350),
    ("Mylapore", "T. Nagar", 3.5, 40, 400),
    ("T. Nagar", "Mylapore", 3.5, 40, 400),

    # West Chennai
    ("Guindy", "Vadapalani", 4.0, 50, 500),
    ("Vadapalani", "Guindy", 4.0, 50, 500),
    ("Vadapalani", "Koyambedu", 3.5, 50, 550),
    ("Koyambedu", "Vadapalani", 3.5, 50, 550),
    ("Koyambedu", "Anna Nagar", 4.0, 50, 500),
    ("Anna Nagar", "Koyambedu", 4.0, 50, 500),
    ("Koyambedu", "Porur", 5.5, 50, 500),
    ("Porur", "Koyambedu", 5.5, 50, 500),
    ("Porur", "Vadapalani", 5.0, 50, 500),
    ("Vadapalani", "Porur", 5.0, 50, 500),

    # North Chennai
    ("Anna Nagar", "Aminjikarai", 3.0, 40, 400),
    ("Aminjikarai", "Anna Nagar", 3.0, 40, 400),
    ("Aminjikarai", "Egmore", 3.5, 50, 500),
    ("Egmore", "Aminjikarai", 3.5, 50, 500),
    ("Egmore", "Perambur", 4.0, 40, 400),
    ("Perambur", "Egmore", 4.0, 40, 400),
    ("Perambur", "Madhavaram", 5.5, 60, 600),
    ("Madhavaram", "Perambur", 5.5, 60, 600),
    ("Anna Nagar", "Perambur", 5.0, 40, 400),
    ("Perambur", "Anna Nagar", 5.0, 40, 400),

    # Additional Cross-Links (for alternative routes)
    ("Sholinganallur", "Velachery", 6.0, 50, 500),
    ("Velachery", "Sholinganallur", 6.0, 50, 500),
    ("Velachery", "Pallavaram", 5.5, 50, 450),
    ("Pallavaram", "Velachery", 5.5, 50, 450),
    ("Besant Nagar", "Mylapore", 3.0, 40, 350),
    ("Mylapore", "Besant Nagar", 3.0, 40, 350),
    ("Mylapore", "Egmore", 4.0, 40, 400),
    ("Egmore", "Mylapore", 4.0, 40, 400),
    ("T. Nagar", "Vadapalani", 3.5, 50, 500),
    ("Vadapalani", "T. Nagar", 3.5, 50, 500),
    ("T. Nagar", "Aminjikarai", 3.5, 40, 400),
    ("Aminjikarai", "T. Nagar", 3.5, 40, 400),
    ("Nungambakkam", "Aminjikarai", 2.5, 40, 400),
    ("Aminjikarai", "Nungambakkam", 2.5, 40, 400),
    ("Chromepet", "Guindy", 7.0, 50, 500),
    ("Guindy", "Chromepet", 7.0, 50, 500),
    ("Pallavaram", "Tambaram", 6.0, 50, 450),
    ("Tambaram", "Pallavaram", 6.0, 50, 450),
]


def build_road_graph() -> nx.DiGraph:
    """
    Build a directed weighted graph representing Chennai's road network.

    Nodes contain:
        - location_id, latitude, longitude, road_name
    Edges contain:
        - distance_km, speed_limit, road_capacity, base_travel_time
    
    Returns:
        NetworkX DiGraph with location nodes and road segment edges.
    """
    global _road_graph

    G = nx.DiGraph()

    # Load location data from database
    locations = get_all_locations()
    loc_map = {loc["location_name"]: loc for loc in locations}

    if not loc_map:
        logger.error("No locations found in database! Run seed_database.py first.")
        raise ValueError("No locations in database")

    # Add nodes
    for name, loc in loc_map.items():
        G.add_node(
            name,
            location_id=loc["location_id"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            road_name=loc["road_name"],
        )

    # Add edges
    edges_added = 0
    for from_loc, to_loc, dist, speed, capacity in ROAD_SEGMENTS:
        if from_loc in loc_map and to_loc in loc_map:
            base_time = (dist / speed) * 60  # minutes
            G.add_edge(
                from_loc, to_loc,
                distance_km=dist,
                speed_limit=speed,
                road_capacity=capacity,
                base_travel_time=round(base_time, 2),
                # These will be updated dynamically by traffic_weighting:
                current_speed=speed,
                congestion_level="Low",
                accident_reported=False,
                route_cost=round(base_time, 2),
            )
            edges_added += 1

    _road_graph = G
    logger.info(
        f"Road graph built: {G.number_of_nodes()} nodes, "
        f"{edges_added} edges"
    )

    return G


def get_graph() -> nx.DiGraph:
    """Get the cached road graph, building it if necessary."""
    global _road_graph
    if _road_graph is None:
        return build_road_graph()
    return _road_graph


def get_neighbors(location: str) -> List[str]:
    """Get directly connected neighbors of a location."""
    G = get_graph()
    if location not in G:
        return []
    return list(G.successors(location))


def get_all_location_names() -> List[str]:
    """Get all location names in the graph."""
    G = get_graph()
    return sorted(list(G.nodes()))
