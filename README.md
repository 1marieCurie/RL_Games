# Stick Game

Simple stick-taking game with:
- a console version in `sticks.py`
- a Tkinter GUI in `sticks_gui.py`

## Rules

- Start with `12` sticks.
- Each turn, a player takes `1`, `2`, or `3` sticks.
- The player who takes the last stick loses.

## Files

- `sticks.py`: game logic, training, and console mode
- `sticks_gui.py`: graphical interface built on top of `sticks.py`

## Run

### Console mode

```powershell
python .\sticks.py
```

- Press `P` at startup to play as the human.
- Press `Enter` to run the automated evaluation.
- During a human game, type `Q` to quit.

### GUI mode

```powershell
python .\sticks_gui.py
```

## Features

- trained agent based on a simple value-function approach
- human vs AI mode
- automated evaluation mode
- game-level and move-level statistics
- Tkinter interface with visual sticks and score tracking

## Demo

Placeholder for demo image:

```text
Add screenshot here later, for example:
![Stick Game Demo](demo.png)
```
