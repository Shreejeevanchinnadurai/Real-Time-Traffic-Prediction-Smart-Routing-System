"""
Routing Service
===============
Business logic layer for routing. Orchestrates fetching predictions,
updating graph weights, finding routes, and saving history.

Usage:
    from services.routing_service import get_smart_route
"""

from typing import Dict, List, Optional
import json

from routing.graph_builder import get_graph
from routing.traffic_weighting import update_edge_weights
from routing.route_optimizer import find_best_routes
from database.queries import insert_route, insert_route_history
from utils.logger import get_logger

logger = get_logger(__name__)


def get_smart_route(
    source_name: str,
    source_id: int,
    destination_name: str,
    destination_id: int,
    preference: str,
    traffic_conditions: Dict[str, Dict],
) -> List[Dict]:
    """
    Get optimal routes, save the best one to DB, and return all routes.

    Args:
        source_name:        Source location name.
        source_id:          Source location ID.
        destination_name:   Destination location name.
        destination_id:     Destination location ID.
        preference:         Routing preference.
        traffic_conditions: Predicted/current traffic mapping for edges.

    Returns:
        List of route dictionaries.
    """
    # 1. Get graph and update weights
    G = get_graph()
    G = update_edge_weights(G, traffic_conditions)

    # 2. Find routes
    routes = find_best_routes(G, source_name, destination_name, preference)

    if not routes:
        logger.warning("No routes returned by optimizer.")
        return []

    # 3. Save best route to database
    best_route = routes[0]
    route_id = insert_route(
        source_id=source_id,
        destination_id=destination_id,
        distance=best_route["total_distance_km"],
        duration=best_route["total_duration_min"],
        congestion_score=best_route["average_congestion_score"],
        route_path=json.dumps(best_route["path"]),
    )

    if route_id:
        # Save history with alternatives
        alternatives = [
            {
                "rank": r["rank"],
                "distance": r["total_distance_km"],
                "duration": r["total_duration_min"],
            }
            for r in routes[1:]
        ]
        
        reason = f"Recommended based on {preference} preference. Time: {best_route['total_duration_min']}m"
        insert_route_history(route_id, reason, alternatives)
        logger.info(f"Saved route {route_id} to database.")
    else:
        logger.warning("Failed to save route to database.")

    return routes
