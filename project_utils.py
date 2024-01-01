import matplotlib.pyplot as plt
import IPython.display as display
import time
from pyswip import Prolog
from minihack import RewardManager
from map_utils import *
import numpy as np

def define_reward():
    reward_manager = RewardManager()
    return reward_manager

def translate_action(action):
    
    if 'northeast' in action: action_id = 4
    elif 'southeast' in action: action_id = 5
    elif 'southwest' in action: action_id = 6
    elif 'northwest' in action: action_id = 7
    elif 'north' in action: action_id = 0
    elif 'east' in action: action_id = 1
    elif 'south' in action: action_id = 2
    elif 'west' in action: action_id = 3

    return action_id

def perform_action(action, env):
    
    action_id = translate_action(action)
    # print(f'Action performed: {repr(env.actions[action_id])}')
    obs, reward, done, info = env.step(action_id)
    return obs, reward, done, info

def game_map_to_kb(color_map: np.ndarray, game_map: np.ndarray, kb: Prolog) -> List:
    kb.retractall("position(_,_,_)")
    asserts = []

    #GETTING PLAYER COORDS
    agent_r, agent_c = get_player_location(game_map) #
    kb.asserta(f'position(agent, {agent_r}, {agent_c})') 
    asserts.append(f'position(agent, {agent_r}, {agent_c}).')

    #GETTING STAIRS COORD
    target_r, target_c = get_target_location(game_map) 
    if target_r is not None and target_c is not None:
        kb.asserta(f'position(down_stairs, {target_r}, {target_c})')
        asserts.append(f'position(down_stairs, {target_r}, {target_c}).') 
    else:
        print("No stairs seen")

    #GETTING MOSNTER COORDS
    monster_position = get_monster_location(game_map)
    if monster_position is not None:
        monster_r, monster_c = monster_position
        kb.asserta(f'position(enemy, {monster_r}, {monster_c})')
        asserts.append(f'position(enemy, {monster_r}, {monster_c}).')
        
    for i in range(game_map.shape[0]):
        for j in range(game_map.shape[1]):
            if not (game_map[i][j] == 0).all():
                obj = (game_map[i][j])
                
                if is_tree(obj,(color_map[i][j])):
                    kb.asserta(f'position(tree, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j}).')
                    
                elif is_cloud(obj,(color_map[i][j])):
                    kb.asserta(f'position(cloud, {i}, {j})')
                    asserts.append(f'position(cloud, {i}, {j}).')

                elif is_floor(obj):
                    kb.asserta(f'position(floor, {i}, {j})')
                    asserts.append(f'position(floor, {i}, {j}).')

                elif is_upstairs(obj):
                    kb.asserta(f'position(up_stairs, {i}, {j})')
                    asserts.append(f'position(up_stairs, {i}, {j}).')

    return asserts

def evaluate(num_ep : int, max_steps : int, kb_path : str, env, speed : str, show: bool):
    monsters_losses = {'giant' : 0, 'naga' : 0, 'lich' : 0, 'ogre' : 0, 'dragon' : 0, 'troll' : 0, 'unknown' : 0} #possible monsters in this environment
    monsters_wins = {'giant' : 0, 'naga' : 0, 'lich' : 0, 'ogre' : 0, 'dragon' : 0, 'troll' : 0, 'unknown' : 0} #possible monsters in this environment
    giant_likes = ["ettin", "minotaur", "titan"]
    slow = False
    if speed == "slow":
        slow = True
        
    rewards = []
    KB = Prolog()
    KB.consult(kb_path)
    for episode in range(num_ep):
        # count the number of steps of the current episode
        steps = 0
        # store the cumulative reward
        reward = 0.0
        # collect obs['pixel'] to visualize
        ep_states = []
        # reset KB before eacj episode starts
        KB.retractall("already_walked(_,_)")
        KB.retractall("lastKnownEnemyPosition(_,_)")
    
        obs = env.reset()
        if show:
            ep_states.append(obs['pixel'])
        done = False
        monster_name = None
        # Main loop
        while not done and steps < max_steps:
            # Get the observation from the env and assert the facts in the kb 
            _, monster_name=process_state(obs, KB, monsters_wins, steps, monster_name)
            # print(f'> Current player position: {player_pos}')
            # Query Prolog
            # Run the inference and get the action to perform
            # Get the first answer from Prolog -> the top-priority action
            try:
                action = list(KB.query('action(X)'))[0]
                action = action['X']
                #print(action)
                #time.sleep(0.5)
            except Exception as e:
                action = None
    
            # Perform the action in the environment
            if action: 
                obs, reward, done, info = perform_action(action, env)
            
                ep_states.append(obs['pixel'])
               # env.render()
            
            steps += 1
    
        # Display game with interface
        if show:
            show_match(ep_states, slow)
        # Print information about the ended episode
        print(f'Episode {episode} - {steps} steps')
        print("Episode = "+str(episode),end="\r")
        
        #translate monster name to dictionary key equivalent
        if monster_name is None:
            monster_name = 'unknown'

        elif monster_name in giant_likes:
            monster_name = "giant"

        elif monster_name is "Olog-hai":
            monster_name = "troll"

        try:
            print(f'End status: {info["end_status"].name}')
            #updating monster count
            if "DEATH" in info["end_status"].name:
                monsters_losses[monster_name] += 1
            elif "SUCCESS" in info["end_status"].name:
                monsters_wins[monster_name] += 1
        except NameError as e1:
            print(f'No end status info available')

        rewards.append(reward)
        obs = env.reset()
        KB.retractall("previous_agent_position(_,_)")
        total_rewards = sum(rewards)
    return monsters_wins, monsters_losses, total_rewards

def process_state(obs: dict, kb: Prolog, monsters: List, steps: int, monster: str):
    kb.retractall("position(_,_,_)")
    asserts = []
    for i in range(21):
        for j in range(79):
            if not (obs['screen_descriptions'][i][j] == 0).all():
                obj = bytes(obs['screen_descriptions'][i][j]).decode('utf-8').rstrip('\x00')
                if 'tree' in obj:
                    kb.asserta(f'position(tree, {i}, {j})')
                    asserts.append(f'position(tree, {i}, {j}).')
                elif 'cloud' in obj:
                    kb.asserta(f'position(cloud, {i}, {j})')
                    asserts.append(f'position(cloud, {i}, {j}).')

                elif 'floor' in obj:
                    kb.asserta(f'position(floor, {i}, {j})')
                    asserts.append(f'position(floor, {i}, {j}).')

                elif 'down' in obj:
                    kb.asserta(f'position(down_stairs, {i}, {j})')
                    asserts.append(f'position(down_stairs, {i}, {j}).')

                elif 'dark' in obj:
                    kb.asserta(f'position(dark, {i}, {j})')
                    asserts.append(f'position(dark, {i}, {j}).')

                elif 'human' in obj:
                    kb.asserta(f'position(agent, {i}, {j})') #maybe use info from obs?
                    asserts.append(f'position(agent, {i}, {j}).')

                elif 'up' in obj:
                    kb.asserta(f'position(up_stairs, {i}, {j})')
                    asserts.append(f'position(up_stairs, {i}, {j}).')

                elif 'boulder' in obj:
                    kb.asserta(f'position(boulder, {i}, {j})')
                    asserts.append(f'position(boulder, {i}, {j}).')
                if monster is None:
                    monster = [key for key in monsters.keys() if key in obj]
                    if (monster):
                        monster = str(monster[0])
                        kb.asserta(f'position(enemy, {i}, {j})')
                        asserts.append(f'position(enemy, {i}, {j}).')
                    else:
                        monster = None
    
    
    return asserts, monster

# DES_COORDS = [111:250, 320:495], NON-DES COORDS = [115:275, 480:750]

# indexes for showing the image are hard-coded
#if we are using a .des file instead of hidenseek, coordinates change
def show_match(states: list, slow : bool):
        image = plt.imshow(states[0][115:275, 480:750])
        for state in states[1:]:
            if bool:
                time.sleep(0.75)
            display.display(plt.gcf())
            display.clear_output(wait=True)
            image.set_data(state[115:275, 480:750])
        if bool:
            time.sleep(0.25)
        display.display(plt.gcf())
        display.clear_output(wait=True)
