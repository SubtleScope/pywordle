import argparse
from random import choice
from os.path import exists
from sqlite3 import connect
from textwrap import dedent
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

global hard_mode_a
global hard_mode_b_correct
global hard_mode_b_partial
global save_answers
hard_mode_a = []
hard_mode_b_correct = ['_', '_', '_', '_', '_']
hard_mode_b_partial = []
save_answers = []

class colors:
    CORRECT = '\033[92m'
    PARTIAL = '\033[93m'
    WRONG = '\033[91m'
    END = '\033[0m'

def build_pywordle_database():
    connection = connect('pywordle.sqlite')
    cursor = connection.cursor()

    cursor.execute('DROP TABLE IF EXISTS pywords')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('CREATE TABLE pywords (words TEXT)')
    cursor.execute('CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, user TEXT NOT NULL UNIQUE, wins INTEGER, losses INTEGER, games_played INTEGER)')

    url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
    word_page = get_web_page(url)
    for word in word_page:
        if word == '':
            continue
        word_list = word.upper().split('\n')

    for word in word_list:
        cursor.execute('INSERT INTO pywords (words) VALUES (?)', (word,))

    connection.commit()
    cursor.close()

def add_user_database(user):
    if exists('pywordle.sqlite'):
        connection = connect('pywordle.sqlite')
        cursor = connection.cursor()

        cursor.execute('INSERT OR IGNORE INTO users (user, wins, losses, games_played) VALUES (?, 0, 0, 0)', (user,))

    connection.commit()
    cursor.close()

    return f'\nUser {user} added to the pyWordle database.'

def check_users():
    if exists('pywordle.sqlite'):
        connection = connect('pywordle.sqlite')
        cursor = connection.cursor()

        user_query = cursor.execute('SELECT COUNT(ALL user) as count FROM users;')
        for count in user_query:
            user_count = count[0]

        if user_count == 0:
            cursor.close()
            return '\nNo users configured. Stats will not be saved.\n'
        elif user_count >= 2:
            print('\nThere are multiple users configured. Please tell pyWordle which user is playing.\n')
            user = input('pyWordle Users: ')
            cursor.execute(f'SELECT user FROM users WHERE user = "{user}"')
            get_user = cursor.fetchall()

            if len(get_user) == 0:
                print('\nUser does not exists. Exiting.\n')
                exit(1)
            else:
                user = get_user[0][0]
                print(f'\nWelcome back, {user}.\n')

            cursor.close()

            return user
        else:
            cursor.execute('SELECT user FROM users;')
            get_user = cursor.fetchall()
            user = get_user[0][0]
            print(f'\nWelcome back, {user}.\n')
            cursor.close()

            return user

def select_pywordle_word():
    if exists('pywordle.sqlite'):
        connection = connect('pywordle.sqlite')
        cursor = connection.cursor()
    
        cursor.execute('SELECT words FROM pywords LIMIT 1;')
        word = cursor.fetchone()

        cursor.execute('SELECT * FROM pywords;')
        word_list = list(cursor.fetchall())

    return word, word_list

def get_web_page(url):
    request = Request(
        url, 
        data = None,
        headers = {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        })
    html = urlopen(request).read()
    soup = BeautifulSoup(html, "html.parser")

    return soup

def check_guess(user, word, word_list, guess, game_mode, counter):
    database_exists = False
    if exists('pywordle.sqlite'):
        database_exists = True
        connection = connect('pywordle.sqlite')
        cursor = connection.cursor()

    if len(guess) == 5 and guess.isalpha():
        guess = guess.upper()

        wrong_word = False
        if guess not in word_list:
            print(f'\nThat word "{guess}" was not found in the word list. Please use a valid word.\n')
            wrong_word = True
            retry_guess = input('Enter your guess: ')
            check_guess(user, word, word_list, retry_guess, game_mode, counter=counter)

        if wrong_word == True:
            return ''

        reused_letter = False
        if game_mode == 'hard_a' and counter > 1:
            guess_letters = [letter for letter in guess]
            in_hard = [letter for letter in guess_letters if letter in hard_mode_a]
            if in_hard:
                print(f'\nYour guess "{guess}" contains previously used letters. Please guess again.\n')
                reused_letter = True
                retry_guess = input('Enter your guess: ')
                check_guess(user, word, word_list, retry_guess, game_mode, counter=counter)

        if reused_letter == True:
            return ''

        mode_b_retry = False
        if game_mode == 'hard_b' and counter > 1:
            word_letters = [letter for letter in word]
            guess_letters = [letter for letter in guess]
            correct_letters = [letter for letter in hard_mode_b_correct]
            positioanl_letters = [letter for letter in hard_mode_b_partial]

            in_guess_positional = all(elem in guess_letters for elem in positioanl_letters)

            for i in range(len(guess_letters)):
                if correct_letters[i] != '_' and correct_letters[i] not in guess_letters:
                    print(f'\nYou guessed {guess} which must contain the letter {correct_letters[i]} in position {str(i)}')
                    mode_b_retry = True
                    retry_guess = input('Enter your guess: ')
                    check_guess(user, word, word_list, retry_guess, game_mode, counter=counter)
                elif not in_guess_positional:
                    print(f'\nYou guessed {guess}, but you word must contain the letter(s) {positioanl_letters}\n')
                    mode_b_retry = True
                    retry_guess = input('Enter your guess: ')
                    check_guess(user, word, word_list, retry_guess, game_mode, counter=counter)
                else:
                    continue

        if mode_b_retry == True:
            return ''

        # split correct answer into letters
        word_letters = [letter for letter in word]
        # split user guess into letters
        guess_letters = [letter for letter in guess]

        # identify which letters exist in both
        in_both = [letter for letter in word_letters if letter in guess_letters]

        if in_both:
            partial_word = []
            for i in range(len(word_letters)):
                if word_letters[i] == guess_letters[i]:
                    partial_word.append(f'{colors.CORRECT}{guess_letters[i]}{colors.END}')
                    
                    if game_mode == 'hard_b':
                        hard_mode_b_correct[i] = guess_letters[i]
                elif guess_letters[i] in word_letters:
                    if guess_letters.count(guess_letters[i]) > word_letters.count(guess_letters[i]):
                        partial_word.append(f'{colors.WRONG}{guess_letters[i]}{colors.END}')
                    elif guess_letters.count(guess_letters[i]) == word_letters.count(guess_letters[i]):
                        partial_word.append(f'{colors.PARTIAL}{guess_letters[i]}{colors.END}')
                    else: 
                        partial_word.append(f'{colors.PARTIAL}{guess_letters[i]}{colors.END}')

                    if game_mode == 'hard_b':
                        if guess_letters[i] not in hard_mode_b_partial:
                            hard_mode_b_partial.append(guess_letters[i])
                else:
                    partial_word.append(f'{colors.WRONG}{guess_letters[i]}{colors.END}')
                    if game_mode == 'hard_a':
                        hard_mode_a.append(guess_letters[i])

            save_answers.append(f'''
            |                     |
        ({counter}) |  {partial_word[0]}   {partial_word[1]}   {partial_word[2]}   {partial_word[3]}   {partial_word[4]}  |
            |                     |
            ''')

            [print(save_answers[i]) for i in range(len(save_answers))]
        else:
            pos_0 = f'{colors.WRONG}{guess_letters[0]}{colors.END}'
            pos_1 = f'{colors.WRONG}{guess_letters[1]}{colors.END}'
            pos_2 = f'{colors.WRONG}{guess_letters[2]}{colors.END}'
            pos_3 = f'{colors.WRONG}{guess_letters[3]}{colors.END}'
            pos_4 = f'{colors.WRONG}{guess_letters[4]}{colors.END}'
            save_answers.append(f'''
            |                     |
        ({counter}) |  {pos_0}   {pos_1}   {pos_2}   {pos_3}   {pos_4}  |
            |                     |
            ''')
            [print(save_answers[i]) for i in range(len(save_answers))]
            if game_mode == 'hard_a':
                [hard_mode_a.append(guess_letters[i]) for i in range(len(guess_letters))]

        if counter == 6 and guess != word:
            if database_exists:
                # Insert stats into the database
                user_data = cursor.execute(f'SELECT wins, losses, games_played FROM users WHERE user = "{user}";')
                for row in user_data:
                    wins, losses, games_played = row

                losses += 1
                games_played += 1

                cursor.execute(f'UPDATE users SET losses = {losses}, games_played = {games_played} WHERE user = "{user}";')
                connection.commit()
                cursor.close()

            print(f'\nYou ran out of attempts and didn\'t pyWordle. Try again.\n')
            print(f'The word you were looking for is {word}.\n')
            exit(0)

        if guess == word:
            if database_exists:
                # Insert stats into the database
                user_data = cursor.execute(f'SELECT wins, losses, games_played FROM users WHERE user = "{user}";')
                for row in user_data:
                    wins, losses, games_played = row

                wins += 1
                games_played += 1

                cursor.execute(f'UPDATE users SET wins = {wins}, games_played = {games_played} WHERE user = "{user}";')
                connection.commit()
                cursor.close()

            print('\nCongrats! You solved the pyWordle!\n')
            if database_exists:
                print(f'Your current win/loss ratio is {(wins/games_played) * 100}%.\n')
                print(f'You have {wins} wins, {losses} losses, and have played {games_played} games.')
            print(save_answers[-1])
            exit(0)
    else:
        print(f'\nError: Too little or too many letters or non-alphabet characters provided in {guess}.\n')
        wrong_word = True
        retry_guess = input('Enter your guess: ')
        check_guess(user, word, word_list, retry_guess, game_mode, counter=counter)

def play_wordle(word, word_list, game_mode):
    word = word.upper()
    word_card = dedent(f'''
    Welcome to 🎵 Dun Dun Duh Dah 🎵
                __    __              _ _      
    _ __  _   _/ / /\ \ \___  _ __ __| | | ___ 
    | '_ \| | | \ \/  \/ / _ \| '__/ _` | |/ _ \\
    | |_) | |_| |\  /\  / (_) | | | (_| | |  __/
    | .__/ \__, | \/  \/ \___/|_|  \__,_|_|\___|
    |_|    |___/                                
    
        .____________________.
        |                    |
    (1) | {colors.CORRECT}A{colors.END}   {colors.WRONG}P{colors.END}   {colors.WRONG}P{colors.END}   {colors.PARTIAL}L{colors.END}   {colors.PARTIAL}E{colors.END}  |
        |                    |
    (2) | {colors.CORRECT}A{colors.END}   {colors.PARTIAL}T{colors.END}   {colors.PARTIAL}L{colors.END}   {colors.PARTIAL}A{colors.END}   {colors.WRONG}S{colors.END}  |
        |                    |
    (3) | {colors.CORRECT}A{colors.END}   {colors.WRONG}B{colors.END}   {colors.WRONG}O{colors.END}   {colors.WRONG}U{colors.END}   {colors.CORRECT}T{colors.END}  |
        |                    |
    (4) | {colors.CORRECT}A{colors.END}   {colors.CORRECT}L{colors.END}   {colors.PARTIAL}L{colors.END}   {colors.WRONG}O{colors.END}   {colors.CORRECT}T{colors.END}  |
        |                    |
    (5) | {colors.CORRECT}A{colors.END}   {colors.CORRECT}L{colors.END}   {colors.CORRECT}E{colors.END}   {colors.CORRECT}R{colors.END}   {colors.CORRECT}T{colors.END}  |
        |                    |
    (6) | __  __  __  __  __ |
        |                    |
        .____________________.
    ''')

    print(word_card)

    user = check_users()

    guess1 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess1, game_mode, counter=1)

    guess2 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess2, game_mode, counter=2)

    guess3 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess3, game_mode, counter=3)

    guess4 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess4, game_mode, counter=4)

    guess5 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess5, game_mode, counter=5)

    guess6 = input('Enter your guess: ')
    check_guess(user, word, word_list, guess6, game_mode, counter=6)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play Wordle with Python!')
    parser.add_argument('-a', '--adduser', metavar='<username>', help='Add a user to the databse.')
    parser.add_argument('-b', '--build', action='store_true', help='Build the pyWordle database.')
    parser.add_argument('--hard_a', action='store_true', help='Enable Hard Mode A: No Repeated wrong letters.')
    parser.add_argument('--hard_b', action='store_true', help='Enable Hard Mode B: Guesses must include ' + 
                                                         'correctly guessed letters and correct, but incorrectly placed letters.')
    parser.add_argument('-r', '--read', metavar='<word list file>', help='Provide a list of five letter words to use the dictionary.')

    args = parser.parse_args()

    if args.build:
        build_pywordle_database()
        exit(0)

    if args.adduser:
        user = args.adduser
        add_user_database(user)
        exit(0)

    if args.hard_a:
        game_mode = 'hard_a'
    elif args.hard_b:
        game_mode = 'hard_b'
    else:
        game_mode = 'easy'

    if args.read:
        word_list = []
        if exists(args.read):
            with open(args.read, 'r') as f:
                words = f.read().splitlines()
            
            for word in words:
                if word not in word_list:
                    word_list.append(word.upper())

        word = choice(word_list)
        play_wordle(word, word_list, game_mode)
        exit(0)

    if exists('pywords.sqlite'):
        word, word_list = select_pywordle_word()
    else:
        url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
        word_page = get_web_page(url)
        for word in word_page:
            if word == '':
                continue
            word_list = word.upper().split('\n')

        word = choice(word_list)

    play_wordle(word, word_list, game_mode)