from pydantic import BaseModel, PositiveInt, Field
import sys
from typing import Annotated, Dict, List, Literal


class drones_num(BaseModel):
    nb_drones: Annotated[PositiveInt, Field(strict=True)]


class HubMetadata(BaseModel):
    zone: Literal["normal", "restricted", "priority", "blocked"] = "normal"
    color: Literal["none", "green", "yellow", "red", "blue", "gray"] = "none"
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


i = 0
start_hub_num = 0
end_hub_num = 0
first_line = 0
names_ls = []
connections_ls = []
with open("./map_des.txt", "r") as f:
    for line in f:
        if ":" in line and not line.startswith("#"):
            first_line += 1
            ls_line = line.split(":")
            valid_keys = {"nb_drones", "connection", "hub", "end_hub", "start_hub"}

            if line.split(":")[0].strip() not in valid_keys:
                print("invalid file form "
                      ": key error -> not a valid key")
                sys.exit(1)

            if line.split(":")[0] != "nb_drones":
                if ls_line[0].strip() != "connection":
                    """
                    parsing data perfectly !
                    """
                    ls_ls = ls_line[1].split("]")
                    ls_ls_2 = ls_ls[0].split("[")
                    ls_ls_dtls = ls_ls_2[0].split()
                    try:
                        ls_ls_meta = ls_ls_2[1].split()
                    except IndexError:
                        sys.stderr.write("no meta passed [...] : error \n")
                    # *********************************
                    if len(ls_ls_dtls) != 3:
                        sys.stderr.write(
                            "Presence of a space "
                            "charachter : error \n"
                            )
                        sys.exit(1)
                    # ## Parsing the meta [] part ## #
                    my_meta = {}
                    for meta_item in ls_ls_meta:
                        try:
                            key = meta_item.split("=")[0]
                            value = meta_item.split("=")[1]
                        except IndexError as e:
                            sys.stderr.write(
                                f"No value present : error -> {e}\n"
                                )
                        if key == "max_drones":
                            my_meta[key] = int(value)
                        else:
                            my_meta[key] = value
                    # ##############################
                    # the zone name contains a dash (-) or a space -> Error
                    if "-" in ls_ls_dtls[0] or " " in ls_ls_dtls[0]:
                        sys.stderr.write("invalid Zone name : error \n")
                        sys.exit(1)
                    # ############################## looking for dup names
                    names_ls.append(ls_ls_dtls[0])
                    my_set = set(names_ls)
                    if len(names_ls) != len(my_set):
                        sys.stderr.write("Presence of a dup name : error \n")
                        sys.exit(1)
                    # ##############################
                    try:
                        hub_dict = {
                            "name": ls_ls_dtls[0],
                            "x": int(ls_ls_dtls[1]),
                            "y": int(ls_ls_dtls[2]),
                            "metadata": my_meta,
                        }
                    except (ValueError, IndexError) as e:
                        sys.stderr.write(
                            "invalid literal for int("
                            f") with base 10 : error {e}\n"
                        )
                else:
                    # if the condition == "connection":
                    ls_ls = ls_line[1].strip().split("]")
                    ls_ls_2 = ls_ls[0].strip().split("[")
                    ls_ls_2 = [i.strip() for i in ls_ls_2]
                    start_point = ls_ls_2[0].split("-")[0]
                    try:
                        end_point = ls_ls_2[0].split("-")[1]
                    except IndexError:
                        print("there's no Endpoint : error \n")
                    # ##############################
                    # A duplicate connection is found
                    connections_ls.append((start_point, end_point))
                    connections_set = set(connections_ls)
                    if len(connections_ls) != len(connections_set):
                        sys.stderr.write(
                            "Presence"
                            " of a dup connections : error \n"
                            )
                        sys.exit(1)
                    connections_ls_reverse = [i[::-1] for i in connections_set]
                    connections_ls_all = (
                        connections_ls +
                        connections_ls_reverse
                    )
                    connections_set_all = set(connections_ls_all)
                    # reversed connection
                    if len(connections_set_all) != (len(connections_ls) * 2):
                        sys.stderr.write(
                            "Presence of a"
                            " reversed connection : error \n"
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
                            "wasn't defined yet : error \n"
                            )
                        sys.exit(1)
                    # ##############################
                    try:
                        link_capacity = int(ls_ls_2[1].split("=")[1])
                    except IndexError:
                        link_capacity = 1

                    hub_dict = {
                        "start": start_point,
                        "end": end_point,
                        "max_link_capacity": link_capacity,
                    }

            #
            # Parsing the "nb_drones" line
            #
            if line.split(":")[0] == "nb_drones":
                try:
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
                    print(f"nb_drones is not correct : {e}")
                    sys.exit(1)
            #
            # Parsing the "start_hub" line
            #
            elif ls_line[0].strip() == "start_hub":
                start_hub_num += 1

                nested_hub_dict = {"start_hub": hub_dict}
                try:
                    if start_hub_num > 1:
                        raise ValueError(
                            "Frequency Error: 'start_hub' appeared"
                            f" {start_hub_num} times! It must appear"
                            " exactly once."
                        )
                    hub_data = StartHub(**nested_hub_dict)
                except ValueError as e:
                    print("invalid file form"
                          f" : error in the start_hub field -> {e}")
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
                    hub_data = EndHub(**nested_hub_dict)
                except ValueError as e:
                    print("invalid file form "
                          f": error in the end_hub field -> {e}")
                    sys.exit(1)
            #
            # Parsing the "hub" line
            #
            elif ls_line[0].strip() == "hub":
                nested_hub_dict = {"hubs": hub_dict}
                try:
                    hub_data = Hub_s(**nested_hub_dict)
                except ValueError as e:
                    print(f"invalid file form : error in the hub field -> {e}")
                    sys.exit(1)
            #
            # Parsing the "connection" line
            #
            elif ls_line[0].strip() == "connection":
                nested_hub_dict = {"connection": hub_dict}
                try:
                    hub_data = Connexion(**nested_hub_dict)
                except ValueError as e:
                    print("invalid file form "
                          f": error in the connection field -> {e}")
                    sys.exit(1)
        else:
            continue
