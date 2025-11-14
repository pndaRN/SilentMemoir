"""
Entry editor screen with Markdown preview.

This screen provides the interface for creating and editing journal entries,
with support for Markdown editing and live preview.
"""

import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Markdown, TextArea

from silentmemoir.config import (
    DEFAULT_ENTRY_PREFIX,
    EMPTY_PREVIEW_MESSAGE,
    MARKDOWN_EXTENSION,
    NEW_ENTRY_PLACEHOLDER,
    TIMESTAMP_FORMAT,
)
from silentmemoir.models import Journal, JournalEntry


class Entry(ModalScreen):
    """Screen for editing journal entries with Markdown preview support."""

    BINDINGS = [
        Binding("ctrl+s", "save_entry", "Save", show=True),
        Binding("escape", "dismiss_screen", "Exit", show=True),
        Binding("tab", "toggle_preview", "Toggle Mode", show=True, priority=True),
    ]

    def __init__(
        self,
        journal: Journal = None,
        entry_name: str = None,
        is_new_entry: bool = False,
    ):
        """
        Initialize the entry editor.

        Args:
            journal: The parent journal
            entry_name: The name of the entry (with or without .md extension)
            is_new_entry: Whether this is a new entry being created
        """
        super().__init__()
        self.journal = journal
        self.entry_name = entry_name
        self.is_new_entry = is_new_entry
        self.editing_mode = True

        self.text_area = None
        self.markdown_viewer = None
        self.status_label = None
        self.scroll_container = None
        self.title_input = None

        if journal and entry_name:
            self.journal_entry = JournalEntry(
                journal, entry_name.replace(MARKDOWN_EXTENSION, "")
            )
        else:
            self.journal_entry = None

    def compose(self) -> ComposeResult:
        """
        Compose the UI for this screen.

        Returns:
            The composed UI elements
        """
        if self.is_new_entry:
            journal_name = getattr(self.journal, "name", "Unknown")
            yield Label(f"Create New Entry in: {self.journal.name}")
            self.title_input = Input(
                placeholder="Enter custom title (optional)", id="title_input"
            )
            yield self.title_input
        else:
            journal_name = getattr(self.journal, "name", "Unknown")
            entry_name = self.entry_name or "Unknown"
            yield Label(f"Editing: {entry_name} in {journal_name}")

        self.status_label = Label(
            "Mode: Editing | Tab: Toggle Preview | Ctrl+S: Save | Esc: Exit"
        )
        yield self.status_label

        content = ""
        if not self.is_new_entry and self.journal_entry:
            try:
                if self.journal_entry.exists():
                    content = self.journal_entry.read()
            except OSError as e:
                # If we can't read the file, show an error and use empty content
                content = f"# Error\n\nCould not read entry: {e}"

        with Vertical(id="contentcontainer"):
            self.text_area = TextArea(content, id="entry_content")
            yield self.text_area

            self.scroll_container = ScrollableContainer(id="markdown_scroll")
            with self.scroll_container:
                self.markdown_viewer = Markdown(
                    content or NEW_ENTRY_PLACEHOLDER,
                    id="markdown_preview",
                )
                yield self.markdown_viewer
            self.scroll_container.display = False

    # ------------------------------------
    # ACTIONS
    # ------------------------------------

    def action_save_entry(self):
        """Action to save the entry without exiting."""
        self.save_entry(exit_after=False)

    def action_dismiss_screen(self):
        """Action to save and exit the entry screen."""
        self.save_entry(exit_after=True)

    def action_toggle_preview(self):
        """Action to toggle between editing and preview modes."""
        self.toggle_mode()

    def action_toggle_mode(self):
        """Action to toggle between editing and preview modes (alternative binding)."""
        self.toggle_mode()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input submission (Enter key on title input).

        Args:
            event: The input submitted event
        """
        if event.input.id == "title_input" and self.text_area:
            self.text_area.focus()

    # ------------------------------------
    # TOGGLE
    # ------------------------------------

    def toggle_mode(self):
        """Toggle between editing mode and preview mode."""
        if self.editing_mode:
            self.save_entry(exit_after=False)

            current_content = self.text_area.text
            if current_content.strip():
                self.markdown_viewer.update(current_content)
            else:
                self.markdown_viewer.update(EMPTY_PREVIEW_MESSAGE)

            self.text_area.display = False
            self.scroll_container.display = True

            self.editing_mode = False
            self.status_label.update(
                "Mode: Preview | Tab: Back to Editing | Ctrl+S: Save | Esc: Exit"
            )

        else:
            self.text_area.display = True
            self.scroll_container.display = False

            self.text_area.focus()

            self.editing_mode = True
            self.status_label.update(
                "Mode: Editing | Tab: Toggle Preview | Ctrl+S: Save | Esc: Exit"
            )

    # ------------------------------------
    # SAVE
    # ------------------------------------

    def save_entry(self, exit_after: bool = False):
        """
        Save the entry content to disk.

        Args:
            exit_after: Whether to exit the screen after saving
        """
        if not self.journal:
            return

        content = self.text_area.text

        if self.is_new_entry:
            if not self.entry_name:
                custom_title = ""
                if self.title_input:
                    custom_title = self.title_input.value.strip()

                if custom_title:
                    self.entry_name = custom_title
                else:
                    timestamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
                    self.entry_name = f"{DEFAULT_ENTRY_PREFIX}{timestamp}"

            self.journal_entry = JournalEntry(self.journal, self.entry_name)

        if self.journal_entry:
            try:
                self.journal_entry.save(content)
                if exit_after:
                    self.dismiss(f"Saved: {self.entry_name}")
            except OSError as e:
                # Show error to user - update status label
                self.status_label.update(f"Error saving entry: {e}")
                # Don't dismiss if there was an error
                return

    def on_mount(self):
        """Set focus when the screen is mounted."""
        if self.is_new_entry and self.title_input:
            self.title_input.focus()
        else:
            if hasattr(self, "text_area"):
                self.text_area.focus()
