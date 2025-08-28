from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key


class JournalEntries(Screen):
    def on_key(self, event: Key):
        if event.key == "b":
            self.goto_view_journals()
        elif event.key == "a":
            self.goto_entry_editor()

    def compose(self) -> ComposeResult:
        yield Label("This is the journal entries view")
        yield Label("Press 'a' to select entry")
        yield Label("Press 'b' to go back (View Journals)")

    def goto_view_journals(self):
        self.app.push_screen("View Journals")

    def goto_entry_editor(self):
        self.app.push_screen("Entry Editor")
