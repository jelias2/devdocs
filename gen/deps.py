import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from gen.log import get_logger
from gen.rootconfig import RootConfig, DependencyConfig, BookConfig
import toml

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
        # Get current commit
        if not run_command(["git", "rev-parse", "HEAD"], cwd=path):
            return False
        current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path).decode().strip()
        log.info(f"Current commit: {current}")

        if not all([
            run_command(["git", "fetch", "origin"], cwd=path),
            run_command(["git", "reset", "--hard", "HEAD"], cwd=path),
            run_command(["git", "clean", "-fd"], cwd=path),
            run_command(["git", "pull", "origin", branch], cwd=path)
        ]):
            return False

        # Get new commit
        if not run_command(["git", "rev-parse", "HEAD"], cwd=path):
            return False
        new = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path).decode().strip()
        log.info(f"Updated to commit: {new}")
    return True

def create_readme(path: Path, content: str) -> bool:
    """Create a readme.md file with the provided content."""
    try:
        # Create parent directories if they don't exist
        path.mkdir(parents=True, exist_ok=True)
        
        readme_path = path / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
            log.info(f"Created readme.md at {readme_path}")
        return True
    except Exception as e:
        log.error(f"Failed to create readme.md: {e}")
        return False

def create_book_toml(path: Path, root_config: RootConfig) -> bool:
    """Create or update book.toml with the provided configuration."""
    try:
        book_path = path / "book.toml"
        
        # Create book config with the correct structure and defaults
        book_config = {
            "book": {
                "authors": getattr(root_config.book, "authors", ["Unknown"]),
                "language": getattr(root_config.book, "language", "en"),
                "multilingual": getattr(root_config.book, "multilingual", False),
                "src": getattr(root_config.book, "src", "src"),
                "title": getattr(root_config.book, "title", "Untitled")
            },
            "build": {
                "create-missing": getattr(root_config.book, "create_missing", False)
            }
        }

        # Only add output.html section if google_analytics is present
        if getattr(root_config.book, "google_analytics", None):
            book_config["output"] = {
                "html": {
                    "google-analytics": root_config.book.google_analytics
                }
            }

        # Write the configuration
        with open(book_path, "w") as f:
            toml.dump(book_config, f)
        log.info(f"Created/updated book.toml at {book_path}")
        return True
    except Exception as e:
        log.error(f"Failed to create book.toml: {e}")
        return False

def manage_dependencies(root_config: RootConfig) -> bool:
    """Manage dependencies based on dependencies.toml configuration."""

    success = True
    # Process dependencies
    for name, dep in root_config.dependencies.items():
        log.info(f"Processing dependency {name} @ {dep.branch}...")
        # Clone/update repository
        if not clone_repo(
            dep.url, 
            dep.path, 
            dep.branch
        ):
            success = False
            log.error(f"Failed to process dependency {name}")
            continue

    # Create summary if it exists
    book_path = Path("submodules/index")
    if root_config.book.summary:
        log.info(f"Creating readme summary for {root_config.book.title}")
        if not create_readme(book_path.joinpath("src"), root_config.book.readme):
           success = False
           log.error(f"Failed to create summary for {name}")

    if root_config.book and not create_book_toml(book_path, root_config):
        success = False
        log.error(f"Failed to create book.toml for {name}")

    if not create_book_toml(book_path, root_config):
        success = False
        log.warning("Failed to create book.toml")
    
    if not create_summary_file(book_path, root_config):
        success = False
        log.warning("Failed to create SUMMARY.md")
    
    
    return success 


def create_summary_file(path: Path, root_config: RootConfig) -> bool:
    """Create or update SUMMARY.md with the provided configuration."""
    try:
        # Ensure src directory exists
        src_dir = path / "src"
        src_dir.mkdir(exist_ok=True)
        
        summary_path = src_dir / "SUMMARY.md"
        
        # Get summary content with default if not present
        summary_content = getattr(root_config.book, "summary", "# Summary\n\n[Introduction](README.md)")
        
        # Write the summary file
        with open(summary_path, "w") as f:
            f.write(summary_content)
        
        log.info(f"Created/updated SUMMARY.md at {summary_path}")
        return True
    except Exception as e:
        log.error(f"Failed to create SUMMARY.md: {e}")
        return False