import sys
import time
from typing import Dict, List, Optional, Any

# Import parsed assets and calculated pathfinding metrics
from parsing import parsed_map, nb_drones
from coast_per_zone import list_zones, zone_lookup, zone_costs, cumulative_costs


class ZoneFormatter:
    """Handles ANSI color mapping, rainbow styling,
    and console output colorization."""

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

    def __init__(self, zones: List[Any]) -> None:
        self.zone_capacities: Dict[str, int] = {}
        self.zone_colors: Dict[str, str] = {}
        self._init_zone_metadata(zones)

    def _extract_metadata_dict(self, zone_obj: Any) -> Dict[str, Any]:
        meta = getattr(zone_obj, "metadata", {})
        if hasattr(meta, "model_dump"):
            return meta.model_dump()
        elif hasattr(meta, "__dict__"):
            return meta.__dict__
        elif isinstance(meta, dict):
            return meta
        return {}

    def _init_zone_metadata(self, zones: List[Any]) -> None:
        for z in zones:
            meta = self._extract_metadata_dict(z)
            self.zone_capacities[z.name] = meta.get("max_drones", 1)

            color_str = str(meta.get("color", "none")).lower()
            if color_str == "rainbow":
                self.zone_colors[z.name] = "rainbow"
            else:
                ansi_num = self.ANSI_COLOR_MAP.get(color_str, "0")
                self.zone_colors[z.name] = f"\033[{ansi_num}m"

    def make_rainbow_text(self, text: str) -> str:
        rainbow_str = ""
        for i, char in enumerate(text):
            color_code = self.RAINBOW_CODES[i % len(self.RAINBOW_CODES)]
            rainbow_str += f"\033[{color_code}m{char}"
        return rainbow_str + self.RESET_CODE

    def colorize_output(self, text: str) -> str:
        if text.count("-") > 1:
            return text

        for zone_name in sorted(self.zone_colors.keys(), key=len, reverse=True):
            if zone_name in text:
                ansi_start = self.zone_colors[zone_name]
                if ansi_start == "rainbow":
                    colored_zone = self.make_rainbow_text(zone_name)
                else:
                    colored_zone = f"{ansi_start}{zone_name}{self.RESET_CODE}"
                text = text.replace(zone_name, colored_zone)
        return text


class DynamicDroneSimulation:
    """Represents an autonomous drone navigating from start to goal."""

    def __init__(self, name: str, start_zone: str, goal_zone: str) -> None:
        self.name: str = name
        self.current_zone: str = start_zone
        self.goal_zone: str = goal_zone
        self.target_zone: Optional[str] = None
        self.cost_accumulated: float = 0.0
        self.finished: bool = False

    def plan_move(
        self,
        occupancy_tracker: Dict[str, int],
        zone_capacities: Dict[str, int],
    ) -> None:
        """Decide next destination towards goal."""
        if self.finished or self.target_zone is not None:
            return

        current_node = zone_lookup.get(self.current_zone)
        if not current_node or self.current_zone == self.goal_zone:
            self.finished = True
            return

        current_rem_cost = cumulative_costs.get(self.current_zone, float("inf"))

        best_neighbor = None
        best_total_cost = float("inf")

        for child in current_node.child:
            remaining_cost = cumulative_costs.get(child, float("inf"))

            # Enforce forward progression
            if remaining_cost >= current_rem_cost:
                continue

            child_step_cost = zone_costs.get(child, 1.0)
            total_path_cost = child_step_cost + remaining_cost

            # Check dynamic capacity
            current_occ = occupancy_tracker.get(child, 0)
            max_capacity = zone_capacities.get(child, 1)

            if current_occ >= max_capacity:
                continue

            if total_path_cost < best_total_cost:
                best_total_cost = total_path_cost
                best_neighbor = child

        if best_neighbor is not None:
            self.target_zone = best_neighbor
            # Reserve occupancy in the target node immediately
            occupancy_tracker[best_neighbor] = occupancy_tracker.get(best_neighbor, 0) + 1

    def execute_move(self, occupancy_tracker: Dict[str, int]) -> Optional[str]:
        """Advance physical movement by 1 step for the current turn."""
        if self.finished:
            return None

        # Waiting at capacity
        if self.target_zone is None:
            return f"{self.name}-{self.current_zone}"

        # Vacate current zone on the first step of transit
        if self.cost_accumulated == 0.0:
            if self.current_zone in occupancy_tracker and occupancy_tracker[self.current_zone] > 0:
                occupancy_tracker[self.current_zone] -= 1

        target_zone_cost = zone_costs.get(self.target_zone, 1.0)
        self.cost_accumulated += 1.0

        if self.cost_accumulated >= target_zone_cost:
            movement_output = f"{self.name}-{self.target_zone}"

            self.current_zone = self.target_zone
            self.target_zone = None
            self.cost_accumulated = 0.0

            if self.current_zone == self.goal_zone:
                self.finished = True
                if self.goal_zone in occupancy_tracker and occupancy_tracker[self.goal_zone] > 0:
                    occupancy_tracker[self.goal_zone] -= 1
        else:
            movement_output = f"{self.name}-{self.current_zone}-{self.target_zone}"

        return movement_output


class SimulationManager:
    """Manages global simulation state, drone spawning, planning, and step execution."""

    def __init__(self, total_drones: int, zones: List[Any]) -> None:
        self.unspawned_count: int = total_drones
        self.next_drone_id: int = 1
        self.active_drones: List[DynamicDroneSimulation] = []
        self.global_occupancy: Dict[str, int] = {}
        self.total_turns: int = 0
        self.display_turn_num: int = 1
        self.sleep_delay: float = 0.0 if total_drones > 100 else 0.1

        self.start_zone: str = "start" if "start" in zone_lookup else parsed_map.start_hub.name
        self.goal_zone: str = "goal" if "goal" in zone_lookup else parsed_map.end_hub.name

        self.formatter: ZoneFormatter = ZoneFormatter(zones)

    def run(self) -> None:
        print("\n--- Connection-Style Simulation ---")

        while self.active_drones or self.unspawned_count > 0:
            self._spawn_drones()
            turn_movements = self._execute_turn()

            if turn_movements:
                print(f"[turn {self.display_turn_num}] " + " ".join(turn_movements))
                self.total_turns += 1
                self.display_turn_num += 1

            if self.sleep_delay > 0:
                time.sleep(self.sleep_delay)

        print(f"nb_turns={self.total_turns}")

    def _spawn_drones(self) -> None:
        """Instantiate drones when start zone capacity is available."""
        start_capacity = self.formatter.zone_capacities.get(self.start_zone, 1)
        current_start_occ = self.global_occupancy.get(self.start_zone, 0)

        while self.unspawned_count > 0 and current_start_occ < start_capacity:
            new_drone = DynamicDroneSimulation(
                f"D{self.next_drone_id}",
                start_zone=self.start_zone,
                goal_zone=self.goal_zone,
            )
            self.active_drones.append(new_drone)

            self.global_occupancy[self.start_zone] = self.global_occupancy.get(self.start_zone, 0) + 1
            current_start_occ += 1

            self.next_drone_id += 1
            self.unspawned_count -= 1

    def _execute_turn(self) -> List[str]:
        """Runs planning and execution in front-to-back order within a single step per turn."""
        turn_movements: List[str] = []
        finished_this_turn: List[DynamicDroneSimulation] = []

        # 1. Sort active drones by proximity to goal (closest first)
        self.active_drones.sort(
            key=lambda d: cumulative_costs.get(d.current_zone, float("inf"))
        )

        # 2. Plan and execute sequentially for each drone
        for drone in self.active_drones:
            # Plan if not currently transitioning
            drone.plan_move(
                self.global_occupancy,
                self.formatter.zone_capacities,
            )
            
            # Execute exactly 1 unit of movement
            move_output = drone.execute_move(self.global_occupancy)
            if move_output:
                turn_movements.append(self.formatter.colorize_output(move_output))

            if drone.finished:
                finished_this_turn.append(drone)

        # Cleanup finished drones
        for finished_drone in finished_this_turn:
            self.active_drones.remove(finished_drone)

        return turn_movements


def run_simulation() -> None:
    simulation = SimulationManager(total_drones=nb_drones, zones=list_zones)
    simulation.run()


if __name__ == "__main__":
    run_simulation()