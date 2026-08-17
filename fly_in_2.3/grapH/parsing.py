import sys
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Literal, Set, Tuple
from pydantic import BaseModel, Field, PositiveInt, ValidationError


# Pydantic Schemas for Validation

class DroneCountModel(BaseModel):
    nb_drones: Annotated[PositiveInt, Field(strict=True)]


class HubMetadata(BaseModel):
    model_config = {"extra": "forbid"}

    zone: Literal["normal", "restricted", "priority", "blocked"] = "normal"
    color: Literal[
        "none", "green", "yellow", "red", "blue", "gray", "cyan", "orange",
        "purple", "brown", "lime", "magenta", "gold", "black", "maroon",
        "darkred", "violet", "crimson", "rainbow",
    ] = "none"
    max_drones: Annotated[int, Field(strict=True, ge=1)] = 1


class HubModel(BaseModel):
    name: str
    x: Annotated[int, Field(strict=True)]
    y: Annotated[int, Field(strict=True)]
    metadata: HubMetadata = Field(default_factory=HubMetadata)


class ConnectionModel(BaseModel):
    start: str
    end: str
    max_link_capacity: Annotated[PositiveInt, Field(strict=True)] = 1


# Domain Data Classes

@dataclass
class Hub:
    name: str
    x: int
    y: int
    metadata: Dict[str, Any]
    child: List[str] = field(default_factory=list)


# Type alias for backward compatibility
zone = Hub


@dataclass
class Connection:
    start: str
    end: str
    max_link_capacity: int


@dataclass
class ParsedMap:
    nb_drones: int
    start_hub: HubModel
    end_hub: HubModel
    hubs: List[Hub]
    connections: List[Connection]


# Object-Oriented Parser Logic

class MapParser:
    VALID_KEYS: Set[str] = {
        "nb_drones",
        "connection",
        "hub",
        "end_hub",
        "start_hub",
    }

    def __init__(self, filepath: str) -> None:
        self.filepath: str = filepath
        self.nb_drones: int | None = None
        self.start_hub: HubModel | None = None
        self.end_hub: HubModel | None = None
        
        self.hubs_dict: Dict[str, HubModel] = {}
        self.connections: List[Connection] = []
        
        self._hub_names: List[str] = []
        self._raw_connections: List[Tuple[str, str]] = []
        self._start_hub_count: int = 0
        self._end_hub_count: int = 0
        self._drone_line_count: int = 0
        self._first_processed_line: int = 0

    def parse(self) -> ParsedMap:
        """Parses the map file line by line and
        returns the fully populated ParsedMap."""
        try:
            with open(self.filepath, "r") as f:
                for line_num, raw_line in enumerate(f, start=1):
                    line = raw_line.strip()
                    if not line or line.startswith("#") or ":" not in line:
                        continue

                    self._first_processed_line += 1
                    key, val = [part.strip() for part in line.split(":", 1)]

                    if key not in self.VALID_KEYS:
                        self._raise_error(
                            f"invalid file form : key error -> not a valid key : in line {line_num}"
                        )

                    # Enforce that nb_drones must be the very first processed line
                    if self._first_processed_line == 1 and key != "nb_drones":
                        print(f"nb_drones is not correct : nb_drones is not in the 1st line ! -> in line {line_num}")
                        sys.exit(1)

                    if key == "nb_drones":
                        self._parse_nb_drones(val, line_num)
                    elif key in {"hub", "start_hub", "end_hub"}:
                        self._parse_hub_entry(key, val, line_num)
                    elif key == "connection":
                        self._parse_connection_entry(val, line_num)

        except (Exception, FileNotFoundError) as e:
            if isinstance(e, SystemExit):
                raise
            print(f"Error reading file: {e}")
            sys.exit(1)

        self._validate_completion()
        return self._build_result()

    # Parsing Line Components

    def _parse_nb_drones(self, value_str: str, line_num: int) -> None:
        self._drone_line_count += 1
        
        if self._first_processed_line != 1:
            print(f"nb_drones is not correct : nb_drones is not in the 1st line ! -> in line {line_num}")
            sys.exit(1)

        if self._drone_line_count > 1:
            print(f"nb_drones is not correct : Frequency Error: 'nb_drones' appeared {self._drone_line_count} times -> in line {line_num}")
            sys.exit(1)

        try:
            val_int = int(value_str)
            if val_int < 0:
                print(f"nb_drones is not correct : value cannot be negative ({val_int}) -> in line {line_num}")
                sys.exit(1)

            DroneCountModel(nb_drones=val_int)
            self.nb_drones = val_int
        except (ValueError, ValidationError) as e:
            print(f"nb_drones is not correct : {e} -> in line {line_num}")
            sys.exit(1)

    def _parse_hub_entry(self, key: str, value_str: str, line_num: int) -> None:
        if "[" in value_str and "]" in value_str:
            main_part, meta_part = value_str.split("[", 1)
            meta_part = meta_part.rstrip("]")
        elif "[" not in value_str and "]" not in value_str:
            main_part = value_str
            meta_part = "zone=normal color=none max_drones=1"
        else:
            sys.stderr.write(f"invalid metadata bracket form : error -> in line {line_num}\n")
            sys.exit(1)

        details = main_part.strip().split()
        if len(details) != 3:
            sys.stderr.write(f"Presence of a space charachter : error in line {line_num}\n")
            sys.exit(1)

        hub_name, x_str, y_str = details[0], details[1], details[2]

        # Zone name invalid if it contains '-' or '#' or spaces
        if "-" in hub_name or "#" in hub_name or " " in hub_name:
            sys.stderr.write(f"invalid Zone name : error -> in line {line_num}\n")
            sys.exit(1)

        if hub_name in self._hub_names:
            sys.stderr.write(f"Presence of a dup name : error -> in line {line_num}\n")
            sys.exit(1)

        # Meta extraction with duplicate key prevention
        meta_dict: Dict[str, Any] = {}
        for item in meta_part.strip().split():
            if "=" not in item:
                sys.stderr.write(f"No value present : error -> in line {line_num}\n")
                sys.exit(1)
            k, v = item.split("=", 1)

            if k in meta_dict:
                sys.stderr.write(f"Duplicate metadata key '{k}' : error -> in line {line_num}\n")
                sys.exit(1)

            meta_dict[k] = int(v) if k == "max_drones" else v

        # Automatically assign max_drones for start_hub and end_hub
        if key in {"start_hub", "end_hub"} and self.nb_drones is not None:
            meta_dict["max_drones"] = self.nb_drones

        try:
            hub_model = HubModel(
                name=hub_name,
                x=int(x_str),
                y=int(y_str),
                metadata=HubMetadata(**meta_dict)
            )
        except (ValueError, ValidationError):
            sys.stderr.write(
                f"invalid file form : error in the {key} field -> in line {line_num}\n"
            )
            sys.exit(1)

        self._hub_names.append(hub_name)
        self.hubs_dict[hub_name] = hub_model

        if key == "start_hub":
            self._start_hub_count += 1
            if self._start_hub_count > 1:
                print(
                    f"invalid file form : error in the start_hub field -> Frequency Error: 'start_hub' appeared {self._start_hub_count} times! It must appear exactly once. -> in line {line_num}"
                )
                sys.exit(1)
            self.start_hub = hub_model

        elif key == "end_hub":
            self._end_hub_count += 1
            if self._end_hub_count > 1:
                print(
                    f"invalid file form : error in the end_hub field -> Frequency Error: 'end_hub' appeared {self._end_hub_count} times! It must appear exactly once. -> in line {line_num}"
                )
                sys.exit(1)
            self.end_hub = hub_model

    def _parse_connection_entry(self, value_str: str, line_num: int) -> None:
        main_part = value_str.split("[")[0].strip() if "[" in value_str else value_str.strip()
        
        if "-" not in main_part:
            print(f"missing character : error -> in line {line_num}")
            sys.exit(1)

        start_p, end_p = main_part.split("-", 1)
        start_p, end_p = start_p.strip(), end_p.strip()

        # Connection duplicate checks
        current_pair = (start_p, end_p)
        if current_pair in self._raw_connections:
            sys.stderr.write(f"Presence of a dup connections : error -> in line {line_num}\n")
            sys.exit(1)

        if (end_p, start_p) in self._raw_connections:
            sys.stderr.write(f"Presence of a reversed connection : error -> in line {line_num} \n")
            sys.exit(1)

        if start_p not in self._hub_names or end_p not in self._hub_names:
            sys.stderr.write(f"zone name wasn't defined yet : error -> in line {line_num} \n")
            sys.exit(1)

        self._raw_connections.append(current_pair)

        # Parsing link capacity
        capacity = 1
        if "[" in value_str and "]" in value_str:
            meta_str = value_str.split("[")[1].split("]")[0].strip()
            if "max_link_capacity=" in meta_str:
                try:
                    capacity = int(meta_str.split("=")[1])
                except ValueError:
                    pass

        try:
            ConnModel = ConnectionModel(start=start_p, end=end_p, max_link_capacity=capacity)
            self.connections.append(
                Connection(
                    start=ConnModel.start,
                    end=ConnModel.end,
                    max_link_capacity=ConnModel.max_link_capacity,
                )
            )
        except ValidationError:
            print(f"invalid file form : error in the connection field -> in line {line_num}")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Post-Parsing Validation & Object Construction
    # ------------------------------------------------------------------

    def _validate_completion(self) -> None:
        if self.nb_drones is None:
            print("nb_drones is missing : error -> nb_drones was not provided in the file")
            sys.exit(1)
        if self.start_hub is None:
            self._raise_error("Missing 'start_hub' definition.")
        if self.end_hub is None:
            self._raise_error("Missing 'end_hub' definition.")

    def _build_result(self) -> ParsedMap:
        """Constructs graph adjacency list and creates Hub and Connection domain objects."""
        adjacency: Dict[str, Set[str]] = {name: set() for name in self._hub_names}
        for start, end in self._raw_connections:
            adjacency[start].add(end)
            adjacency[end].add(start)

        hub_objects: List[Hub] = []
        for name in self._hub_names:
            model = self.hubs_dict[name]
            hub_obj = Hub(
                name=model.name,
                x=model.x,
                y=model.y,
                metadata=model.metadata.model_dump(),
                child=sorted(list(adjacency[name])),
            )
            hub_objects.append(hub_obj)

        return ParsedMap(
            nb_drones=self.nb_drones,
            start_hub=self.start_hub,
            end_hub=self.end_hub,
            hubs=hub_objects,
            connections=self.connections,
        )

    @staticmethod
    def _raise_error(msg: str) -> None:
        print(msg)
        sys.exit(1)


# ==========================================
# Module Initializer / Global Execution
# ==========================================

def _resolve_map_file() -> str:
    """Retrieves target map file from defaults to default.txt."""
    if len(sys.argv) > 1 and sys.argv[1].endswith(".txt"):
        return sys.argv[1]
    return "default.txt"


# Parse automatically when imported so module-level variables are exported
_map_file: str = _resolve_map_file()
parsed_map: ParsedMap = MapParser(filepath=_map_file).parse()

# Exported variables for direct imports
nb_drones: int = parsed_map.nb_drones
list_zones: List[Hub] = parsed_map.hubs
ls_obj_conx: List[Connection] = parsed_map.connections

__all__ = [
    "MapParser",
    "ParsedMap",
    "Hub",
    "zone",
    "Connection",
    "parsed_map",
    "nb_drones",
    "list_zones",
    "ls_obj_conx",
]