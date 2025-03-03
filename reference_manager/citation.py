from typing import List, Dict, Optional
from pylatexenc.latex2text import LatexNodes2Text

from reference_manager.models import Reference


class CitationFormatter:
    """Formats references as LaTeX citations."""
    
    @staticmethod
    def clean_latex(text: str) -> str:
        """Convert LaTeX formatting to plain text."""
        return LatexNodes2Text().latex_to_text(text)
    
    @staticmethod
    def format_citation(reference: Reference, style: str = "cite") -> str:
        """Format a reference as a LaTeX citation."""
        if style == "cite":
            return f"\\cite{{{reference.key}}}"
        elif style == "citep":
            return f"\\citep{{{reference.key}}}"
        elif style == "citet":
            return f"\\citet{{{reference.key}}}"
        elif style == "footcite":
            return f"\\footcite{{{reference.key}}}"
        elif style == "textcite":
            return f"\\textcite{{{reference.key}}}"
        else:
            return f"\\cite{{{reference.key}}}"
    
    @staticmethod
    def format_multiple_citations(references: List[Reference], style: str = "cite") -> str:
        """Format multiple references as a LaTeX citation."""
        keys = [ref.key for ref in references]
        keys_str = ",".join(keys)
        
        if style == "cite":
            return f"\\cite{{{keys_str}}}"
        elif style == "citep":
            return f"\\citep{{{keys_str}}}"
        elif style == "citet":
            return f"\\citet{{{keys_str}}}"
        elif style == "footcite":
            return f"\\footcite{{{keys_str}}}"
        elif style == "textcite":
            return f"\\textcite{{{keys_str}}}"
        else:
            return f"\\cite{{{keys_str}}}"
    
    @staticmethod
    def format_bibtex_entry(reference: Reference) -> str:
        """Format a reference as a BibTeX entry string."""
        entry_type = reference.entry_type.lower()
        key = reference.key
        
        # Start the BibTeX entry
        entry = f"@{entry_type}{{{key},\n"
        
        # Add fields
        for field, value in reference.fields.items():
            entry += f"  {field} = {{{value}}},\n"
        
        # Close the entry
        entry += "}"
        
        return entry
    
    @staticmethod
    def get_formatted_author_year(reference: Reference) -> str:
        """Get author-year citation text."""
        author = reference.fields.get("author", "Unknown")
        year = reference.fields.get("year", "n.d.")
        
        # Extract last name of first author
        last_name = author.split("and")[0].split(",")[0].strip()
        
        # Handle multiple authors
        if "and" in author:
            author_count = len(author.split("and"))
            if author_count == 2:
                authors = author.split("and")
                last_names = [a.split(",")[0].strip() for a in authors]
                return f"{last_names[0]} and {last_names[1]} ({year})"
            else:
                return f"{last_name} et al. ({year})"
        else:
            return f"{last_name} ({year})"
    
    @staticmethod
    def get_full_citation(reference: Reference) -> str:
        """Get a full citation text in a common format."""
        entry_type = reference.entry_type.lower()
        
        # Get common fields
        author = CitationFormatter.clean_latex(reference.fields.get("author", "Unknown"))
        title = CitationFormatter.clean_latex(reference.fields.get("title", "Untitled"))
        year = reference.fields.get("year", "n.d.")
        
        # Replace 'and' with commas for readability
        author_text = author.replace(" and ", ", ")
        
        if entry_type == "article":
            journal = CitationFormatter.clean_latex(reference.fields.get("journal", "Unknown Journal"))
            volume = reference.fields.get("volume", "")
            number = reference.fields.get("number", "")
            pages = reference.fields.get("pages", "")
            
            vol_info = f"{volume}"
            if number:
                vol_info += f"({number})"
            
            return f"{author_text}. ({year}). {title}. {journal}, {vol_info}, {pages}."
            
        elif entry_type == "book":
            publisher = reference.fields.get("publisher", "Unknown Publisher")
            address = reference.fields.get("address", "")
            
            location = f"{address}: " if address else ""
            return f"{author_text}. ({year}). {title}. {location}{publisher}."
            
        elif entry_type == "inproceedings" or entry_type == "conference":
            booktitle = CitationFormatter.clean_latex(reference.fields.get("booktitle", "Unknown Proceedings"))
            pages = reference.fields.get("pages", "")
            
            return f"{author_text}. ({year}). {title}. In {booktitle}, {pages}."
            
        elif entry_type == "techreport":
            institution = reference.fields.get("institution", "Unknown Institution")
            number = reference.fields.get("number", "")
            
            report_info = f"Technical Report"
            if number:
                report_info += f" {number}"
            
            return f"{author_text}. ({year}). {title}. {report_info}, {institution}."
            
        else:
            # Default format for other types
            return f"{author_text}. ({year}). {title}."