import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

import toml
from gen.log import get_logger

log = get_logger(__name__)

@dataclass
class DependencyConfig:
    url: str
    path: str
    branch: str = "main"

@dataclass
class BookConfig:
    # Book metadata
    title: str
    authors: List[str]
    language: str
    multilingual: bool
    src: str
    
    # Build settings
    create_missing: bool
    build_dir: str
    # Content
    summary: str
    readme: str

    # Max depth for book collection
    max_depth: int

    url: Optional[str] = None
    # Analytics
    google_analytics: Optional[str] = None

@dataclass
class RootConfig:
    dependencies: Dict[str, DependencyConfig]
    book: BookConfig

def load_root_config(root_dir: str, config_file: str) -> Optional[RootConfig]:
    """Load the root configuration from the root directory."""
    config_path = Path(root_dir) / config_file
    if not config_path.exists():
        log.error(f"Config file not found at {config_path}")
        return None

    try:
        log.info(f"loading from {config_path}")
        raw_config = toml.load(config_path)
        
        # Parse dependencies
        dependencies = {
            name: DependencyConfig(**dep_config)
            for name, dep_config in raw_config.get("dependencies", {}).items()
        }

        # Parse book config
        book_config = BookConfig(
            # Book metadata
            title=raw_config["book"]["title"],
            authors=raw_config["book"]["authors"],
            language=raw_config["book"]["language"],
            multilingual=raw_config["book"]["multilingual"],
            src=raw_config["book"]["src"],
            url=raw_config["book"].get("url"),
            
            # Build settings
            create_missing=raw_config["book"]["create-missing"],
            build_dir=raw_config["book"]["build-dir"],
            
            # Analytics
            google_analytics=raw_config["book"]["google-analytics"],
            
            # Content
            summary=raw_config["book"]["summary"],
            readme=raw_config["book"]["readme"],

            # Max depth
            max_depth=raw_config["book"].get("max-depth", 5),
        )

        return RootConfig(
            dependencies=dependencies,
            book=book_config
        )
    except Exception as e:
        log.error(f"Error loading config: {e}")
        return None


def create_book_toml(path: Path, root_config: RootConfig) -> bool:
    """Create or update root book.toml with the provided configuration."""
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


def create_index_mdbook(root_config: RootConfig) -> bool:
    # Create summary if it exists
    success = True
    book_path = Path("submodules/index")
    if root_config.book.summary:
        log.info(f"Creating readme.mdfor root submodules/index")
        if not create_readme(book_path.joinpath("src"), root_config.book.readme):
           success = False
           log.error(f"Failed to readme.md for submodules/index")

    if root_config.book and not create_book_toml(book_path, root_config):
        success = False
        log.error(f"Failed to create book.toml for submodules/index")
    
    if not create_summary_file(book_path, root_config):
        success = False
        log.warning("Failed to create SUMMARY.md for submodules/index")
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