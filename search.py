import math
from queue import PriorityQueue
from typing import Dict, List, Tuple
import gym
import numpy as np
import time
import IPython.display as display
import matplotlib.pyplot as plt
from project_utils import game_map_to_kb, translate_action
from map_utils import *
from pyswip import Prolog

MIN_COST = 0
MAX_COST = 10**5
KB_PATH = 'project_kb.pl'

def chebyshev_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    x1, y1 = point1
    x2, y2 = point2
    return max(abs(x1 - x2), abs(y1 - y2))

def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def _compute_cost(game_map: np.ndarray, position: Tuple[int, int], color_map: np.ndarray, precision: str) -> int:
    monster_position = get_monster_location(game_map)

    # if monster is in known position then we exploit clouds to avoid it
    if monster_position is not None:
        if is_cloud(game_map[position], color_map[position]):
            return np.reciprocal(np.floor(float(chebyshev_distance(position, monster_position))))   # the floor gives the cloud a better cost (in some cases)
        monster_distance = chebyshev_distance(position, monster_position)
        if monster_distance == 0:
            return MAX_COST
        return np.reciprocal(float(monster_distance))
    
    # updating at each step
    if precision == 'advanced':
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
    elif precision == 'base':
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

def dynamic_path_finding(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], env: gym.Env, heuristic: callable = chebyshev_distance, precision : str = "advanced", render : bool = False, graphics = False, pixel_map: np.ndarray = None, suppress : bool = False) -> Tuple[str, str]:
    done = False
    monster_type = None
    monster_loc = None
    path = a_star(game_map, color_map, start, target, heuristic, precision=precision)
    actions = actions_from_path(start, path[1:])

    if graphics:
        image = plt.imshow(pixel_map[100:270, 500:760])

    for index, action in enumerate(actions):
        if get_monster_location(game_map) != monster_loc:   # if monster moved from previous location
            monster_loc = get_monster_location(game_map)
            # we get the monster type to derive statistics
            if monster_type is None:
                monster_type = get_monster_type(game_map)
            new_path = a_star(game_map, color_map, path[index], target, heuristic, precision)       # compute new path
            del actions[index:]                                                                     # delete actions from previous path
            actions.extend(actions_from_path(path[index], new_path[1:]))                            # add new actions to actions list
            action = actions[index]                                                                 # update action
            del path[index:]                                                                        # delete path from previous path
            path.extend(new_path)                                                                   # add new path to path list
                    
        s, _, done, info = env.step(action)
        if render:
            env.render()
        
        if graphics:
            display.display(plt.gcf())
            time.sleep(0.5)
            display.clear_output(wait=True)
            image.set_data(s['pixel'][100:270, 500:760])

        if done:
            end_status = info.get('end_status')
            if end_status == 2:
                if not suppress:
                    print("The agent successfully completed the task!")
                return "W", monster_type
            if end_status == 1:
                if not suppress:
                    print("The agent died.")
                return "L", monster_type
            if not suppress:
                print("The game ended for other reasons.")
            return "O", monster_type
        
    return "Not Finished", monster_type 


def dpt_test(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], env: gym.Env, heuristic: callable = chebyshev_distance, precision : str = "advanced", render : bool = False, graphics = False, pixel_map: np.ndarray = None, suppress : bool = False) -> Tuple[str, str]:
    kb = Prolog()
    kb.consult(KB_PATH)
    done = False
    monster_type = None
    path = a_star(game_map, color_map, start, target, heuristic, precision=precision)
    actions = actions_from_path(start, path[1:])
    
    if graphics:
        image = plt.imshow(pixel_map[100:270, 500:760])
        

    if render:
        env.render()

    for index, action in enumerate(actions):
        
        if graphics:
            display.display(plt.gcf())
           # time.sleep(0.5)
            display.clear_output(wait=True)

        if not monster_type:
            monster_type = get_monster_type(game_map)
           
        if monster_type == 'N': #NAGA -> KB TILL THE END
            asserts = game_map_to_kb(color_map, game_map, kb)
            try:
                del actions[index:]
                del path[index + 1:]
                action = list(kb.query('action(X)'))[0]
                action = action['X']
                action = translate_action(action)
                actions.append(action)
                path.append(get_resulting_position(path[index][0], path[index][1], action)) #PASSING AGENT COORDS
                actions.append(None)
            except Exception:
                action = None
                print("ERROR: impossible to perform any action. Please check assertions and definitions in KB.")
                return "O", monster_type
        
        # else:
        #     new_path = a_star(game_map, color_map, path[index], target, heuristic, precision)       # compute new path
        #     del actions[index:]                                                                     # delete actions from previous path
        #     actions.extend(actions_from_path(path[index], new_path[1:]))                            # add new actions to actions list
        #     action = actions[index]                                                                 # update action
        #     del path[index:]                                                                        # delete path from previous path
        #     path.extend(new_path)                                                                   # add new path to path list
        
        s, _, done, info = env.step(action)
        
        if graphics:
            image.set_data(s['pixel'][100:270, 500:760])
            

        if done:
            end_status = info.get('end_status')
            if end_status == 2:
                if not suppress:
                    print("The agent successfully completed the task!")
                return "W", monster_type
            if end_status == 1:
                if not suppress:
                    print("The agent died.")
                return "L", monster_type
            if not suppress:
                print("The game ended for other reasons.")
            return "O", monster_type
        
    return "Not Finished", monster_type 

def evaluate_performance(setting: str, function_to_evaluate: callable, heuristic: callable = chebyshev_distance, des_file: str = None, evaluation_steps: int = 100, graphics: bool = False) -> Tuple[int, int, List[str], List[str]]:
    monsters_win = []
    monsters_loss = []
    win = 0
    loss = 0
    noAction=0
    
    for _ in range(evaluation_steps):
        if des_file is None:
            env = gym.make(setting, observation_keys=["chars", "colors"])
        else: 
            env = gym.make(setting, des_file=des_file, observation_keys=["chars", "colors", "pixel"])
        state = env.reset()
        game_map = state["chars"]
        color_map = state["colors"]
        
        if graphics:
            pixel_map = state["pixel"]
        else:
            pixel_map = None
        
        start = get_player_location(game_map)
        target = get_target_location(game_map)
        if target == (None, None):
            continue
        actions, monster_type = function_to_evaluate(game_map, color_map, start, target, env, heuristic, suppress=True, graphics=graphics, pixel_map=pixel_map)
        if actions == "W":
            win += 1
            monsters_win.append(monster_type)
        elif actions == "O":
            noAction+=1
        else:
            loss += 1
            monsters_loss.append(monster_type)
        env.close()

    return win, loss,noAction, monsters_win, monsters_loss
