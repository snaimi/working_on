import sys
from typing import Dict, List, Optional, Union, Any, Set
from new_parsing import list_zones, zone

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
        self.coast: Union[int, float] = cost  # Maintained 'coast' attribute name for compatibility


class ZoneCostCalculator:
    """Handles individual zone cost evaluation and reverse Dijkstra/BFS path cost propagation."""

    ZONE_TYPE_COSTS: Dict[str, Union[int, float]] = {
        "normal": 1,
        "blocked": 0,
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

    def compute_cumulative_costs(
        self,
        target_goals: Optional[Union[str, List[str]]] = None,
        target_start: str = "start"
    ) -> None:
        """Runs multi-source reverse BFS/Dijkstra to compute shortest path costs to any valid goal node."""
        
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

        # Multi-source BFS/Dijkstra initialization
        queue: List[str] = list(goals_to_check)
        self.cumulative_costs = {goal: 0 for goal in goals_to_check}
        self.parent_map = {}

        while queue:
            element: str = queue.pop(0)
            current_cost: Union[int, float] = self.cumulative_costs[element]
            zone_item: Optional[zone] = self.zone_lookup.get(element)

            if not zone_item:
                continue

            for child in zone_item.child:
                child_cost: Union[int, float] = self.zone_costs.get(child, 1)
                potential_cost: Union[int, float] = current_cost + child_cost

                # If a cheaper route is found, update cost and queue neighbor
                if (
                    child not in self.cumulative_costs
                    or potential_cost < self.cumulative_costs[child]
                ):
                    self.cumulative_costs[child] = potential_cost
                    self.parent_map[child] = element

                    if child not in queue:
                        queue.append(child)

        # Check if at least one path connects the start hub to any goal
        if target_start not in self.cumulative_costs:
            sys.stderr.write(
                f"No path error: No valid path exists between '{target_start}' and any destination goals ({', '.join(goals_to_check)}).\n"
            )
            sys.exit(1)

        # Populate legacy obj_ls objects
        self.obj_ls = [
            ZoneCost(name, final_cost) 
            for name, final_cost in self.cumulative_costs.items()
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