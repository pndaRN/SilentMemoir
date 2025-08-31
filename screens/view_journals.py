from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem, Input
from textual.screen import Screen, ModalScreen
from textual.events import Key
from textual.containers import Vertical, Container

import os


class ViewJournals(Screen):
    journals_path = os.path.expanduser("~/.silentmemoir/journals")
    os.makedirs(journals_path, exist_ok=True)

    def on_key(self, event: Key):
        if event.key == "b":
            self.goto_entry()
        if event.key == "a":
            self.goto_journal()
        if event.key == "n":
            self.goto_new_journal()
        if event.key == "r":
            self.refresh_journals()

    def compose(self) -> ComposeResult:
        journals = self.get_journals()

        self.list_view = ListView(*[ListItem(Label(journal)) for journal in journals])

        with Vertical(id="journal_select"):
            yield Label("Select a Journal")
            yield self.list_view
            yield Label("Press 'a' to accept the journal to view")
            yield Label("Press 'n' to create a new journal")
            yield Label("Press 'r' to refresh")
            yield Label("Press 'b' to go back")

    def goto_entry(self):
        self.app.push_screen("Opening Screen")

    def goto_journal(self):
        self.app.push_screen("Journal Entries")

    def goto_new_journal(self):
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
