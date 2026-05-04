import random
import tkinter as tk

from sticks import StickGame, StickPlayer, build_default_session, train_agents


class StickGameUI:
    NB_STICKS = 12

    def __init__(self, root):
        self.root = root
        self.root.title("Stick Game")
        self.root.configure(bg="#f5f3ee")
        self.root.resizable(False, False)

        self.game, self.agent, self.sparring, _, _ = build_default_session(self.NB_STICKS)
        train_agents(self.game, self.agent, self.sparring, iterations=5000)
        self.agent.reset_stat()
        self.agent.eps = 0.05

        self.human_wins = 0
        self.ai_wins = 0
        self.total_games = 0
        self.human_turn = True
        self.game_over = False

        self._build_ui()
        self.reset_game()

    def _build_ui(self):
        card = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid", padx=24, pady=24)
        card.pack(padx=24, pady=24)

        tk.Label(
            card,
            text="Stick Game",
            font=("Segoe UI", 20, "normal"),
            bg="#ffffff",
            fg="#1a1a1a",
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Take 1, 2, or 3 sticks. Whoever takes the last stick loses.",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#777777",
        ).pack(anchor="w", pady=(0, 18))

        top_bar = tk.Frame(card, bg="#ffffff")
        top_bar.pack(fill="x")

        self.status_var = tk.StringVar()
        tk.Label(
            top_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#1a1a1a",
        ).pack(side="left")

        tk.Button(
            top_bar,
            text="New game",
            command=self.reset_game,
            font=("Segoe UI", 10),
            bg="#1D9E75",
            fg="#ffffff",
            activebackground="#0F6E56",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
        ).pack(side="right")

        self.log_var = tk.StringVar()
        tk.Label(
            card,
            textvariable=self.log_var,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#777777",
        ).pack(anchor="w", pady=(10, 16))

        self.canvas = tk.Canvas(card, width=500, height=90, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(anchor="w", pady=(0, 18))

        actions = tk.Frame(card, bg="#ffffff")
        actions.pack(anchor="w", pady=(0, 18))

        self.move_buttons = []
        for amount in (1, 2, 3):
            button = tk.Button(
                actions,
                text=f"Take\n{amount}",
                command=lambda value=amount: self.human_play(value),
                width=8,
                height=2,
                font=("Segoe UI", 13, "bold"),
                bg="#ffffff",
                fg="#1a1a1a",
                activebackground="#f0f0f0",
                relief="solid",
                bd=1,
            )
            button.pack(side="left", padx=(0, 12))
            self.move_buttons.append(button)

        score = tk.Frame(card, bg="#ffffff")
        score.pack(anchor="w", pady=(0, 20))

        self.score_vars = {
            "You win": tk.StringVar(value="0"),
            "AI wins": tk.StringVar(value="0"),
            "Games": tk.StringVar(value="0"),
        }
        for label, variable in self.score_vars.items():
            score_card = tk.Frame(score, bg="#f5f3ee", padx=18, pady=12)
            score_card.pack(side="left", padx=(0, 12))
            tk.Label(score_card, text=label, font=("Segoe UI", 10), bg="#f5f3ee", fg="#777777").pack()
            tk.Label(score_card, textvariable=variable, font=("Segoe UI", 24, "bold"), bg="#f5f3ee", fg="#1a1a1a").pack()

        tk.Label(
            card,
            text="AI value function - green means safer for AI, orange means risky for AI",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#777777",
        ).pack(anchor="w", pady=(0, 8))

        self.vf_frame = tk.Frame(card, bg="#ffffff")
        self.vf_frame.pack(anchor="w")

    def reset_game(self):
        self.game.reset()
        self.agent.history = []
        self.game_over = False
        self.human_turn = random.choice([True, False])
        self.status_var.set("Your turn" if self.human_turn else "AI goes first...")
        self.log_var.set("Take 1, 2, or 3 sticks. Last stick loses.")
        self.draw_sticks()
        self.update_buttons()
        self.update_value_function()

        if not self.human_turn:
            self.root.after(600, self.ai_turn)

    def draw_sticks(self, highlight_count=0):
        self.canvas.delete("all")
        heights = [48, 52, 46, 54, 50, 44, 56, 48, 52, 46, 54, 50]
        stick_width = 20
        gap = 10
        margin_left = 8
        base_y = 80
        taken = self.NB_STICKS - self.game.nb

        for index in range(self.NB_STICKS):
            x0 = margin_left + index * (stick_width + gap)
            x1 = x0 + stick_width
            height = heights[index % len(heights)]
            y0 = base_y - height

            if index < taken:
                palette = {
                    "body": "#d8d8d8",
                    "edge": "#bababa",
                    "shine": "#efefef",
                    "shadow": "#a7a7a7",
                }
            elif index < taken + highlight_count:
                palette = {
                    "body": "#d79a49",
                    "edge": "#b8792e",
                    "shine": "#efc27e",
                    "shadow": "#99621d",
                }
            else:
                palette = {
                    "body": "#ece8d0",
                    "edge": "#d9d1af",
                    "shine": "#f8f3de",
                    "shadow": "#c9bf95",
                }

            self._draw_stick(x0, y0, x1, base_y, palette)

    def _draw_stick(self, x0, y0, x1, y1, palette):
        mid_x = (x0 + x1) / 2
        top_width = max(6, (x1 - x0) * 0.38)
        left_top = mid_x - top_width / 2
        right_top = mid_x + top_width / 2

        self.canvas.create_polygon(
            x0, y1,
            left_top, y0 + 6,
            mid_x, y0,
            right_top, y0 + 6,
            x1, y1,
            fill=palette["body"],
            outline=palette["edge"],
            width=1,
            smooth=True,
        )

        self.canvas.create_polygon(
            x0 + 3, y1 - 2,
            left_top + 1, y0 + 12,
            mid_x - 1, y0 + 5,
            mid_x - 2, y1 - 6,
            fill=palette["shine"],
            outline="",
            smooth=True,
        )

        self.canvas.create_polygon(
            mid_x + 1, y1 - 4,
            right_top - 1, y0 + 10,
            x1 - 2, y1 - 2,
            fill=palette["shadow"],
            outline="",
            smooth=True,
        )

        self.canvas.create_line(
            mid_x, y0 + 2, mid_x, y1 - 6,
            fill=palette["edge"],
            width=1,
        )

    def update_buttons(self):
        for index, button in enumerate(self.move_buttons, start=1):
            enabled = self.human_turn and not self.game_over and index <= self.game.nb
            button.config(state="normal" if enabled else "disabled")

    def update_score(self):
        self.score_vars["You win"].set(str(self.human_wins))
        self.score_vars["AI wins"].set(str(self.ai_wins))
        self.score_vars["Games"].set(str(self.total_games))

    def update_value_function(self):
        for child in self.vf_frame.winfo_children():
            child.destroy()

        values = [self.agent.V[state] for state in range(1, self.NB_STICKS + 1)]
        vmin = min(values)
        vmax = max(values)

        for state in range(1, self.NB_STICKS + 1):
            value = self.agent.V[state]
            color = self._value_color(value, vmin, vmax)

            cell = tk.Frame(self.vf_frame, bg=color, width=42, height=42)
            cell.pack(side="left", padx=2)
            cell.pack_propagate(False)
            tk.Label(cell, text=f"{value:.2f}", font=("Segoe UI", 9, "bold"), bg=color, fg="#ffffff").pack(pady=(5, 0))
            tk.Label(cell, text=f"s={state}", font=("Segoe UI", 8), bg=color, fg="#f5f5f5").pack()

    def _value_color(self, value, vmin, vmax):
        if vmax == vmin:
            ratio = 0.5
        else:
            ratio = (value - vmin) / (vmax - vmin)
        red = int(216 - (ratio * 186))
        green = int(90 + (ratio * 155))
        blue = int(48 + (ratio * 32))
        return f"#{red:02x}{green:02x}{blue:02x}"

    def human_play(self, action):
        if self.game_over or not self.human_turn:
            return

        previous_state = self.game.nb
        next_state, reward = self.game.step(action)
        self.draw_sticks()

        if self.agent.history:
            state, ai_action, _, _ = self.agent.history[-1]
            self.agent.history[-1] = (state, ai_action, reward * -1, next_state)

        if reward != 0:
            self.game_over = True
            self.ai_wins += 1
            self.total_games += 1
            self.status_var.set("You lose!")
            self.log_var.set("You took the last stick. The AI wins.")
            self.agent.add_game_result(1)
            self.agent.train()
            self.update_score()
            self.update_buttons()
            self.update_value_function()
            return

        self.human_turn = False
        self.status_var.set("AI is thinking...")
        self.log_var.set(f"You took {action}. {previous_state - action} sticks remain.")
        self.update_buttons()
        self.root.after(700, self.ai_turn)

    def ai_turn(self):
        if self.game_over:
            return

        state = self.game.nb
        action = self.agent.play(state)
        next_state, reward = self.game.step(action)
        self.agent.add_transition((state, action, reward, None))
        self.draw_sticks(highlight_count=min(action, self.NB_STICKS - (self.NB_STICKS - state)))
        self.root.after(350, self.draw_sticks)

        if reward != 0:
            self.game_over = True
            self.human_wins += 1
            self.total_games += 1
            self.status_var.set("You win!")
            self.log_var.set(f"AI took the last stick ({action}). You win.")
            self.agent.add_game_result(-1)
            self.agent.train()
            self.update_score()
            self.update_buttons()
            self.update_value_function()
            return

        self.human_turn = True
        self.status_var.set("Your turn")
        self.log_var.set(f"AI took {action}. {next_state} stick{'s' if next_state != 1 else ''} remaining.")
        self.update_buttons()
        self.update_value_function()


if __name__ == "__main__":
    app_root = tk.Tk()
    StickGameUI(app_root)
    app_root.mainloop()
