# pyWordle
```             __    __              _ _      
    _ __  _   _/ / /\ \ \___  _ __ __| | | ___ 
    | '_ \| | | \ \/  \/ / _ \| '__/ _` | |/ _ \
    | |_) | |_| |\  /\  / (_) | | | (_| | |  __/
    | .__/ \__, | \/  \/ \___/|_|  \__,_|_|\___|
    |_|    |___/
```

## Bugs/Issues
- There are known/minor issues that are being worked out
  - Hard Mode B: After incorrect guesses, the counter stays at the number where the error occurred
  - There are probably some other issues too

## Description 
- Wordle game written in Python 3
- Cuttently uses the wordlist from the Stanford GraphBase (Public Domain) 
  - [Five Letter Words](https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt)
  - [Additional Information](https://www-cs-faculty.stanford.edu/~knuth/sgb.html)

## Features
### Database/Word Lists
- Database support (Best)
  - Wordlist only needs to be read once
  - Multi-user support 
  - Score recording 
- Wordlist from file (Decent)
  - Will read a local file to be used as the word list
  - `./pywordle.py -r /path/to/word_list.txt`
- Wordlist from the Internet (Okay)
  - Will pull down the word list every time

### Game Modes
- Easy mode
  - Standard Wordle-like gameplay
- Hard Mode A
  - Cannot use letters which have been previosuly used
- Hard Mode B
  - Each guess has to include previously correctly placed and incorrectly placed letters
  - If the letter is placed correctly, the letter must be used in that position for subsequent guesses
  - If the letter is correct but placed incorrectly, the letter must be used in subsequent guesses 

## Getting Started
1) Install required package(s)
  - `pip install bs4`

2) Set the permissions
  - `chmod +x pywordle.py`

3) Configure the Database
  - `./pywordle.py -b`

4) Add a user to the database
  - `./pywordle -a <username>`

5a) Easy mode/Standard play
  - `./pywordle`

5b) Hard mode A
  - `./pywordle --hard_a`

5c) Hard mode B
  - `./pywordle --hard_b`
