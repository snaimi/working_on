from typing import Dict, List, Optional, Union, Any
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

    def __init__(self, zones: List[zone]) -> None:
        self.zones: List[zone] = zones
        self.zone_lookup: Dict[str, zone] = {z.name: z for z in self.zones}
        self.zone_costs: Dict[str, Union[int, float]] = self._calculate_all_zone_costs()
        
        self.cumulative_costs: Dict[str, Union[int, float]] = {}
        self.parent_map: Dict[str, str] = {}
        self.obj_ls: List[ZoneCost] = []

    def _get_single_zone_cost(self, zone_obj: zone) -> Union[int, float]:
        """Determines the step cost based on zone metadata."""
        if zone_obj.name == "goal":
            return 0
        try:
            zone_type: str = zone_obj.metadata.get("zone", "normal")
            return self.ZONE_TYPE_COSTS.get(zone_type, 1)
        except AttributeError:
            return 1

    def _calculate_all_zone_costs(self) -> Dict[str, Union[int, float]]:
        """Maps each zone name to its individual traversal cost."""
        return {z.name: self._get_single_zone_cost(z) for z in self.zones}

    def compute_cumulative_costs(self, start_node: str = "goal") -> None:
        """Runs reverse BFS/Dijkstra to compute shortest path costs to the goal node."""
        queue: List[str] = [start_node]
        self.cumulative_costs = {start_node: 0}
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

        # Populate legacy obj_ls objects
        self.obj_ls = [
            ZoneCost(name, final_cost) 
            for name, final_cost in self.cumulative_costs.items()
        ]


# ==========================================
# Module-level Execution & Exports
# ==========================================

_calculator = ZoneCostCalculator(list_zones)
_calculator.compute_cumulative_costs(start_node="goal")

# Exported variables matching the expected imports of simulation.py
zone_lookup: Dict[str, zone] = _calculator.zone_lookup
zone_costs: Dict[str, Union[int, float]] = _calculator.zone_costs
cumulative_costs: Dict[str, Union[int, float]] = _calculator.cumulative_costs
obj_ls: List[ZoneCost] = _calculator.obj_ls
parent_map: Dict[str, str] = _calculator.parent_map