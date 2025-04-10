from typer import main


def parse_num_words_arg(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError("number of words must be integer")
    num_words = int(arg)
    if num_words > 100 or num_words < 5:
        raise argparse.ArgumentTypeError("number of words must be from 5 to 100")
    return num_words


def parse_max_word_length_arg(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError("maximum word length must be integer")
    max_word_length = int(arg)
    if max_word_length > 100 or max_word_length < 1:
        raise argparse.ArgumentTypeError("maximum word length must be from 1 to 100")
    return max_word_length


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Typing practice CLI application")
    parser.add_argument(
        '-n', '--num-words',
        type=parse_num_words_arg,
        default=15,
        help='Number of words to type (default: 15)'
    )
    parser.add_argument(
        '-m', '--max-word-length',
        type=parse_max_word_length_arg,
        default=8,
        help='Maximum length of each word (default: 8)'
    )
    args = parser.parse_args()

    main(args.num_words, args.max_word_length)
