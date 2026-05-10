---
author: "Kyle Jones"
date_published: "December 20, 2023"
date_exported_from_medium: "November 10, 2025"
canonical_link: "https://medium.com/@kyle-t-jones/learning-python-by-building-a-simple-guessing-game-86d4f41fc2b8"
---

# Learning Python by building a Simple Guessing Game This is a simple project to show how you can input data and compare it
against the value of a variable.

### Learning Python by building a simple guessing game
#### This is a simple project to show how you can input data and compare it against the value of a variable.
There are lots of ways to build a game in python. The purpose of this project is to introduce people new to python with some of the concepts of writing a simple program --- and to have a little fun.

Learning to code is most fun when you're building something interactive! In this tutorial, we'll create a number guessing game that demonstrates several fundamental Python concepts:

- Importing and using modules
- Getting user input
- Working with variables and data types
- Using conditional statements (if/elif/else)
- Creating loops
- String formatting

The best part? You can play the game you build and share it with friends!

### The Game Concept
The computer "thinks" of a random number between 1 and 20, and the player has 6 chances to guess it. After each guess, the computer provides a hint: "too high" or "too low". Let's build this step by step.

### Step 1: Setting Up the Game
First, we need to import the `random` module and generate our secret number. Python has thousands of modules that add functionality\-\--`random` helps us generate random numbers.

```python
import random

# Generate a random number between 1 and 20
secret_number = random.randint(1, 20)
# Greet the player and get their name
print("=" * 40)
print("Welcome to the Number Guessing Game!")
print("=" * 40)
name = input("What is your name? ")
print(f"\nHello, {name}! I'm thinking of a number between 1 and 20.")
print("You have 6 chances to guess it. Good luck!\n")
```

Key Concepts:

- `random.randint(1, 20)` generates a random integer from 1 to 20 (inclusive)
- `input()` gets text from the user and returns it as a string
- `f"..."` creates a formatted string (called an f-string) where you can embed variables
- `print()` displays text to the user

### Step 2: The Game Loop
Now we create a loop that gives the player up to 6 attempts. We track how many guesses they've made and check if they found the answer.

``` 
max_attempts = 6
attempts = 0
won = False

while attempts < max_attempts:
    attempts += 1
    
    # Get the player's guess and convert it to an integer
    try:
        guess = int(input(f"Attempt {attempts}: Enter your guess: "))
    except ValueError:
        print("Please enter a valid number!")
        attempts -= 1  # Don't count invalid input as an attempt
        continue
    
    # Check the guess
    if guess < secret_number:
        print("Too low! Try a higher number.\n")
    elif guess > secret_number:
        print("Too high! Try a lower number.\n")
    else:
        # They got it!
        won = True
        print(f"\n{'*' * 40}")
        print(f"Congratulations, {name}!")
        print(f"You guessed the number {secret_number} in {attempts} tries!")
        print(f"{'*' * 40}")
        break
```

Key Concepts:

- `while` creates a loop that continues as long as the condition is true
- `attempts += 1` is shorthand for `attempts = attempts + 1`
- `try/except` handles errors gracefully (like when someone types \"five\" instead of 5)
- `break` exits the loop immediately
- `continue` skips the rest of the loop and goes to the next iteration

### Step 3: Ending the Game
Finally, if the player doesn't guess correctly within 6 attempts, we reveal the answer.

``` 
# If they didn't win, tell them the answer
if not won:
    print(f"\nGame Over!")
    print(f"Sorry, {name}. You've used all {max_attempts} attempts.")
    print(f"The secret number was {secret_number}.")
    print(f"Better luck next time!\n")
```

### The Complete Game
Here's the full, working code all together:

```python
import random

# Generate a random number between 1 and 20
secret_number = random.randint(1, 20)
# Greet the player
print("=" * 40)
print("Welcome to the Number Guessing Game!")
print("=" * 40)
name = input("What is your name? ")
print(f"\nHello, {name}! I'm thinking of a number between 1 and 20.")
print("You have 6 chances to guess it. Good luck!\n")
# Game loop
max_attempts = 6
attempts = 0
won = False
while attempts < max_attempts:
    attempts += 1
    
    # Get the player's guess
    try:
        guess = int(input(f"Attempt {attempts}: Enter your guess: "))
    except ValueError:
        print("Please enter a valid number!")
        attempts -= 1
        continue
    
    # Check the guess
    if guess < secret_number:
        print("Too low! Try a higher number.\n")
    elif guess > secret_number:
        print("Too high! Try a lower number.\n")
    else:
        # They got it!
        won = True
        print(f"\n{'*' * 40}")
        print(f"Congratulations, {name}!")
        print(f"You guessed the number {secret_number} in {attempts} tries!")
        print(f"{'*' * 40}")
        break
# End game message
if not won:
    print(f"\nGame Over!")
    print(f"Sorry, {name}. You've used all {max_attempts} attempts.")
    print(f"The secret number was {secret_number}.")
    print(f"Better luck next time!\n")
```

### Example Output
Here's what a game session might look like:

``` 
========================================
Welcome to the Number Guessing Game!
========================================
What is your name? Sarah
```

``` 
Hello, Sarah! I'm thinking of a number between 1 and 20.
You have 6 chances to guess it. Good luck!
```

``` 
Attempt 1: Enter your guess: 10
Too low! Try a higher number.
```

``` 
Attempt 2: Enter your guess: 15
Too high! Try a lower number.
```

``` 
Attempt 3: Enter your guess: 13
Too high! Try a lower number.
```

``` 
Attempt 4: Enter your guess: 11
Too low! Try a higher number.
```

``` 
Attempt 5: Enter your guess: 12
```

``` 
****************************************
Congratulations, Sarah!
You guessed the number 12 in 5 tries!
****************************************
```

### Challenge Yourself!
Now that you have a working game, try these enhancements:

1.  [Difficulty Levels: Let the player choose easy (1--10), medium (1--20), or hard (1--50)]
2.  [Play Again: Add a feature to play multiple rounds without restarting the program]
3.  [Scoring System: Award more points for guessing with fewer attempts]
4.  [Hints: After 3 wrong guesses, tell the player if the number is even or odd]
5.  [Best Score: Keep track of the player's best (fewest attempts) across multiple games]

### What You Learned
By building this game, you've learned:

- How to structure a complete Python program
- Working with user input and output
- Using variables to track state (attempts, won, etc.)
- Conditional logic with if/elif/else
- Loops with while
- Error handling with try/except
- String formatting with f-strings

These are fundamental skills you'll use in every Python program you write, from data analysis to web development to automation. The key is to start simple, make it work, then gradually add features. Keep experimenting and have fun coding!
