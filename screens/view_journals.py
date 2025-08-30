from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem
from textual.screen import Screen, ModalScreen
from textual.events import Key
from textual.containers import Vertical, Horizontal

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

    def compose(self) -> ComposeResult:
        journals = [
            d
            for d in os.listdir(self.journals_path)
            if os.path.isdir(os.path.join(self.journals_path, d))
        ]

        self.list_view = ListView(*[ListItem(Label(journal)) for journal in journals])

        with Vertical(id="journal_select"):
            yield Label("Select a Journal")
            yield self.list_view
            yield Label("Press 'a' to accept the journal to view")
            yield Label("Press 'n' to create a new journal")
            yield Label("Press 'b' to go back")

    def goto_entry(self):
        self.app.push_screen("Opening Screen")

    def goto_journal(self):
        self.app.push_screen("Journal Entries")

    def goto_new_journal(self):
        self.app.push_screen(NewJournal())


class NewJournal(ModalScreen):
    def compose(self) -> ComposeResult:
        with Horizontal(id="new_journal"):
            yield Label("THIS IS A TEST")


# Fixing the overlay
