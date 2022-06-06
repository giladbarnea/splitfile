#!/usr/bin/env python3
"""
join.py PATH... [--dry-run] [-h, --help] [--rm] [-y, --yes] [-v]
join.py 'lesson1/*.m*'
join.py lesson1 --rm
join.py lesson2 lesson1/Lesson_1_Introduction_Part_1.m4a --dry-run

--rm: remove .00 files after joining
--dry-run: don't actually join .00 files into a single file (diff if original exists)
-y: assume "yes" non-problem prompts
"""
import os
import sys
from glob import glob
from pathlib import Path

from rich import print, get_console

from splitfile.util import error, warning, success, info, debug, prompt_continue_or_quit, prompt_quit, is_a_splitpart, get_base_file, get_splits

files_to_join: set[Path] = set()

dry_run = False
rm_after_join = False
assume_yes = False
verbose = 0


def join_file(file: Path) -> bool:
    joined_path = Path(str(file) + '.joined')
    try:
        print()
        splits = get_splits(file)
        if not splits:
            message = warning(f'"{file}" has no splits ({file.stat().st_size / 1_000_000:,.2f} MB)')
            if assume_yes:
                print(message)
                return False
            prompt_quit(message)
            return False
        message = f'[bold]joining "{file}" ({len(splits)} splits, {sum(os.stat(split).st_size for split in splits) / 1_000_000:,.2f} MB total)'
        if verbose:
            print(debug(f'Splits: {", ".join(splits)}'))
        if assume_yes:
            print(message)
        elif not prompt_continue_or_quit(message):
            return False
        join_command = f'cat {" ".join(map(repr, splits))} > "{joined_path}"'
        join_exitcode = os.system(join_command)
        join_success = join_exitcode == 0
        if not join_success:
            prompt_quit(error(f'cat failed ({join_exitcode}) for {len(splits)} splits of "{file}"'))
            return False
        if file.exists():
            diff_command = f'diff -a "{joined_path}" "{file}"'
            diff_exitcode = os.system(diff_command)
            identical = diff_exitcode == 0
            if identical:
                print(info(f'joined file "{joined_path}" is identical to "{file}"'))
                rm_after_join and [os.remove(split) for split in splits]
                return True
            if not prompt_continue_or_quit(warning(f'concatenated file "{joined_path}" is not identical to pre-existing "{file}" (diff -a exitcode: {diff_exitcode})')):
                return False
        if dry_run:
            print(info(f'Dry run; would have renamed "{joined_path}" to "{file}"'))
            return True
        joined_path.rename(file)
        print(success(f'joined {len(splits)} splits into "{file}"'))
        rm_after_join and [os.remove(split) for split in splits]
        return True
    except Exception as e:
        get_console().print_exception(width=os.get_terminal_size()[0], show_locals=True)
        prompt_quit(error(f'[red]FAILED: join_file({file!r}) ({type(e).__qualname__})'))
        return False
    finally:
        joined_path.unlink(missing_ok=True)


def populate_files_to_join(file):
    file = Path(file)
    if is_a_splitpart(file):
        base_file = get_base_file(file)
        files_to_join.add(base_file)
    else:
        files_to_join.add(file)


def join_files(*paths):
    if not paths:
        print(error('no paths provided'))
        sys.exit(1)
    print(f'[bold]join_files({paths = !r})')
    for path in paths:
        if '*' in path:
            for file in filter(os.path.isfile, glob(path)):
                populate_files_to_join(file)
            continue
        if os.path.isfile(path):
            populate_files_to_join(path)
            continue
        if os.path.isdir(path):
            for file in filter(os.path.isfile, glob(f'{path}/*')):
                populate_files_to_join(file)
            continue
        prompt_quit(warning(f'{path!r} is not a file, nor a dir, and no "*" so cant glob. skipping'))
    for file in sorted(files_to_join):
        join_file(file)


def main():
    global dry_run, rm_after_join, assume_yes, verbose
    args = []
    while sys.argv[1:]:
        arg = sys.argv.pop(1)
        if arg == '-h' or 'help' in arg:
            print(__doc__)
            sys.exit(0)
        if arg == '--dry-run':
            dry_run = True
        elif arg == '--rm':
            rm_after_join = True
        elif arg in ('-y', '--yes'):
            assume_yes = True
        elif arg.startswith('-v'):
            verbose = arg.count('v')
        else:
            args.append(arg)

    join_files(*args)


if __name__ == '__main__':
    main()
