from random import randint
import random
import numpy as np

class StickGame(object):
    """
        StickGame.
    """

    def __init__(self, nb):
        # @nb Number of stick to play with
        super(StickGame, self).__init__()
        self.original_nb = nb
        self.nb = nb

    def is_finished(self):
        # Check if the game is over @return Boolean
        if self.nb <= 0:
            return True
        return False

    def reset(self):
        # Reset the state of the game
        self.nb = self.original_nb
        return self.nb

    def display(self):
        # Display the state of the game
        print ("| " * self.nb)

    def step(self, action):
        # @action either 1, 2 or 3. Take an action into the environement
        self.nb -= action
        if self.nb <= 0:
            return None, -1
        else:
            return self.nb, 0

class StickPlayer(object):
    """
        Stick Player
    """

    def __init__(self, is_human, size, trainable=True):
        # @nb Number of stick to play with
        super(StickPlayer, self).__init__()
        self.is_human = is_human
        self.history = []
        self.V = {}
        for s in range(1, size+1):
            self.V[s] = 0.
        self.win_nb = 0.
        self.lose_nb = 0.
        self.rewards = []
        self.game_results = []
        self.eps = 0.99
        self.trainable = trainable

    def reset_stat(self):
        # Reset stat
        self.win_nb = 0
        self.lose_nb = 0
        self.rewards = []
        self.game_results = []

    def greedy_step(self, state):
        # Greedy step
        actions = [1, 2, 3]
        vmin = None
        vi = None
        for i in range(0, 3):
            a = actions[i]
            if state - a > 0 and (vmin is None or vmin > self.V[state - a]):
                vmin = self.V[state - a]
                vi = i
        return actions[vi if vi is not None else 1]

    def play(self, state):
        # PLay given the @state (int)
        if self.is_human is False:
            # Take random action
            if random.uniform(0, 1) < self.eps:
                action = randint(1, 3)
            else: # Or greedy action
                action = self.greedy_step(state)
        else:
            while True:
                try:
                    choice = input(f"$> Take 1, 2, or 3 sticks (remaining: {state}, Q to quit): ").strip()
                    if choice.lower() == "q":
                        raise SystemExit("Exiting the human game loop.")
                    action = int(choice)
                except ValueError:
                    print("Please enter a whole number: 1, 2, or 3.")
                    continue
                except (EOFError, KeyboardInterrupt):
                    raise SystemExit("\nInput cancelled. Exiting the human game loop.")

                if action not in (1, 2, 3):
                    print("Invalid move. Choose 1, 2, or 3.")
                    continue
                if action > state:
                    print(f"Invalid move. You cannot take more than {state} stick(s).")
                    continue
                break
        return action

    def add_transition(self, n_tuple):
        # Add one transition to the history: tuple (s, a , r, s')
        self.history.append(n_tuple)
        s, a, r, sp = n_tuple
        self.rewards.append(r)

    def train(self):
        if not self.trainable or self.is_human is True:
            return

        # Update the value function if this player is not human
        for transition in reversed(self.history):
            s, a, r, sp = transition
            if r == 0:
                self.V[s] = self.V[s] + 0.001*(self.V[sp] - self.V[s])
            else:
                self.V[s] = self.V[s] + 0.001*(r - self.V[s])

        self.history = []

    def add_game_result(self, result):
        self.game_results.append(result)

def should_play_human():
    try:
        choice = input("Press P to play against the agent, or press Enter to run the automated evaluation: ")
    except (EOFError, KeyboardInterrupt):
        return False

    return choice.strip().lower() == "p"

def train_agents(game, p1, p2, iterations=10000):
    for i in range(0, iterations):
        if i % 10 == 0:
            p1.eps = max(p1.eps*0.996, 0.05)
            p2.eps = max(p2.eps*0.996, 0.05)
        play(game, p1, p2)

def build_default_session(nb=12):
    game = StickGame(nb)
    p1 = StickPlayer(is_human=False, size=nb, trainable=True)
    p2 = StickPlayer(is_human=False, size=nb, trainable=True)
    human = StickPlayer(is_human=True, size=nb, trainable=False)
    random_player = StickPlayer(is_human=False, size=nb, trainable=False)
    return game, p1, p2, human, random_player

def play(game, p1, p2, train=True):
    state = game.reset()
    players = [p1, p2]
    random.shuffle(players)
    p = 0
    while game.is_finished() is False:

        if players[p%2].is_human:
            game.display()

        action = players[p%2].play(state)
        n_state, reward = game.step(action)

        #  Game is over. Ass stat
        if (reward != 0):
            # Update stat of the current player
            players[p%2].lose_nb += 1. if reward == -1 else 0
            players[p%2].win_nb += 1. if reward == 1 else 0
            # Update stat of the other player
            players[(p+1)%2].lose_nb += 1. if reward == 1 else 0
            players[(p+1)%2].win_nb += 1. if reward == -1 else 0
            players[p%2].add_game_result(reward)
            players[(p+1)%2].add_game_result(-reward)

            if players[p%2].is_human:
                print("You lose. You took the last stick.")
            elif players[(p+1)%2].is_human:
                print("You win. The agent took the last stick.")

        # Add the reversed reward and the new state to the other player
        if p != 0:
            s, a, r, sp = players[(p+1)%2].history[-1]
            players[(p+1)%2].history[-1] = (s, a, reward * -1, n_state)

        players[p%2].add_transition((state, action, reward, None))

        state = n_state
        p += 1

    if train:
        p1.train()
        p2.train()

if __name__ == '__main__':
    play_human = should_play_human()

    game, p1, p2, human, random_player = build_default_session(12)

    # Train the agent
    train_agents(game, p1, p2, iterations=10000)
    p1.reset_stat()

    if play_human:
        while True:
            play(game, p1, human, train=False)
    else:
        # Display the value function
        for key in p1.V:
            print(key, p1.V[key])
        print("--------------------------")

        # Play agains a random player
        for _ in range(0, 1000):
            play(game, p1, random_player, train=False)
        print("p1 win rate", p1.win_nb/(p1.win_nb + p1.lose_nb))
        print("p1 move reward mean", np.mean(p1.rewards))
        print("p1 game reward mean", np.mean(p1.game_results))
        print("Running automated mode. Press P at startup if you want to play yourself.")
