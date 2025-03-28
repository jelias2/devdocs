import os
import shutil
from pathlib import Path

from gen.log import get_logger
from gen.deps import clone_repostiories, get_git_info, is_subdir
from gen.rootconfig import RootConfig, load_root_config, create_book_toml, create_index_mdbook
from gen.book import BookConfig, load_book_config, build_book
from gen.processor import collect_books, INDEX_MOD, add_ga_tracking

log = get_logger(__name__)

def run(root_dir: str, config_file: str):
    """Run the book generator."""
    # First, manage dependencies
    root_config = load_root_config(root_dir, config_file)
    log.info(f"root_config title: {root_config.book.title}")
    log.info(f"root_config url: {root_config.book.url}")
    
    # Only override URL if DEPLOY_URL is explicitly set in environment
    deploy_url = os.environ.get('DEPLOY_URL')
    if deploy_url:
        deploy_url = deploy_url.rstrip('/')
        root_config.book.url = deploy_url
        log.info(f"Overriding config URL with deploy URL: {deploy_url}")

    if not clone_repostiories(root_config):
        log.error("Failed to manage dependencies")
        return

    if not create_index_mdbook(root_config):
        log.error("Failed to create index mdbook index")
        return

    submodules = os.listdir(os.path.join(root_dir, 'submodules'))

    # Put the index module first since it outputs to the public directory, which will be deleted
    # by the book processor
    index_module_idx = submodules.index(INDEX_MOD)
    submodules[0], submodules[index_module_idx] = submodules[index_module_idx], submodules[0]

    mods_by_book = []

    for mod in submodules:
        mod_path = os.path.join(root_dir, 'submodules', mod)
        book_dirs = collect_books(mod_path, root_config.book.max_depth)
        configs = []
        commit, remote = get_git_info(mod_path)
        
        for book_dir in book_dirs:
            add_ga_tracking(root_config.book.google_analytics, book_dir)
            configs.append(load_book_config(book_dir))
        mods_by_book.append((mod, configs, commit, remote))

    # Generate the README.md file for the index module
    with open(os.path.join(root_dir, 'submodules', 'index', 'src', 'README.md'), 'a') as f:
        for mod, configs, commit, remote in mods_by_book:
            if mod == INDEX_MOD:
                continue
            log.info(f"generating index readme for {mod}")
            f.write(f'## `{remote} @ {commit}`\n\n')
            for config in configs:
                config = load_book_config(config.dir)
                f.write(f'- [{config.title}]({root_config.book.url}/{config.site_url.replace('/', '')})\n')
            f.write('\n')

    # Create the build directory if it doesn't exist
    if not os.path.exists(os.path.join(root_dir, root_config.book.build_dir)):
        log.info(f'Creating build directory {os.path.join(root_dir, root_config.book.build_dir)}')
        os.mkdir(os.path.join(root_dir, root_config.book.build_dir))
    
    for mod, configs, _, _ in mods_by_book:
        log.info(f'Processing submodule {mod}')

        for config in configs:
            log.info(f'Building book {config.title}')
            build_book(config)

            if mod == INDEX_MOD:
                # Move the index book to the root public directory
                outdir = os.path.join(root_dir, root_config.book.build_dir)
            else:
                # For all other books, move them to the public directory with the site_url as the subdirectory
                outdir = os.path.join(root_dir, root_config.book.build_dir, config.site_url)

            log.info(f'Moving book {config.title} to {root_config.book.build_dir} dir {outdir}')

            if not is_subdir(outdir, root_dir):
                raise ValueError(
                    f'Output directory {outdir} is not a subdirectory of root dir {root_dir}!')
            if os.path.exists(outdir):
                log.info(f'Removing existing build dir {outdir}')
                shutil.rmtree(outdir)
            os.mkdir(outdir)

            os.rename(
                os.path.join(config.dir, config.build_dir),
                outdir
            )