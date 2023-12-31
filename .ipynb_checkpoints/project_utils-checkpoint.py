import matplotlib.pyplot as plt
import IPython.display as display
import time
from pyswip import Prolog
from minihack import LevelGenerator
from minihack import RewardManager

def define_reward():
    reward_manager = RewardManager()
    #THERE IS NO DEATH EVENT SO WE USE THIS
    # -> DEATH SHOULD BE PENALISED MORE THAN RUNNING OUT OF STEPS
    # reward_manager.add_message_event(msgs=["End status: DEATH"], reward= -0.5, terminal_required=False, terminal_sufficient=True) 
    # ^ DOESNT WORK
    
    return reward_manager

def perform_action(action, env):

    if 'northeast' in action: action_id = 4
    elif 'southeast' in action: action_id = 5
    elif 'southwest' in action: action_id = 6
    elif 'northwest' in action: action_id = 7
    elif 'north' in action: action_id = 0
    elif 'east' in action: action_id = 1
    elif 'south' in action: action_id = 2
    elif 'west' in action: action_id = 3

    # print(f'Action performed: {repr(env.actions[action_id])}')
    obs, reward, done, info = env.step(action_id)
    return obs, reward, done, info

def process_state(obs: dict, kb: Prolog, monsters: list, steps: int):
    kb.retractall("position(_,_,_)")
    asserts = []
    for i in range(21):
        for j in range(79):
            if not (obs['screen_descriptions'][i][j] == 0).all():
                obj = bytes(obs['screen_descriptions'][i][j]).decode('utf-8').rstrip('\x00')
                if 'tree' in obj:
                    kb.asserta(f'position(tree, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')
                elif 'cloud' in obj:
                    kb.asserta(f'position(cloud, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'floor' in obj:
                    kb.asserta(f'position(floor, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'down' in obj:
                    kb.asserta(f'position(down_stairs, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'dark' in obj:
                    kb.asserta(f'position(dark, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'human' in obj:
                    kb.asserta(f'position(agent, {i}, {j})') #maybe use info from obs?
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'up' in obj:
                    kb.asserta(f'position(up_stairs, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                elif 'boulder' in obj:
                    kb.asserta(f'position(boulder, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                is_there_monster = [value for value in monsters if value in obj]
                if (is_there_monster):
                    kb.asserta(f'position(enemy, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j})')

                try:    
                    enemies_list = list(kb.query('position(enemy,_,_)'))[0]
                except Exception as e:
                    enemies_list = None
                if enemies_list is not None and len(enemies_list) != 0:
                    print(f'ENEMIES: {enemies_list}')

    debug_KB = Prolog()
    debug_KB.consult("debug_kb.pl")
    for string in asserts:
        print(f'adding string ; {}
        ')
        debug_KB.asserta(string)
    
    kb.retractall("position(agent,_,_,_)")
    kb.asserta(f"position(agent, _, {obs['blstats'][1]}, {obs['blstats'][0]})")


# indexes for showing the image are hard-coded
def show_match(states: list):
    image = plt.imshow(states[0][115:275, 480:750])
    for state in states[1:]:
        time.sleep(0.75)
        display.display(plt.gcf())
        display.clear_output(wait=True)
        image.set_data(state[115:275, 480:750])
    time.sleep(0.25)
    display.display(plt.gcf())
    display.clear_output(wait=True)