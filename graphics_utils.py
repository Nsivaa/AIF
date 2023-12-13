import time
import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np

def pre_render(game: np.ndarray):
    return plt.imshow(game[100:270, 500:760])

def render_actions(image: plt.imshow, s: np.ndarray):
    time.sleep(0.5)
    display.display(plt.gcf())
    display.clear_output(wait=True)
    image.set_data(s['pixel'][100:270, 500:760])