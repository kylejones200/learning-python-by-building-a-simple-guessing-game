"""Number guessing game — companion code for article.md."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

BANNER_WIDTH = 40
HINT_AFTER_WRONG_GUESSES = 3


class GuessResult(Enum):
    CORRECT = "correct"
    TOO_LOW = "too_low"
    TOO_HIGH = "too_high"
    DUPLICATE = "duplicate"
    OUT_OF_RANGE = "out_of_range"


@dataclass(frozen=True)
class Difficulty:
    key: str
    low: int
    high: int
    max_attempts: int

    @property
    def span(self) -> int:
        return self.high - self.low + 1


DIFFICULTIES: tuple[Difficulty, ...] = (
    Difficulty("easy", 1, 10, 8),
    Difficulty("medium", 1, 20, 6),
    Difficulty("hard", 1, 50, 8),
)
DIFFICULTY_BY_KEY = {d.key: d for d in DIFFICULTIES}


@dataclass
class GameRound:
    """One round: secret number, guess history, and derived state."""

    difficulty: Difficulty
    secret: int
    guesses: list[int] = field(default_factory=list)
    hints_shown: set[str] = field(default_factory=set)

    @classmethod
    def create(cls, difficulty: Difficulty, rng: random.Random | None = None) -> GameRound:
        source = rng if rng is not None else random
        secret = source.randint(difficulty.low, difficulty.high)
        return cls(difficulty=difficulty, secret=secret)

    @property
    def attempts_used(self) -> int:
        return len(self.guesses)

    @property
    def attempts_remaining(self) -> int:
        return self.difficulty.max_attempts - self.attempts_used

    @property
    def won(self) -> bool:
        return bool(self.guesses) and self.guesses[-1] == self.secret

    @property
    def lost(self) -> bool:
        return not self.won and self.attempts_remaining == 0

    @property
    def wrong_guesses(self) -> list[int]:
        return [g for g in self.guesses if g != self.secret]

    def narrowed_range(self) -> tuple[int, int]:
        """Valid interval implied by guesses so far (inclusive)."""
        low, high = self.difficulty.low, self.difficulty.high
        for guess in self.guesses:
            if guess < self.secret:
                low = max(low, guess + 1)
            else:
                high = min(high, guess - 1)
        return low, high

    def submit(self, guess: int) -> GuessResult:
        """Apply a guess. Does not consume an attempt for duplicate/out-of-range."""
        if guess in self.guesses:
            return GuessResult.DUPLICATE
        if not self.difficulty.low <= guess <= self.difficulty.high:
            return GuessResult.OUT_OF_RANGE

        self.guesses.append(guess)
        if guess == self.secret:
            return GuessResult.CORRECT
        if guess < self.secret:
            return GuessResult.TOO_LOW
        return GuessResult.TOO_HIGH

    def score(self) -> int:
        if not self.won:
            return 0
        difficulty_bonus = self.difficulty.span * 10
        efficiency_bonus = self.attempts_remaining * 5
        return difficulty_bonus + efficiency_bonus

    def next_hint(self) -> str | None:
        if len(self.wrong_guesses) < HINT_AFTER_WRONG_GUESSES:
            return None
        if "parity" not in self.hints_shown:
            self.hints_shown.add("parity")
            parity = "even" if self.secret % 2 == 0 else "odd"
            return f"The number is {parity}."
        return None


@dataclass
class Session:
    """Tracks performance across multiple rounds."""

    player_name: str
    rounds_played: int = 0
    wins: int = 0
    total_score: int = 0
    best_attempts: int | None = None
    best_by_difficulty: dict[str, int] = field(default_factory=dict)

    def record(self, game_round: GameRound) -> None:
        self.rounds_played += 1
        if not game_round.won:
            return

        self.wins += 1
        self.total_score += game_round.score()
        used = game_round.attempts_used
        if self.best_attempts is None or used < self.best_attempts:
            self.best_attempts = used

        key = game_round.difficulty.key
        prior = self.best_by_difficulty.get(key)
        if prior is None or used < prior:
            self.best_by_difficulty[key] = used


# --- Shared feedback (CLI + GUI) ---


def message_for(result: GuessResult, game_round: GameRound, guess: int) -> str:
    if result is GuessResult.DUPLICATE:
        return f"You already tried {guess}. Pick a different number."
    if result is GuessResult.OUT_OF_RANGE:
        lo, hi = game_round.difficulty.low, game_round.difficulty.high
        return f"Stay between {lo} and {hi}."

    low, high = game_round.narrowed_range()
    range_hint = f" It's between {low} and {high}." if low <= high else ""
    if result is GuessResult.TOO_LOW:
        return f"Too low!{range_hint}"
    if result is GuessResult.TOO_HIGH:
        return f"Too high!{range_hint}"
    return ""


def win_message(game_round: GameRound, player_name: str) -> str:
    tries = game_round.attempts_used
    word = "try" if tries == 1 else "tries"
    return (
        f"Congratulations, {player_name}!\n"
        f"You found {game_round.secret} in {tries} {word}.\n"
        f"Score this round: {game_round.score()}"
    )


def loss_message(game_round: GameRound, player_name: str) -> str:
    low, high = game_round.narrowed_range()
    return (
        f"Game over, {player_name}.\n"
        f"The number was {game_round.secret} "
        f"(your clues narrowed it to {low}–{high})."
    )


# --- CLI presentation ---


def banner(title: str) -> None:
    line = "=" * BANNER_WIDTH
    print(line)
    print(title)
    print(line)


def prompt_name() -> str:
    name = input("What is your name? ").strip()
    return name or "Player"


def prompt_difficulty() -> Difficulty:
    print("\nChoose difficulty:")
    for index, diff in enumerate(DIFFICULTIES, start=1):
        print(
            f"  {index}) {diff.key.capitalize():6} ({diff.low}–{diff.high}, {diff.max_attempts} attempts)"
        )
    labels = {str(i): d.key for i, d in enumerate(DIFFICULTIES, start=1)}
    while True:
        choice = input("Enter 1, 2, or 3 [default 2]: ").strip() or "2"
        key = labels.get(choice)
        if key:
            return DIFFICULTY_BY_KEY[key]
        print("Invalid choice. Please enter 1, 2, or 3.")


def read_guess(game_round: GameRound) -> int | None:
    """Read and parse input. None means retry without using an attempt."""
    attempt = game_round.attempts_used + 1
    remaining = game_round.attempts_remaining
    low, high = game_round.difficulty.low, game_round.difficulty.high
    prompt = (
        f"Attempt {attempt}/{game_round.difficulty.max_attempts} "
        f"({remaining} left): guess ({low}–{high}): "
    )
    try:
        return int(input(prompt))
    except ValueError:
        print("Please enter a whole number.")
        return None


def print_win(game_round: GameRound, player_name: str) -> None:
    stars = "*" * BANNER_WIDTH
    print(f"\n{stars}")
    print(win_message(game_round, player_name))
    print(stars)


def print_loss(game_round: GameRound, player_name: str) -> None:
    print(f"\n{loss_message(game_round, player_name)}\n")


def wants_play_again() -> bool:
    while True:
        answer = input("Play again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no", ""):
            return False
        print("Please enter y or n.")


def print_session_summary(session: Session) -> None:
    if session.rounds_played == 0:
        print("Thanks for playing!")
        return

    print("\n--- Session summary ---")
    print(f"Rounds: {session.rounds_played}  |  Wins: {session.wins}")
    if session.total_score:
        print(f"Total score: {session.total_score}")
    if session.best_attempts is not None:
        print(f"Best win: {session.best_attempts} attempt(s)")
    for key, attempts in sorted(session.best_by_difficulty.items()):
        print(f"  {key.capitalize()} best: {attempts} attempt(s)")
    print("Thanks for playing!")


# --- Game loop ---


def run_round(player_name: str, difficulty: Difficulty) -> GameRound:
    game_round = GameRound.create(difficulty)
    print(
        f"\nHello, {player_name}! I'm thinking of a number "
        f"from {difficulty.low} to {difficulty.high}."
    )
    print(f"You have {difficulty.max_attempts} guesses. Good luck!\n")
    while game_round.attempts_remaining > 0:
        guess = read_guess(game_round)
        if guess is None:
            continue

        result = game_round.submit(guess)
        if result in (GuessResult.DUPLICATE, GuessResult.OUT_OF_RANGE):
            print(message_for(result, game_round, guess))
            continue

        if result is GuessResult.CORRECT:
            print_win(game_round, player_name)
            return game_round

        print(message_for(result, game_round, guess))
        if hint := game_round.next_hint():
            print(f"Hint: {hint}")
        print()

    print_loss(game_round, player_name)
    return game_round


def main() -> None:
    banner("Welcome to the Number Guessing Game!")
    session = Session(player_name=prompt_name())
    while True:
        difficulty = prompt_difficulty()
        game_round = run_round(session.player_name, difficulty)
        session.record(game_round)
        if not wants_play_again():
            break

    print_session_summary(session)


if __name__ == "__main__":
    main()
