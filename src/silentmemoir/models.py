"""
Data models for SilentMemoir application.

This module contains all data classes and business logic for journals and entries,
separated from UI concerns.
"""

import os
from typing import ClassVar

from textual.widgets import Label, ListItem

from silentmemoir.config import JOURNALS_BASE_PATH


class Journal:
    """Represents a journal containing multiple entries."""

    base_path: ClassVar[str] = JOURNALS_BASE_PATH

    def __init__(self, name: str):
        """
        Initialize a journal.

        Args:
            name: The name of the journal
        """
        self.name = name
        self.journal_path = os.path.join(self.base_path, self.name)
        os.makedirs(self.journal_path, exist_ok=True)

    @classmethod
    def list_all(cls) -> list["Journal"]:
        """
        List all journals in the base path.

        Returns:
            List of Journal objects
        """
        os.makedirs(cls.base_path, exist_ok=True)
        return [
            cls(d)
            for d in os.listdir(cls.base_path)
            if os.path.isdir(os.path.join(cls.base_path, d))
        ]

    def list_entries(self) -> list[str]:
        """
        List all entry files in this journal.

        Returns:
            Sorted list of entry filenames
        """
        return sorted(os.listdir(self.journal_path))

    def delete(self) -> None:
        """Delete this journal and all its entries."""
        import shutil

        if os.path.exists(self.journal_path):
            shutil.rmtree(self.journal_path)


class JournalEntry:
    """Represents a single journal entry."""

    def __init__(self, journal: Journal, title: str = None):
        """
        Initialize a journal entry.

        Args:
            journal: The parent journal
            title: The entry title (without .md extension)
        """
        self.journal = journal
        self.title = title
        self.filepath = os.path.join(self.journal.journal_path, f"{title}.md")

    def save(self, content: str) -> None:
        """
        Save the entry content to disk.

        Args:
            content: The markdown content to save

        Raises:
            IOError: If the file cannot be written
            OSError: If there are permission or disk space issues
        """
        try:
            # Ensure the parent directory exists
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            raise OSError(f"Failed to save entry: {e}") from e

    def read(self) -> str:
        """
        Read the entry content from disk.

        Returns:
            The entry content, or empty string if file doesn't exist

        Raises:
            IOError: If the file cannot be read
        """
        if not os.path.exists(self.filepath):
            return ""

        try:
            with open(self.filepath, encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Failed to read entry: {e}") from e

    def exists(self) -> bool:
        """
        Check if the entry file exists.

        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(self.filepath)

    def delete(self) -> None:
        """
        Delete this entry from disk.

        Raises:
            IOError: If the file cannot be deleted
        """
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
            except OSError as e:
                raise OSError(f"Failed to delete entry: {e}") from e


# ----------------------------
# UI Helper Classes
# ----------------------------


class JournalListItem(ListItem):
    """Custom ListItem for displaying a journal in a ListView."""

    def __init__(self, journal_name: str):
        """
        Initialize a journal list item.

        Args:
            journal_name: The name of the journal to display
        """
        super().__init__(Label(journal_name))
        self.journal_name = journal_name


class EntryListItem(ListItem):
    """Custom ListItem for displaying an entry in a ListView."""

    def __init__(self, entry_name: str, is_new_entry: bool = False):
        """
        Initialize an entry list item.

        Args:
            entry_name: The name of the entry to display
            is_new_entry: Whether this represents the "Create New Entry" item
        """
        super().__init__(Label(entry_name))
        self.entry_name = entry_name
        self.is_new_entry = is_new_entry
        if is_new_entry:
            self.add_class("new_entry")
        else:
            self.add_class("journal-entry")
