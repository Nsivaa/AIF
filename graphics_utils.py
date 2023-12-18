from typing import List, Tuple
import time
import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np

def render_actions(actions: List, env, game: np.ndarray, width: Tuple[int, int] = None, height: Tuple[int, int] = None):
    if width is not None and height is not None:
        image = plt.imshow(game[width[0]:width[1], height[0]:height[1]])
    else: 
        image = plt.imshow(game)
    for action in actions:
        s, _, done, info = env.step(action)
        time.sleep(0.5)
        display.display(plt.gcf())
        display.clear_output(wait=True)
        if width is not None and height is not None:
            image.set_data(s['pixel'][width[0]:width[1], height[0]:height[1]])
        else:
            image.set_data(s['pixel'])
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