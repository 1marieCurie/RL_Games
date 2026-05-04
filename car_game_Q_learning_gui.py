import tkinter as tk

from car_game_Q_learning import EnvGrid, take_action


class GridWorldQLearningUI:
    ACTION_NAMES = ("Up", "Down", "Left", "Right")
    STATE_COUNT = 9
    MAX_EPISODES = 40
    ALPHA = 0.1
    GAMMA = 0.9
    EPSILON = 0.35

    def __init__(self, root):
        self.root = root
        self.root.title("Grid World Q-Learning")
        self.root.configure(bg="#edf1ed")
        self.root.resizable(False, False)

        self.env = EnvGrid()
        self.q_values = [[0.0, 0.0, 0.0, 0.0] for _ in range(self.STATE_COUNT + 1)]
        self.state = self.env.reset()
        self.episode = 1
        self.step_count = 0
        self.auto_running = False
        self.car_animating = False
        self.last_action = None
        self.last_reward = 0
        self.people_phase = 0

        self.cell_size = 126
        self.canvas_size = self.cell_size * 3
        self.car_position = self._state_to_center(self.state)

        self._build_ui()
        self._draw_scene()
        self._update_q_table()
        self._update_status("Ready. Step once or let the agent drive.")
        self._animate_people()

    def _build_ui(self):
        shell = tk.Frame(self.root, bg="#edf1ed", padx=22, pady=22)
        shell.pack()

        top = tk.Frame(shell, bg="#edf1ed")
        top.pack(fill="x", pady=(0, 14))

        title_area = tk.Frame(top, bg="#edf1ed")
        title_area.pack(side="left", anchor="w")

        tk.Label(
            title_area,
            text="Grid World Q-Learning",
            font=("Segoe UI", 20, "bold"),
            bg="#edf1ed",
            fg="#1d2921",
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Car learns to reach home while avoiding people crossing.",
            font=("Segoe UI", 10),
            bg="#edf1ed",
            fg="#5c675f",
        ).pack(anchor="w")

        controls = tk.Frame(top, bg="#edf1ed")
        controls.pack(side="right", anchor="e")

        self.step_button = self._make_button(controls, "Step", self.step_agent, "#256f56")
        self.step_button.pack(side="left", padx=(0, 8))

        self.auto_button = self._make_button(controls, "Auto", self.toggle_auto, "#32495f")
        self.auto_button.pack(side="left", padx=(0, 8))

        self.reset_button = self._make_button(controls, "Reset", self.reset_learning, "#7c5830")
        self.reset_button.pack(side="left")

        content = tk.Frame(shell, bg="#edf1ed")
        content.pack()

        board_panel = tk.Frame(content, bg="#ffffff", bd=1, relief="solid", padx=14, pady=14)
        board_panel.pack(side="left", anchor="n")

        self.canvas = tk.Canvas(
            board_panel,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#ffffff",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status_var = tk.StringVar()
        tk.Label(
            board_panel,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#334039",
            wraplength=self.canvas_size,
            justify="left",
        ).pack(anchor="w", pady=(12, 0))

        table_panel = tk.Frame(content, bg="#ffffff", bd=1, relief="solid", padx=14, pady=14)
        table_panel.pack(side="left", anchor="n", padx=(16, 0))

        tk.Label(
            table_panel,
            text="Q Values",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#1d2921",
        ).pack(anchor="w")

        tk.Label(
            table_panel,
            text="Highlighted row is the current state. Highlighted cell is the latest action.",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b756f",
            wraplength=500,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        self.q_table = tk.Frame(table_panel, bg="#dfe5df")
        self.q_table.pack(anchor="w")
        self.q_labels = {}
        self._build_q_table(table_panel)

    def _make_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="#ffffff",
            activebackground=color,
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=7,
            cursor="hand2",
        )

    def _build_q_table(self, table_panel):
        headers = ("State",) + self.ACTION_NAMES
        for col, header in enumerate(headers):
            tk.Label(
                self.q_table,
                text=header,
                width=10 if col else 7,
                font=("Consolas", 10, "bold"),
                bg="#38473d",
                fg="#ffffff",
                padx=4,
                pady=6,
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for state in range(1, self.STATE_COUNT + 1):
            state_label = tk.Label(
                self.q_table,
                text=str(state),
                width=7,
                font=("Consolas", 10, "bold"),
                bg="#eef2ee",
                fg="#243029",
                padx=4,
                pady=5,
            )
            state_label.grid(row=state, column=0, sticky="nsew", padx=1, pady=1)
            self.q_labels[(state, "state")] = state_label

            for action_index in range(4):
                value_label = tk.Label(
                    self.q_table,
                    text="0.000",
                    width=10,
                    font=("Consolas", 10),
                    bg="#f8faf8",
                    fg="#243029",
                    padx=4,
                    pady=5,
                )
                value_label.grid(row=state, column=action_index + 1, sticky="nsew", padx=1, pady=1)
                self.q_labels[(state, action_index)] = value_label

        legend = tk.Frame(table_panel, bg="#ffffff")
        legend.pack(anchor="w", pady=(12, 0))
        self._legend_item(legend, "#cfe8d8", "current state").pack(side="left", padx=(0, 10))
        self._legend_item(legend, "#ffd180", "latest action").pack(side="left", padx=(0, 10))
        self._legend_item(legend, "#ffc6c0", "people penalty").pack(side="left")

    def _legend_item(self, parent, color, label):
        item = tk.Frame(parent, bg="#ffffff")
        tk.Label(item, width=2, height=1, bg=color).pack(side="left")
        tk.Label(item, text=label, font=("Segoe UI", 9), bg="#ffffff", fg="#667068").pack(side="left", padx=(4, 0))
        return item

    def step_agent(self):
        if self.car_animating:
            return

        if self.env.is_finished():
            self._start_next_episode()
            return

        if self.episode > self.MAX_EPISODES:
            self._finish_training()
            return

        previous_state = self.state
        previous_center = self.car_position
        action = take_action(previous_state, self.q_values, self.EPSILON)
        next_state, reward = self.env.step(action)
        best_next_action = take_action(next_state, self.q_values, 0.0)

        old_value = self.q_values[previous_state][action]
        target = reward + self.GAMMA * self.q_values[next_state][best_next_action]
        self.q_values[previous_state][action] = old_value + self.ALPHA * (target - old_value)

        self.state = next_state
        self.last_action = (previous_state, action)
        self.last_reward = reward
        self.step_count += 1

        self._update_q_table()
        self._update_status_for_action(previous_state, action, next_state, reward)
        self._set_buttons(False)
        self._animate_car(previous_center, self._state_to_center(next_state), 0)

    def toggle_auto(self):
        self.auto_running = not self.auto_running
        self.auto_button.configure(text="Pause" if self.auto_running else "Auto")
        if self.auto_running:
            self._auto_step()

    def reset_learning(self):
        self.auto_running = False
        self.auto_button.configure(text="Auto")
        self.q_values = [[0.0, 0.0, 0.0, 0.0] for _ in range(self.STATE_COUNT + 1)]
        self.episode = 1
        self.step_count = 0
        self.last_action = None
        self.last_reward = 0
        self.state = self.env.reset()
        self.car_position = self._state_to_center(self.state)
        self._set_buttons(True)
        self._draw_scene()
        self._update_q_table()
        self._update_status("Learning reset. The car is back at the start.")

    def _auto_step(self):
        if not self.auto_running:
            return
        if self.episode > self.MAX_EPISODES:
            self._finish_training()
            return
        self.step_agent()
        self.root.after(650, self._auto_step)

    def _start_next_episode(self):
        if self.episode >= self.MAX_EPISODES:
            self._finish_training()
            return

        self.state = self.env.reset()
        self.car_position = self._state_to_center(self.state)
        self.episode += 1
        self.last_action = None
        self.last_reward = 0
        self._draw_scene()
        self._update_q_table()
        self._update_status("Episode complete. New episode started from state 7.")

    def _finish_training(self):
        self.auto_running = False
        self.auto_button.configure(text="Auto")
        self._set_buttons(False)
        self.reset_button.configure(state="normal")
        self._update_status(f"Training complete after {self.MAX_EPISODES} episodes. Use Reset to train again.")

    def _update_status_for_action(self, previous_state, action, next_state, reward):
        action_name = self.ACTION_NAMES[action]
        reward_text = "home reached" if reward == 1 else "people penalty" if reward == -1 else "street is clear"
        self._update_status(
            f"Episode {self.episode} | Step {self.step_count}: state {previous_state} -> "
            f"{action_name} -> state {next_state}. Reward {reward} ({reward_text})."
        )

    def _update_status(self, message):
        self.status_var.set(message)

    def _update_q_table(self):
        for state in range(1, self.STATE_COUNT + 1):
            row_is_current = state == self.state
            state_label = self.q_labels[(state, "state")]
            state_label.configure(bg="#cfe8d8" if row_is_current else "#eef2ee")

            for action_index in range(4):
                label = self.q_labels[(state, action_index)]
                value = self.q_values[state][action_index]
                is_last_action = self.last_action == (state, action_index)
                is_people_state = state == 5
                if is_last_action:
                    background = "#ffd180"
                elif row_is_current:
                    background = "#e4f3e9"
                elif is_people_state:
                    background = "#ffc6c0"
                else:
                    background = "#f8faf8"
                label.configure(text=f"{value: .3f}", bg=background)

    def _draw_scene(self):
        self.canvas.delete("all")
        self._draw_background()
        self._draw_home()
        self._draw_people()
        self._draw_car(*self.car_position)

    def _draw_background(self):
        for row in range(3):
            for col in range(3):
                x0 = col * self.cell_size
                y0 = row * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                fill = "#68756e" if row == 1 else "#728076"
                if row == 0 and col == 2:
                    fill = "#90c58b"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#edf1ed", width=3)

                if row == 1:
                    stripe_y = y0 + self.cell_size / 2
                    self.canvas.create_line(x0 + 14, stripe_y, x1 - 14, stripe_y, fill="#f4d35e", width=4, dash=(18, 14))
                else:
                    self.canvas.create_line(x0 + 12, y1 - 12, x1 - 12, y1 - 12, fill="#a8c39f", width=3)

                state = row * 3 + col + 1
                self.canvas.create_text(x0 + 16, y0 + 16, text=str(state), fill="#e9efe9", font=("Segoe UI", 9, "bold"))

    def _draw_home(self):
        center_x, center_y = self._cell_center(0, 2)
        roof = [
            center_x - 36, center_y - 6,
            center_x, center_y - 40,
            center_x + 36, center_y - 6,
        ]
        self.canvas.create_polygon(roof, fill="#8d4e3d", outline="#623126", width=2)
        self.canvas.create_rectangle(center_x - 28, center_y - 6, center_x + 28, center_y + 36, fill="#f8e6b8", outline="#6c4f32", width=2)
        self.canvas.create_rectangle(center_x - 8, center_y + 10, center_x + 8, center_y + 36, fill="#6f9f70", outline="#4b704c", width=2)
        self.canvas.create_rectangle(center_x + 12, center_y + 2, center_x + 24, center_y + 14, fill="#9ed2e6", outline="#5e8ea2", width=1)

    def _draw_people(self):
        center_x, center_y = self._cell_center(1, 1)
        offset = (self.people_phase % 24) - 12
        self._draw_person(center_x - 24 + offset, center_y + 2, "#f7c669", "#2f6f9f")
        self._draw_person(center_x + 22 - offset, center_y + 4, "#f2b2a0", "#8356a2")
        self.canvas.create_rectangle(center_x - 48, center_y - 44, center_x + 48, center_y + 44, outline="#ffffff", width=2, dash=(7, 5))

    def _draw_person(self, x, y, skin, shirt):
        self.canvas.create_oval(x - 9, y - 34, x + 9, y - 16, fill=skin, outline="#4f4136", width=1)
        self.canvas.create_rectangle(x - 9, y - 16, x + 9, y + 12, fill=shirt, outline="#35424c", width=1)
        swing = 5 if self.people_phase % 16 < 8 else -5
        self.canvas.create_line(x - 7, y - 8, x - 18, y + swing, fill="#2b3030", width=3)
        self.canvas.create_line(x + 7, y - 8, x + 18, y - swing, fill="#2b3030", width=3)
        self.canvas.create_line(x - 4, y + 12, x - 14, y + 30, fill="#1f2a2a", width=3)
        self.canvas.create_line(x + 4, y + 12, x + 14, y + 30, fill="#1f2a2a", width=3)

    def _draw_car(self, center_x, center_y):
        bob = 2 if self.step_count % 2 else 0
        y = center_y + bob
        self.canvas.create_oval(center_x - 42, y + 20, center_x - 22, y + 40, fill="#151515", outline="")
        self.canvas.create_oval(center_x + 22, y + 20, center_x + 42, y + 40, fill="#151515", outline="")
        self.canvas.create_rectangle(center_x - 48, y - 12, center_x + 48, y + 28, fill="#e9503f", outline="#8c2b24", width=2)
        self.canvas.create_polygon(
            center_x - 28, y - 12,
            center_x - 14, y - 34,
            center_x + 20, y - 34,
            center_x + 36, y - 12,
            fill="#f06f5e",
            outline="#8c2b24",
            width=2,
        )
        self.canvas.create_polygon(
            center_x - 12, y - 29,
            center_x + 14, y - 29,
            center_x + 25, y - 12,
            center_x - 22, y - 12,
            fill="#bfe8f6",
            outline="#739dab",
            width=1,
        )
        self.canvas.create_oval(center_x - 38, y + 25, center_x - 26, y + 37, fill="#eeeeee", outline="")
        self.canvas.create_oval(center_x + 26, y + 25, center_x + 38, y + 37, fill="#eeeeee", outline="")
        self.canvas.create_oval(center_x + 42, y - 1, center_x + 52, y + 9, fill="#ffe66d", outline="")

    def _animate_car(self, start, end, frame):
        self.car_animating = True
        frames = 10
        progress = frame / frames
        x = start[0] + (end[0] - start[0]) * progress
        y = start[1] + (end[1] - start[1]) * progress
        self.car_position = (x, y)
        self._draw_scene()

        if frame < frames:
            self.root.after(24, lambda: self._animate_car(start, end, frame + 1))
        else:
            self.car_position = end
            self.car_animating = False
            self._draw_scene()
            self._set_buttons(True)

    def _animate_people(self):
        self.people_phase = (self.people_phase + 1) % 48
        if not self.car_animating:
            self._draw_scene()
        self.root.after(110, self._animate_people)

    def _set_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.step_button.configure(state=state)
        self.reset_button.configure(state=state)

    def _state_to_center(self, state):
        state_index = state - 1
        row = state_index // 3
        col = state_index % 3
        return self._cell_center(row, col)

    def _cell_center(self, row, col):
        return (
            col * self.cell_size + self.cell_size / 2,
            row * self.cell_size + self.cell_size / 2,
        )


def main():
    root = tk.Tk()
    GridWorldQLearningUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
