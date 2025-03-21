import os

from gen.log import get_logger
import argparse

from gen import run

log = get_logger(__name__)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate book from configuration')
    parser.add_argument(
        '--config', 
        '-c',
        default='infra.dependencies.toml',
        help='Path to dependencies configuration file (default: infra.dependencies.toml)'
    )

    args = parser.parse_args()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log.info(f'Starting book generation from {root_dir}')
    run(root_dir, args.config)


if __name__ == "__main__":
    main()
