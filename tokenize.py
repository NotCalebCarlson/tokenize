import json
import os
import time

BRIGHT_RED = '\033[91m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


class Progressbar:
    def __init__(self, string, interval):
        self.string = string
        self.interval = interval
        self.count = 0
        self.before = 0
        self.current = 0


    def update(self, force = False):
        self.count += 1
        self.current = time.time()
        if self.current - self.before > self.interval or force:
            clear_screen();
            print(self.string.format(self.count))
            self.before = time.time()


def tokenize(string, low, high):
    if len(string) < low:
        raise Exception("Error, lower dimension is greater than the target string")

    tokens = {}

    for window_width in range(low, min(high, len(string)) + 1):
        for pos in range(0, len(string) - window_width + 1):
            token = string[pos:pos+window_width]
            if tokens.get(token):
                tokens[token] += 1
            else:
                tokens[token] = 1

    return tokens


def min_similarities(dict1, dict2):

    similarities = 0

    for key in dict1.keys():
        count2 = dict2.get(key)
        count2 = 0 if not count2 else count2
        count1 = dict1.get(key)
        similarities += min(count2, count1)

    return similarities


def compare_tokens(search_tokens, progressbar):
    def compare(verse_tokens):
        progressbar.update()
        return min_similarities(search_tokens, verse_tokens[0])

    return compare


def color_string(target_string, tokens, low):

    new_string = ""
    residual = -1
    highlight = False

    for pos in range(0, len(target_string) - low + 1):
        token = target_string[pos:pos+low]

        if tokens.get(token):
            residual = low
        else:
            residual -= 1

        # Check to see if we have transitioned from a section
        # of unhighlighted string to highlighted string
        if highlight == False and residual == low:
            new_string += YELLOW
            new_string += target_string[pos]
            highlight = True

        # Check to see if we have transitioned from a section
        # of highlighted string to unhighlighted string
        elif highlight == True and residual == 0:
            new_string += RESET
            new_string += target_string[pos]
            highlight = False

        # Either we are continuing a highlighted portion or we
        # are continuing a portion of unhighlighted string.
        else:
            new_string += target_string[pos]

    # The above for-loop cannot format the last few characters
    # because it only inserts formatting flags at the beginning
    # of a moving window which cannot extend beyond the end of
    # our target_string. For example:
    #
    # token = "her?"
    # target_string = "...commandments of the father?"
    #
    #                           her? < token
    # ...commandments of the father? < target_string
    # ...commandments of the fath    < new_string
    #                           ^
    #                  maximum veiw of loop
    #
    # The limited view of our loop leaves the characters "er?"
    # unformatted.
    #
    # Because of this, we need some extra logic to add proper
    # formatting to the final characters of our target_string

    final_position = len(target_string) - low
    final_characters = target_string[final_position + 1: final_position + low]

    final_characters = final_characters[0:residual-1] +\
                       RESET +\
                       final_characters[residual-1:len(final_characters)]

    return new_string + final_characters


if __name__ == "__main__":

    book_file = open("bom.json")

    references = []
    verses = []
    verse_tokens = []

    bom_json = json.loads(book_file.read())
    book_file.close()

    progressbar = Progressbar("Loading verses... {}/6605", 1/8)

    for book in bom_json.get("books"):
        for chapter in book.get("chapters"):
            for verse in chapter.get("verses"):
                verses.append(verse.get("text").lower())
                references.append(verse.get("reference"))
                verse_tokens.append(tokenize(verses[-1], 3, 7))
                progressbar.update()
    progressbar.update(True)

    while True:

        search_string = input("> ").lower()
        search_tokens = tokenize(search_string, 3, 7)

        progressbar = Progressbar("Searching verses... {}/6605", 1/60)

        sorted_verses = sorted(zip(verse_tokens, references, verses), key = compare_tokens(search_tokens, progressbar), reverse = True)

        progressbar.update(True)
        print(f"\n{YELLOW}{search_string}{RESET}\n")

        for index in range(0, 5):
            highlighted_string = color_string(sorted_verses[index][2], search_tokens, 3)
            print(f"|{GREEN}{sorted_verses[index][1]}{RESET}| ({min_similarities(sorted_verses[index][0], search_tokens)} similarities)\n{highlighted_string}{RESET}\n\n")
