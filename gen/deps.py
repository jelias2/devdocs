import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from gen.log import get_logger

log = get_logger(__name__)

def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """Run a shell command and return True if successful."""
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Error running command {' '.join(cmd)}: {e}")
        return False

def clone_repo(url: str, path: str | Path, branch: str = "main") -> bool:
    """Clone a repository if it doesn't exist, or update it if it does."""
    path = Path(path)
    
    if not path.exists():
        log.info(f"Cloning {url} to {path}")
        if not run_command(["git", "clone", "-b", branch, url, str(path)]):
            return False
    else:
        log.info(f"Updating {path}")
        if not all([
            run_command(["git", "fetch", "origin"], cwd=path),
            run_command(["git", "checkout", branch], cwd=path),
            run_command(["git", "pull", "origin", branch], cwd=path)
        ]):
            return False
    return True

def create_readme(path: Path, content: str) -> bool:
    """Create a summary.md file with the provided content."""
    try:
        readme_path = path / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
        log.info(f"Created readme.md at {readme_path}")
        return True
    except Exception as e:
        log.error(f"Failed to create readme_path.md: {e}")
        return False

def create_book_config(path: Path, config: dict) -> bool:
    """Create or update book.toml with the provided configuration."""
    try:
        book_path = path / "book.toml"
        
        # Create book config from relevant sections
        book_config = {}
        for section in ['book', 'build', 'output']:
            if section in config:
                book_config[section] = config[section]

        # Write the configuration
        import toml
        with open(book_path, "w") as f:
            toml.dump(book_config, f)
        log.info(f"Created/updated book.toml at {book_path}")
        return True
    except Exception as e:
        log.error(f"Failed to create book.toml: {e}")
        return False

def manage_dependencies(root_dir: str) -> bool:
    """Manage dependencies based on dependencies.toml configuration."""
    deps_file = Path(root_dir) / "infra.dependencies.toml"
    if not deps_file.exists():
        log.error(f"Dependencies file not found at {deps_file}")
        return False

    try:
        import toml
        config = toml.load(deps_file)
    except Exception as e:
        log.error(f"Error loading dependencies.toml: {e}")
        return False

    success = True
    # Process dependencies
    for name, dep in config["dependencies"].items():
        log.info(f"Processing dependency {name}...")
        repo_path = Path(dep["path"])
        
        # Clone/update repository
        if not clone_repo(
            dep["url"], 
            repo_path, 
            dep.get("branch", "main")
        ):
            success = False
            log.error(f"Failed to process dependency {name}")
            continue

    # Create summary if it exists
    book_path = Path("submodules/index")
    if "summary" in config and "content" in config["summary"]:
        if not create_readme(book_path.joinpath("src"), config["summary"]["content"]):
           success = False
           log.error(f"Failed to create summary for {name}")

   # Create/update book.toml if book config exists
    if any(section in config for section in ['book', 'build', 'output']):
        if not create_book_config(book_path, config):
           success = False
           log.error(f"Failed to create book.toml for {name}")

    return success 