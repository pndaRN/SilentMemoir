from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem, Input, Footer
from textual.screen import Screen, ModalScreen
from textual.containers import Vertical, Container, Horizontal, ScrollableContainer

from textual.binding import Binding
from textual.events import Key

import os


class ViewJournals(Screen):
    BINDINGS = [
        Binding(key="h", action="goto_home", description="Home"),
        Binding(key="a", action="select_cursor", description="Accept"),
        Binding(key="n", action="goto_new_journal", description="New Journal"),
        Binding(key="r", action="refresh_journals", description="Refresh"),
    ]

    journals_path = os.path.expanduser("~/.silentmemoir/journals")
    os.makedirs(journals_path, exist_ok=True)

    def compose(self) -> ComposeResult:
        journals = self.get_journals()

        self.list_view = ListView(*[ListItem(Label(journal)) for journal in journals])

        with Horizontal(id="main_container"):
            with Vertical(id="journal_panel"):
                yield Label("Select a Journal")
                yield self.list_view
                yield Label("", id="journal_error")

            with Vertical(id="entries_panel"):
                yield Label("Journal Entries", id="entries_title")
                yield ScrollableContainer(id="entries_container")
                yield Label("", id="entries_error")

            yield Footer()

    def action_goto_home(self):
        self.app.push_screen("Opening Screen")

    def on_list_view_selected(self):
        self.load_journal_entries(self.list_view.action_select_cursor())

    def action_goto_new_journal(self):
        def on_new_journal_created(journal_name):
            if journal_name:
                self.refresh_journals()

        self.app.push_screen(NewJournal(), on_new_journal_created)

    def get_journals(self):
        return [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]

    def refresh_journals(self):
        journals = self.get_journals()

        self.list_view.clear()

        for journal in journals:
            self.list_view.append(ListItem(Label(journal)))

    def get_entries(self, journal):
        journal_path = os.path.join(self.journals_path, journal)

        return [
            e
            for e in os.listdir(journal_path)
            if os.path.isfile(os.path.join(journal_path, e))
        ]

    def load_journal_entries(self, journal_name):
        entries = self.get_entries(journal_name)

        if entries is None:
            pass
            # push to create entry modal screen and create .md file
        else:
            self.entry_view = ListView(*[ListItem(Label(entry)) for entry in entries])


class NewJournal(ModalScreen[str]):
    def __init__(self):
        super().__init__()
        self.journals_path = os.path.expanduser("~/.silentmemoir/journals")

    def compose(self) -> ComposeResult:
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
        if event.key == "escape":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        journal_name = event.value.strip()

        if not journal_name:
            self.query_one("#error_message", Label).update(
                "Please enter a journal name"
            )
            return

        existing_journals = self.get_existing_journals()

        if journal_name in existing_journals:
            self.query_one("#error_message", Label).update("Journal already exisits!")
            event.input.value = ""
            return

        try:
            journal_path = os.path.join(self.journals_path, journal_name)
            os.makedirs(journal_path, exist_ok=True)
            self.dismiss(journal_name)
        except Exception as e:
            self.query_one("#error_message", Label).update(
                f"Error creating journal: {str(e)}"
            )

    def get_existing_journals(self):
        return [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]
