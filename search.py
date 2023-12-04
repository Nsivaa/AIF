import math
from queue import PriorityQueue
from typing import Dict, List, Tuple
import numpy as np
from map_utils import get_monster_location, get_valid_moves, is_cloud, actions_from_path, get_clouds_location

MIN_COST = 10**-5
MAX_COST = 10**5

def chebyshev_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2), abs(y1 - y2))

def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def _euclidean_distance_prime(point1: Tuple[int, int], point2: Tuple[int, int]) -> Tuple[float, float]:
    x1, y1 = point1
    x2, y2 = point2
    distance = (x1 - x2)**2 + (y1 - y2)**2
    if distance == 0:
        return MAX_COST, MAX_COST 
    dx = (x1 - x2) / distance
    dy = (y1 - y2) / distance
    return dx, dy

def _compute_cost(game_map: np.ndarray, position: Tuple[int, int], color_map: np.ndarray, precision: str) -> int:
    monster_position = get_monster_location(game_map)

    # if monster is in known position then we exploit clouds to avoid it
    if monster_position is not None:
        if is_cloud(game_map[position], color_map[position]):
            return MIN_COST
        else:
            monster_distance = chebyshev_distance(position, monster_position)
            if monster_distance == 0:
                return MAX_COST
            else:
                return np.reciprocal(float(monster_distance))
    
    # updating at each step
    if precision == 'fully_dynamic':
        cost = 0.0
        clouds = get_clouds_location(game_map, color_map)
        # insted, if monster is in unkown position then we sum the "danger" of each cloud hiding a monster
        for avoid_position in clouds:
            distance = chebyshev_distance(position, avoid_position)
            if distance == 0:                   # position is either a cloud or a monster
                return MAX_COST                 # maximum danger
            cost += np.reciprocal(float(distance))
        return cost
    # updating each type the monster comes clear
    elif precision == 'monster_dynamic':
        if is_cloud(game_map[position], color_map[position]):
            return MAX_COST
        return MIN_COST

def _build_path(parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    path.reverse()
    return path

def a_star(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], h: callable, precision: str) -> List[Tuple[int, int]]:
    frontier = PriorityQueue()                                      #init frontier as PriorityQueue
    frontier.put(start, 0)                                          #init frontier with starting node
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}          #empty dict to store parent nodes
    cost_so_far: Dict[Tuple[int, int], int] = {}                    #empty dict to store cost of path to node
    came_from[start] = None                                         #start has no parent
    cost_so_far[start] = 0                                          #start has no cost

    while not frontier.empty():
        current = frontier.get()

        if current == target:
            return _build_path(came_from, target)
        
        for neighbor in get_valid_moves(game_map, color_map, current):
            # new_cost = cost_so_far[current] + _compute_cost(game_map, neighbor, color_map[neighbor], get_monster_location(game_map))
            new_cost = cost_so_far[current] + _compute_cost(game_map, neighbor, color_map, precision)

            # if neighbor has not been already visited or has been visited but with a higher cost then update cost and add to frontier
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost            #update cost
                priority = new_cost + h(neighbor, target)   #compute priority
                frontier.put(neighbor, priority)            #add neighbor to frontier
                came_from[neighbor] = current               #update parent node

    return None

def dynamic_pathfinding(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], heuristic: callable, precision: str = 'fully_dynamic'):
    path = a_star(game_map, color_map, start, target, heuristic, precision)
    actions = actions_from_path(start, path[1:])
    for index, _ in enumerate(actions):
        if get_monster_location(game_map) is not None or precision == 'fully_dynamic':
            new_path = a_star(game_map, color_map, path[index+1], target, heuristic, precision)
            del actions[index+1:]
            actions.extend(actions_from_path(path[index+1], new_path[1:]))
    return actions
