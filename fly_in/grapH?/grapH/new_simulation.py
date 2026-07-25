import time
from typing import Dict, List, Optional, Union

# Import module directly to pass `mypy --strict` explicit attribute checks
import coast_per_zone
from new_parsing import nb_drones

# Bind module exports locally
list_zones = coast_per_zone.list_zones
cumulative_costs = coast_per_zone.cumulative_costs
zone_costs = coast_per_zone.zone_costs
zone_lookup = coast_per_zone.zone_lookup

# Extract capacity limits and colors dynamically from metadata
zone_capacities: Dict[str, int] = {}
zone_colors: Dict[str, str] = {}

ANSI_COLOR_MAP: Dict[str, str] = {
    "none": "0",
    "black": "90",
    "gray": "90",
    "green": "32",
    "yellow": "33",
    "red": "31",
    "crimson": "38;5;160",
    "maroon": "38;5;88",
    "darkred": "38;5;52",
    "blue": "34",
    "cyan": "36",
    "orange": "38;5;208",
    "purple": "35",
    "violet": "38;5;128",
    "brown": "38;5;94",
    "lime": "92",
    "magenta": "35",
    "gold": "38;5;220",
}

RESET_CODE: str = "\033[0m"
RAINBOW_CODES: List[str] = ["31", "38;5;208", "33", "32", "36", "34", "35"]

# Populate metadata
for z in list_zones:
    try:
        zone_capacities[z.name] = z.metadata.get("max_drones", 1)
    except AttributeError:
        zone_capacities[z.name] = 1

    try:
        color_str: str = z.metadata.get("color", "none").lower()
        if color_str == "rainbow":
            zone_colors[z.name] = "rainbow"
        else:
            ansi_num: str = ANSI_COLOR_MAP.get(color_str, "0")
            zone_colors[z.name] = f"\033[{ansi_num}m"
    except AttributeError:
        zone_colors[z.name] = "\033[0m"


def make_rainbow_text(text: str) -> str:
    """Applies a character-by-character color spectrum shift."""
    rainbow_str: str = "".join(
        f"\033[{RAINBOW_CODES[i % len(RAINBOW_CODES)]}m{char}"
        for i, char in enumerate(text)
    )
    return rainbow_str + RESET_CODE


def colorize_output(text: str) -> str:
    """Wraps recognized zone names in ANSI colors for single-hyphen tokens."""
    if text.count("-") > 1:
        return text

    for zone_name in sorted(zone_colors.keys(), key=len, reverse=True):
        if zone_name in text:
            ansi_start: str = zone_colors[zone_name]
            colored_zone: str = (
                make_rainbow_text(zone_name)
                if ansi_start == "rainbow"
                else f"{ansi_start}{zone_name}{RESET_CODE}"
            )
            text = text.replace(zone_name, colored_zone)
    return text


class DynamicDroneSimulation:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.current_zone: str = "start"
        self.target_zone: Optional[str] = None
        self.cost_accumulated: float = 0.0
        self.finished: bool = False
        self.just_started: bool = True


def run_simulation() -> None:
    drones: List[DynamicDroneSimulation] = [
        DynamicDroneSimulation(f"D{i}") for i in range(1, nb_drones + 1)
    ]
    global_occupancy: Dict[str, int] = {"start": len(drones)}
    total_turns: int = 0
    display_turn_num: int = 0

    def advance_drone_turn(drone: DynamicDroneSimulation) -> Optional[str]:
        if drone.finished:
            return None

        # Print initial starting positions with a hyphen
        if drone.just_started:
            drone.just_started = False
            return f"{drone.name}-{drone.current_zone}"

        # 1. Choose target if not currently traveling
        if drone.target_zone is None:
            current_node = zone_lookup.get(drone.current_zone)
            if not current_node or drone.current_zone == "goal":
                drone.finished = True
                return None

            best_neighbor: Optional[str] = None
            best_total_cost: float = float("inf")
            has_valid_path_neighbor: bool = False

            for child in current_node.child:
                child_step_cost: Union[int, float] = zone_costs.get(child, 1.0)
                remaining_cost: Union[int, float] = cumulative_costs.get(
                    child, float("inf")
                )
                total_path_cost: float = float(
                    child_step_cost + remaining_cost
                )

                # Track if there is any theoretical route out of here
                if remaining_cost != float("inf"):
                    has_valid_path_neighbor = True

                # Capacity Check
                current_occupancy: int = global_occupancy.get(child, 0)
                max_capacity: int = zone_capacities.get(child, 1)

                if current_occupancy >= max_capacity:
                    continue

                if total_path_cost < best_total_cost:
                    best_total_cost = total_path_cost
                    best_neighbor = child

            if best_neighbor is None:
                # Dead-end trap with no valid reach to goal
                if not has_valid_path_neighbor:
                    drone.finished = True
                    if global_occupancy.get(drone.current_zone, 0) > 0:
                        global_occupancy[drone.current_zone] -= 1
                    return None

                # Capacity traffic jam: wait here
                return f"{drone.name}-{drone.current_zone}"

            drone.target_zone = best_neighbor
            global_occupancy[drone.target_zone] = (
                global_occupancy.get(drone.target_zone, 0) + 1
            )

        # 2. Advance travel progress based on the target zone's cost
        target_zone_cost: float = float(
            zone_costs.get(drone.target_zone, 1.0)
        )
        drone.cost_accumulated += 1.0

        # 3. Check arrival state
        if drone.cost_accumulated >= target_zone_cost:
            movement_output: str = f"{drone.name}-{drone.target_zone}"

            # Leave old zone occupancy slot
            if global_occupancy.get(drone.current_zone, 0) > 0:
                global_occupancy[drone.current_zone] -= 1

            drone.current_zone = drone.target_zone
            drone.target_zone = None
            drone.cost_accumulated = 0.0

            if drone.current_zone == "goal":
                drone.finished = True
                if global_occupancy.get("goal", 0) > 0:
                    global_occupancy["goal"] -= 1
        else:
            # Mid-transit movement display
            movement_output = (
                f"{drone.name}-{drone.current_zone}-{drone.target_zone}"
            )

        return movement_output

    print("\n--- Drones Simulation ---")

    while any(not d.finished for d in drones):
        turn_movements: List[str] = []

        for drone in drones:
            move_output: Optional[str] = advance_drone_turn(drone)
            if move_output:
                turn_movements.append(colorize_output(move_output))

        if turn_movements:
            print(f"[turn {display_turn_num}] " + " ".join(turn_movements))

            if display_turn_num > 0:
                total_turns += 1
            display_turn_num += 1

        time.sleep(0.1)

    print(f"nb_turns={total_turns}")


if __name__ == "__main__":
    run_simulation()
