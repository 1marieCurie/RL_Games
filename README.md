# RL Games

Small reinforcement-learning examples with:
- a console version in `sticks.py`
- a Tkinter GUI in `sticks_gui.py`
- a Grid World Q-learning console demo in `grid_world_q_learning.py`
- an interactive Grid World visualizer in `grid_world_gui.py`
- a car-themed Q-learning game in `car_game_Q_learning.py`
- a car-themed Q-learning GUI in `car_game_Q_learning_gui.py`
- a browser-based Metacar DQN demo in `q_learning_nn.html`

## Stick Game Rules

- Start with `12` sticks.
- Each turn, a player takes `1`, `2`, or `3` sticks.
- The player who takes the last stick loses.

## Files

- `sticks.py`: game logic, training, and console mode
- `sticks_gui.py`: graphical interface built on top of `sticks.py`
- `grid_world_q_learning.py`: 3x3 Q-learning environment and console training loop
- `grid_world_gui.py`: Tkinter interface for stepping through Grid World Q-learning
- `car_game_Q_learning.py`: car-themed Q-learning environment where the agent learns a route home
- `car_game_Q_learning_gui.py`: animated Tkinter GUI for the car Q-learning game
- `q_learning_nn.html`: browser-based Metacar environment trained with a DQN-style neural Q-network
- `metacar.min.js`: local Metacar library used by `q_learning_nn.html`
- `public/textures/`: local Metacar texture atlas used to avoid remote CORS issues

## Run

### Stick Game Console Mode

```powershell
python .\sticks.py
```

- Press `P` at startup to play as the human.
- Press `Enter` to run the automated evaluation.
- During a human game, type `Q` to quit.

### Stick Game GUI Mode

```powershell
python .\sticks_gui.py
```

### Car Game Console Mode

```powershell
python .\car_game_Q_learning.py
```

### Car Game GUI Mode

```powershell
python .\car_game_Q_learning_gui.py
```

Use `Step` to watch one Q-learning update, `Auto` to run animated training, and `Reset` to restart learning.

### Metacar DQN Browser Demo

Serve the project folder with a local HTTP server, then open the page in a browser:

```powershell
python -m http.server 5501
```

Open:

```text
http://127.0.0.1:5501/q_learning_nn.html
```

Use `Train` to collect replay-memory experiences and train the neural Q-network, then use `Play` to run the learned policy.

## Stick Game Features

- trained agent based on a simple value-function approach
- human vs AI mode
- automated evaluation mode
- game-level and move-level statistics
- Tkinter interface with visual sticks and score tracking

## Demo
<img src="assets/sticks_gui.png" alt="Stick Game Demo" width="50%">

## Grid World GUI Features

- animated car agent instead of the console `X`
- animated people crossing the center street cell
- home target drawn on the goal cell
- live Q-value table updated after every action
- current state and latest action highlighting

## Car Game Description

The car game is a small 3x3 Q-learning environment. The car starts from the bottom-left cell, tries to reach home in the top-right cell, and receives a penalty when it drives into the cell where people are crossing the street.

The GUI visualizes the learning process with an animated car, animated people, a home target, episode progress, and a Q-value table that updates after every action. Auto training stops after 40 episodes.

## Car Game Demo

![Car Q-Learning Demo](assets/car_q_learning.png)

## Metacar DQN Description

The Metacar demo runs in the browser with Pixi.js for rendering and TensorFlow.js for the neural network. The agent observes the Metacar state, chooses actions with an epsilon-greedy policy, stores transitions in replay memory, and trains a DQN-style model that predicts Q-values for the available actions.

Training runs for 150 episodes with up to 400 steps per episode. Epsilon starts at `1.0` for exploration and decays toward `0.1`; after training, `Play` uses `eps = 0.0` to follow the learned policy.

## Metacar DQN Features

- browser-rendered Metacar driving environment
- TensorFlow.js neural Q-network with one hidden dense layer
- epsilon-greedy action selection
- replay-memory style transition storage
- local texture atlas in `public/textures/` to avoid CORS problems

