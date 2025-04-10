# Typer CLI Application

A terminal-based typing practice application that helps improve your typing speed and accuracy.

## Features

- Real-time typing feedback
- Word-per-minute (WPM) calculation
- Accuracy tracking
- Customizable word count
- Customizable maximum length of words
- Terminal-based interface
- Color-coded feedback

## Installation

### Using pip
```bash
# install from source
git clone https://github.com/satvikgosai/typer.git
cd typer
pip install .
```

## Usage

### Basic Usage
```bash
typer
```

### Command Line Options
Specify the number of words (5 to 100) to practice with:
```bash
typer --num-words <words>
# or
typer -n <words>
```

Specify the maximum length of each word (1 to 100):
```bash
typer --max-word-length <length>
# or
typer -m <length>
```

### Controls
- Type the words as they appear
- Use backspace to correct mistakes
- Press Ctrl+C to exit

## Project Structure
```
typer/
├── typer/             # Main package directory
│   ├── __init__.py
│   ├── __main__.py    # Entry point
│   └── typer.py       # Main application logic
├── pyproject.toml     # Project configuration
└── README.md          # This file
```

## Requirements
- Python 3.6 or higher
- Unix-like terminal (Linux/macOS)
- Terminal with ANSI color support

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License.