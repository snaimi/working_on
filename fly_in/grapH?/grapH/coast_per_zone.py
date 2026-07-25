from typing import Dict, List, Optional, Union

from new_parsing import list_zones, zone

__all__ = [
    "list_zones",
    "cumulative_costs",
    "zone_costs",
    "zone_lookup",
]


class obj_coast:
    def __init__(self, name: str, coast: Union[int, float]) -> None:
        self.name: str = name
        self.coast: Union[int, float] = coast


def get_zone_cost(zone_obj: zone) -> Union[int, float]:
    if zone_obj.name == "goal":
        return 0
    try:
        zone_type: str = zone_obj.metadata.get("zone", "normal")
        if zone_type == "normal":
            return 1
        elif zone_type == "blocked":
            return 0
        elif zone_type == "restricted":
            return 2
        elif zone_type == "priority":
            return 0.9
        else:
            return 1
    except AttributeError:
        return 1


# Create a lookup map for each zone and it's coast
zone_lookup: Dict[str, zone] = {z.name: z for z in list_zones}
zone_costs: Dict[str, Union[int, float]] = {
    z.name: get_zone_cost(z) for z in list_zones
}

# print("--------zone_lookup--------")
# for e,j in zone_lookup.items():
#     print(f"{e}:{j}")
# print("--------zone_costs--------")
# for e,j in zone_costs.items():
#     print(f"{e}:{j}")

# BFS (Dijkstra-like)
place: List[str] = ["goal"]
parent_map: Dict[str, str] = {}
# Tracks the cheapest cost to reach each node
cumulative_costs: Dict[str, Union[int, float]] = {"goal": 0}

while place:
    element: str = place.pop(0)
    current_cost: Union[int, float] = cumulative_costs[element]
    zone_item: Optional[zone] = zone_lookup.get(element)

    if not zone_item:
        continue

    for child in zone_item.child:
        child_cost: Union[int, float] = zone_costs.get(child, 1)
        potential_cost: Union[int, float] = current_cost + child_cost

        # If we found a cheaper way to reach this child,
        # update its parent and cost
        if (
            child not in cumulative_costs
            or potential_cost < cumulative_costs[child]
        ):
            cumulative_costs[child] = potential_cost
            parent_map[child] = element

            # Re-queue the child to propagate the cheaper cost to its neighbors
            if child not in place:
                place.append(child)

# Build the final obj_ls based on the cheapest accumulated costs
obj_ls: List[obj_coast] = []
for name, final_cost in cumulative_costs.items():
    node: obj_coast = obj_coast(name, final_cost)
    obj_ls.append(node)


# ------ Output results ------
# print("\n--- Node Cumulative Costs ---")
# for el in obj_ls:
#     print(f"{el.name} : {el.coast}")


# print("\n--- Parent Map ---")
# for e, j in parent_map.items():
#     print(f"{e}:{j}")
