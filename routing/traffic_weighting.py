"""
Traffic Weighting Module
========================
Updates edge weights in the road graph based on predicted traffic conditions.
Computes route_cost = travel_time × congestion_penalty × incident_penalty.

Usage:
    from routing.traffic_weighting import update_edge_weights
    update_edge_weights(graph, traffic_conditions)
"""

import networkx as nx
from typing import Dict, List, Optional

from config.config import Config
from utils.constants import ROAD_CONDITION_PENALTY
from utils.helpers import safe_divide
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_edge_cost(
    distance_km: float,
    current_speed: float,
    congestion_level: str,
    accident_reported: bool,
    road_condition: str = "Good",
) -> float:
    """
    Compute the traffic-aware edge cost (in minutes).

    Formula:
        base_travel_time = distance_km / current_speed × 60 (minutes)
        route_cost = base_travel_time × congestion_penalty × incident_penalty × road_penalty

    Args:
        distance_km:      Road segment length.
        current_speed:     Predicted/current speed on this segment (km/h).
        congestion_level:  "Low", "Moderate", "High", or "Severe".
        accident_reported: Whether an accident is active on this segment.
        road_condition:    "Good", "Fair", "Poor", or "Under Construction".

    Returns:
        Route cost in minutes.
    """
    # Base travel time
    speed = max(current_speed, 3.0)  # Minimum 3 km/h (crawling traffic)
    base_time = (distance_km / speed) * 60  # minutes

    # Congestion penalty
    cong_penalty = Config.CONGESTION_PENALTIES.get(congestion_level, 1.0)

    # Incident penalty
    inc_penalty = Config.INCIDENT_PENALTY if accident_reported else 1.0

    # Road condition penalty
    road_penalty = ROAD_CONDITION_PENALTY.get(road_condition, 1.0)

    return base_time * cong_penalty * inc_penalty * road_penalty


def update_edge_weights(
    G: nx.DiGraph,
    traffic_conditions: Dict[str, Dict],
) -> nx.DiGraph:
    """
    Update all edge weights based on current/predicted traffic conditions.

    Args:
        G:                  Road network graph.
        traffic_conditions: Dict mapping location_name to traffic info:
            {
                "location_name": {
                    "average_speed": float,
                    "congestion_level": str,
                    "accident_reported": bool,
                    "road_condition": str,
                }
            }

    Returns:
        Updated graph (modified in-place).
    """
    updated_count = 0

    for u, v, data in G.edges(data=True):
        # Use traffic conditions from the destination node (entering that area)
        traffic = traffic_conditions.get(v, {})

        current_speed = traffic.get(
            "average_speed", data.get("speed_limit", 50)
        )
        congestion = traffic.get(
            "congestion_level", data.get("congestion_level", "Low")
        )
        accident = traffic.get(
            "accident_reported", data.get("accident_reported", False)
        )
        road_cond = traffic.get(
            "road_condition", "Good"
        )

        # Compute new cost
        cost = compute_edge_cost(
            distance_km=data["distance_km"],
            current_speed=current_speed,
            congestion_level=congestion,
            accident_reported=accident,
            road_condition=road_cond,
        )

        # Update edge attributes
        G[u][v]["current_speed"] = current_speed
        G[u][v]["congestion_level"] = congestion
        G[u][v]["accident_reported"] = accident
        G[u][v]["route_cost"] = round(cost, 2)
        updated_count += 1

    logger.info(f"Updated {updated_count} edge weights with traffic conditions")
    return G


def get_edge_summary(G: nx.DiGraph, path: List[str]) -> List[Dict]:
    """
    Get a summary of each edge in a route path.

    Args:
        G:    Road network graph.
        path: List of location names forming the route.

    Returns:
        List of edge info dicts for the route.
    """
    edges = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if G.has_edge(u, v):
            data = G[u][v]
            edges.append({
                "from": u,
                "to": v,
                "distance_km": data.get("distance_km", 0),
                "current_speed": data.get("current_speed", 0),
                "congestion_level": data.get("congestion_level", "Low"),
                "accident_reported": data.get("accident_reported", False),
                "route_cost": data.get("route_cost", 0),
            })
    return edges
