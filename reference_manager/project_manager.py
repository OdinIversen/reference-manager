from typing import List, Optional

from reference_manager.models import Project, Reference
from reference_manager.file_manager import FileManager
from reference_manager.bibtex_parser import BibTexManager


class ProjectManager:
    """Manages research projects and their references."""
    
    def __init__(self, base_dir: str = "references"):
        self.file_manager = FileManager(base_dir)
        self.active_project: Optional[Project] = None
    
    def create_project(self, name: str) -> Project:
        """Create a new project."""
        project = Project(name=name)
        self.file_manager.save_project(project)
        return project
    
    def load_project(self, name: str) -> Optional[Project]:
        """Load an existing project."""
        project = self.file_manager.load_project(name)
        if project:
            self.active_project = project
        return project
    
    def save_project(self) -> None:
        """Save the active project."""
        if self.active_project:
            self.file_manager.save_project(self.active_project)
    
    def list_projects(self) -> List[str]:
        """List all available projects."""
        return self.file_manager.list_projects()
    
    def delete_project(self, name: str) -> bool:
        """Delete a project."""
        if self.active_project and self.active_project.name == name:
            self.active_project = None
        return self.file_manager.delete_project(name)
    
    def import_bibtex(self, file_path: str) -> List[Reference]:
        """Import references from a BibTeX file."""
        if not self.active_project:
            raise ValueError("No active project to import into")
        
        references = BibTexManager.parse_bibtex_file(file_path)
        
        # Resolve duplicate keys
        all_references = list(self.active_project.references.values()) + references
        resolved_references = BibTexManager.resolve_duplicate_keys(all_references)
        
        # Get only the new references after resolution
        existing_keys = set(self.active_project.references.keys())
        new_references = [ref for ref in resolved_references if ref.key not in existing_keys]
        
        # Add to project
        for ref in new_references:
            self.active_project.add_reference(ref)
        
        self.save_project()
        return new_references
    
    def export_bibtex(self, file_path: str) -> None:
        """Export project references to a BibTeX file."""
        if not self.active_project:
            raise ValueError("No active project to export from")
        
        references = list(self.active_project.references.values())
        BibTexManager.write_bibtex_file(references, file_path)
    
    def add_reference_file(self, reference_key: str, file_path: str) -> None:
        """Add a reference file to the active project."""
        if not self.active_project:
            raise ValueError("No active project")
        
        reference = self.active_project.get_reference(reference_key)
        if not reference:
            raise ValueError(f"Reference with key '{reference_key}' not found")
        
        self.file_manager.add_reference_file(self.active_project, reference, file_path)
        self.save_project()