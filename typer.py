#!/usr/bin/env python3
import collections
import itertools
import os
import random
import string
import sys
import termios
import time
import tty

WORDS_PATH = '/usr/share/dict/words'

with open(WORDS_PATH, 'r') as f:
    words = f.read().splitlines()

ascii_letters = set(string.ascii_letters)

usable_words = list(set(word.lower() for word in words if not (set(word) - ascii_letters)))

codes = {
    'clear': '\x1b[H\x1b[2J\x1b[3J',
    'back': '\x7f',
    'color': '\x1b[{back};2;{r};{g};{b}m{char}\x1b[0m',
    'cursor_invisible': '\x1b[?25l',
    'cursor_visible': '\x1b[?12l\x1b[?25h',
    'underline': '\x1b[4m{char}\x1b[0m'
}


def pixel(char, r, g, b, back=False):
    back = [38, 48][back]
    return codes['color'].format(back=back, r=r, g=g, b=b, char=char)


class Sentence:

    def __init__(self, length=15):
        self._remain = collections.deque(' '.join(random.choices(usable_words, k=length)))
        self._len = len(self._remain)
        self._success = []
        self._errors = []

    def __repr__(self):
        errors, remain, u = self._errors, self._remain, ''
        if errors:
            *errors, u = errors
        elif remain:
            u, *remain = remain
        return ''.join(itertools.chain(self._success, errors, [codes['underline'].format(char=u)], remain))

    def __len__(self):
        return self._len

    def __bool__(self):
        return bool(self._remain)

    @property
    def head(self):
        return self._remain[0]

    def success(self):
        self._success.append(pixel(self._remain.popleft(), 100, 102, 105))

    @property
    def errors(self):
        return bool(self._errors)

    def pop_error(self):
        self._errors.pop()

    def append_error(self, val):
        self._errors.append(pixel(val, 217, 4, 82))


def stdout(*args):
    print(*args, sep='', end='', flush=True)


def main():
    stdin_fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)
    try:
        while not (inp := input('Enter word amount: ') or '15').isdigit() or not (num := int(inp)): pass
        sentence = Sentence(num)
        tty.setcbreak(stdin_fd)
        stdout(codes['cursor_invisible'])
        stdout(codes['clear'])
        stdout(sentence)
        count_raw = 0
        total_time = 0
        while sentence:
            t0 = time.time()
            ch = os.read(stdin_fd, 80).decode("utf-8", errors="ignore")
            total_time += (time.time() - t0) if count_raw else 0
            if sentence.errors:
                if ch == codes['back']:
                    sentence.pop_error()
                elif ch.isalnum():
                    count_raw += 1
                    sentence.append_error(ch)
            elif sentence.head == ch:
                count_raw += 1
                sentence.success()
            elif ch.isalnum():
                count_raw += 1
                sentence.append_error(ch)
            stdout(codes['clear'])
            stdout(sentence)
        total_time /= 60
        print('\nRWPM: ', rwpm := round(count_raw / 5 / total_time, 1))
        print('Accuracy: ', acc := round(len(sentence) / count_raw * 100, 1))
        print('WPM: ', round(rwpm * acc / 100, 1))
    except(KeyboardInterrupt, SystemExit):
        print('\nExiting gracefully...')
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
        stdout(codes['cursor_visible'])
    return main() if input().lower() == 'y' else None

if __name__ == '__main__':
    main()
