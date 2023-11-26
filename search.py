from queue import PriorityQueue
from typing import List, Tuple
from map_utils import get_valid_moves, is_cloud, get_monster_location
import numpy as np

MIN_COST = 1
MAX_COST = 10**5

def chebyshev_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2), abs(y1 - y2))

def _euclidean_distance_prime(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = (x1 - x2)**2 + (y1 - y2)**2

    if distance == 0:
        return MAX_COST, MAX_COST 
    
    dx = (x1 - x2) / distance
    dy = (y1 - y2) / distance
    
    return dx, dy

def _compute_cost(position: Tuple[int, int], color_char: int, monster_position: Tuple[int, int] = None) -> int:
    if monster_position is None:
        if is_cloud(position, color_char):
            return MIN_COST
        else:
            return MIN_COST
    else:
        if is_cloud(position, color_char):
            return MIN_COST
        else:
            return np.sum(_euclidean_distance_prime(position, monster_position))

def _build_path(parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    path.reverse()
    return path

def a_star(game_map: np.ndarray, color_matrix: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], h: callable) -> List[Tuple[int, int]]:
    # initialize open and close list
    open_list = PriorityQueue()
    close_list = []
    # additional dict which maintains the nodes in the open list for an easier access and check
    support_list = {}

    starting_state_g = 0
    starting_state_h = h(start, target)
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
            path = _build_path(parent, target)
            return path

        for neighbor in get_valid_moves(game_map, color_matrix, current):
            # check if neighbor in close list, if so continue
            if neighbor in close_list:
                continue
            # compute neighbor g, h and f values
            neighbor_g = _compute_cost(neighbor, color_matrix[neighbor], get_monster_location(game_map)) + current_cost
            neighbor_h = h(neighbor, target)
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