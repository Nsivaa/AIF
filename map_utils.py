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
    """
    Returns the location of the player on the game map.

    Parameters:
    - game_map (np.ndarray): The game map represented as a numpy array.
    - symbol (str): The symbol representing the player on the game map. Default is '@'.

    Returns:
    - Tuple[int, int]: The coordinates (row, column) of the player's location.
    """
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])
    
def get_target_location(game_map: np.ndarray, symbol : str = _Characters.STAIRS.value) -> Tuple[int, int]:
    """
    Returns the location of the target (stairs) on the game map.

    Parameters:
    - game_map (np.ndarray): The game map represented as a numpy array.
    - symbol (str): The symbol representing the target on the game map. Default is '>'.

    Returns:
    - Tuple[int, int]: The coordinates (row, column) of the target's location.
    """
    x, y = np.where(game_map == ord(symbol))
    return (x[0], y[0])

def get_monster_location(game_map: np.ndarray):
    """
    Returns the location of the first monster found on the game map.

    Parameters:
    - game_map (np.ndarray): The game map represented as a numpy array.

    Returns:
    - Tuple[int, int] or None: The coordinates (row, column) of the monster's location if found, None otherwise.
    """
    for monster in _Characters.MONSTERS.value:
        locations = np.where(game_map == ord(monster))
        if locations[0].size > 0:  # If a monster is found, return its position
            return locations[0][0], locations[1][0]
    return None  # Otherwise return None

def is_wall(position_element: int) -> bool:
    """
    Checks if the given position element represents a wall.

    Parameters:
    - position_element (int): The element at the given position on the game map.

    Returns:
    - bool: True if the position element represents a wall, False otherwise.
    """
    return chr(position_element) in _Characters.OBSTACLES.value

def is_tree(position_element: int, color_element: int) -> bool:
    """
    Checks if the given position element represents a tree.

    Parameters:
    - position_element (int): The element at the given position on the game map.
    - color_element (int): The color element at the given position on the game map.

    Returns:
    - bool: True if the position element represents a tree, False otherwise.
    """
    return position_element == ord(_Characters.HASHTAG.value) and color_element == _Colors.GREEN.value

def is_cloud(position_element: int, color_element: int) -> bool:
    """
    Checks if the given position element represents a cloud.

    Parameters:
    - position_element (int): The element at the given position on the game map.
    - color_element (int): The color element at the given position on the game map.

    Returns:
    - bool: True if the position element represents a cloud, False otherwise.
    """
    return position_element == ord(_Characters.HASHTAG.value) and color_element == _Colors.WHITE.value

def get_valid_moves(game_map: np.ndarray, colors: np.ndarray, current_position: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Returns a list of valid moves from the current position on the game map.

    Parameters:
    - game_map (np.ndarray): The game map represented as a numpy array.
    - colors (np.ndarray): The color map represented as a numpy array.
    - current_position (Tuple[int, int]): The current position on the game map.

    Returns:
    - List[Tuple[int, int]]: A list of valid moves as coordinates (row, column).
    """
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
    """
    Returns a list of actions (moves) to follow the given path from the start position.

    Parameters:
    - start (Tuple[int, int]): The start position on the game map.
    - path (List[Tuple[int, int]]): The path to follow as a list of coordinates (row, column).

    Returns:
    - List[int]: A list of actions (moves) represented as integers.
    """
    actions = []
    row_s, col_s = start
    for (row, col) in path:
        if row_s == row:
            if col_s > col:
                actions.append(_Moves.WEST.value)
            else: actions.append(_Moves.EAST.value)
        elif col_s == col:
            if row_s > row:
                actions.append(_Moves.NORTH.value)
            else: actions.append(_Moves.SOUTH.value)
        elif row_s > row:
            if col_s > col:
                actions.append(_Moves.NORTH_WEST.value)
            else: actions.append(_Moves.NORTH_EAST.value)
        elif row_s < row:
            if col_s > col:
                actions.append(_Moves.SOUTH_WEST.value)
            else: actions.append(_Moves.SOUTH_EAST.value)
        row_s = row
        col_s = col
    
    return actions
