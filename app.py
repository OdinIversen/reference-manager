#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QComboBox, QFileDialog,
    QMessageBox, QLineEdit, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QFormLayout, QRadioButton,
    QButtonGroup, QGroupBox
)
from PyQt6.QtCore import Qt, QSize

from reference_manager.project_manager import ProjectManager
from reference_manager.models import Reference
from reference_manager.citation import CitationFormatter


class CreateProjectDialog(QDialog):
    """Dialog for creating a new project."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.resize(400, 100)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.project_name = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name)
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class CitationDialog(QDialog):
    """Dialog for generating citations."""
    
    def __init__(self, reference: Reference, parent=None):
        super().__init__(parent)
        self.reference = reference
        self.setWindowTitle("Generate Citation")
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Citation styles group
        style_group = QGroupBox("Citation Style")
        style_layout = QVBoxLayout()
        
        self.style_buttons = QButtonGroup(self)
        styles = [
            ("\\cite{key}", "cite"),
            ("\\citep{key}", "citep"),
            ("\\citet{key}", "citet"),
            ("\\footcite{key}", "footcite"),
            ("\\textcite{key}", "textcite")
        ]
        
        for i, (label, style) in enumerate(styles):
            radio = QRadioButton(label)
            if i == 0:
                radio.setChecked(True)
            self.style_buttons.addButton(radio, i)
            style_layout.addWidget(radio)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Preview section
        layout.addWidget(QLabel("Preview:"))
        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)
        
        # Full citation
        layout.addWidget(QLabel("Full Citation:"))
        self.full_citation = QLineEdit()
        self.full_citation.setReadOnly(True)
        layout.addWidget(self.full_citation)
        
        # Update the preview
        self.update_preview()
        
        # Connect signals
        for button in self.style_buttons.buttons():
            button.toggled.connect(self.update_preview)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def update_preview(self):
        """Update the citation preview."""
        style = "cite"  # Default
        
        for i, button in enumerate(self.style_buttons.buttons()):
            if button.isChecked():
                style = ["cite", "citep", "citet", "footcite", "textcite"][i]
                break
        
        self.preview.setText(CitationFormatter.format_citation(self.reference, style))
        self.full_citation.setText(CitationFormatter.get_full_citation(self.reference))
    
    def get_citation(self) -> str:
        """Get the selected citation."""
        return self.preview.text()


class ReferenceManagerApp(QMainWindow):
    """Main application window for the Reference Manager."""
    
    def __init__(self):
        super().__init__()
        
        self.project_manager = ProjectManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Reference Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Project selection section
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Current Project:"))
        
        self.project_combo = QComboBox()
        self.update_project_list()
        self.project_combo.currentIndexChanged.connect(self.on_project_selected)
        project_layout.addWidget(self.project_combo)
        
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.on_new_project)
        project_layout.addWidget(new_project_btn)
        
        main_layout.addLayout(project_layout)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # References tab
        self.refs_tab = QWidget()
        refs_layout = QVBoxLayout(self.refs_tab)
        
        # References table
        self.refs_table = QTableWidget()
        self.refs_table.setColumnCount(5)
        self.refs_table.setHorizontalHeaderLabels(["Key", "Author", "Title", "Year", "Type"])
        self.refs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.refs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        refs_layout.addWidget(self.refs_table)
        
        # Action buttons for references
        buttons_layout = QHBoxLayout()
        
        import_bib_btn = QPushButton("Import BibTeX")
        import_bib_btn.clicked.connect(self.on_import_bibtex)
        buttons_layout.addWidget(import_bib_btn)
        
        export_bib_btn = QPushButton("Export BibTeX")
        export_bib_btn.clicked.connect(self.on_export_bibtex)
        buttons_layout.addWidget(export_bib_btn)
        
        add_file_btn = QPushButton("Add Paper File")
        add_file_btn.clicked.connect(self.on_add_paper_file)
        buttons_layout.addWidget(add_file_btn)
        
        cite_btn = QPushButton("Generate Citation")
        cite_btn.clicked.connect(self.on_generate_citation)
        buttons_layout.addWidget(cite_btn)
        
        delete_ref_btn = QPushButton("Delete Reference")
        delete_ref_btn.clicked.connect(self.on_delete_reference)
        buttons_layout.addWidget(delete_ref_btn)
        
        refs_layout.addLayout(buttons_layout)
        
        self.tabs.addTab(self.refs_tab, "References")
        main_layout.addWidget(self.tabs)
        
        self.setCentralWidget(central_widget)
    
    def update_project_list(self):
        """Update the project dropdown list."""
        self.project_combo.clear()
        projects = self.project_manager.list_projects()
        
        if projects:
            self.project_combo.addItems(projects)
        else:
            self.project_combo.addItem("No projects available")
    
    def update_references_table(self):
        """Update the references table with data from the current project."""
        self.refs_table.setRowCount(0)
        
        if not self.project_manager.active_project:
            return
        
        references = self.project_manager.active_project.get_all_references()
        
        self.refs_table.setRowCount(len(references))
        for row, ref in enumerate(references):
            self.refs_table.setItem(row, 0, QTableWidgetItem(ref.key))
            self.refs_table.setItem(row, 1, QTableWidgetItem(ref.fields.get("author", "")))
            self.refs_table.setItem(row, 2, QTableWidgetItem(ref.fields.get("title", "")))
            self.refs_table.setItem(row, 3, QTableWidgetItem(ref.fields.get("year", "")))
            self.refs_table.setItem(row, 4, QTableWidgetItem(ref.entry_type))
    
    def on_project_selected(self, index):
        """Handle project selection from dropdown."""
        if index < 0 or self.project_combo.currentText() == "No projects available":
            return
        
        project_name = self.project_combo.currentText()
        self.project_manager.load_project(project_name)
        self.update_references_table()
    
    def on_new_project(self):
        """Handle new project creation."""
        dialog = CreateProjectDialog(self)
        if dialog.exec():
            project_name = dialog.project_name.text().strip()
            
            if not project_name:
                QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
                return
            
            self.project_manager.create_project(project_name)
            self.update_project_list()
            
            # Select the new project
            index = self.project_combo.findText(project_name)
            if index >= 0:
                self.project_combo.setCurrentIndex(index)
    
    def on_import_bibtex(self):
        """Handle BibTeX import."""
        if not self.project_manager.active_project:
            QMessageBox.warning(self, "Warning", "Please select or create a project first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import BibTeX File", "", "BibTeX Files (*.bib);;All Files (*)"
        )
        
        if file_path:
            try:
                new_refs = self.project_manager.import_bibtex(file_path)
                self.update_references_table()
                
                QMessageBox.information(
                    self, "Import Successful", 
                    f"Successfully imported {len(new_refs)} references."
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Error importing BibTeX: {str(e)}")
    
    def on_export_bibtex(self):
        """Handle BibTeX export."""
        if not self.project_manager.active_project:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export BibTeX File", "", "BibTeX Files (*.bib);;All Files (*)"
        )
        
        if file_path:
            try:
                self.project_manager.export_bibtex(file_path)
                QMessageBox.information(self, "Export Successful", "References exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting BibTeX: {str(e)}")
    
    def on_add_paper_file(self):
        """Handle adding a paper file to a reference."""
        if not self.project_manager.active_project:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        selected_rows = self.refs_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a reference first.")
            return
        
        row = selected_rows[0].row()
        ref_key = self.refs_table.item(row, 0).text()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Paper File", "", "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                self.project_manager.add_reference_file(ref_key, file_path)
                QMessageBox.information(self, "Success", "Paper file added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding paper file: {str(e)}")
    
    def on_generate_citation(self):
        """Handle citation generation."""
        if not self.project_manager.active_project:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        selected_rows = self.refs_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a reference first.")
            return
        
        row = selected_rows[0].row()
        ref_key = self.refs_table.item(row, 0).text()
        reference = self.project_manager.active_project.get_reference(ref_key)
        
        if not reference:
            QMessageBox.warning(self, "Warning", "Reference not found.")
            return
        
        dialog = CitationDialog(reference, self)
        if dialog.exec():
            citation = dialog.get_citation()
            # Copy to clipboard or show in a message box
            clipboard = QApplication.clipboard()
            clipboard.setText(citation)
            QMessageBox.information(self, "Citation Copied", 
                "Citation has been copied to clipboard:\n\n" + citation)
    
    def on_delete_reference(self):
        """Handle reference deletion."""
        if not self.project_manager.active_project:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        selected_rows = self.refs_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a reference first.")
            return
        
        row = selected_rows[0].row()
        ref_key = self.refs_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete reference '{ref_key}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project_manager.active_project.remove_reference(ref_key)
            self.project_manager.save_project()
            self.update_references_table()


def main():
    """Main entry point of the application."""
    app = QApplication(sys.argv)
    window = ReferenceManagerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()