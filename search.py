import numpy as np
from typing import List, Tuple
from queue import PriorityQueue
from map_utils import get_valid_movesadd, get_monster_location, is_cloud
import math

def chebyshev_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2), abs(y1 - y2))

def heuristic(game_map, point1, point2):
    dist = chebyshev_distance(point1, point2)
    monst = get_monster_location(game_map)
    penalty = 0

    if monst != None:
        dist_monst = euclidean_distance(point1, monst)
        if dist_monst < 3:
            penalty = 100
        elif 3 <= dist_monst <= 7:
            penalty = 50
    return dist + penalty


def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def build_path(parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    path.reverse()
    return path

def a_star(game_map: np.ndarray, colors: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], h: callable) -> List[Tuple[int, int]]:
    # initialize open and close list
    open_list = PriorityQueue()
    close_list = []
    # additional dict which maintains the nodes in the open list for an easier access and check
    support_list = {}

    starting_state_g = 0
    starting_state_h = h(game_map, start, target)
    starting_state_f = starting_state_g + starting_state_h

    open_list.put((starting_state_f, (start, starting_state_g)))
    support_list[start] = starting_state_g
    parent = {start: None}

    while not open_list.empty():
        # get the node with lowest f
        _, (current, current_cost) = open_list.get()
        # add the node to the close list
        close_list.append(current)

        if current == target:
            print("Target found!")
            path = build_path(parent, target)
            return path

        for neighbor in get_valid_moves(game_map, colors, current):
            # check if neighbor in close list, if so continue
            if neighbor in close_list:
                continue
            # compute neighbor g, h and f values
            neighbor_g = 1 + current_cost
            neighbor_h = h(game_map, neighbor, target)
            neighbor_f = neighbor_g + neighbor_h
            parent[neighbor] = current
            neighbor_entry = (neighbor_f, (neighbor, neighbor_g))
            # if neighbor in open_list
            if neighbor in support_list.keys():
                # if neighbor_g is greater or equal to the one in the open list, continue
                if neighbor_g >= support_list[neighbor]:
                    continue
            
            # add neighbor to open list and update support_list
            open_list.put(neighbor_entry)
            support_list[neighbor] = neighbor_g

    print("Target node not found!")
    return None