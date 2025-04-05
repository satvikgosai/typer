from typer import main


def parse_words_arg(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError("words must be integer")
    words = int(arg)
    if words > 100 or words < 5:
        raise argparse.ArgumentTypeError("words must be from 5 to 100")
    return words


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Typing practice CLI application")
    parser.add_argument('-w', '--words', type=parse_words_arg, default=15, help='Number of words (default: 15)')
    args = parser.parse_args()

    main(args.words)
