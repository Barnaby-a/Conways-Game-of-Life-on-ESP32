import numpy as np

num_simulations = 10_000_000
def simulate_battles(attacker_dice, defender_dice, num_simulations):
    attacker_rolls = np.sort(np.random.randint(1, 7, (num_simulations, attacker_dice)), axis=1)[:, ::-1]
    defender_rolls = np.sort(np.random.randint(1, 7, (num_simulations, defender_dice)), axis=1)[:, ::-1]
    attacker_wins = 0
    defender_wins = 0
    first_battles = attacker_rolls[:, 0] > defender_rolls[:, 0]
    attacker_wins += np.sum(first_battles)
    defender_wins += np.sum(~first_battles)
    if attacker_dice > 1 and defender_dice > 1:
        second_battles = attacker_rolls[:, 1] > defender_rolls[:, 1]
        attacker_wins += np.sum(second_battles & ~first_battles)
        defender_wins += np.sum(~second_battles & ~first_battles)
        return attacker_wins/(attacker_wins + defender_wins)*100
        configurations = [
            (3, 2),
            (3, 1),
            (2, 2),
            (2, 1),
            (1, 2),
            (1, 1),
        ]

        for attacker_dice, defender_dice in configurations:
            win_percentage = simulate_battles(attacker_dice, defender_dice, num_simulations)
            print(f"Attacker dice: {attacker_dice}, Defender dice: {defender_dice}, Percentage: {win_rate:.2f}%")

simulate_battles(3, 2, num_simulations)