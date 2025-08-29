from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key


class ViewJournals(Screen):
    def on_key(self, event: Key):
        if event.key == "b":
            self.goto_entry()
        if event.key == "a":
            self.goto_journal()

    def compose(self) -> ComposeResult:
        yield Label("This is the journal view")
        yield Label("Press 'a' to accept the journal to view")
        yield Label("Press 'b' to go back")

    def goto_entry(self):
        self.app.push_screen("Opening Screen")

    def goto_journal(self):
        self.app.push_screen("Journal Entries")
