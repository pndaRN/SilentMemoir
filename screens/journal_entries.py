from textual.app import App, ComposeResult 
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key

class JournalEntries(Screen):

    def on_key(self, event: Key):
        if event.key == "b":
            self.goto_view_journals()

    def compose(self) -> ComposeResult:
        yield Label("This is the journal entries view")
        yield Label("Press 'b' to go back (View Journals)")
    
    def goto_view_journals(self):
        self.app.push_screen("View Journals")
