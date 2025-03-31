import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from gen.log import get_logger
from gen.rootconfig import RootConfig, DependencyConfig, BookConfig
from gen.rootconfig import create_book_toml
import toml

log = get_logger(__name__)


def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """Run a shell command and return True if successful."""
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True,
                       text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Error running command {' '.join(cmd)}: {e}")
        return False


def clone_repostiories(root_config: RootConfig) -> bool:
    """Clone all repositories based on dependencies.toml configuration."""

    success = True
    # Clone repositories
    for name, dep in root_config.dependencies.items():
        log.info(f"Processing dependency {name} @ {dep.branch}...")
        # Clone/update repository
        if not clone_repo(
            dep.url,
            dep.path,
            dep.branch
        ):
            success = False
            log.error(f"Failed to clone repository {name}")
            continue

    return success


def clone_repo(url: str, path: str | Path, branch: str = "main") -> bool:
    """Clone a repository if it doesn't exist, or update it if it does."""
    path = Path(path)

    # Modify URL if GitHub PAT exists
    github_pat = os.environ.get('GITHUB_PAT')
    github_user = os.environ.get('GITHUB_USER')
    if github_pat and url.startswith('https://github.com/') and github_user:
        log.info("Using GitHub PAT for authentication")
        # Format: https://{username}:{gh_pat_token}@github.com/org/repo.git
        auth_url = f'https://{github_user}:{github_pat}@github.com/{url.split("github.com/")[1]}'
        # log.info(f"Auth URL: {auth_url}")
        log.info(
            f"Auth URL (PAT hidden): https://{github_user}:****@github.com/{url.split('github.com/')[1]}")
        url = auth_url

    if not path.exists():
        log.info(f"Cloning {url} to {path}")
        if not run_command(["git", "clone", "-b", branch, url, str(path)]):
            return False
    else:
        log.info(f"Updating {path}")
        # Get current commit
        current = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=path).decode().strip()
        log.info(f"Current commit: {current}")

        # Just fetch the latest changes
        if not run_command(["git", "fetch", "origin", branch], cwd=path):
            return False

        # Get new commit
        new = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=path).decode().strip()
        log.info(f"Updated to commit: {new}")
    return True


def get_git_info(path: Path) -> tuple[str, str]:
    """Get git information for a repository."""
    commit = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=path).decode().strip()
    remote = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"], cwd=path).decode().strip()
    # Extract org/repo from remote URL
    if remote.endswith('.git'):
        remote = remote[:-4]
    remote = '/'.join(remote.split('/')[-2:])

    return commit, remote


def is_subdir(path: str | Path, parent: str | Path) -> bool:
    # Convert to Path objects and resolve to absolute paths
    path = Path(path).resolve()
    parent = Path(parent).resolve()

    try:
        # Use relative_to to check if path starts with parent
        path.relative_to(parent)
        return True
    except ValueError:
        return False
