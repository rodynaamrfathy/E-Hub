import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.tools import Tool
from exa_py import Exa
from .config import Config

class KnowledgeLoader:
    """Utility class to load knowledge base files"""
    
    @staticmethod
    def load_yaml(filepath: Path) -> Dict:
        """Load YAML file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Warning: Knowledge file {filepath} not found")
            return {}
    
    @staticmethod
    def load_json(filepath: Path) -> Dict:
        """Load JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Warning: Knowledge file {filepath} not found")
            return {}


