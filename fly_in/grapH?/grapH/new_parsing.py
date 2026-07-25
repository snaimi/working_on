import sys
from typing import Annotated, Any, Dict, List, Literal, Tuple
from pydantic import BaseModel, Field, PositiveInt
from sys import argv


class drones_num(BaseModel):
    nb_drones: Annotated[PositiveInt, Field(strict=True)]


class HubMetadata(BaseModel):
    zone: Literal["normal", "restricted", "priority", "blocked"] = "normal"
    color: Literal[
        "none",
        "green",
        "yellow",
        "red",
        "blue",
        "gray",
        "cyan",
        "orange",
        "purple",
        "brown",
        "lime",
        "magenta",
        "gold",
        "black",
        "maroon",
        "darkred",
        "violet",
        "crimson",
        "rainbow",
    ] = "none"
    max_drones: Annotated[int, Field(strict=True, ge=1)] = 1


class HubModel(BaseModel):
    name: str
    x: Annotated[int, Field(strict=True)]
    y: Annotated[int, Field(strict=True)]
    metadata: HubMetadata = Field(default_factory=HubMetadata)


class StartHub(BaseModel):
    start_hub: HubModel


class EndHub(BaseModel):
    end_hub: HubModel


class Hub_s(BaseModel):
    hubs: HubModel


class Connexion_s(BaseModel):
    start: str
    end: str
    max_link_capacity: Annotated[PositiveInt, Field(strict=True)]


class Connexion(BaseModel):
    connection: Connexion_s


# zone holds : name x y metadata -> connections to build the graph
class zone:

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        metadata: Dict[str, Any],
        child: Any,
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.metadata: Dict[str, Any] = metadata
        self.child: Any = child


class base_conex:

    def __init__(
        self, start: str, end: str, max_link_capacity: int
    ) -> None:
        self.start: str = start
        self.end: str = end
        self.max_link_capacity: int = max_link_capacity


i: int = 0
start_hub_num: int = 0
end_hub_num: int = 0
first_line: int = 0
names_ls: List[str] = []
connections_ls: List[Tuple[str, str]] = []
ls_conex: List[Dict[str, Any]] = []
#
# saving data as objects in with zone class name
#
sum_goal: int = 0
ls_zones: List[Dict[str, Any]] = []
ls_zone_connections: List[Dict[str, Any]] = []
line_num: int = 0
hub_dict: Dict[str, Any] = {}


if len(argv) == 1:
    print("Usage: uv run python3 new_simulation.py <map-file.txt>")
    exit(1)

map_file = argv[1]
try:
    with open(map_file, "r") as f:
        for line in f:
            line_num += 1
            if ":" in line and not line.startswith("#"):
                first_line += 1
                ls_line: List[str] = line.split(":")
                valid_keys = {
                    "nb_drones",
                    "connection",
                    "hub",
                    "end_hub",
                    "start_hub",
                }

                if line.split(":")[0].strip() not in valid_keys:
                    print(
                        "invalid file form "
                        f": key error -> not a valid key : in line {line_num}"
                    )
                    sys.exit(1)
                if line.split(":")[0] != "nb_drones":
                    if ls_line[0].strip() != "connection":
                        """
                        parsing data perfectly !
                        """
                        ls_ls: List[str] = ls_line[1].split("]")
                        ls_ls_2: List[str] = ls_ls[0].split("[")
                        ls_ls_dtls: List[str] = ls_ls_2[0].split()
                        try:
                            ls_ls_meta: List[str] = ls_ls_2[1].split()
                        except IndexError:
                            sys.stderr.write(
                                "no meta passed [...] : error "
                                f": in line {line_num} \n"
                            )
                            sys.exit(1)
                        # *********************************
                        if len(ls_ls_dtls) != 3:
                            sys.stderr.write(
                                "Presence of a space "
                                f"charachter : error in line {line_num}\n"
                            )
                            sys.exit(1)
                        # ## Parsing the meta [] part ## #
                        my_meta: Dict[str, Any] = {}
                        for meta_item in ls_ls_meta:
                            try:
                                key: str = meta_item.split("=")[0]
                                value: str = meta_item.split("=")[1]
                            except IndexError:
                                sys.stderr.write(
                                    "No value present : "
                                    f"error -> in line {line_num}\n"
                                )
                                sys.exit(1)
                            if key == "max_drones":
                                my_meta[key] = int(value)
                            else:
                                my_meta[key] = value
                        # ##############################
                        # the zone name contains a dash (-) or a space -> Error
                        if "-" in ls_ls_dtls[0] or " " in ls_ls_dtls[0]:
                            sys.stderr.write(
                                "invalid Zone name "
                                f": error -> in line {line_num}\n"
                            )
                            sys.exit(1)
                        # ############################## looking for dup names
                        names_ls.append(ls_ls_dtls[0])
                        my_set: set[str] = set(names_ls)
                        if len(names_ls) != len(my_set):
                            sys.stderr.write(
                                "Presence of a dup name "
                                f": error -> in line {line_num}\n"
                            )
                            sys.exit(1)
                        # ##############################
                        zone_data: Dict[str, Any] = {}
                        try:
                            hub_dict = {
                                "name": ls_ls_dtls[0],
                                "x": int(ls_ls_dtls[1]),
                                "y": int(ls_ls_dtls[2]),
                                "metadata": my_meta,
                            }
                            # creating all_zones dict
                            # self.name = name
                            # self.x = x
                            # self.y = y
                            # self.metadata = meta
                            # self.child = child
                            zone_data = {
                                "name": ls_ls_dtls[0],
                                "x": int(ls_ls_dtls[1]),
                                "y": int(ls_ls_dtls[2]),
                                "metadata": my_meta,
                                "child": [],
                            }
                            ls_zones.append(zone_data)
                        except (ValueError, IndexError):
                            sys.stderr.write(
                                "invalid literal for int("
                                f") with base 10 : error -> in line {line_num}\n"
                            )
                            sys.exit(1)
                    else:
                        # if the condition == "connection":
                        ls_ls = ls_line[1].strip().split("]")
                        ls_ls_2 = ls_ls[0].strip().split("[")
                        ls_ls_2 = [item.strip() for item in ls_ls_2]
                        start_point: str = ls_ls_2[0].split("-")[0]
                        try:
                            end_point: str = ls_ls_2[0].split("-")[1]
                        except IndexError:
                            print(
                                f"missing character : error -> in line {line_num}"
                            )
                            sys.exit(1)
                        # ##############################
                        # A duplicate connection is found
                        connections_ls.append((start_point, end_point))
                        connections_set: set[Tuple[str, str]] = set(connections_ls)
                        if len(connections_ls) != len(connections_set):
                            sys.stderr.write(
                                "Presence"
                                " of a dup connections "
                                f": error -> in line {line_num}\n"
                            )
                            sys.exit(1)
                        connections_ls_reverse: List[Tuple[str, str]] = [
                            (i[1], i[0]) for i in connections_set
                        ]
                        connections_ls_all: List[Tuple[str, str]] = (
                            connections_ls + connections_ls_reverse
                        )
                        connections_set_all: set[Tuple[str, str]] = set(
                            connections_ls_all
                        )
                        # reversed connection
                        if len(connections_set_all) != (len(connections_ls) * 2):
                            sys.stderr.write(
                                "Presence of a"
                                " reversed connection "
                                f": error -> in line {line_num} \n"
                            )
                            sys.exit(1)
                        # ##############################
                        # A connection references a zone
                        # name that wasn't defined yet
                        if (
                            start_point not in names_ls
                            or end_point not in names_ls
                        ):
                            sys.stderr.write(
                                "zone name "
                                "wasn't defined yet : error"
                                f" -> in line {line_num} \n"
                            )
                            sys.exit(1)
                        # ##############################
                        try:
                            link_capacity: int = int(ls_ls_2[1].split("=")[1])
                        except IndexError:
                            link_capacity = 1

                        hub_dict = {
                            "start": start_point,
                            "end": end_point,
                            "max_link_capacity": link_capacity,
                        }
                        ls_conex.append(hub_dict)
                        # modifying the child connection from being
                        #  None to a valid zone name
                        sum_goal += 1
                        for element in ls_zones:
                            zone_data_conx: Dict[str, Any] = {
                                "name": element["name"],
                                "x": element["x"],
                                "y": element["y"],
                                "metadata": element["metadata"],
                                "child": [],
                            }
                            if element["name"] == start_point:
                                zone_data_conx["child"] = end_point
                                ls_zone_connections.append(zone_data_conx)
                            elif element["name"] == "goal" and sum_goal == 1:
                                ls_zone_connections.append(element)

                #
                # Parsing the "nb_drones" line
                #
                if line.split(":")[0] == "nb_drones":
                    try:
                        nb_drones: int = int(line.split(":")[1].strip())
                        i += 1
                        drones_num(nb_drones=int(line.split(":")[1].strip()))
                        if i > 1:
                            raise ValueError(
                                "Frequency Error:"
                                " 'nb_drones' appeared" f" {i} times"
                            )
                        if first_line != 1:
                            raise ValueError("nb_drones is not in the 1st line !")
                    except ValueError as e:
                        print(
                            f"nb_drones is not correct : {e} -> in line {line_num}"
                        )
                        sys.exit(1)
                #
                # Parsing the "start_hub" line
                #
                elif ls_line[0].strip() == "start_hub":
                    start_hub_num += 1

                    nested_hub_dict: Dict[str, Any] = {"start_hub": hub_dict}
                    try:
                        if start_hub_num > 1:
                            raise ValueError(
                                "Frequency Error: 'start_hub' appeared"
                                f" {start_hub_num} times! It must appear"
                                f" exactly once."
                            )
                        hub_data_start: StartHub = StartHub(**nested_hub_dict)
                    except ValueError as e:
                        print(
                            "invalid file form"
                            f" : error in the start_hub field -> {e}"
                            f" -> in line {line_num}"
                        )
                        sys.exit(1)
                #
                # Parsing the "end_hub" line
                #
                elif ls_line[0].strip() == "end_hub":
                    end_hub_num += 1

                    nested_hub_dict = {"end_hub": hub_dict}
                    try:
                        if end_hub_num > 1:
                            raise ValueError(
                                "Frequency Error: 'end_hub' appeared"
                                f" {end_hub_num} times! It must appear"
                                " exactly once."
                            )
                        hub_data_end: EndHub = EndHub(**nested_hub_dict)
                    except ValueError as e:
                        print(
                            "invalid file form "
                            ": error in the end_hub field "
                            f"-> {e} -> in line {line_num}"
                        )
                        sys.exit(1)
                #
                # Parsing the "hub" line
                #
                elif ls_line[0].strip() == "hub":
                    nested_hub_dict = {"hubs": hub_dict}
                    try:
                        hub_data_s: Hub_s = Hub_s(**nested_hub_dict)
                    except ValueError:
                        print(
                            "invalid file form : error in the hub field ->"
                            f" in line {line_num}"
                        )
                        sys.exit(1)
                #
                # Parsing the "connection" line
                #
                elif ls_line[0].strip() == "connection":
                    nested_hub_dict = {"connection": hub_dict}
                    try:
                        hub_data_conn: Connexion = Connexion(**nested_hub_dict)
                    except ValueError:
                        print(
                            "invalid file form "
                            ": error in the connection "
                            f"field -> in line {line_num}"
                        )
                        sys.exit(1)

            else:
                continue

except Exception as e:
    print(e)
    exit(1)

ls_final_data: List[Dict[str, Any]] = []
for name in names_ls:
    ls_childs: List[Any] = []
    zone_final: Dict[str, Any] = {}
    for elmnt in ls_zone_connections:
        if name == elmnt["name"]:
            zone_final = {
                "name": elmnt["name"],
                "x": elmnt["x"],
                "y": elmnt["y"],
                "metadata": elmnt["metadata"],
                "child": None,
            }
            for x_val, y_val in connections_ls:
                if y_val == name:
                    ls_childs.append(x_val)
            ls_childs.append(elmnt["child"])
    for r in list(ls_childs):
        if r == []:
            ls_childs.remove(r)
    unique_childs: List[Any] = list(set(ls_childs))
    zone_final["child"] = unique_childs
    ls_final_data.append(zone_final)

list_zones: List[zone] = []
for lk in ls_final_data:
    zone_obj: zone = zone(**lk)
    list_zones.append(zone_obj)

ls_obj_conx: List[base_conex] = []
for e_item in ls_conex:
    cnx_obj: base_conex = base_conex(**e_item)
    ls_obj_conx.append(cnx_obj)
