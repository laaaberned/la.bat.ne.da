"""Project management for ART.WE.ED.IT"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List
import json
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Project:
    """Music video project"""
    name: str
    audio_path: str
    clips_dir: str
    output_dir: str
    config_path: str = "config.yaml"
    metadata: Dict[str, Any] = None
    
    def save_project(self, project_file: str) -> None:
        """Save project configuration to file"""
        project_data = {
            "name": self.name,
            "audio_path": self.audio_path,
            "clips_dir": self.clips_dir,
            "output_dir": self.output_dir,
            "config_path": self.config_path,
            "metadata": self.metadata or {}
        }
        
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        logger.info(f"Project saved: {project_file}")
    
    @classmethod
    def load_project(cls, project_file: str) -> "Project":
        """Load project from file"""
        with open(project_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Project loaded: {project_file}")
        return cls(**data)
