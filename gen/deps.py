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
    for name, dep in config["dependencies"].items():
        log.info(f"Processing dependency {name}...")
        if not clone_repo(dep["url"], dep["path"], dep.get("branch", "main")):
            success = False
            log.error(f"Failed to process dependency {name}")

    return success 