import numpy as np
from typing import Tuple, List


def get_player_location(game_map: np.ndarray, symbol : str = "@") -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])
    

#where the stairs are
def get_target_location(game_map: np.ndarray, symbol : str = ">") -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])


def get_monster_location(game_map: np.ndarray):
    monsters = "LNHODT" 
    for monster in monsters:
        locations = np.where(game_map == ord(monster))
        if locations[0].size > 0:  # If a monster is found, return its position
            return locations[0][0], locations[1][0]
    return None  # Otherwise return None


def is_wall(position_element: int) -> bool:
    obstacles = "|- "
    return chr(position_element) in obstacles
 

def is_tree(x, y, colors) -> bool:
    tree = 2
    return colors[x, y] == tree


def is_cloud(position_element, x, y, colors) -> bool:
    cloud = "#"
    return (colors[x, y] != 2) & (chr(position_element) == cloud)


def get_valid_moves(game_map: np.ndarray, current_position: Tuple[int, int], colors: np.ndarray) -> List[Tuple[int, int]]:
    x_limit, y_limit = game_map.shape
    valid = []
    x, y = current_position    
    # North
    if y - 1 > 0 and not is_wall(game_map[x, y-1]) and not is_tree(x, y-1, colors):
        valid.append((x, y-1)) 
    # East 
    if x + 1 < x_limit and not is_wall(game_map[x+1, y]) and not is_tree(x+1, y, colors):
        valid.append((x+1, y)) 
    # South
    if y + 1 < y_limit and not is_wall(game_map[x, y+1]) and not is_tree(x, y+1, colors):
        valid.append((x, y+1)) 
    # West
    if x - 1 > 0 and not is_wall(game_map[x-1, y]) and not is_tree(x-1, y, colors):
        valid.append((x-1, y))
    # Left - Down
    if x - 1 > 0 and y - 1 > 0 and not is_wall(game_map[x-1, y-1]) and not is_tree(x-1, y-1, colors):
        valid.append((x-1, y-1))
    # Rigth - Up
    if x + 1 < x_limit and y + 1 < y_limit and not is_wall(game_map[x+1, y+1]) and not is_tree(x+1, y+1, colors):
        valid.append((x+1, y+1))
    # Left - Up
    if x - 1 > 0 and y + 1 < y_limit and not is_wall(game_map[x-1, y+1]) and not is_tree(x-1, y+1, colors):
        valid.append((x-1, y+1))
    # Rigth - Down 
    if x + 1 < x_limit and y - 1 > 0 and not is_wall(game_map[x+1, y-1]) and not is_tree(x+1, y-1, colors):
        valid.append((x+1, y-1))

    return valid