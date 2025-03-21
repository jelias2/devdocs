#!/usr/bin/env python3

import os
import yaml
import subprocess
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def generate_gitmodules(config):
    gitmodules_content = []
    for submodule in config["submodules"]:
        gitmodules_content.extend([
            f'[submodule "{submodule["path"]}"]',
            f'    path = {submodule["path"]}',
            f'    url = {submodule["url"]}',
            ''
        ])
    
    with open('.gitmodules', 'w') as f:
        f.write('\n'.join(gitmodules_content))

def init_submodules(config):
    for submodule in config["submodules"]:
        path = submodule["path"]
        url = submodule["url"]
        branch = submodule["branch"]
        
        # Create parent and child directories if they don't exist
        os.makedirs(path, exist_ok=True)
        # Initialize submodule if it doesn't exist
        subprocess.run(["git", "submodule", "add", url, path])
        
        # Checkout the correct branch
        subprocess.run(["git", "-C", path, "checkout", branch])

def main():
    config = load_config()
    generate_gitmodules(config)
    init_submodules(config)

if __name__ == "__main__":
    main() 