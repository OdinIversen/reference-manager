from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Reference:
    """Represents a bibliography reference."""
    key: str
    entry_type: str
    fields: Dict[str, str]
    original_key: Optional[str] = None
    file_path: Optional[str] = None
    
    def get_standardized_filename(self) -> str:
        """Generate a standardized filename for the reference."""
        # Format: AuthorLastName_Year_Title_FirstFewWords.pdf
        author = self.fields.get("author", "Unknown")
        year = self.fields.get("year", "XXXX")
        title = self.fields.get("title", "Untitled")
        
        # Extract last name of first author
        last_name = author.split("and")[0].split(",")[0].strip()
        
        # Clean the title and get first few words
        clean_title = "".join(c for c in title if c.isalnum() or c.isspace())
        title_words = clean_title.split()[:3]
        short_title = "_".join(title_words)
        
        return f"{last_name}_{year}_{short_title}.pdf"


@dataclass
class Project:
    """Represents a research project with its own set of references."""
    name: str
    references: Dict[str, Reference] = field(default_factory=dict)
    file_path: Optional[str] = None
    
    def add_reference(self, reference: Reference) -> None:
        """Add a reference to the project, avoiding duplicates."""
        self.references[reference.key] = reference
    
    def remove_reference(self, key: str) -> None:
        """Remove a reference from the project."""
        if key in self.references:
            del self.references[key]
    
    def get_reference(self, key: str) -> Optional[Reference]:
        """Get a reference by key."""
        return self.references.get(key)
    
    def get_all_references(self) -> List[Reference]:
        """Get all references."""
        return list(self.references.values())