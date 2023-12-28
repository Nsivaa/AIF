from typing import List, Tuple
import time
import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


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



def plot(data, data2, width_plot, labels, x_label, y_label, title, type):
    
    if type == "1":
        # Create a bar chart
        plt.bar(labels, data, color=['orange', 'green'], width=width_plot)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)


    elif type == "2":
        # Utilizzo di Counter per contare gli elementi
        counter_w = Counter(data)
        counter_l = Counter(data2)

        # Prepara i dati per il grafico
        monsters = [labels[elem] for elem in counter_w.keys()]
        occurrencies_wins = list(counter_w.values())
        occurrencies_lost = list(counter_l.values())

        # Posizioni X per i gruppi di barre
        x = np.arange(len(monsters))

        # Creazione delle barre
        fig, ax = plt.subplots()
        plt.bar(x - width_plot/2, occurrencies_wins, width_plot, label='Wins', color='orange')
        plt.bar(x + width_plot/2, occurrencies_lost, width_plot, label='Losses', color='green')

        # Aggiungi titolo e etichette agli assi
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(x, monsters)
        plt.legend()

        plt.show()
    
    plt.show()