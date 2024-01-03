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
from graphics_utils import *
from itertools import groupby


MIN_COST = 0
MAX_COST = 10**5
KB_PATH = 'kbs/project_kb.pl'

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
        if clouds:
            # instead, if monster is in unkown position then we sum the "danger" of each cloud hiding a monster
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

#versione con stessa gestione di Naga e Gigante
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
            
        if monster_type == 'N' or monster_type == "H" : #NAGA -> KB TILL THE END
            asserts = game_map_to_kb(color_map, game_map, kb) 
            temp= asserts
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
                return "O", monster_type
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

def get_actions_distance(monsterR: int, monsterC: int, playerR: int, playerC: int) -> int:
    deltaR=abs(monsterR-playerR)
    deltaC = abs(monsterC-playerC)
    if monsterR == playerR:
        return deltaC
    if monsterC == playerC:
        return deltaR
    if deltaR == deltaC:
        return deltaR
    #una mossa in diagonale verso il target e ripeti
    #target è in basso a destra
    if monsterR> playerR:
        if monsterC > playerC:
            #mostro in basso a destra
            return 1 + get_actions_distance(monsterR,monsterC,playerR + 1, playerC+1)
        else:
            #mostro in basso a sinistra
            return 1 + get_actions_distance(monsterR,monsterC,playerR + 1, playerC-1)
    else:
        if monsterC > playerC:
            #mostro in alto a destra
            return 1 + get_actions_distance(monsterR,monsterC,playerR - 1, playerC+1)
        else:
            #mostro in alto a sinistra
            return 1 + get_actions_distance(monsterR,monsterC,playerR - 1, playerC-1)
        
#versione con gestione differente per gigante rispetto a Naga
def dpt_testv2(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], target: Tuple[int, int], env: gym.Env, heuristic: callable = chebyshev_distance, precision : str = "advanced", render : bool = False, graphics = False, pixel_map: np.ndarray = None, suppress : bool = False) -> Tuple[str, str]:
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
    lastMoveKB=False
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
                return "O", monster_type 
        elif monster_type == 'H':
            #mostro è gigante, Se è a max due blocchi di distanza ->A* else KB
            #quando scompare tra le nuvole segue la KB
            monster_position = get_monster_location(game_map)
            player_position = get_player_location(game_map) 
            if monster_position == None:
                distance=-1
            else:
                distance=get_actions_distance(monster_position[0],monster_position[1],player_position[0],player_position[1])
            if distance <= 2 :
                #KB
                lastMoveKB = True
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
                    return "O", monster_type
            #ricalcola A* quando distance è maggiore di 2 e avevamo switchato a KB lo step scorso   
            elif lastMoveKB:
                lastMoveKB= False
                new_path = a_star(game_map, color_map, get_player_location(game_map), target, heuristic, precision)       # compute new path
                del actions[index:]                                                                     # delete actions from previous path
                actions.extend(actions_from_path(path[index], new_path[1:]))                            # add new actions to actions list
                action = actions[index]                                                                 # update action
                del path[index:]                                                                        # delete path from previous path
                path.extend(new_path)
                # add new path to path list
        
        
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


def evaluate_performance(setting: str, function_to_evaluate: callable, heuristic: callable = chebyshev_distance, des_file: str = None, evaluation_steps: int = 100, graphics: bool = False, po: bool = False) -> Tuple[int, int, List[str], List[str]]:
    monsters_win = []
    monsters_loss = []
    win = 0
    loss = 0
    noAction=0
    
    for _ in range(evaluation_steps):
        #ogni episodio
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

        if po:
            actions, monster_type = function_to_evaluate(game_map, color_map, start, env, heuristic, graphics=graphics, pixel_map=pixel_map, suppress=True)
        else:
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

    return win, loss , noAction, monsters_win, monsters_loss



def frontier_position2(possible_targets):
    # Ordina le tuple prima per il primo elemento (x) e poi per il secondo (y)
    sorted_tuples = sorted(possible_targets, key=lambda x: (x[0], x[1]))

    # Raggruppa le tuple per il primo elemento
    grouped = groupby(sorted_tuples, key=lambda x: x[0])
    results = []
    for _, group in grouped:
        tuples = list(group)
        min_tuple = min(tuples, key=lambda x: x[1])
        max_tuple = max(tuples, key=lambda x: x[1])
        results.append(min_tuple)
        if min_tuple != max_tuple:
            results.append(max_tuple)

    return results

def frontier_position1(entire_map, game_map, color_map):
    frontier = []

    # Definisci le direzioni dei vicini
    neighbor_directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    # Controlla ciascun vicino di ciascuna posizione
    for position in entire_map:
        x, y = position
        for dx, dy in neighbor_directions:
            neighbor_pos = (x + dx, y + dy)
            x, y = position

            # Se a una posizione manca anche un solo vicino, è una posizione di frontiera
            # Ma viene aggiunta solo se non è un albero o il mostro (ovviamente, non possono essere presi questi comne target) 
            if neighbor_pos not in entire_map:
                if not ((is_tree(game_map[x,y], color_map[x,y])) and (position != get_monster_location(game_map))):
                    frontier.append(position)
                break

    return frontier

# Recupera le posizioni di tutto nella mappa
def entire_map(game_map, color_map):
    entire_map = []
    if get_floor_location(game_map):
        entire_map = get_floor_location(game_map)
    
    if get_clouds_location(game_map, color_map):
        entire_map += get_clouds_location(game_map, color_map)
    
    if get_tree_location(game_map, color_map):
        entire_map += get_tree_location(game_map, color_map)
    
    if get_monster_location(game_map):
        entire_map += get_monster_location(game_map)

    entire_map.append(get_player_location(game_map))

    return entire_map

def next_target(game_map, color_map, prev_targets, current_position, monster_position):
    possible_targets = []

    if get_floor_location(game_map):
        possible_targets = get_floor_location(game_map)
        if prev_targets:
            possible_targets = [x for x in possible_targets if not any(el in prev_targets for el in x)]

    if get_clouds_location(game_map, color_map):
        # Aggiungi le nuvole alle posizioni di potenziali target se:
        # - ci sono 3 o meno posizioni esplorabili
        # - il mostro è visibile
        if len(possible_targets) <= 3 or monster_position is not None:
            possible_targets += get_clouds_location(game_map, color_map)
    
    if len(possible_targets) > 5:
        # Trova come posizione di frontiera solo i max/min di una colonna
        results = frontier_position2(possible_targets)
    else:
        map_ = entire_map(game_map, color_map)
        # Trova tutte le posizioni di frontiera (walkable, quindi solo nuvole o floor)
        results = frontier_position1(map_, game_map, color_map)

    if current_position in results:
        results.remove(current_position)
    
    # Genera un indice casuale
    indice_casuale = np.random.randint(0, len(results))
    # Seleziona l'elemento corrispondente all'indice casuale
    prossima_posizione = results[int(indice_casuale)]

    return prossima_posizione



def dynamic_pathfinding_po(game_map: np.ndarray, color_map: np.ndarray, start: Tuple[int, int], env: gym.Env, heuristic: callable = chebyshev_distance, precision : str = "advanced", render : bool = False, graphics = False, pixel_map: np.ndarray = None, suppress : bool = True) -> Tuple[str, str]:
    done = False
    stairs = False
    visited_targets = []
    monster_position = None
    monster_type = None
    prev_target = None
    # Flag per vedere se è stata aggiunta la posizione fittizia
    flag = False

    if get_monster_location(game_map):
        monster_position = get_monster_location(game_map)
        monster_type = get_monster_type(game_map)

    # Inizializza un target 
    if get_target_location(game_map):
        target = get_target_location(game_map)
        stairs = True
    else:
        target = next_target(game_map, color_map, visited_targets, start, monster_position)
        visited_targets.append(target)
    
    prev_target = target
    path = a_star(game_map, color_map, start, target, chebyshev_distance, precision=precision)

    if graphics:
        image = plt.imshow(pixel_map[100:270, 500:760])

    if path is not None:
        actions = actions_from_path(start, path[1:])
        # Se la lunghezza di azioni è uguale a 1, aggiungiamo un'azione casuale (solo per non uscire subito dal ciclo for)
        # Questa azione fasulla sarà rimossa dopo e non influirà sul percorso dell'agente (l'agente non la compierà mai)
        if len(actions) == 1 and stairs == False:
            actions.append(1)
            flag = True

        for index, action in enumerate(actions):
            # Se non hai ancora trovato le scale, controlla se le vedi, altrimenti prendi come obiettivo una casella casuale
            # Una volta che hai trovato le scale il target non cambia più (nemmeno il percorso, a meno che non ci sia il mostro)
            if stairs == False:
                if get_target_location(game_map):
                    target = get_target_location(game_map)
                    stairs = True
                else:
                    monster_position =  get_monster_location(game_map)
                    if monster_position:
                        monster_type = get_monster_type(game_map)
                    # Se prima è stata aggiunta la posizione fittizia, calcola un nuovo target 
                    if flag == True:
                        possible_target = next_target(game_map, color_map, prev_target, path[index], monster_position)
                        prev_target = target
                        target = possible_target
                        # Aggiungi il target a quelli già presi come obiettivo 
                        if target not in visited_targets:
                            visited_targets.append(target)

            if prev_target != target or monster_position is not None or stairs == True or flag == True:
                # A* ricalcolato quando cambia il target (= siamo arrivati al target), quando c'è il mostro (senza cambiare target),
                # O quando troviamo le scale (la prima volta)
                new_path = a_star(game_map, color_map, path[index], target, chebyshev_distance, precision)       
            
                if new_path is not None:
                    del actions[index:]                                     
                    actions.extend(actions_from_path(path[index], new_path[1:]))           
                    action = actions[index]                                                                 
                    del path[index:]                                    
                    path.extend(new_path)
                else: 
                    break

            s, _, done, info = env.step(action)

            # Se aggiungiamo la posizione fittizia, impostiamo il flag a True
            if len(actions[index:]) == 1 and stairs == False:
                actions.append(1)
                flag = True 
            else:
                flag = False

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

def solve_and_plt(env: gym.Env, heuristic: callable, precision: str, plt_width: Tuple[int, int], plt_height: Tuple[int, int], dynamic: bool = False, suppress = False, rate: bool = False, graph: bool = True):
    state = env.reset()
    game_map = state["chars"]
    color_map = state["colors"]
    pixel_map = state["pixel"]

    start = get_player_location(game_map)
    target = get_target_location(game_map)

    if dynamic:
        x, y = dynamic_path_finding(game_map, color_map, start, target, env, heuristic, precision=precision, graphics=graph, pixel_map=pixel_map, suppress=suppress)
        if rate:
            return x, y
    else:
        path = a_star(game_map, color_map, start, target, heuristic, precision=precision)
        actions = actions_from_path(start, path[1:])
        x, y = render_actions(actions, env, pixel_map, plt_width, plt_height, suppress = suppress, game_map = game_map, graphics = graph)
        if rate:
            return x, y

def simple_evaluation(env: gym.Env, precision: str, dynamic: bool = False, steps: int = None):
    i = 0
    win = 0

    while i < steps:
        actions, monster_type = solve_and_plt(env, heuristic = chebyshev_distance, precision = precision, plt_width=(100, 270), plt_height=(500, 760), dynamic = dynamic, suppress = True, rate = True, graph = False)

        if actions == "W":
            win += 1
        i += 1

    return win

