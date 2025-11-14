"""
Journal and entry management screen.

This screen provides the main interface for viewing, creating, and managing
journals and their entries.
"""

import os

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Input, Label, ListView

from silentmemoir.config import ERROR_MESSAGE_DISPLAY_DURATION, JOURNALS_BASE_PATH
from silentmemoir.models import EntryListItem, Journal, JournalListItem


class ViewJournals(Screen):
    """Main screen for viewing and managing journals and entries."""

    BINDINGS = [
        Binding(key="h", action="goto_home", description="Home"),
        Binding(key="Enter", action="select_cursor", description="Accept"),
        Binding(key="n", action="goto_new_journal", description="New Journal"),
        Binding(key="d", action="delete_item", description="Delete Highlighted Item"),
    ]

    def __init__(self):
        """Initialize the ViewJournals screen."""
        super().__init__()
        self.current_journal = None

    def compose(self) -> ComposeResult:
        """
        Compose the UI for this screen.

        Returns:
            The composed UI elements
        """
        journals = Journal.list_all()

        self.journals_list = ListView(
            *[JournalListItem(journal.name) for journal in journals], id="journals_list"
        )

        self.entries_list = ListView(id="entries_list")

        with Horizontal(id="main_container"):
            with Vertical(id="journal_panel"):
                yield Label("Journals")
                yield self.journals_list
                yield Label("", id="journal_error")

            with Vertical(id="entries_panel"):
                yield Label("Entries")
                yield self.entries_list
                yield Label("", id="entries_error")

            yield Footer()

    def on_key(self, event: Key):
        """
        Handle keyboard events.

        Args:
            event: The keyboard event
        """
        if event.key == "right":
            if self.focused is self.journals_list:
                selected_item = self.journals_list.highlighted_child
                if isinstance(selected_item, JournalListItem):
                    journal_name = selected_item.journal_name
                    self.current_journal = Journal(journal_name)

                    self.rebuild_entries_list(self.current_journal)
                    self.set_focus(self.entries_list)

                    if len(self.entries_list.children) > 0:
                        self.entries_list.index = 0

                    self.set_focus(self.entries_list)
                    event.prevent_default()
        if event.key == "left":
            self.set_focus(self.journals_list)
            self.entries_list.clear()
            event.prevent_default()

    # ----------------------------
    # JOURNAL HANDLING
    # ----------------------------

    def action_goto_home(self):
        """Navigate to the home screen."""
        self.app.push_screen("Opening Screen")

    def action_goto_new_journal(self):
        """Open the new journal creation dialog."""

        def on_new_journal_created(journal_name):
            if journal_name:
                self.refresh_journals()

        self.app.push_screen(NewJournal(), on_new_journal_created)

    def refresh_journals(self):
        """Refresh the journals list from disk."""
        journals = Journal.list_all()

        self.journals_list.clear()

        for journal in journals:
            self.journals_list.append(JournalListItem(journal.name))

    def action_delete_item(self):
        """
        Delete the currently focused item (journal or entry).

        Determines which list is focused and delegates to the appropriate
        delete method.
        """
        if self.focused is self.journals_list:
            self.delete_journal()
        elif self.focused is self.entries_list:
            self.delete_entry()

    def delete_journal(self):
        """Delete the currently selected journal and all its entries."""
        if not self.current_journal:
            return

        journal_name = self.current_journal.name

        def on_confirm(confirmed: bool):
            if confirmed:
                try:
                    self.current_journal.delete()
                    self.show_temporary_message(
                        f"Deleted journal: {journal_name}", "#journal_error"
                    )
                except OSError as e:
                    self.show_temporary_message(
                        f"Error deleting journal: {e}", "#journal_error"
                    )

                self.current_journal = None
                self.refresh_journals()
                self.entries_list.clear()

        self.app.push_screen(
            ConfirmDeleteModal("journal", journal_name), on_confirm
        )

    def delete_entry(self):
        """Delete the currently selected entry."""
        if not self.current_journal:
            return

        selected_item = self.entries_list.highlighted_child

        if not selected_item:
            return

        # Don't allow deletion of the "new entry" item
        if isinstance(selected_item, EntryListItem) and selected_item.is_new_entry:
            return

        if isinstance(selected_item, EntryListItem):
            entry_name = selected_item.entry_name
            entry_path = os.path.join(self.current_journal.journal_path, entry_name)

            def on_confirm(confirmed: bool):
                if confirmed:
                    try:
                        if os.path.exists(entry_path):
                            os.remove(entry_path)
                            self.show_temporary_message(
                                f"Deleted entry: {entry_name}", "#entries_error"
                            )
                    except OSError as e:
                        self.show_temporary_message(
                            f"Error deleting entry: {e}", "#entries_error"
                        )

                    self.rebuild_entries_list(self.current_journal)

            self.app.push_screen(
                ConfirmDeleteModal("entry", entry_name), on_confirm
            )

    def show_temporary_message(self, message: str, label_id: str):
        """
        Display a temporary message that auto-clears after a duration.

        Args:
            message: The message to display
            label_id: The CSS ID of the label to update
        """
        label = self.query_one(label_id, Label)
        label.update(message)
        self.set_timer(ERROR_MESSAGE_DISPLAY_DURATION, lambda: label.update(""))

    # ----------------------------
    # ENTRY HANDLING
    # ----------------------------

    def rebuild_entries_list(self, journal: Journal):
        """
        Rebuild the entries list for the given journal.

        Args:
            journal: The journal whose entries should be displayed
        """
        # Remove all children and rebuild
        self.entries_list.clear()

        # Add the "Create New Entry" item
        self.entries_list.append(EntryListItem("Create New Entry", is_new_entry=True))

        # Add actual entries
        for entry in journal.list_entries():
            self.entries_list.append(EntryListItem(entry, is_new_entry=False))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """
        Handle selection of items in either the journals or entries list.

        Args:
            event: The selection event
        """
        if event.list_view.id == "journals_list":
            self.handle_journal_selected(event.item)
        elif event.list_view.id == "entries_list":
            self.handle_entry_selected(event.item)

    def handle_journal_selected(self, selected_item):
        """
        Handle selection of a journal.

        Args:
            selected_item: The selected journal list item
        """
        if isinstance(selected_item, JournalListItem):
            journal_name = selected_item.journal_name
            self.current_journal = Journal(journal_name)

            self.rebuild_entries_list(self.current_journal)
            self.set_focus(self.entries_list)

            if len(self.entries_list.children) > 0:
                self.entries_list.index = 0

    def handle_entry_selected(self, selected_item):
        """
        Handle selection of an entry (or the new entry item).

        Args:
            selected_item: The selected entry list item
        """
        if not self.current_journal:
            return

        if not isinstance(selected_item, EntryListItem):
            return

        # Import here to avoid circular dependency
        from silentmemoir.screens.entry import Entry

        if selected_item.is_new_entry:
            # Creating a new entry
            def on_entry_saved(result):
                if result:
                    self.rebuild_entries_list(self.current_journal)

            entry_screen = Entry(
                journal=self.current_journal, entry_name=None, is_new_entry=True
            )
            self.app.push_screen(entry_screen, on_entry_saved)
        else:
            # Editing an existing entry
            entry_name = selected_item.entry_name

            def on_entry_saved(result):
                # Optionally rebuild list if needed
                pass

            entry_screen = Entry(
                journal=self.current_journal,
                entry_name=entry_name,
                is_new_entry=False,
            )
            self.app.push_screen(entry_screen, on_entry_saved)


class NewJournal(ModalScreen[str]):
    """Modal dialog for creating a new journal."""

    def __init__(self):
        """Initialize the new journal dialog."""
        super().__init__()
        self.journals_path = JOURNALS_BASE_PATH

    def compose(self) -> ComposeResult:
        """
        Compose the UI for this dialog.

        Returns:
            The composed UI elements
        """
        yield Container(
            Vertical(
                Label("Create New Journal"),
                Input(placeholder="Enter Journal Name"),
                Label("Press 'Enter' to accept"),
                Label("Press 'Esc' to go back"),
                Label("", id="error_message"),
                id="modal_content",
            ),
            id="modal_container",
        )

    def on_key(self, event: Key):
        """
        Handle keyboard events.

        Args:
            event: The keyboard event
        """
        if event.key == "escape":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input submission.

        Args:
            event: The input submitted event
        """
        self.create_journal(event)

    def create_journal(self, text):
        """
        Create a new journal with the given name.

        Args:
            text: The input event containing the journal name
        """
        journal_name = text.value.strip()
        if not journal_name:
            self.query_one("#error_message", Label).update("Please enter a name")
            return
        elif journal_name in self.get_existing_journals():
            self.query_one("#error_message", Label).update("Journal already exists")
            return

        try:
            journal = Journal(journal_name)
            self.dismiss(journal.name)
        except OSError as e:
            self.query_one("#error_message", Label).update(f"Error creating journal: {e}")

    def get_existing_journals(self):
        """
        Get list of existing journal names.

        Returns:
            List of journal directory names
        """
        if not os.path.exists(self.journals_path):
            return []
        return [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]


class ConfirmDeleteModal(ModalScreen[bool]):
    """Modal dialog for confirming deletion of journals or entries."""

    def __init__(self, item_type: str, item_name: str):
        """
        Initialize the confirmation dialog.

        Args:
            item_type: Type of item being deleted ("journal" or "entry")
            item_name: Name of the item to delete
        """
        super().__init__()
        self.item_type = item_type
        self.item_name = item_name

    def compose(self) -> ComposeResult:
        """
        Compose the UI for this dialog.

        Returns:
            The composed UI elements
        """
        with Container(id="modal_container"):
            with Vertical(id="modal_content"):
                yield Label(f"Delete {self.item_type}?", classes="titleText")
                yield Label(f"Are you sure you want to delete {self.item_type}:")
                yield Label(f'"{self.item_name}"?', classes="accent")
                if self.item_type == "journal":
                    yield Label("This will delete all entries in this journal!")
                yield Label("")
                with Horizontal():
                    yield Button("Yes", id="confirm_yes", variant="error")
                    yield Button("No", id="confirm_no", variant="primary")
                yield Label("")
                yield Label("Press 'Esc' to cancel")

    def on_key(self, event: Key):
        """
        Handle keyboard events.

        Args:
            event: The keyboard event
        """
        if event.key == "escape":
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: The button pressed event
        """
        if event.button.id == "confirm_yes":
            self.dismiss(True)
        elif event.button.id == "confirm_no":
            self.dismiss(False)
