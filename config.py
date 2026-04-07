#!/usr/bin/env python3

import os
import json
import shutil
from pathlib import Path


class ConfigManager:
    """Manages configuration and project structure"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_file = os.path.join(base_dir, "config.json")
        self.images_dir = os.path.join(base_dir, "images")
        self.sounds_dir = os.path.join(base_dir, "sounds")
        self.create_directories()
    
    def create_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.sounds_dir, exist_ok=True)
    
    def load_config(self):
        """Load config from JSON file, return None if missing or empty"""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Check if config is empty or has no triggers
                if not config or not config.get("triggers"):
                    return None
                return config
        except (json.JSONDecodeError, IOError):
            return None
    
    def save_config(self, config):
        """Save config to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_default_config(self):
        """Create a default empty config structure"""
        return {
            "triggers": []
        }
    
    def add_trigger(self, trigger_id, images, sounds, phrases):
        """Add or update a trigger in config"""
        config = self.load_config() or self.create_default_config()
        
        # Remove existing trigger with same ID
        config["triggers"] = [t for t in config["triggers"] if t["id"] != trigger_id]
        
        # Add new trigger
        config["triggers"].append({
            "id": trigger_id,
            "images": images,
            "sounds": sounds,
            "phrases": phrases
        })
        
        self.save_config(config)
        return config
    
    def get_local_images(self):
        """Get list of images in images directory"""
        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        try:
            return [f for f in os.listdir(self.images_dir) 
                    if f.lower().endswith(valid_extensions)]
        except:
            return []
    
    def get_local_sounds(self):
        """Get list of sounds in sounds directory"""
        valid_extensions = (".ogg", ".wav", ".mp3", ".flac")
        try:
            return [f for f in os.listdir(self.sounds_dir) 
                    if f.lower().endswith(valid_extensions)]
        except:
            return []
    
    def copy_file_to_project(self, src_path, dest_dir):
        """Copy a file to project directory"""
        try:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(src_path, dest_path)
            return filename
        except Exception as e:
            print(f"Error copying file: {e}")
            return None

