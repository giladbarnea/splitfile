#!/usr/bin/env python3
"""
split.py PATH... [-b, --bytes=SIZE (default 49MB)] [--dry-run] [-h, --help]
split.py 'lesson1/*.m*'
split.py lesson1 --bytes 49MB
split.py lesson2 lesson1/Lesson_1_Introduction_Part_1.m4a -b 10MB
"""
import os
import sys
from glob import glob
from pathlib import Path

from rich import print, get_console

from splitfile.util import prompt_quit, debug, info, prompt_continue_or_quit, success, error, warning, is_a_splitpart, get_splits

split_bytes = '49MB'
dry_run = False


def split_file(path, split: str):
    """'split' is e.g '49MB' or '10KB'"""
    try:
        path = Path(path)
        split = split.upper()
        stat = os.stat(path)
        # 'normalized_file_size' is normalized to 'unit', depending on 'split', to compare afterwards.
        # e.g if 'split' is '49MB', and actual file size is 50MB, then 'normalized_file_size' is 50, 'split_by' is 49, and 'unit' is 'MB'.
        if split.endswith('KB'):
            normalized_file_size = stat.st_size / 1_000
            split_by = int(split[:-2])
            unit = 'KB'
        elif split.endswith('MB'):
            normalized_file_size = stat.st_size / 1_000_000
            split_by = int(split[:-2])
            unit = 'MB'
        elif split.endswith('GB'):
            normalized_file_size = stat.st_size / 1_000_000_000
            split_by = int(split[:-2])
            unit = 'GB'
        else:
            normalized_file_size = stat.st_size
            split_by = int(split)
            unit = 'B'
        if is_a_splitpart(path):
            print(debug(f'{path} is a split part, skipping'))
            return True
        print()
        if normalized_file_size <= split_by:
            print(info(f'"{path}" size is <= {split}; skipping ({normalized_file_size = :,.2f}{unit})'))
            return True

        if splits := get_splits(path):
            print(info(f'"{path}" already split to {len(splits)} splits; skipping'))
            return True
        # suffix_length is 2 by default. This means max 100 splits. With big files, that's not enough.
        suffix_length = len(str(int(normalized_file_size / split_by)))
        prefix = str(path) + '.'
        split_command = f'split -d -b {split} -a {suffix_length} "{path}" "{prefix}"'
        prompt_continue_or_quit(f'[bold]splitting "{path}" ({normalized_file_size = :,.2f}{unit}) by running:\n\t[/][reset][i on rgb(50,50,50)]{split_command}')
        if dry_run:
            print(info(f'Dry run; would have run: {split_command!r}'))
            return True
        print(info(f'running: {split_command!r}...'))
        split_exitcode = os.system(split_command)
        split_success = split_exitcode == 0
        if split_success:
            print(success(split_command))
        else:
            prompt_quit(error(f'FAILED: {split_command}'))
        return success
    except Exception as e:
        get_console().print_exception(width=os.get_terminal_size()[0], show_locals=True)
        prompt_quit(error(f'[red]FAILED: "{path}" ({type(e).__qualname__})'))
        return False


def split_files(*paths, split: str):
    if not paths:
        print(error('no paths provided'))
        sys.exit(1)
    print(f'[bold]split_files({paths = !r}, {split = !r})')
    for path in paths:
        if '*' in path:
            for file in filter(os.path.isfile, glob(path)):
                split_file(file, split)
            continue
        if os.path.isfile(path):
            split_file(path, split)
            continue
        if os.path.isdir(path):
            for file in filter(os.path.isfile, glob(f'{path}/*')):
                split_file(file, split)
            continue
        prompt_quit(warning(f'{path!r} is not a file, nor a dir, and no "*" so cant glob. skipping'))


def main():
    global dry_run, split_bytes
    args = []
    while sys.argv[1:]:
        arg = sys.argv.pop(1)
        if arg.startswith('-b') or arg.startswith('--bytes'):
            if '=' in arg:
                split_bytes = arg.split('=')[1]
            else:
                split_bytes = sys.argv.pop(1)
        elif arg == '--dry-run':
            dry_run = True
        elif arg == '-h' or 'help' in arg:
            print(__doc__)
            sys.exit(0)
        else:
            args.append(arg)

    split_files(*args, split=split_bytes)


if __name__ == '__main__':
    main()
