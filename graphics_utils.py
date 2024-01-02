from typing import List, Tuple
import time
import IPython.display as display
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from map_utils import get_monster_location, get_monster_type



def render_actions(actions: List, env, game: np.ndarray, width: Tuple[int, int] = None, height: Tuple[int, int] = None, suppress: bool = False, graphics: bool = True, game_map: np.ndarray = None):
    
    monster = None

    if graphics:
        if width is not None and height is not None:
            image = plt.imshow(game[width[0]:width[1], height[0]:height[1]])
        else: 
            image = plt.imshow(game)

    for action in actions:
        s, _, done, info = env.step(action)


        if graphics:
            display.display(plt.gcf())
            time.sleep(0.5)
            display.clear_output(wait=True)
            if width is not None and height is not None:
                image.set_data(s['pixel'][width[0]:width[1], height[0]:height[1]])
            else:
                image.set_data(s['pixel'])
        
        if get_monster_location(game_map):
            monster = get_monster_type(game_map)

        # Check if the game has ended
        if done:
            end_status = info.get('end_status')
            if end_status == 2:
                if not suppress:
                    print("The agent successfully completed the task!")
                return "W", monster
            if end_status == 1:
                if not suppress:
                    print("The agent died.")
                return "L", monster
            if not suppress:
                print("The game ended for other reasons.")
            return "O", monster
    
    return "Not Finished", monster


def plot(data, plot_type, width_plot, labels, y_label, title, data2=None, x_label=None, percentage=None):
    
    if plot_type == "1":
        
        # Create a bar chart
        if percentage:
            data =  [(value / percentage) * 100 for value in data]
            # Calcola il valore massimo nei dati
            max_value = max(data)
            # Imposta l'intervallo dell'asse y
            plt.ylim(top=max_value + 10)

        plt.bar(labels, data, color=['orange', 'green', 'red'], width=width_plot)

        if percentage:
        # Add percentage labels above the bars
            for label, value in zip(labels, data):
                plt.text(label, value + 1, f"{value:.1f}%", ha='center', va='bottom')

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

    elif plot_type == "2":
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

    elif plot_type == "3":
        monsters = [labels[item] for item in data.keys()]
        x = np.arange(len(monsters))
        fig, ax = plt.subplots()
        plt.bar(x - width_plot/2, data.values(), width_plot, label='Wins', color='orange')
        plt.bar(x + width_plot/2, data2.values(), width_plot, label='Losses', color='green')
        # Aggiungi titolo e etichette agli assi
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(x, monsters)
        plt.legend()
        plt.show()
