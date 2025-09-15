from textual.app import App

from screens.opening_screen import OpeningScreen
from screens.view_journals import ViewJournals
from screens.entry import Entry


class SilentMemoir(App):
    CSS_PATH = "assests/css.tcss"

    SCREENS = {
        "Entry Editor": Entry,
        "Opening Screen": OpeningScreen,
        "View Journals": ViewJournals,
    }

    def on_mount(self):
        self.push_screen("Opening Screen")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = SilentMemoir()
    app.run()
