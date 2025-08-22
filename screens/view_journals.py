from textual.app import App, ComposeResult 
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key

class ViewJournals(Screen):

    def on_key(self, event: Key):
        if event.key == "e":
            self.enter()

    def compose(self) -> ComposeResult:
        yield Label("This is the journal view")
        yield Label("Press 'e' to go back")
    
    def enter(self):
        self.app.push_screen("Opening Screen")
