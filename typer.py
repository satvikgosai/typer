#!/usr/bin/env python3
import collections
import functools
import itertools
import os
import pathlib
import random
import signal
import string
import sys
import termios
import textwrap
import time
import tty

ascii_letters = set(string.ascii_letters)

printable = set(string.printable)

codes = {
    'clear': '\x1b[2J\x1b[3J',
    'back': '\x7f',
    'color_start': '\x1b[38;2;{r};{g};{b}m',
    'color_end': '\x1b[0m',
    'cursor_invisible': '\x1b[?25l',
    'cursor_visible': '\x1b[?12l\x1b[?25h',
    'cursor_start': '\x1b[H',
    'underline': '\x1b[4m{char}\x1b[0m'
}


def usable_words(max_word_length=8):
    words_path = pathlib.Path('/usr/share/dict/words')
    if not words_path.exists():
        print(f'Could not find words to use')
        exit(0)
    words = words_path.read_text().splitlines()
    return [word.lower() for word in words if len(word) <= max_word_length and not (set(word) - ascii_letters)]


class Sentence:
    _width = 100
    _height = 15
    _lines = 0
    _tmp_lines = 0
    _pad = ' '
    _cover = ' '

    def __init__(self, num_words=15, max_word_length=8):
        self._remain = collections.deque(' '.join(random.choices(usable_words(max_word_length), k=num_words)))
        self._len = len(self._remain)
        self._success = []
        self._errors = []
        self.refresh_dimensions()

    def __repr__(self):
        text = ''.join(itertools.chain(self._success, self._errors, self._remain))
        wrapped = textwrap.wrap(text, width=self._width, expand_tabs=False, drop_whitespace=False)
        success_errors = len(self._success) + len(self._errors)
        underline = success_errors - 1 if self.errors else success_errors
        final, count = ['\n\n', codes['color_start'].format(r=100, g=102, b=105)], 0
        self._tmp_lines = 2
        for sen in wrapped:
            final.append(self._pad)
            for w in sen:
                if count == len(self._success) and self.errors:
                    final.append(codes['color_start'].format(r=217, g=4, b=82))
                elif count == success_errors:
                    final.append(codes['color_end'])
                final.append(codes['underline'].format(char=w) if count == underline else w)
                count += 1
            final.append('\n')
            self._tmp_lines += 1
        final.append(codes['color_end'])
        return ''.join(final)

    def __len__(self):
        return self._len

    def __bool__(self):
        return bool(self._remain)

    @property
    def head(self):
        return self._remain[0]

    @classmethod
    def refresh_dimensions(cls):
        print(codes['clear'])
        term_size = os.get_terminal_size()
        cls._height = term_size.lines
        cls._width = int((term_size.columns * 0.8))
        cls._pad = ' ' * int((term_size.columns * 0.2) // 2)
        cls._cover = cls._pad + (' ' * cls._width)

    def success(self):
        self._success.append(self._remain.popleft())

    @property
    def errors(self):
        return bool(self._errors)

    def pop_error(self):
        self._errors.pop()

    def append_error(self, val):
        self._errors.append(val)


def refresh(cls):
    output_data = repr(cls)
    if cls._lines < cls._height:
        clear_data = codes['cursor_start'] + '\n'.join(cls._cover for _ in range(cls._lines))
    else:
        clear_data = codes['clear']
    sys.stdout.write(clear_data + codes['cursor_start'] + output_data)
    sys.stdout.flush()
    cls._lines = cls._tmp_lines


def resize(out, *_):
    Sentence.refresh_dimensions()
    refresh(out)


def main(num_words, max_word_length):
    stdin_fd = sys.stdin.fileno()
    try:
        old_settings = termios.tcgetattr(stdin_fd)
    except termios.error as e:
        print(f'This terminal is not supported: {e}')
        exit(0)
    try:
        sentence = Sentence(num_words, max_word_length)
        tty.setcbreak(stdin_fd)
        print(codes['cursor_invisible'])
        refresh(sentence)
        signal.signal(signal.SIGWINCH, functools.partial(resize, sentence))
        count_raw = total_time = 0
        while sentence:
            t0 = time.time()
            ch = os.read(stdin_fd, 80).decode("utf-8", errors="ignore")
            total_time += (time.time() - t0) if count_raw else 0
            if ch == codes['back']:
                if sentence.errors:
                    sentence.pop_error()
                    refresh(sentence)
            elif ch in printable:
                if sentence.errors or sentence.head != ch:
                    sentence.append_error(ch)
                else:
                    sentence.success()
                count_raw += 1
                refresh(sentence)
        total_time /= 60
        print('\nRaw Words/Minute: ', rwpm := round(count_raw / 5 / total_time, 1))
        print('Accuracy: ', acc := round(len(sentence) / count_raw * 100, 1), '%')
        print('Words/Minute: ', round(rwpm * acc / 100, 1))
    except(KeyboardInterrupt, SystemExit):
        print('\nExiting typer...')
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
        print(codes['cursor_visible'])
