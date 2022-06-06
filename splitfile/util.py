import sys
from glob import glob
from pathlib import Path
from typing import NoReturn

from rich import print, prompt


def error(message):
    return f'[bold red on rgb(60,0,0)]error  [/]｜ {message}'


def warning(message):
    return f'[bold yellow on rgb(60,60,0)]warning[/]｜ {message}'


def success(message):
    return f'[bold green on rgb(0,60,0)]success[/]｜ {message}'


def info(message):
    return f'[bold on rgb(60,60,60)]info  [/]｜ {message}'


def debug(message):
    return f'[bold dim on rgb(60,60,60)]debug  [/]｜ [dim]{message}'


def prompt_continue_or_quit(message) -> bool:
    """True means '[c]ontinue', False means '[s]kip'. Quits program if 'q' is entered."""
    print(message)
    choice = prompt.Prompt.ask('[bright_cyan]Continue?[/] (\[c]ontinue, \[s]kip current, \[q]uit program)', choices=['c', 's', 'q'])
    if choice == 'q':
        sys.exit(2)
    return choice == 'c'


def prompt_quit(message) -> NoReturn:
    print(message)
    choice = prompt.Prompt.ask('[bright_cyan]Quit program?[/] (\[n]o, \[q]uit program)', choices=['q', 'n'])
    if choice == 'q':
        sys.exit(2)


def is_a_splitpart(file):
    return Path(file).suffix[1:].isdigit()


def get_base_file(file) -> Path:
    file = Path(file)
    if not is_a_splitpart(file):
        return file
    return file.with_suffix('')


def get_splits(file) -> list[str]:
    file = Path(file)
    if is_a_splitpart(file):
        return list()
    prefix = str(file) + '.'
    splits = glob(prefix + '*')
    return sorted(splits)
