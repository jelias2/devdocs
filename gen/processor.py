import os
from typing import Callable
from gen.log import get_logger
import toml

log = get_logger(__name__)

MAX_DEPTH = 5
INDEX_MOD = 'index'


def collect_files(root_path: str, predicate: Callable[[str, list[str], list[str]], bool], max_depth=MAX_DEPTH) -> list[str]:
    book_dirs = []
    for current_dir, subdirs, files in os.walk(root_path):
        relative_path = os.path.relpath(current_dir, root_path)
        current_depth = 0 if relative_path == '.' else relative_path.count(
            os.sep) + 1

        if current_depth > max_depth:
            subdirs.clear()
            continue

        if predicate(current_dir, subdirs, files):
            log.info(f'Found book in {current_dir}')
            book_dirs.append(current_dir)
    return book_dirs


def collect_books(root_path: str, max_depth: int) -> list[str]:
    return collect_files(root_path, lambda current_dir, subdirs, files: 'book.toml' in files, max_depth) 



def add_ga_tracking(ga_id: str, book_dir: str):
    """Add Google Analytics tracking to each of the books."""
    config_path = os.path.join(book_dir, 'book.toml')
    raw_config = toml.load(config_path)
    if 'output' not in raw_config:
        raw_config['output'] = {}
    if 'html' not in raw_config['output']:
        raw_config['output']['html'] = {}
    raw_config['output']['html']['google-analytics'] = ga_id
    with open(config_path, 'w') as f:
        toml.dump(raw_config, f)
