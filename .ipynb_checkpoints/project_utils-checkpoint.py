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
    reward_manager.add_message_event(msgs=["END STATUS: DEATH"], reward= -0.5, terminal_required=False, terminal_sufficient=True) #???

    return reward_manager

def perform_action(action, env):

    # Movement/Attack/Run/Get_To_Weapon actions
    # in the end, they all are movement in a direction
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

def process_state(obs: dict, kb: Prolog, monster: List(str), weapon: str):
    kb.retractall("position(_,_,_,_)")

    for i in range(21):
        for j in range(79):
            if not (obs['screen_descriptions'][i][j] == 0).all(): #.all() returns TRUE if all the items are true:???
                obj = bytes(obs['screen_descriptions'][i][j]).decode('utf-8').rstrip('\x00')
                if 'tree' in obj:
                    kb.asserta(f'position(tree, {i}, {j})')
                elif 'cloud' in obj:
                    kb.asserta(f'position(cloud, {i}, {j})')
                elif 'floor' in obj:
                    kb.asserta(f'position(floor, {i}, {j})')
                elif 'down' in obj:
                    kb.asserta(f'position(down_stairs, {i}, {j})')
                elif 'human' in obj:
                    kb.asserta(f'position(player, {i}, {j})')
                elif 'dark' in obj:
                    kb.asserta(f'position(dark, {i}, {j})')
                elif obj in monster:
                    kb.asserta(f'position(enemy, {monster.replace(" ", "")}, {i}, {j})')                    

                
    kb.retractall("wields_weapon(_,_)")
    kb.retractall("has(agent,_,_)")    
    for obj in obs['inv_strs']:
        obj = bytes(obj).decode('utf-8').rstrip('\x00')
        if 'weapon in hand' in obj:
            # the actual name of the weapon is in position 2
            wp = obj.split()[2]
            kb.asserta(f'wields_weapon(agent, {wp})')
        if 'apple' in obj:
            kb.asserta('has(agent, comestible, apple)')

    kb.retractall("position(agent,_,_,_)")
    kb.retractall("health(_)")
    kb.asserta(f"position(agent, _, {obs['blstats'][1]}, {obs['blstats'][0]})")
    kb.asserta(f"health({int(obs['blstats'][10]/obs['blstats'][11]*100)})")

    message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
    if 'You see here' in message:
        if 'apple' in message:
            kb.asserta('stepping_on(agent, comestible, apple)')
        if 'sword' in message:
            kb.asserta(f'stepping_on(agent, weapon, {weapon})')

    for m in message.split('.'):
        if 'picks' in m:
            if 'apple' in m:
                print('The enemy took your apple!')

# indexes for showing the image are hard-coded
def show_match(states: list):
    image = plt.imshow(states[0][115:275, 480:750])
    for state in states[1:]:
        time.sleep(0.25)
        display.display(plt.gcf())
        display.clear_output(wait=True)
        image.set_data(state[115:275, 480:750])
    time.sleep(0.25)
    display.display(plt.gcf())
    display.clear_output(wait=True)