"""Tkinter UI for the number guessing game."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from guessing_game import (
    DIFFICULTIES,
    DIFFICULTY_BY_KEY,
    GameRound,
    GuessResult,
    Session,
    loss_message,
    message_for,
    win_message,
)


class GuessingGameApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Number Guessing Game")
        self.minsize(420, 480)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.session: Session | None = None
        self.game_round: GameRound | None = None
        self.difficulty_var = tk.StringVar(value="medium")
        self.name_var = tk.StringVar()
        self.guess_var = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Enter your name and choose a difficulty.")
        self.attempts_var = tk.StringVar()
        self.range_var = tk.StringVar()
        self.stats_var = tk.StringVar()
        self._build_setup_frame()
        self._build_play_frame()
        self.show_setup()

    def _build_setup_frame(self) -> None:
        self.setup_frame = ttk.Frame(self, padding=16)
        self.setup_frame.columnconfigure(0, weight=1)
        ttk.Label(
            self.setup_frame,
            text="Number Guessing Game",
            font=("", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(self.setup_frame, text="Your name").grid(row=1, column=0, sticky="w")
        name_entry = ttk.Entry(self.setup_frame, textvariable=self.name_var, width=32)
        name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        name_entry.focus_set()
        ttk.Label(self.setup_frame, text="Difficulty").grid(row=3, column=0, sticky="w")
        diff_frame = ttk.Frame(self.setup_frame)
        diff_frame.grid(row=4, column=0, sticky="w", pady=(0, 16))
        for diff in DIFFICULTIES:
            ttk.Radiobutton(
                diff_frame,
                text=f"{diff.key.capitalize()} ({diff.low}–{diff.high}, {diff.max_attempts} guesses)",
                value=diff.key,
                variable=self.difficulty_var,
            ).pack(anchor="w")

        ttk.Button(self.setup_frame, text="Start game", command=self.start_game).grid(
            row=5, column=0, sticky="ew"
        )
        self.bind("<Return>", lambda _e: self._on_return())

    def _build_play_frame(self) -> None:
        self.play_frame = ttk.Frame(self, padding=16)
        self.play_frame.columnconfigure(0, weight=1)
        self.play_frame.rowconfigure(4, weight=1)
        self.greeting_label = ttk.Label(self.play_frame, font=("", 12, "bold"))
        self.greeting_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        info = ttk.Frame(self.play_frame)
        info.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        info.columnconfigure(1, weight=1)
        ttk.Label(info, text="Attempts:").grid(row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.attempts_var).grid(row=0, column=1, sticky="w")
        ttk.Label(info, text="Possible range:").grid(row=1, column=0, sticky="w")
        ttk.Label(info, textvariable=self.range_var).grid(row=1, column=1, sticky="w")
        self.feedback_label = ttk.Label(
            self.play_frame,
            textvariable=self.feedback_var,
            wraplength=360,
            foreground="#1a5276",
        )
        self.feedback_label.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(self.play_frame, text="Guess history").grid(row=3, column=0, sticky="w")
        history_frame = ttk.Frame(self.play_frame)
        history_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 8))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        self.history_list = tk.Listbox(history_frame, height=8, activestyle="none")
        self.history_list.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.history_list.configure(yscrollcommand=scroll.set)
        guess_row = ttk.Frame(self.play_frame)
        guess_row.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        guess_row.columnconfigure(0, weight=1)
        self.guess_entry = ttk.Entry(guess_row, textvariable=self.guess_var, width=12)
        self.guess_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.guess_button = ttk.Button(guess_row, text="Guess", command=self.submit_guess)
        self.guess_button.grid(row=0, column=1)
        ttk.Label(self.play_frame, textvariable=self.status_var, foreground="#555").grid(
            row=6, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Label(self.play_frame, textvariable=self.stats_var, font=("", 9)).grid(
            row=7, column=0, sticky="w", pady=(0, 8)
        )
        actions = ttk.Frame(self.play_frame)
        actions.grid(row=8, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        self.new_round_button = ttk.Button(
            actions, text="New round", command=self.new_round, state="disabled"
        )
        self.new_round_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(actions, text="Change player", command=self.show_setup).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

    def _on_return(self) -> None:
        if self.setup_frame.winfo_ismapped():
            self.start_game()
        elif self.game_round and self.game_round.attempts_remaining > 0:
            self.submit_guess()

    def show_setup(self) -> None:
        self.play_frame.grid_remove()
        self.setup_frame.grid(row=0, column=0, sticky="nsew")
        self.game_round = None
        self.feedback_var.set("")
        self.status_var.set("Enter your name and choose a difficulty.")

    def show_play(self) -> None:
        self.setup_frame.grid_remove()
        self.play_frame.grid(row=0, column=0, sticky="nsew")

    def start_game(self) -> None:
        name = self.name_var.get().strip() or "Player"
        if self.session is None or self.session.player_name != name:
            self.session = Session(player_name=name)
        self.new_round()

    def new_round(self) -> None:
        if self.session is None:
            return

        difficulty = DIFFICULTY_BY_KEY[self.difficulty_var.get()]
        self.game_round = GameRound.create(difficulty)
        self.show_play()
        self.greeting_label.configure(
            text=(
                f"Hello, {self.session.player_name}! "
                f"Guess a number from {difficulty.low} to {difficulty.high}."
            )
        )
        self.feedback_var.set("Make your first guess.")
        self.feedback_label.configure(foreground="#1a5276")
        self.guess_var.set("")
        self.history_list.delete(0, tk.END)
        self.guess_entry.configure(state="normal")
        self.guess_button.configure(state="normal")
        self.new_round_button.configure(state="disabled")
        self._refresh_hud()
        self._update_stats()
        self.guess_entry.focus_set()

    def _refresh_hud(self) -> None:
        if not self.game_round:
            return
        r = self.game_round
        d = r.difficulty
        low, high = r.narrowed_range()
        self.attempts_var.set(
            f"{r.attempts_used} / {d.max_attempts} used ({r.attempts_remaining} remaining)"
        )
        self.range_var.set(f"{low} – {high}")

    def _update_stats(self) -> None:
        if not self.session or self.session.rounds_played == 0:
            self.stats_var.set("")
            return
        s = self.session
        parts = [f"Session: {s.wins}/{s.rounds_played} wins", f"score {s.total_score}"]
        if s.best_attempts is not None:
            parts.append(f"best {s.best_attempts} tries")
        self.stats_var.set(" · ".join(parts))

    def _append_history(self, guess: int, note: str) -> None:
        self.history_list.insert(tk.END, f"{guess} — {note}")
        self.history_list.see(tk.END)

    def _set_feedback(self, text: str, *, success: bool = False, error: bool = False) -> None:
        self.feedback_var.set(text)
        if success:
            color = "#1e8449"
        elif error:
            color = "#922b21"
        else:
            color = "#1a5276"
        self.feedback_label.configure(foreground=color)

    def submit_guess(self) -> None:
        if not self.session or not self.game_round:
            return
        if self.game_round.attempts_remaining <= 0:
            return

        raw = self.guess_var.get().strip()
        try:
            guess = int(raw)
        except ValueError:
            self._set_feedback("Please enter a whole number.", error=True)
            return

        result = self.game_round.submit(guess)
        if result in (GuessResult.DUPLICATE, GuessResult.OUT_OF_RANGE):
            self._set_feedback(message_for(result, self.game_round, guess), error=True)
            return

        if result is GuessResult.CORRECT:
            self._append_history(guess, "correct!")
            self._finish_round(won=True)
            return

        text = message_for(result, self.game_round, guess)
        self._append_history(guess, text.split("!")[0].lower())
        self._set_feedback(text)
        self.guess_var.set("")
        if hint := self.game_round.next_hint():
            self.status_var.set(f"Hint: {hint}")
        else:
            self.status_var.set("")

        self._refresh_hud()
        if self.game_round.attempts_remaining <= 0:
            self._finish_round(won=False)

    def _finish_round(self, *, won: bool) -> None:
        if not self.session or not self.game_round:
            return

        self.session.record(self.game_round)
        player = self.session.player_name
        if won:
            self._set_feedback(win_message(self.game_round, player), success=True)
        else:
            self._set_feedback(loss_message(self.game_round, player), error=True)

        self.guess_entry.configure(state="disabled")
        self.guess_button.configure(state="disabled")
        self.new_round_button.configure(state="normal")
        self.status_var.set("Start a new round or change player.")
        self._refresh_hud()
        self._update_stats()


def main() -> None:
    app = GuessingGameApp()
    app.mainloop()


if __name__ == "__main__":
    main()
