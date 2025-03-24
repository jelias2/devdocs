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

    url: Optional[str] = None
    # Analytics
    google_analytics: Optional[str] = None

@dataclass
class RootConfig:
    dependencies: Dict[str, DependencyConfig]
    book: BookConfig

def load_root_config(root_dir: str) -> Optional[RootConfig]:
    """Load the root configuration from the root directory."""
    config_path = Path(root_dir) / 'infra.dependencies.toml'
    if not config_path.exists():
        log.error(f"Config file not found at {config_path}")
        return None

    try:
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
            summary=raw_config["book"]["summary"]
        )

        return RootConfig(
            dependencies=dependencies,
            book=book_config
        )
    except Exception as e:
        log.error(f"Error loading config: {e}")
        return None