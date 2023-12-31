from typing import Tuple, List
from enum import Enum
import numpy as np

class _Colors(Enum):
    GREEN = 2
    WHITE = 15

class _Characters(Enum):
    PLAYER = "@"
    MONSTERS = "LNHODT"
    OBSTACLES = "|- "
    HASHTAG = "#"
    STAIRS = ">"

class _Moves(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTH_EAST = 4
    SOUTH_EAST = 5
    SOUTH_WEST = 6
    NORTH_WEST = 7


def get_player_location(game_map: np.ndarray, symbol : str = _Characters.PLAYER.value) -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])
    
def get_target_location(game_map: np.ndarray, symbol : str = _Characters.STAIRS.value) -> Tuple[int, int]:
    x, y = np.where(game_map == ord(symbol))
    if x.size == 0 or y.size == 0:
        return (None, None)
    return (x[0], y[0])

def get_monster_location(game_map: np.ndarray):
    for monster in _Characters.MONSTERS.value:
        locations = np.where(game_map == ord(monster))
        if locations[0].size > 0:  # If a monster is found, return its position
            return locations[0][0], locations[1][0]
    return None  # Otherwise return None

def get_monster_type(game_map: np.ndarray) -> str:
    for monster in _Characters.MONSTERS.value:
        locations = np.where(game_map == ord(monster))
        if locations[0].size > 0:
            return monster
    return None

def get_clouds_location(game_map: np.ndarray, color_map: np.ndarray) -> List[Tuple[int, int]]:
    locations = np.where(np.logical_and(game_map == ord(_Characters.HASHTAG.value), color_map != _Colors.GREEN.value))
    if locations[0].size > 0:
        return list(zip(locations[0], locations[1]))

def is_wall(position_element: int) -> bool:
    return chr(position_element) in _Characters.OBSTACLES.value

def is_tree(position_element: int, color_element: int) -> bool:
    return position_element == ord(_Characters.HASHTAG.value) and color_element == _Colors.GREEN.value

def is_cloud(position_element: int, color_element: int) -> bool:
    return position_element == ord(_Characters.HASHTAG.value) and color_element != _Colors.GREEN.value

def get_valid_moves(game_map: np.ndarray, colors: np.ndarray, current_position: Tuple[int, int]) -> List[Tuple[int, int]]:
    x_limit, y_limit = game_map.shape
    valid = []
    x, y = current_position    
    # North
    if y - 1 > 0 and not is_wall(game_map[x, y-1]) and not is_tree(game_map[x, y-1], colors[x, y-1]):
        valid.append((x, y-1)) 
    # East 
    if x + 1 < x_limit and not is_wall(game_map[x+1, y]) and not is_tree(game_map[x+1, y], colors[x+1, y]):
        valid.append((x+1, y)) 
    # South
    if y + 1 < y_limit and not is_wall(game_map[x, y+1]) and not is_tree(game_map[x, y+1], colors[x, y+1]):
        valid.append((x, y+1)) 
    # West
    if x - 1 > 0 and not is_wall(game_map[x-1, y]) and not is_tree(game_map[x-1, y], colors[x-1, y]):
        valid.append((x-1, y))
    # North - West
    if x - 1 > 0 and y - 1 > 0 and not is_wall(game_map[x-1, y-1]) and not is_tree(game_map[x-1, y-1], colors[x-1, y-1]):
        valid.append((x-1, y-1))
    # South - East
    if x + 1 < x_limit and y + 1 < y_limit and not is_wall(game_map[x+1, y+1]) and not is_tree(game_map[x+1, y+1], colors[x+1, y+1]):
        valid.append((x+1, y+1))
    # Southh - West
    if x - 1 > 0 and y + 1 < y_limit and not is_wall(game_map[x-1, y+1]) and not is_tree(game_map[x-1, y+1], colors[x-1, y+1]):
        valid.append((x-1, y+1))
    # Notht - East 
    if x + 1 < x_limit and y - 1 > 0 and not is_wall(game_map[x+1, y-1]) and not is_tree(game_map[x+1, y-1], colors[x+1, y-1]):
        valid.append((x+1, y-1))

    return valid


def actions_from_path(start: Tuple[int, int], path: List[Tuple[int, int]]) -> List[int]:
    actions = []
    col_s, row_s = start
    for (col, row) in path:
        if col_s == col:
            if row_s > row:
                actions.append(_Moves.WEST.value)
            else: actions.append(_Moves.EAST.value)
        elif row_s == row:
            if col_s > col:
                actions.append(_Moves.NORTH.value)
            else: actions.append(_Moves.SOUTH.value)
        elif col_s > col:
            if row_s > row:
                actions.append(_Moves.NORTH_WEST.value)
            else: actions.append(_Moves.NORTH_EAST.value)
        elif col_s < col:
            if row_s > row:
                actions.append(_Moves.SOUTH_WEST.value)
            else: actions.append(_Moves.SOUTH_EAST.value)
        col_s = col
        row_s = row
    
    return actions
