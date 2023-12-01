from typing import List
import time
import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np

def render_actions(actions: List, env, game: np.ndarray):
    image = plt.imshow(game[100:270, 500:760])
    for action in actions:
        s, _, done, info = env.step(action)
        time.sleep(0.5)
        display.display(plt.gcf())
        display.clear_output(wait=True)
        image.set_data(s['pixel'][100:270, 500:760])
        # Check if the game has ended
        if done:
            end_status = info.get('end_status')
            if end_status == 2: 
                print("The agent successfully completed the task!")
                break
            elif end_status == 1:
                print("The agent died.")
                break
            else:
                print("The game ended for other reasons.")
