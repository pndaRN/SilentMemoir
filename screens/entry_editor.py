from textual.app import App, ComposeResult 
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key

class EntryEditor(Screen):

    def on_key(self, event: Key):
        if event.key == "b":
            self.goto_journal_entries()

    def compose(self) -> ComposeResult:
        yield Label("This is the entry editor")
        yield Label("Press 'b' to go back (Journal Entries)")
    
    def goto_journal_entries(self):
        self.app.push_screen("Journal Entries")
        
