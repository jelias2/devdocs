from dataclasses import dataclass
import os
import toml
import subprocess
import sys

@dataclass
class BookConfig:
    site_url: str
    build_dir: str
    title: str
    description: str
    dir: str


def load_book_config(book_dir: str) -> BookConfig:
    dirname = os.path.basename(book_dir)
    raw_config = toml.load(os.path.join(book_dir, 'book.toml'))

    book_config = raw_config.get('book', {})
    build_config = raw_config.get('build', {})
    html_config = raw_config.get('output', {}).get('html', {})
    site_url = html_config.get('site-url', dirname)

    if site_url.startswith('/'):
        site_url = site_url[1:]

    config = BookConfig(
        site_url=site_url,
        build_dir=build_config.get('build-dir', 'book'),
        title=book_config.get('title', None),
        description=book_config.get('description', None),
        dir=book_dir,
    )
    return config 


def build_book(config: BookConfig):
    subprocess.run(
        ['mdbook', 'build'],
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        check=True,
        cwd=config.dir
    )