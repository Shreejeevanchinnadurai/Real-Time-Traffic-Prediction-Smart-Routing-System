import pytest
import networkx as nx
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from routing.traffic_weighting import compute_edge_cost
from routing.route_optimizer import find_best_routes

def test_compute_edge_cost():
    # Base travel time for 10km at 50km/h = 12 mins
    cost = compute_edge_cost(10.0, 50.0, "Low", False)
    assert cost == 12.0
    
    # Severe congestion penalty (2.5x) -> 30 mins
    cost = compute_edge_cost(10.0, 50.0, "Severe", False)
    assert cost == 30.0

def test_find_best_routes():
    G = nx.DiGraph()
    G.add_edge("A", "B", distance_km=5, route_cost=10, congestion_level="Low")
    G.add_edge("B", "C", distance_km=5, route_cost=10, congestion_level="Low")
    G.add_edge("A", "C", distance_km=15, route_cost=25, congestion_level="High")
    
    # A -> B -> C is faster (20) than A -> C (25)
    routes = find_best_routes(G, "A", "C", "Fastest")
    assert len(routes) > 0
    assert routes[0]["path"] == ["A", "B", "C"]
    assert routes[0]["total_duration_min"] == 20
