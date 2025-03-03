import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import BibDatabase

from reference_manager.models import Reference


class BibTexManager:
    """Manages BibTeX files and references."""
    
    @staticmethod
    def parse_bibtex_file(file_path: str) -> List[Reference]:
        """Parse a BibTeX file and return a list of Reference objects."""
        with open(file_path, 'r', encoding='utf-8') as bibtex_file:
            parser = BibTexParser(common_strings=True)
            bib_database = bibtexparser.load(bibtex_file, parser)
        
        references = []
        for entry in bib_database.entries:
            key = entry.pop('ID')
            entry_type = entry.pop('ENTRYTYPE')
            references.append(Reference(
                key=key,
                entry_type=entry_type,
                fields=entry,
                original_key=key,
                file_path=file_path
            ))
        
        return references
    
    @staticmethod
    def write_bibtex_file(references: List[Reference], file_path: str) -> None:
        """Write a list of Reference objects to a BibTeX file."""
        db = BibDatabase()
        db.entries = []
        
        for ref in references:
            entry = {
                'ID': ref.key,
                'ENTRYTYPE': ref.entry_type,
                **ref.fields
            }
            db.entries.append(entry)
        
        with open(file_path, 'w', encoding='utf-8') as bibtex_file:
            bibtexparser.dump(db, bibtex_file)
    
    @staticmethod
    def find_duplicate_keys(references: List[Reference]) -> Dict[str, List[Reference]]:
        """Find duplicate keys in a list of references."""
        key_map: Dict[str, List[Reference]] = {}
        
        for ref in references:
            if ref.key not in key_map:
                key_map[ref.key] = []
            key_map[ref.key].append(ref)
        
        # Return only the keys that have duplicates
        return {k: v for k, v in key_map.items() if len(v) > 1}
    
    @staticmethod
    def resolve_duplicate_keys(references: List[Reference]) -> List[Reference]:
        """Resolve duplicate keys by adding suffixes."""
        # Create a copy of the references list to avoid modifying the original
        resolved_refs = references.copy()
        
        # Check for duplicates
        duplicates = BibTexManager.find_duplicate_keys(resolved_refs)
        
        # If there are duplicates, resolve them
        if duplicates:
            for key, dups in duplicates.items():
                for i, ref in enumerate(dups):
                    if i > 0:  # Skip the first one (keep original)
                        # Create a new key with a suffix
                        new_key = f"{key}_{i}"
                        
                        # Update the reference object
                        ref.original_key = ref.key
                        ref.key = new_key
        
        return resolved_refs
    
    @staticmethod
    def merge_bibtex_files(file_paths: List[str], output_path: str) -> None:
        """Merge multiple BibTeX files, resolving duplicates."""
        all_references = []
        
        for file_path in file_paths:
            references = BibTexManager.parse_bibtex_file(file_path)
            all_references.extend(references)
        
        # Resolve duplicates
        resolved_references = BibTexManager.resolve_duplicate_keys(all_references)
        
        # Write the merged file
        BibTexManager.write_bibtex_file(resolved_references, output_path)