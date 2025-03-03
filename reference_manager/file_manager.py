import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from reference_manager.models import Project, Reference


class FileManager:
    """Manages files for the reference manager."""
    
    def __init__(self, base_dir: str = "references"):
        self.base_dir = Path(base_dir)
        self.projects_file = self.base_dir / "projects.json"
        self.ensure_base_dir()
    
    def ensure_base_dir(self) -> None:
        """Ensure the base directory exists."""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def get_project_dir(self, project_name: str) -> Path:
        """Get the directory for a specific project."""
        project_dir = self.base_dir / project_name
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    def save_project(self, project: Project) -> None:
        """Save a project to disk."""
        project_dir = self.get_project_dir(project.name)
        project_file = project_dir / "project.json"
        
        # Create a serializable representation of the project
        project_data = {
            "name": project.name,
            "references": {
                key: {
                    "key": ref.key,
                    "entry_type": ref.entry_type,
                    "fields": ref.fields,
                    "original_key": ref.original_key,
                    "file_path": ref.file_path
                }
                for key, ref in project.references.items()
            }
        }
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)
        
        # Update projects list
        self.update_projects_list()
    
    def load_project(self, project_name: str) -> Optional[Project]:
        """Load a project from disk."""
        project_dir = self.get_project_dir(project_name)
        project_file = project_dir / "project.json"
        
        if not project_file.exists():
            return None
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Create a Project object
        project = Project(name=project_data["name"])
        
        # Add references
        for key, ref_data in project_data.get("references", {}).items():
            project.references[key] = Reference(
                key=ref_data["key"],
                entry_type=ref_data["entry_type"],
                fields=ref_data["fields"],
                original_key=ref_data.get("original_key"),
                file_path=ref_data.get("file_path")
            )
        
        return project
    
    def list_projects(self) -> List[str]:
        """List all available projects."""
        if not self.projects_file.exists():
            return []
        
        with open(self.projects_file, 'r', encoding='utf-8') as f:
            projects_data = json.load(f)
        
        return projects_data.get("projects", [])
    
    def update_projects_list(self) -> None:
        """Update the list of available projects."""
        projects = []
        
        # Scan directories for project files
        for item in self.base_dir.iterdir():
            if item.is_dir() and (item / "project.json").exists():
                projects.append(item.name)
        
        # Save the list
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            json.dump({"projects": projects}, f, indent=2)
    
    def add_reference_file(self, project: Project, reference: Reference, file_path: str) -> None:
        """Add a reference file to a project."""
        project_dir = self.get_project_dir(project.name)
        
        # Generate the standardized filename
        std_filename = reference.get_standardized_filename()
        
        # Destination path
        dest_path = project_dir / std_filename
        
        # Copy the file
        shutil.copy2(file_path, dest_path)
        
        # Update the reference's file path
        reference.file_path = str(dest_path)
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project and its files."""
        project_dir = self.get_project_dir(project_name)
        
        if not project_dir.exists():
            return False
        
        # Remove the directory
        shutil.rmtree(project_dir)
        
        # Update the projects list
        self.update_projects_list()
        return True