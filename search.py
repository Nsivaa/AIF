import math
from queue import PriorityQueue
from typing import Dict, List, Tuple
import numpy as np
from map_utils import get_monster_location, get_valid_moves, is_cloud

MIN_COST = 1
MAX_COST = 10**5

def chebyshev_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    """
    Calculates the Chebyshev distance between two points in a grid.

    Args:
        point1 (Tuple[int, int]): The coordinates of the first point.
        point2 (Tuple[int, int]): The coordinates of the second point.

    Returns:
        int: The Chebyshev distance between the two points.
    """
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2), abs(y1 - y2))

def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    """
    Calculates the Euclidean distance between two points in a grid.

    Args:
        point1 (Tuple[int, int]): The coordinates of the first point.
        point2 (Tuple[int, int]): The coordinates of the second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def _euclidean_distance_prime(point1: Tuple[int, int], point2: Tuple[int, int]) -> Tuple[float, float]:
    """
    Calculates the derivative of the Euclidean distance between two points in a grid.

    Args:
        point1 (Tuple[int, int]): The coordinates of the first point.
        point2 (Tuple[int, int]): The coordinates of the second point.

    Returns:
        Tuple[float, float]: The partial derivatives of the Euclidean distance with respect to x and y.
    """
    x1, y1 = point1
    x2, y2 = point2
    distance = (x1 - x2)**2 + (y1 - y2)**2
    if distance == 0:
        return MAX_COST, MAX_COST 
    dx = (x1 - x2) / distance
    dy = (y1 - y2) / distance
    return dx, dy

def _compute_cost(game_map: np.ndarray, position: Tuple[int, int], color_char: int, monster_position: Tuple[int, int] = None) -> int:
    """
    Computes the cost of moving from one position to another in the game map.

    Args:
        game_map (np.ndarray): The game map.
        position (Tuple[int, int]): The current position.
        color_char (int): The color character at the current position.
        monster_position (Tuple[int, int], optional): The position of the monster. Defaults to None.

    Returns:
        int: The cost of moving from the current position to the new position.
    """
    if monster_position is None:
        if is_cloud(game_map[position], color_char):
            return MAX_COST
        return MIN_COST
    
    # monster is in known position
    if is_cloud(game_map[position], color_char):
        return MIN_COST
    edge_weight = np.sum(np.ceil(_euclidean_distance_prime(position, monster_position)))
    return edge_weight

def _build_path(parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Builds the path from the start position to the target position.

    Args:
        parent (dict): A dictionary that stores the parent nodes.
        target (Tuple[int, int]): The target position.

    Returns:
        List[Tuple[int, int]]: The path from the start position to the target position.
    """
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    path.reverse()
    return path

def a_star(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], h: callable) -> List[Tuple[int, int]]:
    """
    Finds the shortest path from the start position to the target position using the A* algorithm.

    Args:
        game_map (np.ndarray): The game map.
        color_map (np.ndarray): The color map.
        start (Tuple[int, int]): The start position.
        target (Tuple[int, int]): The target position.
        h (callable): The heuristic function.

    Returns:
        List[Tuple[int, int]]: The shortest path from the start position to the target position.
    """
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
            new_cost = cost_so_far[current] + _compute_cost(game_map, neighbor, color_map[neighbor], get_monster_location(game_map))
            
            # if neighbor has not been already visited or has been visited but with a higher cost then update cost and add to frontier
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost            #update cost
                priority = new_cost + h(neighbor, target)   #compute priority
                frontier.put(neighbor, priority)            #add neighbor to frontier
                came_from[neighbor] = current               #update parent node

    return None
