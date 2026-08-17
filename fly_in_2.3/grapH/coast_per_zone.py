import sys
import heapq
from typing import Dict, List, Optional, Union, Any, Set
from parsing import list_zones, zone

__all__ = [
    "list_zones",
    "cumulative_costs",
    "zone_costs",
    "zone_lookup",
]


class ZoneCost:
    """Represents a calculated cumulative cost entry for a zone."""
    
    def __init__(self, name: str, cost: Union[int, float]) -> None:
        self.name: str = name
        self.cost: Union[int, float] = cost


class ZoneCostCalculator:
    """Handles individual zone cost evaluation and reverse Dijkstra path cost propagation."""

    ZONE_TYPE_COSTS: Dict[str, Union[int, float]] = {
        "normal": 1,
        "blocked": float("inf"),  # Impassable zone
        "restricted": 2,
        "priority": 0.9,
    }

    TARGET_GOAL_NAMES: Set[str] = {"goal", "impossible_goal"}

    def __init__(self, zones: List[zone]) -> None:
        self.zones: List[zone] = zones
        self.zone_lookup: Dict[str, zone] = {z.name: z for z in self.zones}
        self.zone_costs: Dict[str, Union[int, float]] = self._calculate_all_zone_costs()
        
        self.cumulative_costs: Dict[str, Union[int, float]] = {}
        self.parent_map: Dict[str, str] = {}
        self.obj_ls: List[ZoneCost] = []

    def _get_single_zone_cost(self, zone_obj: zone) -> Union[int, float]:
        """Determines the step cost based on zone metadata."""
        if zone_obj.name in self.TARGET_GOAL_NAMES:
            return 0
        try:
            zone_type: str = zone_obj.metadata.get("zone", "normal")
            return self.ZONE_TYPE_COSTS.get(zone_type, 1)
        except AttributeError:
            return 1

    def _calculate_all_zone_costs(self) -> Dict[str, Union[int, float]]:
        """Maps each zone name to its individual traversal cost."""
        return {z.name: self._get_single_zone_cost(z) for z in self.zones}

    def is_path_blocked(self, target_start: str = "start") -> bool:
        """
        Validates if the path from start to a goal is missing, infinite cost, or passes through blocked nodes.
        Returns True if the path is blocked/unreachable, False if a valid path exists.
        """
        if target_start not in self.cumulative_costs:
            return True
        
        if self.cumulative_costs[target_start] == float("inf"):
            return True

        # Trace path from start to goal via parent_map to ensure no blocked nodes
        curr: Optional[str] = target_start
        visited: Set[str] = set()

        while curr is not None:
            if curr in visited:  # Cycle detection safety check
                return True
            visited.add(curr)

            # Check if current node is explicitly marked blocked or impassable
            if self.zone_costs.get(curr) == float("inf"):
                return True

            if curr in self.TARGET_GOAL_NAMES:
                return False  # Successfully reached goal without encountering blocked nodes

            curr = self.parent_map.get(curr)

        return True

    def compute_cumulative_costs(
        self,
        target_goals: Optional[Union[str, List[str]]] = None,
        target_start: str = "start"
    ) -> None:
        """Runs multi-source reverse Dijkstra using a min-heap priority queue."""
        
        # Determine target goals to search from
        if target_goals is None:
            goals_to_check = [g for g in ["goal", "impossible_goal"] if g in self.zone_lookup]
        elif isinstance(target_goals, str):
            goals_to_check = [target_goals] if target_goals in self.zone_lookup else []
        else:
            goals_to_check = [g for g in target_goals if g in self.zone_lookup]

        if not goals_to_check:
            sys.stderr.write(
                "No path error: Neither 'goal' nor 'impossible_goal' exists in the map graph.\n"
            )
            sys.exit(1)

        # Priority Queue for Dijkstra: stores tuples of (cost, zone_name)
        pq: List[tuple] = []
        self.cumulative_costs = {}
        self.parent_map = {}

        for goal in goals_to_check:
            self.cumulative_costs[goal] = 0
            heapq.heappush(pq, (0, goal))

        while pq:
            current_cost, element = heapq.heappop(pq)

            # Skip processing if we already found a cheaper way to 'element'
            if current_cost > self.cumulative_costs.get(element, float("inf")):
                continue

            zone_item: Optional[zone] = self.zone_lookup.get(element)
            if not zone_item:
                continue

            for child in zone_item.child:
                child_cost: Union[int, float] = self.zone_costs.get(child, 1)

                # Skip impassable/blocked nodes entirely
                if child_cost == float("inf"):
                    continue

                potential_cost: Union[int, float] = current_cost + child_cost

                # If a strictly cheaper route is found, update cost and push to priority queue
                if potential_cost < self.cumulative_costs.get(child, float("inf")):
                    self.cumulative_costs[child] = potential_cost
                    self.parent_map[child] = element
                    heapq.heappush(pq, (potential_cost, child))

        # Validate if path from start is blocked or unreachable
        if self.is_path_blocked(target_start):
            sys.stderr.write(
                f"Path error: Path from '{target_start}' to destination goals ({', '.join(goals_to_check)}) is blocked or non-existent.\n"
            )
            sys.exit(1)

        # Populate obj_ls with reachable non-infinite cost nodes
        self.obj_ls = [
            ZoneCost(name, final_cost) 
            for name, final_cost in self.cumulative_costs.items()
            if final_cost != float("inf")
        ]


# ==========================================
# Module-level Execution & Exports
# ==========================================

_calculator = ZoneCostCalculator(list_zones)
_calculator.compute_cumulative_costs(target_goals=["goal", "impossible_goal"], target_start="start")

# Exported variables matching the expected imports of simulation.py
zone_lookup: Dict[str, zone] = _calculator.zone_lookup
zone_costs: Dict[str, Union[int, float]] = _calculator.zone_costs
cumulative_costs: Dict[str, Union[int, float]] = _calculator.cumulative_costs
obj_ls: List[ZoneCost] = _calculator.obj_ls
parent_map: Dict[str, str] = _calculator.parent_map