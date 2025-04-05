#!/usr/bin/env python3
import collections
import functools
import itertools
import os
import random
import signal
import string
import sys
import termios
import textwrap
import time
import tty

WORDS_PATH = '/usr/share/dict/words'

with open(WORDS_PATH, 'r') as f:
    words = f.read().splitlines()

ascii_letters = set(string.ascii_letters)

usable_words = list(set(word.lower() for word in words if not (set(word) - ascii_letters)))

printable = set(string.printable)

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
    _width = 100
    _pad = ' '

    def __init__(self, length=15):
        self._remain = collections.deque(' '.join(random.choices(usable_words, k=length)))
        self._len = len(self._remain)
        self._success = ''
        self._errors = []
        self.update_width()

    def __repr__(self):
        text = ''.join(itertools.chain(self._success, self._errors, self._remain))
        wrapped = textwrap.wrap(text, width=self._width, expand_tabs=False, drop_whitespace=False)
        s_cur = len(self._success)
        e_cur = s_cur + len(self._errors)
        u = s_cur if s_cur == e_cur else e_cur - 1
        final, count = ['\n\n'], 0
        for sen in wrapped:
            final.append(self._pad)
            for w in sen:
                if count < s_cur:
                    cur = pixel(w, 100, 102, 105)
                elif count < e_cur:
                    cur = pixel(w, 217, 4, 82)
                else:
                    cur = w
                final.append(cur if count != u else codes['underline'].format(char=cur))
                count += 1
            final.append('\n')
        return ''.join(final)

    def __len__(self):
        return self._len

    def __bool__(self):
        return bool(self._remain)

    @property
    def head(self):
        return self._remain[0]

    @classmethod
    def update_width(cls):
        term_len = os.get_terminal_size().columns
        cls._width = int((term_len * 0.8))
        cls._pad = ' ' * int((term_len * 0.2) // 2)

    def success(self):
        self._success += self._remain.popleft()

    @property
    def errors(self):
        return bool(self._errors)

    def pop_error(self):
        self._errors.pop()

    def append_error(self, val):
        self._errors.append(val)


def refresh(out):
    t0 = time.time()
    out_repr = repr(out)
    t1 = time.time() - t0
    sys.stdout.write(codes['clear'])
    sys.stdout.write(out_repr)
    sys.stdout.flush()
    print(f'repr: {t1}', f'raw: {out_repr!r}')


def resize(out, *_):
    Sentence.update_width()
    refresh(out)


def main():
    stdin_fd = sys.stdin.fileno()
    try:
        old_settings = termios.tcgetattr(stdin_fd)
    except termios.error as e:
        print(f'This terminal is not supported: {e}')
        exit(0)
    try:
        while not (inp := input('Enter word amount: ') or '15').isdigit() or not (num := int(inp)): pass
        sentence = Sentence(num)
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
        print('\nRWPM: ', rwpm := round(count_raw / 5 / total_time, 1))
        print('Accuracy: ', acc := round(len(sentence) / count_raw * 100, 1))
        print('WPM: ', round(rwpm * acc / 100, 1))
    except(KeyboardInterrupt, SystemExit):
        print('\nExiting gracefully...')
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
        print(codes['cursor_visible'])
    return main() if input().lower() == 'y' else None


if __name__ == '__main__':
    main()
